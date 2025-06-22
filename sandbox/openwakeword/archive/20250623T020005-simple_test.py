#!/usr/bin/env python3
"""
OpenWakeWordの最もシンプルなテスト
tfliteの代わりにonnxを使用
"""

import numpy as np
import sounddevice as sd
import time

def test_audio_recording():
    """音声録音のテスト"""
    print("=== 音声録音テスト ===")
    print("3秒間録音します...")
    
    # 録音パラメータ
    sample_rate = 16000
    duration = 3
    
    # 録音
    recording = sd.rec(int(sample_rate * duration), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype='float32')
    sd.wait()
    
    print(f"録音完了: {recording.shape}")
    print(f"最大値: {np.max(np.abs(recording)):.3f}")
    
    return recording

def test_wake_word_stub():
    """ウェイクワード検出のスタブ実装"""
    print("\n=== ウェイクワード検出（スタブ） ===")
    print("マイク入力をモニタリング中... (Ctrl+Cで終了)")
    
    sample_rate = 16000
    frame_length = 1280  # 80ms
    
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"エラー: {status}")
        
        # 音量レベルの計算
        volume = np.sqrt(np.mean(indata**2))
        
        # 簡単な音量ベースの検出（実際のウェイクワード検出ではない）
        if volume > 0.01:  # 閾値
            bar = '█' * int(volume * 50)
            print(f"\r音量: [{bar:<20}] {volume:.3f}", end="", flush=True)
            
            # 大きな音を検出
            if volume > 0.1:
                print(f"\n🎯 大きな音を検出！ (音量: {volume:.3f})")
                print("（実際のウェイクワード検出はOpenWakeWordモデルが必要）")
    
    try:
        with sd.InputStream(callback=audio_callback,
                          channels=1,
                          samplerate=sample_rate,
                          blocksize=frame_length):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n終了しました")

def main():
    """メイン関数"""
    print("OpenWakeWord サンドボックス - シンプルテスト")
    print("=" * 50)
    
    # オーディオデバイスの確認
    print("\n利用可能なオーディオデバイス:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"  {i}: {device['name']} (入力ch: {device['max_input_channels']})")
    
    print("\nデフォルトデバイス:")
    default_device = sd.query_devices(sd.default.device[0])
    print(f"  {default_device['name']}")
    
    # テスト選択
    print("\n選択してください:")
    print("1. 音声録音テスト")
    print("2. 音量モニタリング（ウェイクワード検出のスタブ）")
    print("3. 終了")
    
    try:
        choice = input("\n選択 (1-3): ")
        
        if choice == "1":
            test_audio_recording()
        elif choice == "2":
            test_wake_word_stub()
        else:
            print("終了します")
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()