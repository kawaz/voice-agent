#!/usr/bin/env python3
import whisper
import pyaudio
import numpy as np
import wave
import tempfile
import os
import time
import threading
import queue
import multiprocessing as mp
from collections import deque
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import sys
import signal

# ANSIカラーコード
class Colors:
    SHORT = '\033[96m'    # シアン
    MEDIUM = '\033[93m'   # 黄色
    LONG = '\033[92m'     # 緑
    ULTRA = '\033[95m'    # マゼンタ
    RESET = '\033[0m'
    GRAY = '\033[90m'

@dataclass
class AudioChunk:
    """音声チャンクのデータクラス"""
    audio: np.ndarray
    timestamp: float
    start_time: float
    end_time: float
    duration: float
    level: str
    rms: float

class ContinuousRecorder:
    """連続録音バッファ（最大2分保持）"""
    def __init__(self, sample_rate=16000, max_duration=120):
        self.sample_rate = sample_rate
        self.max_duration = max_duration
        self.max_samples = int(max_duration * sample_rate)
        self.buffer = deque(maxlen=self.max_samples)
        self.start_timestamp = time.time()
        self.silence_start = None
        self.silence_threshold = 300
        self.silence_duration = 2.0  # 2秒の無音で区切り
        self.recording_start_time = 0  # 録音開始からの経過時間
        
    def add_audio(self, audio_data: np.ndarray) -> Optional[Tuple[np.ndarray, float, float]]:
        """音声を追加し、長い無音があれば区切りを返す"""
        self.buffer.extend(audio_data)
        
        # RMS計算
        rms = np.sqrt(np.mean(audio_data.astype(np.float32)**2))
        
        # 無音検出
        if rms < self.silence_threshold:
            if self.silence_start is None:
                self.silence_start = time.time()
            elif time.time() - self.silence_start > self.silence_duration:
                # 長い無音を検出 - 全体を返す
                if len(self.buffer) > self.sample_rate * 5:  # 5秒以上ある場合
                    audio_array = np.array(self.buffer)
                    duration = len(audio_array) / self.sample_rate
                    start_time = self.recording_start_time
                    result = (audio_array, start_time, duration)
                    # バッファをクリア
                    self.buffer.clear()
                    self.recording_start_time += duration
                    self.silence_start = None
                    return result
        else:
            self.silence_start = None
            
        return None
    
    def get_buffer_info(self) -> Dict[str, float]:
        """バッファ情報を取得"""
        current_duration = len(self.buffer) / self.sample_rate
        memory_mb = len(self.buffer) * 2 / (1024 * 1024)  # 16bit = 2bytes
        return {
            'duration': current_duration,
            'memory_mb': memory_mb,
            'usage_percent': (current_duration / self.max_duration) * 100
        }

class MultiLevelBuffer:
    """改良版マルチレベルバッファ"""
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.recording_start = time.time()
        
        # 各レベルの設定
        self.levels = {
            'short': {
                'duration': 3.0,
                'overlap': 1.0,
                'min_speech_ratio': 0.2
            },
            'medium': {
                'duration': 8.0,
                'overlap': 2.0,
                'min_speech_ratio': 0.15
            },
            'long': {
                'duration': 20.0,
                'overlap': 5.0,
                'min_speech_ratio': 0.1
            }
        }
        
        self.buffers = {
            level: deque(maxlen=int(config['duration'] * sample_rate * 2))
            for level, config in self.levels.items()
        }
        
        self.last_processed = {level: 0 for level in self.levels}
        self.total_samples = 0
        self.processed_texts = {}  # タイムスタンプごとの認識結果を保存
        self.segment_cache = {}  # レベル別のセグメント情報を保存
        
    def add_audio(self, audio_data: np.ndarray):
        """音声データを追加"""
        for buffer in self.buffers.values():
            buffer.extend(audio_data)
        self.total_samples += len(audio_data)
        
    def get_chunks_to_process(self) -> List[AudioChunk]:
        """処理すべきチャンクを取得"""
        chunks = []
        current_time = time.time()
        
        for level, config in self.levels.items():
            samples_needed = int(config['duration'] * self.sample_rate)
            samples_since_last = self.total_samples - self.last_processed[level]
            samples_step = samples_needed - int(config['overlap'] * self.sample_rate)
            
            if samples_since_last >= samples_step and len(self.buffers[level]) >= samples_needed:
                audio_data = np.array(list(self.buffers[level])[-samples_needed:])
                
                # 音声分析
                rms = np.sqrt(np.mean(audio_data.astype(np.float32)**2))
                
                # 開始・終了時刻を計算
                end_time = (self.total_samples / self.sample_rate)
                start_time = end_time - config['duration']
                
                if rms > 200:  # 最小閾値
                    chunk = AudioChunk(
                        audio=audio_data,
                        timestamp=current_time,
                        start_time=start_time,
                        end_time=end_time,
                        duration=config['duration'],
                        level=level,
                        rms=rms
                    )
                    chunks.append(chunk)
                    
                self.last_processed[level] = self.total_samples
                
        return chunks
    
    def get_buffer_info(self) -> Dict[str, Dict[str, float]]:
        """各レベルのバッファ情報"""
        info = {}
        for level, buffer in self.buffers.items():
            duration = len(buffer) / self.sample_rate
            memory_kb = len(buffer) * 2 / 1024
            info[level] = {
                'duration': duration,
                'memory_kb': memory_kb
            }
        return info

class TranscriptionWorker(mp.Process):
    """文字起こしワーカー"""
    def __init__(self, model_name: str, input_queue: mp.Queue, output_queue: mp.Queue):
        super().__init__()
        self.model_name = model_name
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.daemon = True
        self.shutdown = mp.Event()
        
    def run(self):
        """プロセスのメインループ"""
        # シグナルハンドラを無効化（メインプロセスのみで処理）
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        
        print(f"{Colors.GRAY}[Worker-{os.getpid()}] モデルロード中...{Colors.RESET}")
        model = whisper.load_model(self.model_name)
        print(f"{Colors.GRAY}[Worker-{os.getpid()}] 準備完了{Colors.RESET}")
        
        while not self.shutdown.is_set():
            try:
                task = self.input_queue.get(timeout=0.5)
                
                if task is None:
                    break
                    
                # 音声ファイルを文字起こし
                start_time = time.time()
                
                options = {
                    'language': 'ja',
                    'fp16': False,
                    'temperature': 0.0,
                    'compression_ratio_threshold': 2.0,  # より厳しく
                    'logprob_threshold': -1.0,
                    'no_speech_threshold': 0.7,  # より厳しく
                    'condition_on_previous_text': False  # 前の文脈の影響を減らす
                }
                
                result = model.transcribe(task['audio_file'], **options)
                transcribe_time = time.time() - start_time
                
                # テキストの後処理
                text = result['text'].strip()
                
                # 繰り返しの検出と除去
                if text:
                    text = self.remove_repetitions(text)
                    
                # 圧縮率が高すぎる場合は無効
                if result.get('compression_ratio', 0) > 2.0:
                    text = ""
                    
                # セグメント情報も処理
                segments = []
                if task['level'] in ['long', 'ultra'] and result.get('segments'):
                    for seg in result['segments']:
                        if seg.get('no_speech_prob', 0) < 0.7:  # 音声がある可能性が高い
                            segments.append({
                                'start': task['start_time'] + seg['start'],
                                'end': task['start_time'] + seg['end'],
                                'text': seg['text'].strip()
                            })
                
                # 結果を返す
                self.output_queue.put({
                    'text': text,
                    'segments': segments,
                    'level': task['level'],
                    'start_time': task['start_time'],
                    'end_time': task['end_time'],
                    'duration': task['duration'],
                    'transcribe_time': transcribe_time,
                    'rms': task['rms']
                })
                
                # 一時ファイルを削除
                if os.path.exists(task['audio_file']):
                    os.unlink(task['audio_file'])
                    
            except queue.Empty:
                continue
            except Exception as e:
                if not self.shutdown.is_set():
                    print(f"\n{Colors.GRAY}[Worker] エラー: {e}{Colors.RESET}")
    
    def remove_repetitions(self, text: str) -> str:
        """繰り返しを除去"""
        # 同じフレーズの繰り返しを検出
        words = text.split()
        if len(words) < 10:
            return text
            
        # 繰り返しパターンを検出
        for pattern_len in range(2, min(10, len(words) // 2)):
            pattern = words[:pattern_len]
            is_repetition = True
            
            for i in range(pattern_len, len(words), pattern_len):
                if words[i:i+pattern_len] != pattern[:min(pattern_len, len(words)-i)]:
                    is_repetition = False
                    break
                    
            if is_repetition:
                return ' '.join(pattern)
                
        return text
    
    def stop(self):
        """ワーカーを停止"""
        self.shutdown.set()

class AdvancedTranscriber:
    """高度な音声認識システム"""
    def __init__(self, model_name="small", num_workers=2):
        self.model_name = model_name
        self.num_workers = num_workers
        self.sample_rate = 16000
        self.chunk_size = 1024
        
        # PyAudio初期化
        self.p = pyaudio.PyAudio()
        
        # バッファ
        self.multilevel_buffer = MultiLevelBuffer(self.sample_rate)
        self.continuous_recorder = ContinuousRecorder(self.sample_rate)
        
        # マルチプロセス
        self.task_queue = mp.Queue(maxsize=10)
        self.result_queue = mp.Queue()
        self.workers = []
        
        # 結果管理
        self.all_results = []
        self.is_running = False
        
    def start_workers(self):
        """ワーカープロセスを起動"""
        for i in range(self.num_workers):
            worker = TranscriptionWorker(
                self.model_name,
                self.task_queue,
                self.result_queue
            )
            worker.start()
            self.workers.append(worker)
            
    def stop_workers(self):
        """ワーカープロセスを停止"""
        # 停止シグナルを送信
        for worker in self.workers:
            if hasattr(worker, 'stop'):
                worker.stop()
        
        # 終了シグナルを送信
        for _ in self.workers:
            try:
                self.task_queue.put(None, timeout=1)
            except:
                pass
                
        # プロセスの終了を待つ
        for worker in self.workers:
            worker.join(timeout=3)
            if worker.is_alive():
                worker.terminate()
                worker.join(timeout=1)
                
    def save_audio_chunk(self, chunk: AudioChunk) -> str:
        """音声チャンクを保存"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_filename = tmp_file.name
            
        with wave.open(tmp_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(chunk.audio.astype(np.int16).tobytes())
            
        return tmp_filename
        
    def recording_thread(self):
        """録音スレッド"""
        stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        print(f"\n🎤 高度な音声認識を開始... (Ctrl+Cで終了)")
        print(f"📊 レベル: {Colors.SHORT}■ short(3s){Colors.RESET} / {Colors.MEDIUM}■ medium(8s){Colors.RESET} / {Colors.LONG}■ long(20s){Colors.RESET} / {Colors.ULTRA}■ ultra(無音区切り){Colors.RESET}")
        print("-" * 100)
        
        try:
            while self.is_running:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                
                # 両方のバッファに追加
                self.multilevel_buffer.add_audio(audio_chunk)
                ultra_result = self.continuous_recorder.add_audio(audio_chunk)
                
                # 超長期録音の処理
                if ultra_result:
                    audio_array, start_time, duration = ultra_result
                    print(f"\n{Colors.ULTRA}🎯 長期録音検出！ ({duration:.1f}秒の録音を処理){Colors.RESET}")
                    
                    # Ultraレベルとして処理
                    chunk = AudioChunk(
                        audio=audio_array,
                        timestamp=time.time(),
                        start_time=start_time,
                        end_time=start_time + duration,
                        duration=duration,
                        level='ultra',
                        rms=np.sqrt(np.mean(audio_array.astype(np.float32)**2))
                    )
                    
                    audio_file = self.save_audio_chunk(chunk)
                    try:
                        self.task_queue.put_nowait({
                            'audio_file': audio_file,
                            'level': 'ultra',
                            'start_time': start_time,
                            'end_time': start_time + duration,
                            'duration': duration,
                            'rms': chunk.rms
                        })
                    except queue.Full:
                        os.unlink(audio_file)
                
                # 通常のマルチレベル処理
                chunks_to_process = self.multilevel_buffer.get_chunks_to_process()
                
                for chunk in chunks_to_process:
                    audio_file = self.save_audio_chunk(chunk)
                    
                    try:
                        self.task_queue.put_nowait({
                            'audio_file': audio_file,
                            'level': chunk.level,
                            'start_time': chunk.start_time,
                            'end_time': chunk.end_time,
                            'duration': chunk.duration,
                            'rms': chunk.rms
                        })
                    except queue.Full:
                        os.unlink(audio_file)
                        
                # バッファ情報を定期的に更新（1秒ごと）
                if int(time.time()) % 1 == 0:
                    self.update_status_line()
                        
        except Exception as e:
            if self.is_running:
                print(f"\n録音エラー: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            
    def update_status_line(self):
        """ステータスラインを更新"""
        ml_info = self.multilevel_buffer.get_buffer_info()
        cont_info = self.continuous_recorder.get_buffer_info()
        
        status = f"\r📊 バッファ: "
        for level, info in ml_info.items():
            status += f"{level[:1]}:{info['memory_kb']:.0f}KB "
        status += f"| 連続:{cont_info['memory_mb']:.1f}MB({cont_info['usage_percent']:.0f}%) "
        
        print(status, end="", flush=True)
            
    def result_handler_thread(self):
        """結果処理スレッド"""
        while self.is_running or not self.result_queue.empty():
            try:
                result = self.result_queue.get(timeout=0.5)
                
                if result['text']:
                    self.all_results.append(result)
                    self.display_result(result)
                    
                    # セグメント情報をキャッシュに保存
                    if result['segments']:
                        self.multilevel_buffer.segment_cache[result['level']] = result['segments']
                    
            except queue.Empty:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"\n結果処理エラー: {e}")
                
    def display_result(self, result):
        """結果を表示（改良版）"""
        # レベルごとの色とアイコン
        level_config = {
            'short': (Colors.SHORT, '●'),
            'medium': (Colors.MEDIUM, '◆'),
            'long': (Colors.LONG, '■'),
            'ultra': (Colors.ULTRA, '★')
        }
        
        color, icon = level_config.get(result['level'], (Colors.RESET, '?'))
        
        # セグメントがある場合は複数行で表示
        if result['segments'] and len(result['segments']) > 1:
            # ヘッダー行
            meta = f"{icon} [{result['start_time']:6.1f}s-{result['end_time']:6.1f}s] {result['duration']:4.1f}s/{result['transcribe_time']:3.1f}s"
            print(f"\n{meta} | {color}[セグメント表示]{Colors.RESET}")
            
            # 各セグメントを表示
            for seg in result['segments']:
                if seg['text']:
                    seg_time = f"  [{seg['start']:6.1f}s-{seg['end']:6.1f}s]"
                    print(f"{seg_time} {color}{seg['text']}{Colors.RESET}")
        else:
            # 通常の1行表示
            timestamp = f"[{result['start_time']:6.1f}s-{result['end_time']:6.1f}s]"
            meta = f"{icon} {timestamp} {result['duration']:4.1f}s/{result['transcribe_time']:3.1f}s"
            text = f"{color}{result['text']}{Colors.RESET}"
            print(f"\n{meta} | {text}")
        
    def run(self):
        """メインループ"""
        self.is_running = True
        
        self.start_workers()
        
        record_thread = threading.Thread(target=self.recording_thread)
        record_thread.daemon = True
        record_thread.start()
        
        result_thread = threading.Thread(target=self.result_handler_thread)
        result_thread.daemon = True
        result_thread.start()
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(f"\n\n{Colors.GRAY}👋 終了処理中...{Colors.RESET}")
            self.is_running = False
            
            # スレッドの終了を待つ
            record_thread.join(timeout=2)
            result_thread.join(timeout=3)
            
            # ワーカーを停止
            self.stop_workers()
            
            print(f"{Colors.GRAY}✅ 終了しました{Colors.RESET}")
            
        finally:
            self.p.terminate()

def main():
    print("=== 高度な音声認識システム（最終版）===")
    
    model_name = "small"
    num_workers = 2
    
    print(f"設定: モデル={model_name}, ワーカー={num_workers}")
    
    transcriber = AdvancedTranscriber(
        model_name=model_name,
        num_workers=num_workers
    )
    
    transcriber.run()

if __name__ == "__main__":
    main()