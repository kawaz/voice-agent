#!/usr/bin/env python3
"""
閾値調整のテストプログラム
最適な検出閾値を見つけるためのツール
"""

import sounddevice as sd
import numpy as np
from openwakeword.model import Model
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import time

class ThresholdTuner:
    def __init__(self, model_name="alexa", window_seconds=10):
        """
        Args:
            model_name: テストするウェイクワードモデル
            window_seconds: グラフに表示する時間窓（秒）
        """
        self.model_name = model_name
        self.window_seconds = window_seconds
        
        # モデルのロード
        print(f"モデル '{model_name}' をロード中...")
        self.model = Model(wakeword_models=[model_name], inference_framework="onnx")
        
        # 音声パラメータ
        self.sample_rate = 16000
        self.frame_length = 1280
        
        # データ保存
        self.max_points = int(window_seconds / 0.08)  # 80ms per frame
        self.scores = deque(maxlen=self.max_points)
        self.timestamps = deque(maxlen=self.max_points)
        self.audio_buffer = np.array([], dtype=np.int16)
        
        # 統計情報
        self.detection_events = []  # (timestamp, score, threshold)
        self.false_positives = 0
        self.true_positives = 0
        
        # グラフ設定
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.suptitle(f'Wake Word Detection Threshold Tuning - "{model_name}"')
        
        # 閾値候補
        self.test_thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        self.current_threshold = 0.5
        
    def audio_callback(self, indata, frames, time_info, status):
        """音声入力コールバック"""
        if status:
            print(f"オーディオエラー: {status}")
        
        # float32 -> int16
        audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
        self.audio_buffer = np.append(self.audio_buffer, audio_int16)
    
    def process_audio(self):
        """音声処理ループ"""
        while True:
            # フレーム単位で処理
            if len(self.audio_buffer) >= self.frame_length:
                frame = self.audio_buffer[:self.frame_length]
                self.audio_buffer = self.audio_buffer[self.frame_length:]
                
                # 推論
                prediction = self.model.predict(frame)
                score = prediction.get(self.model_name, 0)
                
                # データ保存
                current_time = time.time()
                self.scores.append(score)
                self.timestamps.append(current_time)
                
                # 検出イベントの記録
                if score > self.current_threshold:
                    self.detection_events.append((current_time, score, self.current_threshold))
                
            time.sleep(0.01)  # CPU使用率を下げる
    
    def update_plot(self, frame):
        """グラフ更新"""
        if len(self.scores) < 2:
            return
        
        # スコアの時系列グラフ
        self.ax1.clear()
        self.ax1.set_title('Detection Score Over Time')
        self.ax1.set_xlabel('Time (seconds ago)')
        self.ax1.set_ylabel('Score')
        self.ax1.set_ylim(0, 1)
        self.ax1.grid(True, alpha=0.3)
        
        # 時間軸の計算
        if self.timestamps:
            current_time = time.time()
            time_ago = [current_time - t for t in self.timestamps]
            
            # スコアのプロット
            self.ax1.plot(time_ago, self.scores, 'b-', label='Score')
            
            # 閾値ラインの描画
            for threshold in self.test_thresholds:
                alpha = 1.0 if threshold == self.current_threshold else 0.3
                self.ax1.axhline(y=threshold, color='r', linestyle='--', 
                               alpha=alpha, label=f'Threshold {threshold}' if alpha == 1 else '')
            
            # 最新スコアの表示
            if self.scores:
                latest_score = self.scores[-1]
                self.ax1.text(0.02, 0.95, f'Latest: {latest_score:.3f}', 
                            transform=self.ax1.transAxes, fontsize=12,
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        self.ax1.legend(loc='upper right')
        self.ax1.set_xlim(self.window_seconds, 0)
        
        # スコア分布のヒストグラム
        self.ax2.clear()
        self.ax2.set_title('Score Distribution')
        self.ax2.set_xlabel('Score')
        self.ax2.set_ylabel('Frequency')
        
        if len(self.scores) > 10:
            scores_array = np.array(self.scores)
            self.ax2.hist(scores_array, bins=50, alpha=0.7, color='blue', edgecolor='black')
            
            # 統計情報
            mean_score = np.mean(scores_array)
            std_score = np.std(scores_array)
            max_score = np.max(scores_array)
            
            stats_text = f'Mean: {mean_score:.3f}\nStd: {std_score:.3f}\nMax: {max_score:.3f}'
            self.ax2.text(0.7, 0.7, stats_text, transform=self.ax2.transAxes,
                        fontsize=10, bbox=dict(boxstyle='round', facecolor='lightgray'))
            
            # 閾値ライン
            for threshold in self.test_thresholds:
                self.ax2.axvline(x=threshold, color='red', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
    
    def on_key_press(self, event):
        """キーボードイベント処理"""
        if event.key in ['1', '2', '3', '4', '5', '6']:
            # 数字キーで閾値変更
            idx = int(event.key) - 1
            if idx < len(self.test_thresholds):
                self.current_threshold = self.test_thresholds[idx]
                print(f"\n閾値を {self.current_threshold} に変更しました")
        elif event.key == 't':
            # True Positive をマーク
            self.true_positives += 1
            print(f"\n✓ True Positive! (Total: {self.true_positives})")
        elif event.key == 'f':
            # False Positive をマーク
            self.false_positives += 1
            print(f"\n✗ False Positive! (Total: {self.false_positives})")
        elif event.key == 'r':
            # リセット
            self.detection_events.clear()
            self.false_positives = 0
            self.true_positives = 0
            print("\n統計をリセットしました")
        elif event.key == 's':
            # 統計表示
            self.show_statistics()
    
    def show_statistics(self):
        """統計情報の表示"""
        print(f"\n{'='*50}")
        print(f"統計情報 - {self.model_name}")
        print(f"{'='*50}")
        
        # 各閾値での検出数を計算
        for threshold in self.test_thresholds:
            detections = sum(1 for _, score, _ in self.detection_events if score > threshold)
            print(f"閾値 {threshold}: {detections} 回検出")
        
        print(f"\nマニュアルマーキング:")
        print(f"True Positives: {self.true_positives}")
        print(f"False Positives: {self.false_positives}")
        
        if self.true_positives + self.false_positives > 0:
            precision = self.true_positives / (self.true_positives + self.false_positives)
            print(f"Precision: {precision:.2%}")
        
        # スコア分析
        if self.scores:
            scores_array = np.array(self.scores)
            percentiles = np.percentile(scores_array, [50, 90, 95, 99])
            print(f"\nスコア分布:")
            print(f"50%: {percentiles[0]:.3f}")
            print(f"90%: {percentiles[1]:.3f}")
            print(f"95%: {percentiles[2]:.3f}")
            print(f"99%: {percentiles[3]:.3f}")
    
    def run(self):
        """メイン実行"""
        print(f"\n{'='*60}")
        print(f"閾値調整ツール - {self.model_name}")
        print(f"{'='*60}")
        print("\nキーボードショートカット:")
        print("  1-6: 閾値を変更 (0.3, 0.4, 0.5, 0.6, 0.7, 0.8)")
        print("  t: True Positive としてマーク")
        print("  f: False Positive としてマーク")
        print("  s: 統計情報を表示")
        print("  r: カウンターをリセット")
        print("\nグラフウィンドウを閉じると終了します")
        print(f"{'='*60}\n")
        
        # イベントハンドラ設定
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
        # 音声処理スレッド開始
        import threading
        audio_thread = threading.Thread(target=self.process_audio)
        audio_thread.daemon = True
        audio_thread.start()
        
        # オーディオストリーム開始
        try:
            with sd.InputStream(
                callback=self.audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.frame_length // 4
            ):
                # アニメーション開始
                ani = FuncAnimation(self.fig, self.update_plot, 
                                  interval=100, blit=False)
                plt.show()
                
        except Exception as e:
            print(f"エラー: {e}")
        
        # 終了時の統計表示
        print("\n最終統計:")
        self.show_statistics()

def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ウェイクワード検出の閾値調整ツール"
    )
    parser.add_argument(
        "--model", "-m",
        default="alexa",
        help="テストするウェイクワードモデル"
    )
    parser.add_argument(
        "--window", "-w",
        type=int,
        default=10,
        help="グラフの時間窓（秒）"
    )
    
    args = parser.parse_args()
    
    # matplotlib バックエンドの設定
    import matplotlib
    matplotlib.use('TkAgg')  # または 'Qt5Agg'
    
    tuner = ThresholdTuner(
        model_name=args.model,
        window_seconds=args.window
    )
    
    tuner.run()

if __name__ == "__main__":
    main()