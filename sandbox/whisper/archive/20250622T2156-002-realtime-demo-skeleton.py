#!/usr/bin/env python3
import whisper
import numpy as np
import time
from collections import deque

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

class RealtimeWhisperDemo:
    def __init__(self, model_name="base", chunk_duration=3):
        """
        リアルタイム音声認識のデモ
        
        Args:
            model_name: Whisperモデル名 (tiny, base, small, medium, large)
            chunk_duration: 音声チャンクの長さ（秒）
        """
        print(f"Whisperモデル '{model_name}' をロード中...")
        self.model = whisper.load_model(model_name)
        self.chunk_duration = chunk_duration
        self.sample_rate = 16000  # Whisperは16kHzを想定
        
        # PyAudioの設定
        if PYAUDIO_AVAILABLE:
            self.p = pyaudio.PyAudio()
            self.stream = None
        else:
            self.p = None
            self.stream = None
        
        # 音声バッファ
        self.audio_buffer = deque(maxlen=int(self.sample_rate * chunk_duration))
        
    def start_stream(self):
        """音声ストリームを開始"""
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1024,
            stream_callback=self.audio_callback
        )
        print("音声ストリーム開始")
        
    def audio_callback(self, in_data, frame_count, time_info, status):
        """音声データのコールバック"""
        audio_chunk = np.frombuffer(in_data, dtype=np.float32)
        self.audio_buffer.extend(audio_chunk)
        return (in_data, pyaudio.paContinue)
        
    def transcribe_chunk(self):
        """バッファ内の音声を文字起こし"""
        if len(self.audio_buffer) < self.sample_rate:
            return None
            
        # バッファから音声データを取得
        audio_data = np.array(self.audio_buffer)
        
        # Whisperで認識
        result = self.model.transcribe(
            audio_data,
            language="ja",
            fp16=False
        )
        
        return result["text"]
        
    def run(self):
        """リアルタイム認識のメインループ"""
        print("\n音声認識を開始します。Ctrl+Cで終了。")
        print("=" * 50)
        
        try:
            self.start_stream()
            self.stream.start_stream()
            
            while True:
                time.sleep(self.chunk_duration)
                
                # 音声認識実行
                text = self.transcribe_chunk()
                if text and text.strip():
                    print(f"認識結果: {text}")
                    
        except KeyboardInterrupt:
            print("\n\n終了します...")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            self.p.terminate()

def demo_batch_transcription():
    """バッチ処理のデモ（録音済みファイル）"""
    print("\n=== バッチ処理デモ ===")
    print("録音済みの音声ファイルを文字起こしする例:")
    
    code = '''
# 音声ファイルの文字起こし
model = whisper.load_model("base")
result = model.transcribe("interview.mp3", language="ja")

# 全文表示
print(result["text"])

# タイムスタンプ付きで表示
for segment in result["segments"]:
    start = segment["start"]
    end = segment["end"]
    text = segment["text"]
    print(f"[{start:.1f}s - {end:.1f}s] {text}")
'''
    print(code)

def demo_api_usage():
    """API使用のデモ"""
    print("\n=== Whisper API使用例 ===")
    print("OpenAI APIを使用する場合:")
    
    code = '''
from openai import OpenAI
client = OpenAI()

# 音声ファイルをアップロードして文字起こし
audio_file = open("speech.mp3", "rb")
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="ja"
)
print(transcription.text)
'''
    print(code)

if __name__ == "__main__":
    print("Whisperデモプログラム")
    print("=" * 50)
    
    # バッチ処理のデモ
    demo_batch_transcription()
    
    # API使用のデモ
    demo_api_usage()
    
    # リアルタイムデモ（PyAudioが必要）
    print("\n=== リアルタイム認識デモ ===")
    if not PYAUDIO_AVAILABLE:
        print("注意: リアルタイム認識にはpyaudioのインストールが必要です")
        print("実行するには以下をインストール:")
        print("  uv pip install pyaudio")
    print("\nリアルタイム認識のコード例:")
    print("  demo = RealtimeWhisperDemo(model_name='tiny')")
    print("  demo.run()")