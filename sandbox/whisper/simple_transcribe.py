#!/usr/bin/env python3
import whisper
import sys

def transcribe_file(audio_file, model_name="base"):
    """音声ファイルを文字起こし"""
    print(f"モデル '{model_name}' をロード中...")
    model = whisper.load_model(model_name)
    
    print(f"ファイル '{audio_file}' を処理中...")
    result = model.transcribe(audio_file, language="ja", fp16=False)
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python simple_transcribe.py <音声ファイル> [モデル名]")
        print("モデル名: tiny, base, small, medium, large (デフォルト: base)")
        print("\n例:")
        print("  python simple_transcribe.py interview.mp3")
        print("  python simple_transcribe.py podcast.wav small")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "base"
    
    try:
        result = transcribe_file(audio_file, model_name)
        
        print("\n=== 認識結果 ===")
        print(result["text"])
        
        print("\n=== タイムスタンプ付き ===")
        for segment in result["segments"]:
            print(f"[{segment['start']:.1f}s - {segment['end']:.1f}s] {segment['text']}")
            
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)