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
from collections import deque

class RealtimeTranscriber:
    def __init__(self, model_name="small", silence_threshold=250, silence_duration=1.2, chunk_duration=5.0):
        """
        リアルタイム音声認識システム（改良版）
        
        Args:
            model_name: Whisperモデル名
            silence_threshold: 無音判定の閾値
            silence_duration: 無音継続時間（秒）で録音を区切る
            chunk_duration: 最大録音時間（秒）- この時間で強制的に区切る
        """
        print(f"🤖 Whisperモデル '{model_name}' をロード中...")
        self.model = whisper.load_model(model_name)
        print("✅ モデルのロード完了！")
        
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.chunk_duration = chunk_duration
        
        # PyAudio初期化
        self.p = pyaudio.PyAudio()
        
        # 音声データのキュー
        self.audio_queue = queue.Queue()
        self.is_running = False
        
        # 音量レベルの統計
        self.volume_history = deque(maxlen=50)
        
    def calculate_rms(self, data):
        """音声データのRMS（Root Mean Square：二乗平均平方根）を計算"""
        try:
            audio_data = np.frombuffer(data, dtype=np.int16)
            if len(audio_data) == 0:
                return 0
            mean_square = np.mean(audio_data.astype(np.float32)**2)
            if mean_square < 0:
                return 0
            return np.sqrt(mean_square)
        except:
            return 0
    
    def print_volume_meter(self, rms, is_recording=False):
        """音量メーターを表示"""
        max_level = 50
        level = min(int(rms / 100), max_level)
        bar = "█" * level + "░" * (max_level - level)
        
        if is_recording:
            status = "🔴 録音中..."
        else:
            status = "🔇 無音" if rms < self.silence_threshold else "🔊 音声検出"
        
        print(f"\r音量: [{bar}] RMS: {rms:>6.0f} {status}   ", end="", flush=True)
    
    def get_audio_duration(self, frames):
        """音声データの長さを秒単位で計算"""
        total_samples = len(frames) * self.chunk_size
        duration = total_samples / self.sample_rate
        return duration
    
    def record_audio_chunk(self):
        """音声チャンクを録音して無音検出"""
        stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        print("\n🎤 録音を開始します... (Ctrl+Cで終了)")
        print("話すと自動的に認識されます")
        print(f"RMS = Root Mean Square（二乗平均平方根）: 音量レベルの指標")
        print("-" * 80)
        
        frames = []
        silence_chunks = 0
        chunks_per_second = self.sample_rate / self.chunk_size
        silence_chunks_needed = int(self.silence_duration * chunks_per_second)
        max_chunks = int(self.chunk_duration * chunks_per_second)
        is_speaking = False
        recording_start_time = None
        
        try:
            while self.is_running:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                rms = self.calculate_rms(data)
                
                # 音量履歴を記録
                self.volume_history.append(rms)
                
                # 音声検出
                if rms > self.silence_threshold:
                    if not is_speaking:
                        print(f"\n🔊 音声検出！録音中... (RMS: {rms:.0f})")
                        is_speaking = True
                        recording_start_time = time.time()
                    frames.append(data)
                    silence_chunks = 0
                    
                    # 最大録音時間チェック
                    if len(frames) >= max_chunks:
                        print(f"\n⏱️ 最大録音時間（{self.chunk_duration}秒）に達しました")
                        self._process_audio(frames, recording_start_time)
                        frames = []
                        silence_chunks = 0
                        is_speaking = False
                        recording_start_time = None
                    
                elif is_speaking:
                    # 話している最中の無音
                    frames.append(data)
                    silence_chunks += 1
                    
                    # 無音が一定時間続いたら録音終了
                    if silence_chunks > silence_chunks_needed:
                        print(" ✅ 録音完了！")
                        self._process_audio(frames, recording_start_time)
                        frames = []
                        silence_chunks = 0
                        is_speaking = False
                        recording_start_time = None
                else:
                    # 録音していない時は音量メーターを表示
                    self.print_volume_meter(rms, is_recording=False)
                        
        finally:
            stream.stop_stream()
            stream.close()
    
    def _process_audio(self, frames, start_time):
        """音声データを処理してキューに追加"""
        if len(frames) > self.sample_rate / self.chunk_size:  # 1秒以上の音声のみ
            audio_duration = self.get_audio_duration(frames)
            self.audio_queue.put((frames.copy(), audio_duration, start_time))
            
            # 統計情報を表示
            if self.volume_history:
                avg_volume = np.mean(list(self.volume_history))
                max_volume = max(self.volume_history)
                print(f"📊 音量統計 - 平均: {avg_volume:.0f}, 最大: {max_volume:.0f}")
                print(f"⏱️  録音時間: {audio_duration:.1f}秒")
                print("-" * 80)
    
    def save_audio(self, frames):
        """音声データを一時ファイルに保存"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_filename = tmp_file.name
            
        with wave.open(tmp_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))
            
        return tmp_filename
    
    def transcribe_worker(self):
        """文字起こしワーカー"""
        while self.is_running or not self.audio_queue.empty():
            try:
                # キューから音声データを取得
                frames, audio_duration, start_time = self.audio_queue.get(timeout=1)
                
                # 一時ファイルに保存
                audio_file = self.save_audio(frames)
                
                try:
                    # 文字起こし
                    print("🤔 認識中...", end="", flush=True)
                    transcribe_start = time.time()
                    result = self.model.transcribe(audio_file, language="ja", fp16=False)
                    transcribe_time = time.time() - transcribe_start
                    
                    # 結果表示
                    text = result["text"].strip()
                    if text:
                        print(f"\r📝 認識結果: {text}")
                        print(f"   音声長: {audio_duration:.1f}秒 / 処理時間: {transcribe_time:.1f}秒 (速度: {audio_duration/transcribe_time:.1f}倍)")
                        
                        # セグメント情報も表示（長い音声の場合）
                        if audio_duration > 10 and len(result["segments"]) > 1:
                            print("   セグメント:")
                            for seg in result["segments"][:5]:  # 最初の5セグメントまで
                                print(f"   [{seg['start']:.1f}s-{seg['end']:.1f}s] {seg['text']}")
                            if len(result["segments"]) > 5:
                                print(f"   ... 他 {len(result["segments"])-5} セグメント")
                        
                        print("-" * 80)
                    else:
                        print("\r❓ 認識できませんでした")
                        print("-" * 80)
                        
                except Exception as e:
                    if self.is_running:
                        print(f"\n認識エラー: {e}")
                finally:
                    # 一時ファイルの削除
                    if os.path.exists(audio_file):
                        os.unlink(audio_file)
                        
            except queue.Empty:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"\n処理エラー: {e}")
    
    def run(self):
        """連続音声認識を開始"""
        self.is_running = True
        
        # 録音スレッドを開始
        record_thread = threading.Thread(target=self.record_audio_chunk)
        record_thread.daemon = True
        record_thread.start()
        
        # 文字起こしスレッドを開始
        transcribe_thread = threading.Thread(target=self.transcribe_worker)
        transcribe_thread.daemon = True
        transcribe_thread.start()
        
        try:
            # メインスレッドで待機
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\n👋 終了中...")
            self.is_running = False
            
            # スレッドの終了を待つ
            record_thread.join(timeout=2)
            
            # 残りのキューを処理
            if not self.audio_queue.empty():
                print("残りの音声を処理中...")
            transcribe_thread.join(timeout=10)
            
            print("✅ 終了しました")
            
        finally:
            self.p.terminate()

def main():
    print("=== Whisper リアルタイム音声認識（改良版）===")
    print("長い音声も最大5秒で区切って順次認識します")
    
    # パラメータ設定
    model_name = "small"
    silence_threshold = 250
    silence_duration = 1.2
    chunk_duration = 5.0  # 最大録音時間（秒）
    
    print(f"\n設定:")
    print(f"- モデル: {model_name}")
    print(f"- 無音閾値: {silence_threshold}")
    print(f"- 無音継続時間: {silence_duration}秒")
    print(f"- 最大録音時間: {chunk_duration}秒")
    
    # 連続認識システムを起動
    transcriber = RealtimeTranscriber(
        model_name=model_name,
        silence_threshold=silence_threshold,
        silence_duration=silence_duration,
        chunk_duration=chunk_duration
    )
    
    transcriber.run()

if __name__ == "__main__":
    main()