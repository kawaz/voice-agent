#!/usr/bin/env python3
"""
実用的な連続ウェイクワード検出
- バッファリング機能
- 検出前後の音声保存
- Whisperとの連携準備
"""

import sounddevice as sd
import numpy as np
from openwakeword.model import Model
import time
from collections import deque
import threading
import queue
from datetime import datetime
import os

class ContinuousWakeWordDetector:
    def __init__(self, 
                 wake_word="alexa",
                 threshold=0.5,
                 pre_buffer_sec=1.0,
                 post_buffer_sec=2.0):
        """
        Args:
            wake_word: 検出するウェイクワード
            threshold: 検出閾値
            pre_buffer_sec: ウェイクワード検出前の音声バッファ（秒）
            post_buffer_sec: ウェイクワード検出後の音声録音時間（秒）
        """
        self.wake_word = wake_word
        self.threshold = threshold
        self.pre_buffer_sec = pre_buffer_sec
        self.post_buffer_sec = post_buffer_sec
        
        # モデルのロード
        print(f"モデル '{wake_word}' をロード中...")
        self.model = Model(wakeword_models=[wake_word], inference_framework="onnx")
        print("✓ モデルのロードに成功しました")
        
        # 音声パラメータ
        self.sample_rate = 16000
        self.frame_length = 1280  # 80ms
        self.block_size = 320     # 20ms (低レイテンシ)
        
        # バッファ
        pre_buffer_samples = int(self.sample_rate * self.pre_buffer_sec)
        self.pre_buffer = deque(maxlen=pre_buffer_samples)
        self.audio_queue = queue.Queue()
        
        # 状態管理
        self.is_listening = True
        self.is_recording_command = False
        self.command_buffer = []
        self.command_start_time = 0
        
        # 検出履歴
        self.detection_history = []
        
    def audio_callback(self, indata, frames, time, status):
        """音声入力コールバック"""
        if status:
            print(f"オーディオエラー: {status}")
        
        # float32 -> int16
        audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
        
        # キューに追加（処理は別スレッド）
        self.audio_queue.put(audio_int16)
    
    def process_audio_stream(self):
        """音声ストリーム処理（別スレッド）"""
        frame_buffer = np.array([], dtype=np.int16)
        
        while self.is_listening:
            try:
                # キューから音声データを取得
                audio_chunk = self.audio_queue.get(timeout=0.1)
                
                # プリバッファに追加（常時）
                self.pre_buffer.extend(audio_chunk)
                
                # コマンド録音中の場合
                if self.is_recording_command:
                    self.command_buffer.extend(audio_chunk)
                    
                    # 録音時間チェック
                    elapsed = time.time() - self.command_start_time
                    if elapsed >= self.post_buffer_sec:
                        self.process_command()
                        continue
                
                # フレームバッファに追加
                frame_buffer = np.append(frame_buffer, audio_chunk)
                
                # フレーム単位で処理
                while len(frame_buffer) >= self.frame_length:
                    frame = frame_buffer[:self.frame_length]
                    frame_buffer = frame_buffer[self.frame_length:]
                    
                    # ウェイクワード検出
                    if not self.is_recording_command:
                        self.detect_wake_word(frame)
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"処理エラー: {e}")
    
    def detect_wake_word(self, frame):
        """ウェイクワード検出"""
        # 推論
        prediction = self.model.predict(frame)
        score = prediction.get(self.wake_word, 0)
        
        # スコア表示（デバッグ）
        if score > 0.1:
            bar = '█' * int(score * 20)
            print(f"\r[{bar:<20}] {score:.3f}", end="", flush=True)
        
        # 閾値チェック
        if score > self.threshold:
            self.on_wake_word_detected(score)
    
    def on_wake_word_detected(self, score):
        """ウェイクワード検出時の処理"""
        print(f"\n\n{'='*50}")
        print(f"🎯 ウェイクワード '{self.wake_word}' を検出！")
        print(f"スコア: {score:.3f}")
        print(f"時刻: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*50}")
        print(f"\n📢 音声コマンドをどうぞ... ({self.post_buffer_sec}秒間録音)")
        
        # コマンド録音開始
        self.is_recording_command = True
        self.command_start_time = time.time()
        
        # プリバッファの内容をコマンドバッファに追加
        self.command_buffer = list(self.pre_buffer)
        
        # 検出履歴に追加
        self.detection_history.append({
            'timestamp': datetime.now(),
            'score': score
        })
    
    def process_command(self):
        """録音されたコマンドを処理"""
        self.is_recording_command = False
        
        # 音声データを numpy 配列に変換
        audio_data = np.array(self.command_buffer, dtype=np.int16)
        
        print(f"\n✅ 録音完了！")
        print(f"録音時間: {len(audio_data) / self.sample_rate:.1f}秒")
        print(f"サンプル数: {len(audio_data)}")
        
        # ここでWhisperによる音声認識を実行
        print("\n🤖 音声認識を実行... (Whisperとの連携部分)")
        print(">>> ここで whisper.transcribe(audio_data) を実行")
        
        # 音声データを保存（デバッグ用）
        if os.environ.get('SAVE_AUDIO', '').lower() == 'true':
            self.save_audio(audio_data)
        
        # バッファをクリア
        self.command_buffer = []
        
        print(f"\n{'='*50}")
        print("再びウェイクワードを待っています...\n")
    
    def save_audio(self, audio_data):
        """音声データを保存（デバッグ用）"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"wake_command_{timestamp}.wav"
        
        import wave
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        print(f"📁 音声を保存しました: {filename}")
    
    def show_statistics(self):
        """統計情報の表示"""
        print("\n📊 検出統計:")
        print(f"総検出回数: {len(self.detection_history)}")
        
        if self.detection_history:
            avg_score = np.mean([d['score'] for d in self.detection_history])
            print(f"平均スコア: {avg_score:.3f}")
            
            # 最近の5件
            print("\n最近の検出:")
            for detection in self.detection_history[-5:]:
                print(f"  - {detection['timestamp'].strftime('%H:%M:%S')} "
                      f"(スコア: {detection['score']:.3f})")
    
    def run(self):
        """検出開始"""
        print(f"\n{'='*60}")
        print("💫 連続ウェイクワード検出システム")
        print(f"{'='*60}")
        print(f"ウェイクワード: '{self.wake_word}'")
        print(f"検出閾値: {self.threshold}")
        print(f"プリバッファ: {self.pre_buffer_sec}秒")
        print(f"録音時間: {self.post_buffer_sec}秒")
        print(f"{'='*60}")
        print("\nウェイクワードを話してください... (Ctrl+Cで終了)")
        print("ヒント: 音声保存を有効にする場合は SAVE_AUDIO=true を設定\n")
        
        # 処理スレッド開始
        process_thread = threading.Thread(target=self.process_audio_stream)
        process_thread.daemon = True
        process_thread.start()
        
        try:
            # オーディオストリーム開始
            with sd.InputStream(
                callback=self.audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.block_size
            ):
                while True:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            self.is_listening = False
            print("\n\n検出を終了します...")
            self.show_statistics()
            print("\n👋 お疲れ様でした！")

def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="連続ウェイクワード検出"
    )
    parser.add_argument(
        "--model", "-m",
        default="alexa",
        help="ウェイクワードモデル"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=0.5,
        help="検出閾値"
    )
    parser.add_argument(
        "--pre-buffer", "-p",
        type=float,
        default=1.0,
        help="ウェイクワード前のバッファ時間（秒）"
    )
    parser.add_argument(
        "--post-buffer", "-o",
        type=float,
        default=3.0,
        help="ウェイクワード後の録音時間（秒）"
    )
    
    args = parser.parse_args()
    
    detector = ContinuousWakeWordDetector(
        wake_word=args.model,
        threshold=args.threshold,
        pre_buffer_sec=args.pre_buffer,
        post_buffer_sec=args.post_buffer
    )
    
    detector.run()

if __name__ == "__main__":
    main()