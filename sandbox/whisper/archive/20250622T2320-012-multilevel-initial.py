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
    level: str  # 'short', 'medium', 'long'

class MultiLevelBuffer:
    """マルチレベルの音声バッファ管理"""
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        
        # 各レベルのバッファ（秒単位）
        self.levels = {
            'short': {'duration': 2.0, 'overlap': 0.5},   # 高速レスポンス用
            'medium': {'duration': 5.0, 'overlap': 1.0},  # バランス型
            'long': {'duration': 15.0, 'overlap': 2.0}    # 高精度用
        }
        
        # 各レベルのバッファ
        self.buffers = {
            level: deque(maxlen=int(config['duration'] * sample_rate * 2))
            for level, config in self.levels.items()
        }
        
        # 最後に処理したサンプル数
        self.last_processed = {level: 0 for level in self.levels}
        self.total_samples = 0
        
    def add_audio(self, audio_data: np.ndarray):
        """音声データを全レベルのバッファに追加"""
        for buffer in self.buffers.values():
            buffer.extend(audio_data)
        self.total_samples += len(audio_data)
        
    def get_chunks_to_process(self) -> List[AudioChunk]:
        """処理すべきチャンクを取得"""
        chunks = []
        
        for level, config in self.levels.items():
            samples_needed = int(config['duration'] * self.sample_rate)
            samples_since_last = self.total_samples - self.last_processed[level]
            samples_step = samples_needed - int(config['overlap'] * self.sample_rate)
            
            # このレベルで処理が必要か判定
            if samples_since_last >= samples_step and len(self.buffers[level]) >= samples_needed:
                # バッファから必要な分を取得
                audio_data = list(self.buffers[level])[-samples_needed:]
                
                chunk = AudioChunk(
                    audio=np.array(audio_data),
                    timestamp=time.time(),
                    duration=len(audio_data) / self.sample_rate,
                    level=level
                )
                chunks.append(chunk)
                self.last_processed[level] = self.total_samples
                
        return chunks

class TranscriptionWorker(mp.Process):
    """文字起こし専用プロセス"""
    def __init__(self, model_name: str, input_queue: mp.Queue, output_queue: mp.Queue):
        super().__init__()
        self.model_name = model_name
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.daemon = True
        
    def run(self):
        """プロセスのメインループ"""
        # プロセス内でモデルをロード（プロセス間でモデルを共有できないため）
        print(f"[Worker] Whisperモデル '{self.model_name}' をロード中...")
        model = whisper.load_model(self.model_name)
        print("[Worker] モデルのロード完了！")
        
        while True:
            try:
                # タスクを取得
                task = self.input_queue.get(timeout=1)
                
                if task is None:  # 終了シグナル
                    break
                    
                # 音声ファイルを文字起こし
                start_time = time.time()
                result = model.transcribe(
                    task['audio_file'],
                    language="ja",
                    fp16=False,
                    initial_prompt=task.get('prompt', None)
                )
                transcribe_time = time.time() - start_time
                
                # 結果を返す
                self.output_queue.put({
                    'text': result['text'].strip(),
                    'segments': result.get('segments', []),
                    'level': task['level'],
                    'timestamp': task['timestamp'],
                    'duration': task['duration'],
                    'transcribe_time': transcribe_time
                })
                
                # 一時ファイルを削除
                if os.path.exists(task['audio_file']):
                    os.unlink(task['audio_file'])
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Worker] エラー: {e}")

class MultiLevelTranscriber:
    """マルチレベル音声認識システム"""
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
        # 終了シグナルを送信
        for _ in self.workers:
            self.task_queue.put(None)
            
        # プロセスの終了を待つ
        for worker in self.workers:
            worker.join(timeout=5)
            if worker.is_alive():
                worker.terminate()
                
    def save_audio_chunk(self, chunk: AudioChunk) -> str:
        """音声チャンクを一時ファイルに保存"""
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
        
        print("\n🎤 マルチレベル録音を開始... (Ctrl+Cで終了)")
        print("📊 レベル: short(2秒) / medium(5秒) / long(15秒)")
        print("-" * 80)
        
        try:
            while self.is_running:
                # 音声データを読み取り
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                
                # バッファに追加
                self.buffer.add_audio(audio_chunk)
                
                # 処理すべきチャンクを確認
                chunks_to_process = self.buffer.get_chunks_to_process()
                
                for chunk in chunks_to_process:
                    # 音声ファイルを保存
                    audio_file = self.save_audio_chunk(chunk)
                    
                    # 前の結果から文脈を取得
                    prompt = self.get_context_prompt(chunk.level)
                    
                    # タスクをキューに追加
                    try:
                        self.task_queue.put_nowait({
                            'audio_file': audio_file,
                            'level': chunk.level,
                            'timestamp': chunk.timestamp,
                            'duration': chunk.duration,
                            'prompt': prompt
                        })
                        print(f"\r📤 [{chunk.level}] チャンク送信", end="", flush=True)
                    except queue.Full:
                        print(f"\n⚠️ キューが満杯です。スキップします。")
                        os.unlink(audio_file)
                        
        finally:
            stream.stop_stream()
            stream.close()
            
    def get_context_prompt(self, level: str) -> Optional[str]:
        """文脈としての前回の結果を取得"""
        # より詳細なレベルの結果を文脈として使用
        if level == 'medium' and self.results_by_level['short']:
            return self.results_by_level['short'][-1]['text'][-100:]
        elif level == 'long' and self.results_by_level['medium']:
            return self.results_by_level['medium'][-1]['text'][-200:]
        return None
        
    def result_handler_thread(self):
        """結果処理スレッド"""
        while self.is_running or not self.result_queue.empty():
            try:
                result = self.result_queue.get(timeout=1)
                
                # レベル別に結果を保存
                self.results_by_level[result['level']].append(result)
                
                # 結果を表示
                self.display_result(result)
                
            except queue.Empty:
                continue
                
    def display_result(self, result):
        """結果を表示"""
        level_emoji = {
            'short': '🏃',  # 速報
            'medium': '🚶', # 標準
            'long': '🎯'    # 確定
        }
        
        emoji = level_emoji.get(result['level'], '❓')
        speed = result['duration'] / result['transcribe_time']
        
        print(f"\n{emoji} [{result['level']:6}] {result['text']}")
        print(f"   音声: {result['duration']:.1f}秒 / 処理: {result['transcribe_time']:.1f}秒 (速度: {speed:.1f}倍)")
        
        # longレベルの場合、前のレベルとの差分を表示
        if result['level'] == 'long' and self.results_by_level['medium']:
            print("   📈 精度向上: より長い文脈で再認識しました")
            
        print("-" * 80)
        
    def run(self):
        """メインループ"""
        self.is_running = True
        
        # ワーカープロセスを起動
        self.start_workers()
        
        # 録音スレッド
        record_thread = threading.Thread(target=self.recording_thread)
        record_thread.daemon = True
        record_thread.start()
        
        # 結果処理スレッド
        result_thread = threading.Thread(target=self.result_handler_thread)
        result_thread.daemon = True
        result_thread.start()
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\n👋 終了処理中...")
            self.is_running = False
            
            # スレッドの終了を待つ
            record_thread.join(timeout=2)
            result_thread.join(timeout=5)
            
            # ワーカープロセスを停止
            self.stop_workers()
            
            print("✅ 終了しました")
            
        finally:
            self.p.terminate()

def main():
    print("=== Whisper マルチレベル音声認識 ===")
    print("複数の時間スケールで並列認識を行います")
    
    # パラメータ設定
    model_name = "small"
    num_workers = 2  # 並列処理数
    
    print(f"\n設定:")
    print(f"- モデル: {model_name}")
    print(f"- ワーカー数: {num_workers}")
    print(f"- レベル: short(2秒) / medium(5秒) / long(15秒)")
    
    # マルチレベル認識を開始
    transcriber = MultiLevelTranscriber(
        model_name=model_name,
        num_workers=num_workers
    )
    
    transcriber.run()

if __name__ == "__main__":
    main()