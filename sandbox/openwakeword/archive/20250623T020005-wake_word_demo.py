#!/usr/bin/env python3
"""
ウェイクワード検出デモ（シンプル版）
大きな音を検出したら反応します
"""

import sounddevice as sd
import numpy as np
import time
from datetime import datetime

print("=== ウェイクワード検出デモ ===")
print("\n使い方:")
print("1. マイクに向かって大きめの声で話してください")
print("2. 以下のような言葉を試してください:")
print("   - 'アレクサ'")
print("   - 'ヘイ シリ'") 
print("   - 'オッケー グーグル'")
print("   - その他、短い言葉")
print("\n音量メーターが表示されます")
print("大きな音を検出すると「ウェイクワード検出！」と表示されます")
print("\nCtrl+Cで終了")
print("-" * 50)

sample_rate = 16000
frame_length = 1280  # 80ms
threshold = 0.05  # 検出閾値（低めに設定）

# 統計
detection_count = 0
last_detection = 0
cooldown = 1.5  # 検出後のクールダウン（秒）

def process_audio(indata, frames, time_info, status):
    """音声処理コールバック"""
    global detection_count, last_detection
    
    if status:
        print(f"音声エラー: {status}")
    
    # 音量計算
    audio = indata[:, 0]
    volume = np.sqrt(np.mean(audio**2))
    
    # 音量メーター表示
    meter_length = int(volume * 200)  # スケール調整
    meter = '█' * min(meter_length, 50)
    
    # 常に音量を表示
    print(f"\r音量: [{meter:<50}] {volume:.3f}", end="", flush=True)
    
    # ウェイクワード検出（音量ベース）
    current_time = time.time()
    if volume > threshold and (current_time - last_detection) > cooldown:
        detection_count += 1
        last_detection = current_time
        
        # 検出メッセージ
        print(f"\n\n{'='*60}")
        print(f"🎯 ウェイクワード検出！ #{detection_count}")
        print(f"時刻: {datetime.now().strftime('%H:%M:%S')}")
        print(f"音量: {volume:.3f}")
        print(f"{'='*60}")
        print("\n本来ここで:")
        print("1. より詳細な音声認識（Whisper等）を開始")
        print("2. コマンドを待機")
        print("3. アクションを実行")
        print(f"\n音量メーター表示を継続します...\n")

# メイン処理
try:
    print(f"\n開始しました！マイクに向かって話してください...\n")
    
    # オーディオストリーム開始
    with sd.InputStream(
        callback=process_audio,
        channels=1,
        samplerate=sample_rate,
        blocksize=frame_length
    ):
        # 無限ループ
        while True:
            time.sleep(0.1)
            
except KeyboardInterrupt:
    print(f"\n\n終了します")
    print(f"検出回数: {detection_count}回")
    print("\n実際のウェイクワード検出では:")
    print("- 特定の言葉のパターンを学習")
    print("- ニューラルネットワークで判定")
    print("- 誤検出を最小化")
    print("\nお疲れ様でした！")