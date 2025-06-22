#!/usr/bin/env python3
import whisper
import time
import os

def test_whisper():
    print("Whisperのテストを開始します...")
    
    # 利用可能なモデル
    models = ["tiny", "base", "small"]
    
    print("\n利用可能なモデル:")
    for model_name in models:
        model_info = {
            "tiny": "39MB - 最速、精度は低め",
            "base": "74MB - バランス型",
            "small": "244MB - 高精度"
        }
        print(f"- {model_name}: {model_info[model_name]}")
    
    # baseモデルをロード
    print("\nbaseモデルをロードしています...")
    start_time = time.time()
    model = whisper.load_model("base")
    load_time = time.time() - start_time
    print(f"モデルのロード完了 (所要時間: {load_time:.2f}秒)")
    
    # テスト用の音声ファイルが必要
    print("\n注意: 実際のテストには音声ファイル（.mp3, .wav等）が必要です")
    print("使用方法:")
    print("1. 音声ファイルを用意")
    print("2. 以下のコードで認識:")
    print('   result = model.transcribe("your_audio.mp3", language="ja")')
    print('   print(result["text"])')
    
    # サンプルコード
    sample_code = '''
# 音声ファイルの文字起こし例
def transcribe_audio(file_path):
    # モデルのロード
    model = whisper.load_model("base")
    
    # 音声認識実行
    result = model.transcribe(file_path, language="ja")
    
    # 結果表示
    print("認識結果:", result["text"])
    
    # セグメント単位の結果も取得可能
    for segment in result["segments"]:
        print(f"[{segment['start']:.2f}s -> {segment['end']:.2f}s] {segment['text']}")
'''
    
    print("\n--- サンプルコード ---")
    print(sample_code)
    
    # システム情報
    print("\n--- システム情報 ---")
    print(f"Whisperバージョン: {whisper.__version__ if hasattr(whisper, '__version__') else 'unknown'}")
    print(f"Python: {os.sys.version.split()[0]}")

if __name__ == "__main__":
    test_whisper()