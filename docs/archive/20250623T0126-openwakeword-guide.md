# OpenWakeWord 詳細ガイド

## OpenWakeWordとは

OpenWakeWordは、オープンソースのウェイクワード（起動ワード）検出ライブラリです。"Hey Siri"や"OK Google"のような特定の言葉を検出して、音声アシスタントを起動する機能を提供します。

### 主な特徴
- **完全オープンソース**（Apache 2.0ライセンス）
- **無料**で商用利用可能
- **軽量**なニューラルネットワークモデル
- **カスタムウェイクワード**の作成が可能
- **複数のウェイクワード**を同時に検出可能

## 仕組み

### 技術的な動作原理
1. **音声ストリーム処理**: 連続的な音声入力を短いフレーム（80ms）に分割
2. **特徴抽出**: メルスペクトログラムを使用して音声の特徴を抽出
3. **ニューラルネットワーク**: 訓練済みモデルが特徴からウェイクワードを検出
4. **スコアリング**: 0-1の確率スコアで検出の確信度を出力

### アーキテクチャ
```
音声入力 → フレーム分割 → メルスペクトログラム → NN推論 → スコア出力
  ↓           (80ms)         (特徴抽出)         (ONNX)    (0-1)
マイク
```

## インストール方法

```bash
# Python環境でのインストール
uv pip install openwakeword

# 依存関係
# - onnxruntime (推論エンジン)
# - scipy (信号処理)
# - tqdm (プログレスバー)
```

## 基本的な使い方

### 1. シンプルな例

```python
import openwakeword
from openwakeword.model import Model
import pyaudio
import numpy as np

# モデルの初期化
model = Model(
    wakeword_models=["hey_jarvis"],  # プリトレーニング済みモデル
    inference_framework="onnx"
)

# 音声ストリームの設定
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1280  # 80ms at 16kHz

audio = pyaudio.PyAudio()
stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

print("Listening for wake word...")

# 検出ループ
while True:
    # 音声データの読み取り
    audio_data = stream.read(CHUNK, exception_on_overflow=False)
    
    # numpy配列に変換
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    
    # 推論実行
    prediction = model.predict(audio_array)
    
    # ウェイクワードごとのスコアをチェック
    for wakeword, score in prediction.items():
        if score > 0.5:  # 閾値
            print(f"Wake word '{wakeword}' detected! (score: {score:.2f})")
```

### 2. 実用的な実装

```python
import openwakeword
import numpy as np
import threading
import queue
from collections import deque

class WakeWordDetector:
    def __init__(self, 
                 model_names=["alexa", "hey_mycroft"], 
                 threshold=0.5,
                 buffer_duration=1.5):
        """
        Args:
            model_names: 使用するウェイクワードモデル
            threshold: 検出閾値 (0-1)
            buffer_duration: 音声バッファの長さ（秒）
        """
        self.model = Model(wakeword_models=model_names)
        self.threshold = threshold
        self.is_running = False
        
        # 音声バッファ（検出前後の音声を保持）
        self.buffer_size = int(16000 * buffer_duration)
        self.audio_buffer = deque(maxlen=self.buffer_size)
        
        # 検出結果のキュー
        self.detection_queue = queue.Queue()
        
    def start(self):
        """検出開始"""
        self.is_running = True
        self.thread = threading.Thread(target=self._detection_loop)
        self.thread.start()
        
    def stop(self):
        """検出停止"""
        self.is_running = False
        self.thread.join()
        
    def _detection_loop(self):
        """検出ループ（別スレッド）"""
        import sounddevice as sd
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio error: {status}")
            
            # バッファに音声を追加
            audio_chunk = indata[:, 0] * 32768  # float32 to int16
            self.audio_buffer.extend(audio_chunk.astype(np.int16))
            
            # 80msフレームで推論
            if len(self.audio_buffer) >= 1280:
                frame = np.array(list(self.audio_buffer)[-1280:])
                prediction = self.model.predict(frame)
                
                for wakeword, score in prediction.items():
                    if score > self.threshold:
                        # 検出時の音声バッファも保存
                        detection_data = {
                            'wakeword': wakeword,
                            'score': score,
                            'audio_buffer': np.array(self.audio_buffer),
                            'timestamp': time.inputBufferAdcTime
                        }
                        self.detection_queue.put(detection_data)
        
        # 音声ストリーム開始
        with sd.InputStream(
            callback=audio_callback,
            channels=1,
            samplerate=16000,
            blocksize=1280
        ):
            while self.is_running:
                sd.sleep(100)
    
    def get_detection(self, timeout=None):
        """検出結果を取得"""
        try:
            return self.detection_queue.get(timeout=timeout)
        except queue.Empty:
            return None

# 使用例
detector = WakeWordDetector(
    model_names=["alexa"],
    threshold=0.6
)

detector.start()

try:
    while True:
        detection = detector.get_detection(timeout=1)
        if detection:
            print(f"Wake word detected: {detection['wakeword']}")
            print(f"Score: {detection['score']:.2f}")
            # 検出後の処理（音声認識など）
            # process_voice_command(detection['audio_buffer'])
except KeyboardInterrupt:
    detector.stop()
```

## カスタムウェイクワードの作成

### 1. 日本語ウェイクワードの作成手順

```python
# training/create_custom_wakeword.py
import openwakeword
from openwakeword.custom_model_training import train_custom_model

# トレーニングデータの準備
# 1. ポジティブサンプル（ウェイクワードを含む音声）
# 2. ネガティブサンプル（ウェイクワードを含まない音声）

config = {
    "model_name": "hey_agent_japanese",
    "target_phrase": "ねえエージェント",
    "language": "ja",
    
    # TTSで合成音声を生成
    "use_tts": True,
    "tts_engine": "gTTS",  # or "pyttsx3"
    "num_tts_samples": 1000,
    
    # データ拡張
    "augmentation": {
        "speed_change": [0.9, 1.0, 1.1],
        "pitch_shift": [-2, 0, 2],
        "add_noise": True,
        "noise_levels": [0.1, 0.2, 0.3]
    },
    
    # トレーニングパラメータ
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001,
    "validation_split": 0.2
}

# モデルのトレーニング
model = train_custom_model(config)

# モデルの保存
model.save("models/hey_agent_japanese.onnx")
```

### 2. 実際のトレーニングプロセス（簡易版）

```python
import numpy as np
from openwakeword.custom_model_training import ModelTrainer
import librosa

class JapaneseWakeWordTrainer:
    def __init__(self, wake_phrase="ねえエージェント"):
        self.wake_phrase = wake_phrase
        self.trainer = ModelTrainer()
        
    def generate_training_data(self):
        """TTSを使用してトレーニングデータを生成"""
        import pyttsx3
        from pydub import AudioSegment
        import tempfile
        
        engine = pyttsx3.init()
        positive_samples = []
        
        # 異なる速度・ピッチでサンプル生成
        for rate in [150, 200, 250]:  # 話速
            for volume in [0.7, 1.0]:  # 音量
                engine.setProperty('rate', rate)
                engine.setProperty('volume', volume)
                
                # 一時ファイルに保存
                with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
                    engine.save_to_file(self.wake_phrase, tmp.name)
                    engine.runAndWait()
                    
                    # 音声を読み込み
                    audio, sr = librosa.load(tmp.name, sr=16000)
                    positive_samples.append(audio)
        
        return positive_samples
    
    def augment_audio(self, audio_samples):
        """データ拡張"""
        augmented = []
        
        for audio in audio_samples:
            # 元の音声
            augmented.append(audio)
            
            # ノイズ追加
            noise = np.random.normal(0, 0.005, audio.shape)
            augmented.append(audio + noise)
            
            # ピッチシフト
            pitched = librosa.effects.pitch_shift(audio, sr=16000, n_steps=2)
            augmented.append(pitched)
            
        return augmented
    
    def train(self):
        """モデルのトレーニング"""
        # データ生成
        positive_samples = self.generate_training_data()
        positive_samples = self.augment_audio(positive_samples)
        
        # ネガティブサンプル（一般的な日本語音声）
        # ここでは省略（実際には必要）
        negative_samples = []
        
        # トレーニング
        model = self.trainer.train(
            positive_samples=positive_samples,
            negative_samples=negative_samples,
            model_name="hey_agent_ja"
        )
        
        return model

# 使用例
trainer = JapaneseWakeWordTrainer()
custom_model = trainer.train()
```

## 実用的なTips

### 1. 検出精度の向上
```python
# 複数フレームでの確認（誤検出削減）
class RobustWakeWordDetector:
    def __init__(self, model, threshold=0.5, confirmations=2):
        self.model = model
        self.threshold = threshold
        self.confirmations = confirmations
        self.detection_history = deque(maxlen=confirmations)
    
    def detect(self, audio_frame):
        prediction = self.model.predict(audio_frame)
        
        for wakeword, score in prediction.items():
            if score > self.threshold:
                self.detection_history.append((wakeword, score))
                
                # 連続して検出された場合のみ確定
                if len(self.detection_history) == self.confirmations:
                    if all(w == wakeword for w, _ in self.detection_history):
                        avg_score = np.mean([s for _, s in self.detection_history])
                        self.detection_history.clear()
                        return wakeword, avg_score
        
        return None, 0
```

### 2. 省電力化
```python
# CPU使用率を下げる設定
model = Model(
    wakeword_models=["alexa"],
    inference_framework="onnx",
    # 推論の頻度を下げる（精度とのトレードオフ）
    inference_period=0.2  # 200msごと（デフォルトは80ms）
)
```

### 3. 複数ウェイクワード対応
```python
# 異なるアクションを持つ複数のウェイクワード
wake_actions = {
    "alexa": lambda: print("Alexaモード起動"),
    "computer": lambda: print("コンピューターモード起動"),
    "hey_agent": lambda: print("エージェントモード起動")
}

model = Model(wakeword_models=list(wake_actions.keys()))
```

## トラブルシューティング

### よくある問題

1. **検出されない**
   - マイクの音量確認
   - サンプリングレート（16kHz必須）
   - 閾値の調整（0.3-0.7）

2. **誤検出が多い**
   - 閾値を上げる（0.6-0.8）
   - 確認フレーム数を増やす
   - ノイズ除去の追加

3. **CPU使用率が高い**
   - 推論頻度を下げる
   - より小さいモデルを使用
   - C++実装の使用を検討

## まとめ

OpenWakeWordは無料で使えるウェイクワード検出ライブラリとして、十分実用的な性能を持っています。特に：
- プライバシーを重視する場合
- カスタムウェイクワードが必要な場合
- 完全オフラインで動作させたい場合

に適しています。