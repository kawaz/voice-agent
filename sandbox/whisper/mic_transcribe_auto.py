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

class AutoTranscriber:
    def __init__(self, model_name="small", silence_threshold=250, silence_duration=1.2):
        """
        自動連続音声認識システム（最適化版）
        
        Args:
            model_name: Whisperモデル名
            silence_threshold: 無音判定の閾値（デフォルト: 250）
            silence_duration: 無音継続時間（秒）で録音を区切る
        """
        print(f"🤖 Whisperモデル '{model_name}' をロード中...")
        self.model = whisper.load_model(model_name)
        print("✅ モデルのロード完了！")
        
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        
        # PyAudio初期化
        self.p = pyaudio.PyAudio()
        
        # 音声データのキュー
        self.audio_queue = queue.Queue()
        self.is_running = False
        
    def calculate_rms(self, data):
        """音声データのRMS（音量）を計算"""
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
        print("-" * 50)
        
        frames = []
        silence_chunks = 0
        chunks_per_second = self.sample_rate / self.chunk_size
        silence_chunks_needed = int(self.silence_duration * chunks_per_second)
        is_speaking = False
        
        try:
            while self.is_running:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                rms = self.calculate_rms(data)
                
                # 音声検出
                if rms > self.silence_threshold:
                    if not is_speaking:
                        print("🔊 録音中...", end="", flush=True)
                        is_speaking = True
                    frames.append(data)
                    silence_chunks = 0
                elif is_speaking:
                    # 話している最中の無音
                    frames.append(data)
                    silence_chunks += 1
                    
                    # 無音が一定時間続いたら録音終了
                    if silence_chunks > silence_chunks_needed:
                        print(" ✅")
                        
                        # 音声データをキューに追加
                        if len(frames) > chunks_per_second:  # 1秒以上の音声のみ
                            self.audio_queue.put(frames.copy())
                        
                        # リセット
                        frames = []
                        silence_chunks = 0
                        is_speaking = False
                        
        except Exception as e:
            if self.is_running:
                print(f"\n録音エラー: {e}")
        finally:
            stream.stop_stream()
            stream.close()
    
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
                frames = self.audio_queue.get(timeout=1)
                
                # 一時ファイルに保存
                audio_file = self.save_audio(frames)
                
                try:
                    # 文字起こし
                    result = self.model.transcribe(audio_file, language="ja", fp16=False)
                    
                    # 結果表示
                    text = result["text"].strip()
                    if text:
                        print(f"📝 {text}")
                        print("-" * 50)
                        
                except Exception as e:
                    if self.is_running:
                        print(f"認識エラー: {e}")
                finally:
                    # 一時ファイルの削除
                    if os.path.exists(audio_file):
                        os.unlink(audio_file)
                        
            except queue.Empty:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"処理エラー: {e}")
    
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
            print("残りの音声を処理中...")
            transcribe_thread.join(timeout=10)
            
            print("✅ 終了しました")
            
        finally:
            self.p.terminate()

def main():
    print("=== Whisper 自動音声認識 ===")
    print("話すと自動的に文字起こしされます")
    
    # ffmpegの確認
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except:
        print("\n⚠️  ffmpegがインストールされていません")
        print("インストール方法: brew install ffmpeg")
        return
    
    # パラメータ設定
    model_name = "small"  # 使用するモデル
    silence_threshold = 250  # 無音判定の閾値（最適化済み）
    silence_duration = 1.2  # 無音継続時間（秒）
    
    print(f"\n設定:")
    print(f"- モデル: {model_name}")
    print(f"- 無音閾値: {silence_threshold}")
    print(f"- 無音継続時間: {silence_duration}秒")
    
    # 連続認識システムを起動
    transcriber = AutoTranscriber(
        model_name=model_name,
        silence_threshold=silence_threshold,
        silence_duration=silence_duration
    )
    
    transcriber.run()

if __name__ == "__main__":
    main()