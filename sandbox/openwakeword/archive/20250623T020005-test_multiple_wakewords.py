#!/usr/bin/env python3
"""
複数のウェイクワードを同時に検出するテスト
異なるウェイクワードで異なるアクションを実行
"""

import sounddevice as sd
import numpy as np
from openwakeword.model import Model
import time
from datetime import datetime
import threading

class MultiWakeWordDetector:
    def __init__(self):
        # 複数のウェイクワードとそれぞれのアクション
        self.wake_configs = {
            "alexa": {
                "threshold": 0.5,
                "action": self.alexa_action,
                "color": "\033[94m",  # 青
                "last_detection": 0
            },
            "hey_jarvis": {
                "threshold": 0.5,
                "action": self.jarvis_action,
                "color": "\033[93m",  # 黄
                "last_detection": 0
            },
            "hey_mycroft": {
                "threshold": 0.5,
                "action": self.mycroft_action,
                "color": "\033[92m",  # 緑
                "last_detection": 0
            }
        }
        
        # モデルのロード
        print("複数のウェイクワードモデルをロード中...")
        wake_words = list(self.wake_configs.keys())
        self.model = Model(wakeword_models=wake_words, inference_framework="onnx")
        print(f"✓ {len(wake_words)}個のモデルをロードしました: {wake_words}")
        
        # 音声パラメータ
        self.sample_rate = 16000
        self.frame_length = 1280
        self.audio_buffer = np.array([], dtype=np.int16)
        
        # 検出のクールダウン（連続検出を防ぐ）
        self.cooldown_period = 2.0  # 秒
        
        # 統計情報
        self.detection_counts = {word: 0 for word in wake_words}
        self.start_time = time.time()
        
    def alexa_action(self):
        """Alexa検出時のアクション"""
        print(f"{self.wake_configs['alexa']['color']}[Alexa Mode] 音楽を再生しますか？\033[0m")
        # ここで音楽プレイヤーAPIを呼び出すなど
        
    def jarvis_action(self):
        """Jarvis検出時のアクション"""
        print(f"{self.wake_configs['hey_jarvis']['color']}[Jarvis Mode] システム状態をチェックします...\033[0m")
        # ここでシステム監視機能を起動など
        
    def mycroft_action(self):
        """Mycroft検出時のアクション"""
        print(f"{self.wake_configs['hey_mycroft']['color']}[Mycroft Mode] オープンソースアシスタントです！\033[0m")
        # ここでカスタムコマンドの受付など
    
    def audio_callback(self, indata, frames, time, status):
        """音声入力コールバック"""
        if status:
            print(f"オーディオエラー: {status}")
        
        # float32 -> int16 変換
        audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
        self.audio_buffer = np.append(self.audio_buffer, audio_int16)
        
        # フレーム単位で処理
        while len(self.audio_buffer) >= self.frame_length:
            frame = self.audio_buffer[:self.frame_length]
            self.audio_buffer = self.audio_buffer[self.frame_length:]
            self.process_frame(frame)
    
    def process_frame(self, frame):
        """1フレームの処理"""
        # 全ウェイクワードで推論
        predictions = self.model.predict(frame)
        
        current_time = time.time()
        
        # 各ウェイクワードのスコアをチェック
        for wake_word, score in predictions.items():
            config = self.wake_configs[wake_word]
            
            # スコア表示（デバッグ用）
            if score > 0.1:  # ノイズ除去
                bar = '█' * int(score * 10)
                print(f"\r{wake_word:<12}: [{bar:<10}] {score:.3f}", end="", flush=True)
            
            # 閾値を超えた場合
            if score > config["threshold"]:
                # クールダウンチェック
                if current_time - config["last_detection"] > self.cooldown_period:
                    self.on_detection(wake_word, score)
                    config["last_detection"] = current_time
    
    def on_detection(self, wake_word, score):
        """ウェイクワード検出時の処理"""
        # 画面をクリア
        print("\n" * 2)
        
        # タイムスタンプ
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 検出メッセージ
        config = self.wake_configs[wake_word]
        print(f"\n{config['color']}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🎯 [{timestamp}] '{wake_word}' を検出！ (スコア: {score:.3f})")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
        
        # カウントアップ
        self.detection_counts[wake_word] += 1
        
        # アクション実行
        config["action"]()
        
        # 統計表示
        self.show_stats()
        print("\n待機中...\n")
    
    def show_stats(self):
        """統計情報の表示"""
        elapsed = time.time() - self.start_time
        print(f"\n📊 検出統計 (経過時間: {elapsed:.0f}秒)")
        for wake_word, count in self.detection_counts.items():
            config = self.wake_configs[wake_word]
            print(f"  {config['color']}{wake_word:<12}\033[0m: {count}回")
    
    def run(self):
        """検出開始"""
        print("\n=== 複数ウェイクワード検出デモ ===\n")
        print("検出可能なウェイクワード:")
        for wake_word, config in self.wake_configs.items():
            print(f"  {config['color']}• {wake_word} (閾値: {config['threshold']})\033[0m")
        
        print("\n異なるウェイクワードを話してみてください！")
        print("(Ctrl+Cで終了)\n")
        
        try:
            with sd.InputStream(
                callback=self.audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.frame_length // 2
            ):
                while True:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n\n=== 最終統計 ===")
            self.show_stats()
            print("\n検出を終了しました。")

def main():
    """メイン関数"""
    detector = MultiWakeWordDetector()
    detector.run()

if __name__ == "__main__":
    main()