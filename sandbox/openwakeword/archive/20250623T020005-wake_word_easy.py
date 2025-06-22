#!/usr/bin/env python3
"""
ウェイクワード検出デモ（超簡単版）
とても低い閾値で反応します
"""

import sounddevice as sd
import numpy as np
import time
from datetime import datetime

print("=== ウェイクワード検出デモ（簡単版） ===")
print("\n🎤 マイクに向かって何か話してください！")
print("\n検出レベル:")
print("  🟢 0.01以上 - 小さな声でも検出")
print("  🟡 0.05以上 - 普通の声")  
print("  🔴 0.10以上 - 大きな声")
print("\nCtrl+Cで終了")
print("-" * 50)

sample_rate = 16000
frame_length = 1280  # 80ms

# 統計
detection_count = 0
last_detection = 0
max_volume = 0

def process_audio(indata, frames, time_info, status):
    """音声処理コールバック"""
    global detection_count, last_detection, max_volume
    
    if status:
        print(f"音声エラー: {status}")
    
    # 音量計算
    audio = indata[:, 0]
    volume = np.sqrt(np.mean(audio**2))
    
    # 最大音量更新
    if volume > max_volume:
        max_volume = volume
    
    # 音量メーター表示（常時）
    meter_length = int(volume * 300)  # より大きくスケール
    meter = '█' * min(meter_length, 40)
    level = ""
    
    if volume >= 0.10:
        level = "🔴"
    elif volume >= 0.05:
        level = "🟡"
    elif volume >= 0.01:
        level = "🟢"
    
    print(f"\r[{meter:<40}] {volume:.3f} {level}", end="", flush=True)
    
    # ウェイクワード検出（とても低い閾値）
    current_time = time.time()
    if volume > 0.01 and (current_time - last_detection) > 1.0:  # 1秒のクールダウン
        detection_count += 1
        last_detection = current_time
        
        # 検出メッセージ
        wake_words = ["アレクサ", "ヘイ シリ", "オッケー グーグル", "ねえ エージェント"]
        simulated_wake = wake_words[detection_count % len(wake_words)]
        
        print(f"\n\n{'='*60}")
        print(f"🎯 ウェイクワード「{simulated_wake}」を検出！（シミュレーション）")
        print(f"検出回数: {detection_count}回目")
        print(f"音量レベル: {volume:.3f}")
        print(f"時刻: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        if detection_count == 1:
            print("\n💡 ヒント: 実際のOpenWakeWordでは、")
            print("   特定の音声パターンを学習して検出します")
        elif detection_count == 2:
            print("\n💡 これは音量ベースの簡易検出です")
            print("   実際はニューラルネットワークを使用します")
        else:
            print("\n🎤 音声コマンド待機中...")
            print("   「電気をつけて」「今日の天気は？」など")
        
        print(f"\n検出を続けます...\n")

# メイン処理
try:
    print(f"\n開始しました！何か話してください...\n")
    print("（小さな声でもOKです）\n")
    
    # オーディオストリーム開始
    with sd.InputStream(
        callback=process_audio,
        channels=1,
        samplerate=sample_rate,
        blocksize=frame_length // 2  # より高頻度で処理
    ):
        start_time = time.time()
        
        # 無限ループ
        while True:
            time.sleep(1)
            
            # 10秒ごとにヒント
            elapsed = int(time.time() - start_time)
            if elapsed > 0 and elapsed % 10 == 0 and detection_count == 0:
                print(f"\n\n💡 マイクに向かって何か話してみてください")
                print(f"   最大音量: {max_volume:.3f}\n")
            
except KeyboardInterrupt:
    print(f"\n\n=== 終了 ===")
    print(f"総検出回数: {detection_count}回")
    print(f"最大音量: {max_volume:.3f}")
    print("\n実際のウェイクワード検出の特徴:")
    print("✓ 特定の言葉だけに反応")
    print("✓ 周囲の雑音に強い")
    print("✓ 低消費電力で常時待機")
    print("\nお疲れ様でした！")