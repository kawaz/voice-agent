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
from typing import List, Tuple, Optional

@dataclass
class AudioChunk:
    """音声チャンクのデータクラス"""
    audio: np.ndarray
    timestamp: float
    duration: float
    level: str
    rms: float  # 音量レベル

class AudioAnalyzer:
    """音声分析ユーティリティ"""
    @staticmethod
    def calculate_rms(audio_data: np.ndarray) -> float:
        """RMS（音量）を計算"""
        if len(audio_data) == 0:
            return 0
        return np.sqrt(np.mean(audio_data.astype(np.float32)**2))
    
    @staticmethod
    def is_speech(audio_data: np.ndarray, threshold: float = 300) -> bool:
        """音声かどうかを判定"""
        rms = AudioAnalyzer.calculate_rms(audio_data)
        return rms > threshold
    
    @staticmethod
    def get_energy_ratio(audio_data: np.ndarray) -> float:
        """エネルギー比率を計算（無音部分の割合）"""
        # フレームごとのエネルギーを計算
        frame_size = 1024
        energies = []
        
        for i in range(0, len(audio_data) - frame_size, frame_size):
            frame = audio_data[i:i+frame_size]
            energy = np.sum(frame.astype(np.float32)**2)
            energies.append(energy)
        
        if not energies:
            return 0
            
        # 低エネルギーフレームの割合
        threshold = np.percentile(energies, 30)
        low_energy_frames = sum(1 for e in energies if e < threshold)
        return low_energy_frames / len(energies)

class MultiLevelBuffer:
    """改良版マルチレベルバッファ"""
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        
        # 各レベルの設定（音声検出閾値を追加）
        self.levels = {
            'short': {
                'duration': 2.0, 
                'overlap': 0.5,
                'min_speech_ratio': 0.3  # 30%以上音声がある場合のみ処理
            },
            'medium': {
                'duration': 5.0, 
                'overlap': 1.0,
                'min_speech_ratio': 0.2  # 20%以上
            },
            'long': {
                'duration': 15.0, 
                'overlap': 2.0,
                'min_speech_ratio': 0.1  # 10%以上
            }
        }
        
        self.buffers = {
            level: deque(maxlen=int(config['duration'] * sample_rate * 2))
            for level, config in self.levels.items()
        }
        
        self.last_processed = {level: 0 for level in self.levels}
        self.total_samples = 0
        
    def add_audio(self, audio_data: np.ndarray):
        """音声データを追加"""
        for buffer in self.buffers.values():
            buffer.extend(audio_data)
        self.total_samples += len(audio_data)
        
    def get_chunks_to_process(self) -> List[AudioChunk]:
        """処理すべきチャンクを取得（音声検出付き）"""
        chunks = []
        
        for level, config in self.levels.items():
            samples_needed = int(config['duration'] * self.sample_rate)
            samples_since_last = self.total_samples - self.last_processed[level]
            samples_step = samples_needed - int(config['overlap'] * self.sample_rate)
            
            if samples_since_last >= samples_step and len(self.buffers[level]) >= samples_needed:
                # バッファから音声データを取得
                audio_data = np.array(list(self.buffers[level])[-samples_needed:])
                
                # 音声分析
                rms = AudioAnalyzer.calculate_rms(audio_data)
                energy_ratio = AudioAnalyzer.get_energy_ratio(audio_data)
                speech_ratio = 1 - energy_ratio
                
                # 音声が十分含まれている場合のみ処理
                if speech_ratio >= config['min_speech_ratio'] and rms > 200:
                    chunk = AudioChunk(
                        audio=audio_data,
                        timestamp=time.time(),
                        duration=len(audio_data) / self.sample_rate,
                        level=level,
                        rms=rms
                    )
                    chunks.append(chunk)
                    self.last_processed[level] = self.total_samples
                else:
                    # 無音が多い場合はスキップ（ただしカウンタは更新）
                    if level == 'short':  # shortレベルのみログ表示
                        print(f"\r🔇 無音スキップ (音声比率: {speech_ratio:.0%}, RMS: {rms:.0f})", end="", flush=True)
                    self.last_processed[level] = self.total_samples
                
        return chunks

class TranscriptionWorker(mp.Process):
    """改良版文字起こしワーカー"""
    def __init__(self, model_name: str, input_queue: mp.Queue, output_queue: mp.Queue):
        super().__init__()
        self.model_name = model_name
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.daemon = True
        
    def run(self):
        """プロセスのメインループ"""
        print(f"[Worker-{os.getpid()}] Whisperモデル '{self.model_name}' をロード中...")
        model = whisper.load_model(self.model_name)
        print(f"[Worker-{os.getpid()}] モデルのロード完了！")
        
        # 既知の誤認識パターン
        false_positives = [
            "ご視聴ありがとうございました",
            "字幕制作者",
            "提供",
            "ありがとうございました",
            "ご視聴ありがとうございます"
        ]
        
        while True:
            try:
                task = self.input_queue.get(timeout=1)
                
                if task is None:
                    break
                    
                # 音声ファイルを文字起こし
                start_time = time.time()
                
                # 音声レベルに応じた設定
                options = {
                    'language': 'ja',
                    'fp16': False,
                    'temperature': 0.0,  # より決定的な出力
                    'compression_ratio_threshold': 2.4,  # 圧縮率が高い場合は無効
                    'logprob_threshold': -1.0,  # 信頼度の低い結果を除外
                    'no_speech_threshold': 0.6  # 無音検出の閾値
                }
                
                # 文脈がある場合は追加
                if task.get('prompt'):
                    options['initial_prompt'] = task['prompt']
                    
                result = model.transcribe(task['audio_file'], **options)
                transcribe_time = time.time() - start_time
                
                # 結果のフィルタリング
                text = result['text'].strip()
                
                # 既知の誤認識を除外
                for fp in false_positives:
                    if fp in text and len(text) < len(fp) * 1.5:
                        text = ""
                        break
                
                # 圧縮率チェック（同じ文字の繰り返しを検出）
                if text and result.get('compression_ratio', 0) > 2.4:
                    text = ""
                    
                # 結果を返す
                self.output_queue.put({
                    'text': text,
                    'segments': result.get('segments', []),
                    'level': task['level'],
                    'timestamp': task['timestamp'],
                    'duration': task['duration'],
                    'transcribe_time': transcribe_time,
                    'rms': task['rms'],
                    'no_speech_prob': result.get('no_speech_prob', 0)
                })
                
                # 一時ファイルを削除
                if os.path.exists(task['audio_file']):
                    os.unlink(task['audio_file'])
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Worker-{os.getpid()}] エラー: {e}")

class MultiLevelTranscriber:
    """改良版マルチレベル音声認識"""
    def __init__(self, model_name="small", num_workers=2):
        self.model_name = model_name
        self.num_workers = num_workers
        self.sample_rate = 16000
        self.chunk_size = 1024
        
        # PyAudio初期化
        self.p = pyaudio.PyAudio()
        
        # マルチレベルバッファ
        self.buffer = MultiLevelBuffer(self.sample_rate)
        
        # マルチプロセス用のキュー
        self.task_queue = mp.Queue(maxsize=10)
        self.result_queue = mp.Queue()
        
        # ワーカープロセス
        self.workers = []
        
        # 結果管理
        self.results_by_level = {
            'short': deque(maxlen=10),
            'medium': deque(maxlen=5),
            'long': deque(maxlen=2)
        }
        
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
        for _ in self.workers:
            self.task_queue.put(None)
            
        for worker in self.workers:
            worker.join(timeout=5)
            if worker.is_alive():
                worker.terminate()
                
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
        
        print("\n🎤 改良版マルチレベル録音を開始... (Ctrl+Cで終了)")
        print("📊 レベル: short(2秒) / medium(5秒) / long(15秒)")
        print("🔇 無音は自動的にスキップされます")
        print("-" * 80)
        
        try:
            while self.is_running:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                
                # バッファに追加
                self.buffer.add_audio(audio_chunk)
                
                # 処理すべきチャンクを確認
                chunks_to_process = self.buffer.get_chunks_to_process()
                
                for chunk in chunks_to_process:
                    audio_file = self.save_audio_chunk(chunk)
                    
                    # 前の結果から文脈を取得（誤認識は除外）
                    prompt = self.get_clean_context(chunk.level)
                    
                    try:
                        self.task_queue.put_nowait({
                            'audio_file': audio_file,
                            'level': chunk.level,
                            'timestamp': chunk.timestamp,
                            'duration': chunk.duration,
                            'prompt': prompt,
                            'rms': chunk.rms
                        })
                        print(f"\r📤 [{chunk.level}] チャンク送信 (RMS: {chunk.rms:.0f})", end="", flush=True)
                    except queue.Full:
                        print(f"\n⚠️ キューが満杯です。スキップします。")
                        os.unlink(audio_file)
                        
        finally:
            stream.stop_stream()
            stream.close()
            
    def get_clean_context(self, level: str) -> Optional[str]:
        """クリーンな文脈を取得（誤認識を除外）"""
        context_map = {
            'medium': ('short', 100),
            'long': ('medium', 200)
        }
        
        if level in context_map:
            source_level, max_chars = context_map[level]
            if self.results_by_level[source_level]:
                # 最新の有効な結果を探す
                for result in reversed(self.results_by_level[source_level]):
                    if result['text'] and result.get('no_speech_prob', 0) < 0.5:
                        return result['text'][-max_chars:]
        return None
        
    def result_handler_thread(self):
        """結果処理スレッド"""
        while self.is_running or not self.result_queue.empty():
            try:
                result = self.result_queue.get(timeout=1)
                
                # 有効な結果のみ保存・表示
                if result['text']:
                    self.results_by_level[result['level']].append(result)
                    self.display_result(result)
                    
            except queue.Empty:
                continue
                
    def display_result(self, result):
        """結果を表示"""
        level_emoji = {
            'short': '🏃',
            'medium': '🚶',
            'long': '🎯'
        }
        
        emoji = level_emoji.get(result['level'], '❓')
        speed = result['duration'] / result['transcribe_time']
        
        print(f"\n{emoji} [{result['level']:6}] {result['text']}")
        print(f"   音声: {result['duration']:.1f}秒 / 処理: {result['transcribe_time']:.1f}秒 (速度: {speed:.1f}倍) / RMS: {result['rms']:.0f}")
        
        if result['level'] == 'long' and self.results_by_level['medium']:
            print("   📈 精度向上: より長い文脈で再認識しました")
            
        print("-" * 80)
        
    def run(self):
        """メインループ"""
        self.is_running = True
        
        # ワーカープロセスを起動
        self.start_workers()
        
        # 各スレッドを起動
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
            print("\n\n👋 終了処理中...")
            self.is_running = False
            
            record_thread.join(timeout=2)
            result_thread.join(timeout=5)
            self.stop_workers()
            
            print("✅ 終了しました")
            
        finally:
            self.p.terminate()

def main():
    print("=== Whisper マルチレベル音声認識 v2 ===")
    print("無音検出と誤認識フィルタリング機能付き")
    
    model_name = "small"
    num_workers = 2
    
    print(f"\n設定:")
    print(f"- モデル: {model_name}")
    print(f"- ワーカー数: {num_workers}")
    print(f"- 自動無音スキップ: ON")
    print(f"- 誤認識フィルター: ON")
    
    transcriber = MultiLevelTranscriber(
        model_name=model_name,
        num_workers=num_workers
    )
    
    transcriber.run()

if __name__ == "__main__":
    main()