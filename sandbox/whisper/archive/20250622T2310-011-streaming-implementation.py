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

class StreamingTranscriber:
    def __init__(self, model_name="small", chunk_duration=3.0, overlap_duration=0.5):
        """
        ストリーミング音声認識システム（連続録音版）
        
        Args:
            model_name: Whisperモデル名
            chunk_duration: 処理単位の長さ（秒）
            overlap_duration: オーバーラップの長さ（秒）
        """
        print(f"🤖 Whisperモデル '{model_name}' をロード中...")
        self.model = whisper.load_model(model_name)
        print("✅ モデルのロード完了！")
        
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.chunk_duration = chunk_duration
        self.overlap_duration = overlap_duration
        
        # バッファサイズの計算
        self.chunk_samples = int(chunk_duration * self.sample_rate)
        self.overlap_samples = int(overlap_duration * self.sample_rate)
        
        # PyAudio初期化
        self.p = pyaudio.PyAudio()
        
        # 音声バッファ（連続録音用）
        self.audio_buffer = deque(maxlen=self.chunk_samples * 2)
        self.process_queue = queue.Queue()
        self.is_running = False
        
        # 前回の処理結果を保持
        self.last_text = ""
        self.total_processed_duration = 0
        
    def continuous_recording(self):
        """連続録音（停止しない）"""
        stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        print("\n🎤 連続録音を開始します... (Ctrl+Cで終了)")
        print(f"📊 設定: {self.chunk_duration}秒ごとに処理, {self.overlap_duration}秒のオーバーラップ")
        print("-" * 80)
        
        sample_count = 0
        last_process_time = time.time()
        
        try:
            while self.is_running:
                # 音声データを読み取り
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                
                # バッファに追加
                self.audio_buffer.extend(audio_chunk)
                sample_count += len(audio_chunk)
                
                # chunk_duration秒分のデータが溜まったら処理
                if sample_count >= self.chunk_samples:
                    # バッファから必要な分を取得
                    current_audio = list(self.audio_buffer)[-self.chunk_samples:]
                    
                    # 処理キューに追加
                    self.process_queue.put({
                        'audio': np.array(current_audio),
                        'timestamp': time.time(),
                        'duration': len(current_audio) / self.sample_rate
                    })
                    
                    # オーバーラップ分を残してカウンタをリセット
                    sample_count = self.overlap_samples
                    
                    # 進捗表示
                    elapsed = time.time() - last_process_time
                    print(f"\r🔄 チャンク送信 (経過: {elapsed:.1f}秒)", end="", flush=True)
                    last_process_time = time.time()
                    
        finally:
            stream.stop_stream()
            stream.close()
    
    def save_audio_array(self, audio_array):
        """numpy配列を一時WAVファイルに保存"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_filename = tmp_file.name
            
        with wave.open(tmp_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_array.astype(np.int16).tobytes())
            
        return tmp_filename
    
    def process_audio_chunks(self):
        """音声チャンクを処理"""
        while self.is_running or not self.process_queue.empty():
            try:
                # キューからチャンクを取得
                chunk_data = self.process_queue.get(timeout=1)
                
                # 一時ファイルに保存
                audio_file = self.save_audio_array(chunk_data['audio'])
                
                try:
                    # 文字起こし
                    start_time = time.time()
                    result = self.model.transcribe(
                        audio_file, 
                        language="ja", 
                        fp16=False,
                        initial_prompt=self.last_text[-100:] if self.last_text else None  # 前の文脈をヒントとして提供
                    )
                    transcribe_time = time.time() - start_time
                    
                    # 結果処理
                    text = result["text"].strip()
                    if text:
                        # 重複部分を検出して除去（簡易版）
                        if self.last_text and len(self.last_text) > 10:
                            # 前回の最後の部分と今回の最初が重複していないかチェック
                            overlap_text = self._find_overlap(self.last_text, text)
                            if overlap_text:
                                text = text[len(overlap_text):]
                        
                        if text:  # 重複除去後もテキストがある場合
                            print(f"\n📝 [{self.total_processed_duration:.1f}s-{self.total_processed_duration + chunk_data['duration']:.1f}s] {text}")
                            print(f"   (処理時間: {transcribe_time:.1f}秒)")
                            self.last_text = text
                        
                        self.total_processed_duration += chunk_data['duration'] - self.overlap_duration
                        
                except Exception as e:
                    print(f"\n❌ 認識エラー: {e}")
                finally:
                    # 一時ファイルの削除
                    if os.path.exists(audio_file):
                        os.unlink(audio_file)
                        
            except queue.Empty:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"\n処理エラー: {e}")
    
    def _find_overlap(self, text1, text2, min_overlap=5):
        """2つのテキストの重複部分を検出"""
        for i in range(min(len(text1), len(text2), 20), min_overlap - 1, -1):
            if text1[-i:] == text2[:i]:
                return text2[:i]
        return ""
    
    def run(self):
        """ストリーミング認識を開始"""
        self.is_running = True
        
        # 録音スレッド
        record_thread = threading.Thread(target=self.continuous_recording)
        record_thread.daemon = True
        record_thread.start()
        
        # 処理スレッド
        process_thread = threading.Thread(target=self.process_audio_chunks)
        process_thread.daemon = True
        process_thread.start()
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\n👋 終了中...")
            self.is_running = False
            
            # スレッドの終了を待つ
            record_thread.join(timeout=2)
            process_thread.join(timeout=5)
            
            print("✅ 終了しました")
            
        finally:
            self.p.terminate()

def main():
    print("=== Whisper ストリーミング音声認識 ===")
    print("連続録音しながら定期的に認識結果を表示します")
    
    # パラメータ設定
    model_name = "small"
    chunk_duration = 3.0  # 3秒ごとに処理
    overlap_duration = 0.5  # 0.5秒のオーバーラップ
    
    print(f"\n設定:")
    print(f"- モデル: {model_name}")
    print(f"- 処理間隔: {chunk_duration}秒")
    print(f"- オーバーラップ: {overlap_duration}秒")
    
    # ストリーミング認識を開始
    transcriber = StreamingTranscriber(
        model_name=model_name,
        chunk_duration=chunk_duration,
        overlap_duration=overlap_duration
    )
    
    transcriber.run()

if __name__ == "__main__":
    main()