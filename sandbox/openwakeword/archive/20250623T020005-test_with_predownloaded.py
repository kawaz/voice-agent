#!/usr/bin/env python3
"""
OpenWakeWordで利用可能なモデルを確認して実行
"""

import numpy as np
import sounddevice as sd
from pathlib import Path
import time

def check_available_models():
    """利用可能なモデルを確認"""
    print("=== OpenWakeWordモデル確認 ===\n")
    
    try:
        from openwakeword.model import Model
        
        # 空のモデルで初期化して、利用可能なモデルを確認
        print("1. pretrained_model_pathsを調査中...")
        
        # openwakewordパッケージ内を確認
        import openwakeword
        package_path = Path(openwakeword.__file__).parent
        
        print(f"パッケージパス: {package_path}")
        
        # モデルディレクトリを探索
        possible_paths = [
            package_path / "resources" / "models",
            package_path / "models",
            package_path / "pretrained",
        ]
        
        for path in possible_paths:
            if path.exists():
                print(f"\n見つかったディレクトリ: {path}")
                for file in path.glob("*"):
                    print(f"  - {file.name}")
        
        # 手動でダウンロードする方法を提案
        print("\n2. モデルを手動でダウンロードします...")
        return download_and_test()
        
    except Exception as e:
        print(f"エラー: {e}")
        return None

def download_and_test():
    """簡易的なウェイクワード検出デモ"""
    print("\n=== 簡易ウェイクワード検出デモ ===")
    print("\n利用可能なウェイクワード:")
    print("- 'alexa' (アレクサ)")
    print("- 'hey jarvis' (ヘイ ジャービス)")
    print("- 'hey mycroft' (ヘイ マイクロフト)")
    
    print("\n※ 実際のOpenWakeWordモデルは利用できないため、")
    print("  音声パターンマッチングでシミュレーションします")
    
    return simulate_wake_word_detection()

def simulate_wake_word_detection():
    """ウェイクワード検出のシミュレーション"""
    print("\n=== ウェイクワード検出シミュレーション開始 ===")
    print("マイクに向かって話してください (Ctrl+Cで終了)")
    print("\n以下のフレーズを試してください:")
    print("- 大きな声で話す")
    print("- 'あ' で始まる言葉（alexaのシミュレーション）")
    print("- 'へい' と言う（hey jarvisのシミュレーション）")
    print("-" * 50)
    
    sample_rate = 16000
    frame_length = 1280  # 80ms
    
    # バッファと状態
    audio_buffer = []
    last_detection_time = 0
    cooldown = 2.0  # 検出後のクールダウン
    
    # 簡易的な音声特徴
    energy_history = []
    
    def audio_callback(indata, frames, time_info, status):
        nonlocal last_detection_time
        
        if status:
            print(f"エラー: {status}")
        
        # 音声エネルギー計算
        audio = indata[:, 0]
        energy = np.sqrt(np.mean(audio**2))
        
        # エネルギー履歴を保存（最大10フレーム）
        energy_history.append(energy)
        if len(energy_history) > 10:
            energy_history.pop(0)
        
        # 音量表示
        if energy > 0.01:
            bar = '█' * int(energy * 50)
            print(f"\r[{bar:<30}] {energy:.3f}", end="", flush=True)
        
        # ウェイクワード検出のシミュレーション
        current_time = time.time()
        if current_time - last_detection_time > cooldown:
            
            # パターン1: 大きな音の後に音が続く（"alexa"風）
            if len(energy_history) >= 3:
                if energy_history[-3] > 0.1 and energy_history[-2] > 0.05:
                    print(f"\n\n🎯 'Alexa' を検出しました！（シミュレーション）")
                    print(f"   エネルギーパターン: {[f'{e:.2f}' for e in energy_history[-3:]]}")
                    print("   >>> ここでWhisperによる音声認識を開始...")
                    print("")
                    last_detection_time = current_time
            
            # パターン2: 短い大きな音（"hey"風）
            if energy > 0.15 and len(energy_history) >= 2:
                if energy_history[-2] < 0.05:  # 前は静か
                    print(f"\n\n🎯 'Hey Jarvis' を検出しました！（シミュレーション）")
                    print(f"   突発的なエネルギー: {energy:.3f}")
                    print("   >>> ここでWhisperによる音声認識を開始...")
                    print("")
                    last_detection_time = current_time
    
    try:
        print("\n開始しました。話しかけてください...\n")
        
        with sd.InputStream(callback=audio_callback,
                          channels=1,
                          samplerate=sample_rate,
                          blocksize=frame_length):
            
            start_time = time.time()
            detection_count = 0
            
            while True:
                time.sleep(0.1)
                
                # 10秒ごとにヒント表示
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0 and elapsed > 0 and elapsed % 20 == 0:
                    print(f"\n\nヒント: 大きめの声で短く話すと検出されやすいです")
                    print(f"経過時間: {elapsed}秒\n")
    
    except KeyboardInterrupt:
        print("\n\n=== 終了 ===")
        print("\n実際のOpenWakeWordでは、ニューラルネットワークにより")
        print("正確なウェイクワード検出が可能です。")
        print("\n代替案:")
        print("1. Picovoice Porcupine (日本語対応)")
        print("2. Whisper + VAD (音声検出)")

def main():
    check_available_models()

if __name__ == "__main__":
    main()