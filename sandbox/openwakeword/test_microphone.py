#!/usr/bin/env python3
"""
マイク入力でOpenWakeWordのウェイクワード検出をテスト
"""

import argparse
import sounddevice as sd
import numpy as np
from openwakeword.model import Model
import time
from collections import deque
import sys

class WakeWordDetector:
    def __init__(self, model_name="alexa", threshold=0.5, debug=False):
        """
        Args:
            model_name: 使用するウェイクワードモデル
            threshold: 検出閾値 (0-1)
            debug: デバッグ出力の有効/無効
        """
        self.model_name = model_name
        self.threshold = threshold
        self.debug = debug
        
        # モデルのロード
        print(f"モデル '{model_name}' をロード中...")
        try:
            self.model = Model(wakeword_models=[model_name], inference_framework="onnx")
            print("✓ モデルのロードに成功しました")
        except Exception as e:
            print(f"✗ モデルのロードに失敗しました: {e}")
            sys.exit(1)
        
        # 音声パラメータ
        self.sample_rate = 16000
        self.frame_length = 1280  # 80ms at 16kHz
        
        # バッファとステート
        self.audio_buffer = np.array([], dtype=np.int16)
        self.detection_history = deque(maxlen=5)  # 過去5フレームの履歴
        self.last_detection_time = 0
        self.detection_cooldown = 2.0  # 検出後のクールダウン（秒）
        
    def audio_callback(self, indata, frames, time, status):
        """音声入力コールバック"""
        if status:
            print(f"オーディオエラー: {status}")
        
        # float32 -> int16 変換
        audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
        
        # バッファに追加
        self.audio_buffer = np.append(self.audio_buffer, audio_int16)
        
        # フレーム単位で処理
        while len(self.audio_buffer) >= self.frame_length:
            # 1フレーム取り出し
            frame = self.audio_buffer[:self.frame_length]
            self.audio_buffer = self.audio_buffer[self.frame_length:]
            
            # 推論実行
            self.process_frame(frame)
    
    def process_frame(self, frame):
        """1フレームの処理"""
        # 推論
        prediction = self.model.predict(frame)
        
        # 結果の取得
        score = prediction.get(self.model_name, 0)
        
        # デバッグ出力
        if self.debug and score > 0.1:  # ノイズ除去のため0.1以上のみ表示
            print(f"\rスコア: {score:.3f} {'█' * int(score * 20):<20}", end="", flush=True)
        
        # 閾値チェック
        if score > self.threshold:
            current_time = time.time()
            
            # クールダウンチェック
            if current_time - self.last_detection_time > self.detection_cooldown:
                self.on_wake_word_detected(score)
                self.last_detection_time = current_time
    
    def on_wake_word_detected(self, score):
        """ウェイクワード検出時の処理"""
        print(f"\n🎯 ウェイクワード '{self.model_name}' を検出しました！ (スコア: {score:.3f})")
        print(">>> 音声コマンドをどうぞ... (ここでWhisperなどと連携)")
        print()
    
    def run(self):
        """検出開始"""
        print(f"\n=== ウェイクワード検出開始 ===")
        print(f"モデル: {self.model_name}")
        print(f"閾値: {self.threshold}")
        print(f"サンプリングレート: {self.sample_rate}Hz")
        print(f"フレーム長: {self.frame_length}サンプル (80ms)")
        print("\n話しかけてください... (Ctrl+Cで終了)\n")
        
        try:
            # オーディオストリーム開始
            with sd.InputStream(
                callback=self.audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.frame_length // 2  # 低レイテンシのため半フレーム
            ):
                # 無限ループで待機
                while True:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n\n検出を終了しました。")
        except Exception as e:
            print(f"\nエラーが発生しました: {e}")

def list_audio_devices():
    """利用可能なオーディオデバイスを表示"""
    print("=== 利用可能なオーディオデバイス ===\n")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"{i}: {device['name']} (入力チャンネル: {device['max_input_channels']})")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="OpenWakeWordのマイク入力テスト"
    )
    parser.add_argument(
        "--model", "-m",
        default="alexa",
        choices=["alexa", "hey_jarvis", "hey_mycroft", "hey_rhasspy"],
        help="使用するウェイクワードモデル (default: alexa)"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=0.5,
        help="検出閾値 0-1 (default: 0.5)"
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="デバッグ出力を有効化"
    )
    parser.add_argument(
        "--list-devices", "-l",
        action="store_true",
        help="利用可能なオーディオデバイスを表示"
    )
    
    args = parser.parse_args()
    
    # デバイスリスト表示
    if args.list_devices:
        list_audio_devices()
        return
    
    # 閾値の検証
    if not 0 < args.threshold <= 1:
        print("エラー: 閾値は0-1の範囲で指定してください")
        return
    
    # 検出器の作成と実行
    detector = WakeWordDetector(
        model_name=args.model,
        threshold=args.threshold,
        debug=args.debug
    )
    
    detector.run()

if __name__ == "__main__":
    main()