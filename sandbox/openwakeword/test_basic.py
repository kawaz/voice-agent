#!/usr/bin/env python3
"""
OpenWakeWordの基本的な動作確認スクリプト
"""

import openwakeword
from openwakeword.model import Model
import numpy as np
import time

def test_model_loading():
    """モデルのロードテスト"""
    print("=== OpenWakeWord 基本テスト ===\n")
    
    # バージョン確認
    print(f"OpenWakeWord version: {openwakeword.__version__}")
    print()
    
    # 利用可能なプリトレーニング済みモデル
    available_models = [
        "alexa",
        "hey_jarvis", 
        "hey_mycroft",
        "hey_rhasspy"
    ]
    
    print("利用可能なモデル:")
    for model_name in available_models:
        print(f"  - {model_name}")
    print()
    
    # モデルのロードテスト
    print("モデルのロードテスト...")
    try:
        model = Model(wakeword_models=["alexa"], inference_framework="onnx")
        print("✓ モデルのロードに成功しました")
    except Exception as e:
        print(f"✗ モデルのロードに失敗しました: {e}")
        return False
    
    return True

def test_inference():
    """推論テスト（ダミーデータ）"""
    print("\n=== 推論テスト ===\n")
    
    # モデルのロード
    model = Model(wakeword_models=["alexa"], inference_framework="onnx")
    
    # ダミー音声データ（16kHz, 80ms = 1280サンプル）
    dummy_audio = np.random.randint(-32768, 32767, size=1280, dtype=np.int16)
    
    print("ダミー音声データで推論実行...")
    start_time = time.time()
    
    # 推論
    prediction = model.predict(dummy_audio)
    
    inference_time = (time.time() - start_time) * 1000
    
    print(f"推論時間: {inference_time:.2f}ms")
    print("\n結果:")
    for wake_word, score in prediction.items():
        print(f"  {wake_word}: {score:.4f}")
    
    return True

def test_multiple_models():
    """複数モデルの同時ロード"""
    print("\n=== 複数モデルテスト ===\n")
    
    models_to_load = ["alexa", "hey_jarvis"]
    
    print(f"ロードするモデル: {models_to_load}")
    
    try:
        model = Model(wakeword_models=models_to_load)
        print("✓ 複数モデルのロードに成功しました")
        
        # ダミーデータで推論
        dummy_audio = np.random.randint(-32768, 32767, size=1280, dtype=np.int16)
        prediction = model.predict(dummy_audio)
        
        print("\n推論結果:")
        for wake_word, score in prediction.items():
            print(f"  {wake_word}: {score:.4f}")
            
    except Exception as e:
        print(f"✗ エラーが発生しました: {e}")
        return False
    
    return True

def test_continuous_inference():
    """連続推論のパフォーマンステスト"""
    print("\n=== 連続推論テスト ===\n")
    
    model = Model(wakeword_models=["alexa"], inference_framework="onnx")
    
    # 1秒分のテスト（80ms × 12.5 = 1秒）
    num_frames = 13
    frame_times = []
    
    print(f"{num_frames}フレームの連続推論...")
    
    for i in range(num_frames):
        dummy_audio = np.random.randint(-32768, 32767, size=1280, dtype=np.int16)
        
        start_time = time.time()
        prediction = model.predict(dummy_audio)
        frame_time = (time.time() - start_time) * 1000
        
        frame_times.append(frame_time)
        
        # 進捗表示
        print(f".", end="", flush=True)
    
    print("\n")
    
    # 統計情報
    avg_time = np.mean(frame_times)
    max_time = np.max(frame_times)
    min_time = np.min(frame_times)
    
    print(f"平均推論時間: {avg_time:.2f}ms")
    print(f"最大推論時間: {max_time:.2f}ms")
    print(f"最小推論時間: {min_time:.2f}ms")
    
    # リアルタイム性のチェック
    print(f"\nリアルタイム処理: {'✓ 可能' if max_time < 80 else '✗ 不可'} (80ms以内)")
    
    return True

def main():
    """メインテスト実行"""
    print("OpenWakeWord 基本動作確認を開始します...\n")
    
    tests = [
        ("モデルロード", test_model_loading),
        ("基本推論", test_inference),
        ("複数モデル", test_multiple_models),
        ("連続推論", test_continuous_inference)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n{test_name}でエラーが発生しました: {e}")
            results.append((test_name, False))
        
        print("\n" + "="*50 + "\n")
    
    # 結果サマリー
    print("=== テスト結果サマリー ===\n")
    for test_name, success in results:
        status = "✓ 成功" if success else "✗ 失敗"
        print(f"{test_name}: {status}")
    
    # 全体の成功/失敗
    all_success = all(success for _, success in results)
    print(f"\n全体結果: {'✓ すべて成功' if all_success else '✗ 一部失敗'}")

if __name__ == "__main__":
    main()