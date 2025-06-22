#!/usr/bin/env python3
"""
音声入力モニタリング - OpenWakeWordなしでの動作確認
"""

import sounddevice as sd
import numpy as np
import time

def main():
    """音声モニタリング"""
    print("=== 音声入力モニタリング ===")
    print("マイクに向かって話してください")
    print("音量レベルが表示されます (Ctrl+Cで終了)")
    print("-" * 50)
    
    sample_rate = 16000
    frame_length = 1280  # 80ms
    
    # 統計情報
    max_volume = 0
    detection_count = 0
    
    def audio_callback(indata, frames, time_info, status):
        nonlocal max_volume, detection_count
        
        if status:
            print(f"エラー: {status}")
        
        # float32 -> int16相当に変換して音量計算
        audio_int16 = indata[:, 0] * 32767
        volume = np.sqrt(np.mean(audio_int16**2)) / 32767
        
        # 最大音量更新
        if volume > max_volume:
            max_volume = volume
        
        # 音量バー表示
        bar_length = int(volume * 100)
        bar = '█' * min(bar_length, 50)
        
        # 音量レベルに応じた表示
        if volume > 0.001:  # ノイズフロア以上
            level_indicator = ""
            if volume > 0.3:
                level_indicator = " 🔴 大音量!"
                detection_count += 1
            elif volume > 0.1:
                level_indicator = " 🟡 中音量"
            elif volume > 0.05:
                level_indicator = " 🟢 小音量"
            
            print(f"\r[{bar:<50}] {volume:.3f} {level_indicator}", end="", flush=True)
            
            # ウェイクワード検出のシミュレーション
            if volume > 0.2 and np.random.random() > 0.9:  # ランダムに「検出」
                print(f"\n🎯 ウェイクワード検出をシミュレート！ (実際はOpenWakeWordが必要)")
                print(f"   検出回数: {detection_count}")
                print("")
    
    try:
        print("\n開始します...\n")
        
        with sd.InputStream(callback=audio_callback,
                          channels=1,
                          samplerate=sample_rate,
                          blocksize=frame_length):
            
            start_time = time.time()
            
            while True:
                time.sleep(1)
                
                # 定期的な統計表示
                elapsed = time.time() - start_time
                if int(elapsed) % 10 == 0 and int(elapsed) > 0:
                    print(f"\n\n--- {int(elapsed)}秒経過 ---")
                    print(f"最大音量: {max_volume:.3f}")
                    print(f"大音量検出: {detection_count}回")
                    print("")
                    
    except KeyboardInterrupt:
        print("\n\n=== 終了 ===")
        print(f"最大音量: {max_volume:.3f}")
        print(f"大音量検出: {detection_count}回")
        print("\nOpenWakeWordが正しく動作すれば、実際のウェイクワード検出が可能になります")

if __name__ == "__main__":
    main()