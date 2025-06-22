#!/usr/bin/env python3
import whisper
import pyaudio
import numpy as np
import wave
import tempfile
import os
import time

def record_audio(duration=5, sample_rate=16000):
    """マイクから音声を録音"""
    print(f"\n🎤 録音を開始します（{duration}秒間）...")
    print("話してください！")
    
    # PyAudioの初期化
    p = pyaudio.PyAudio()
    
    # ストリームの設定
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=1024
    )
    
    # 録音
    frames = []
    for i in range(0, int(sample_rate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
        
        # プログレス表示
        progress = (i + 1) / (sample_rate / 1024 * duration) * 100
        print(f"\r録音中... {progress:.0f}%", end="", flush=True)
    
    print("\n✅ 録音完了！")
    
    # ストリームのクリーンアップ
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # 一時ファイルに保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_filename = tmp_file.name
        
    # WAVファイルとして保存
    with wave.open(tmp_filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
    
    return tmp_filename

def transcribe_audio(audio_file, model_name="base"):
    """音声ファイルを文字起こし"""
    print(f"\n🤖 Whisperモデル '{model_name}' で認識中...")
    
    # モデルのロード（初回のみ時間がかかる）
    model = whisper.load_model(model_name)
    
    # 文字起こし
    result = model.transcribe(audio_file, language="ja", fp16=False)
    
    return result

def main():
    print("=== Whisper マイク入力デモ ===")
    print("macのマイクを使って音声認識を行います")
    
    # 設定
    duration = 5  # 録音時間（秒）
    model_name = "small"  # 使用するモデル (より高精度)
    
    try:
        while True:
            print("\n" + "="*50)
            input("Enterキーを押すと録音を開始します（Ctrl+Cで終了）")
            
            # 録音
            audio_file = record_audio(duration=duration)
            
            try:
                # 文字起こし
                start_time = time.time()
                result = transcribe_audio(audio_file, model_name=model_name)
                transcribe_time = time.time() - start_time
                
                # 結果表示
                print("\n📝 認識結果:")
                print("-" * 40)
                print(result["text"])
                print("-" * 40)
                print(f"認識時間: {transcribe_time:.2f}秒")
                
            finally:
                # 一時ファイルの削除
                if os.path.exists(audio_file):
                    os.unlink(audio_file)
                    
    except KeyboardInterrupt:
        print("\n\n👋 終了します")

if __name__ == "__main__":
    main()