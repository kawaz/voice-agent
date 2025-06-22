# 最終実装計画

## 概要

ローカルファーストのアプローチで、プライバシー保護とオフライン動作を実現する音声エージェントを開発します。

## 技術スタック

- **音声認識**: OpenAI Whisper（ローカル版）
- **ウェイクワード**: Picovoice Porcupine（検証済み、高性能）
- **音声合成**: VOICEVOX
- **実装言語**: Python（uvでパッケージ管理）
- **プラットフォーム**: macOS（開発）、Raspberry Pi 4（本番）

## 実装スケジュール

### Week 1: 基本機能実装

#### Day 1-2: 環境構築とWhisper実装
```python
# mvp/speech_recognition.py
import whisper
import sounddevice as sd
import numpy as np
from queue import Queue
import threading

class SpeechRecognizer:
    def __init__(self, model_size="base"):
        self.model = whisper.load_model(model_size)
        self.audio_queue = Queue()
        self.is_recording = False
        
    def start_recording(self):
        self.is_recording = True
        self.stream = sd.InputStream(
            callback=self._audio_callback,
            channels=1,
            samplerate=16000
        )
        self.stream.start()
        
    def _audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            self.audio_queue.put(indata.copy())
            
    def process_audio(self):
        # 1秒ごとに音声を処理
        audio_buffer = []
        while self.is_recording:
            if not self.audio_queue.empty():
                audio_buffer.append(self.audio_queue.get())
                if len(audio_buffer) >= 16:  # 1秒分
                    audio = np.concatenate(audio_buffer)
                    result = self.model.transcribe(
                        audio.flatten(), 
                        language='ja'
                    )
                    yield result["text"]
                    # 0.5秒重複させて連続性を保つ
                    audio_buffer = audio_buffer[-8:]
```

#### Day 3-4: VOICEVOX統合
```python
# mvp/speech_synthesis.py
import requests
import json
import simpleaudio as sa
import subprocess

class SpeechSynthesizer:
    def __init__(self, speaker_id=1):
        self.base_url = "http://localhost:50021"
        self.speaker_id = speaker_id
        self._start_voicevox()
        
    def _start_voicevox(self):
        # VOICEVOXエンジンを起動
        subprocess.Popen([
            "/path/to/VOICEVOX/run"
        ])
        
    def synthesize(self, text):
        # 音声クエリの作成
        query_response = requests.post(
            f"{self.base_url}/audio_query",
            params={"text": text, "speaker": self.speaker_id}
        )
        query = query_response.json()
        
        # 音声合成
        synthesis_response = requests.post(
            f"{self.base_url}/synthesis",
            params={"speaker": self.speaker_id},
            json=query
        )
        
        return synthesis_response.content
        
    def play_audio(self, audio_data):
        # 音声再生
        play_obj = sa.play_buffer(
            audio_data,
            num_channels=1,
            bytes_per_sample=2,
            sample_rate=24000
        )
        play_obj.wait_done()
```

#### Day 5: 統合とテスト
```python
# mvp/main.py
from speech_recognition import SpeechRecognizer
from speech_synthesis import SpeechSynthesizer
import threading

class VoiceAgent:
    def __init__(self):
        self.recognizer = SpeechRecognizer()
        self.synthesizer = SpeechSynthesizer()
        
    def run(self):
        print("音声エージェント起動中...")
        self.recognizer.start_recording()
        
        for text in self.recognizer.process_audio():
            if text.strip():
                print(f"認識: {text}")
                # エコーバック（認識した内容を読み上げ）
                audio = self.synthesizer.synthesize(text)
                self.synthesizer.play_audio(audio)

if __name__ == "__main__":
    agent = VoiceAgent()
    agent.run()
```

### Week 2: ウェイクワード実装

#### Day 6-7: Porcupine導入
```python
# mvp/wake_word_detector.py
import pvporcupine
import pvrecorder
import os

class WakeWordDetector:
    def __init__(self, keywords=None, keyword_paths=None):
        # APIキー取得
        access_key = os.environ.get('PICOVOICE_ACCESS_KEY')
        if not access_key:
            raise ValueError("PICOVOICE_ACCESS_KEY環境変数が必要です")
        
        # Porcupine初期化
        if keyword_paths:
            # カスタムウェイクワード（.ppnファイル）
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keyword_paths=keyword_paths
            )
        else:
            # プリセットキーワード
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keywords=keywords or ['picovoice']
            )
        
        # レコーダー初期化
        self.recorder = pvrecorder.PvRecorder(
            frame_length=self.porcupine.frame_length
        )
    
    def start(self):
        """検出開始"""
        self.recorder.start()
    
    def detect(self):
        """ウェイクワード検出（ブロッキング）"""
        pcm = self.recorder.read()
        keyword_index = self.porcupine.process(pcm)
        return keyword_index >= 0
    
    def stop(self):
        """検出停止"""
        self.recorder.stop()
    
    def cleanup(self):
        """リソース解放"""
        self.recorder.delete()
        self.porcupine.delete()
```

#### Day 8-9: カスタムウェイクワード作成
- Picovoice Consoleで日本語ウェイクワード作成
- 推奨: 「ねえハウス」「おっけーはうす」など
- 作成時間: 約5分（Webコンソール使用）
- 複数パターン登録で認識率向上

#### Day 10: 統合
- ウェイクワード検出後のみ音声認識を開始
- 省電力モードの実装（待機時CPU 2.4%）
- Porcupine（常時待機）→ Whisper（検出時のみ）の連携

### Week 3-4: 高度な機能

#### 意図理解エンジン
```python
# mvp/intent_engine.py
class IntentEngine:
    def __init__(self):
        self.commands = {
            "電気": self.control_light,
            "エアコン": self.control_ac,
            "天気": self.get_weather,
        }
        
    def process(self, text):
        for keyword, action in self.commands.items():
            if keyword in text:
                return action(text)
        return "理解できませんでした"
```

#### 家電制御API連携
- Nature Remo API
- SwitchBot API

## ディレクトリ構造

```
voice-agent/
├── mvp/
│   ├── __init__.py
│   ├── main.py                 # メインエントリーポイント
│   ├── speech_recognition.py   # 音声認識（Whisper）
│   ├── speech_synthesis.py     # 音声合成（VOICEVOX）
│   ├── wake_word_detector.py   # ウェイクワード検出
│   ├── intent_engine.py        # 意図理解
│   └── config.py              # 設定
├── models/                     # Whisperモデル、カスタムウェイクワード
├── tests/                      # テストコード
├── requirements.txt            # 依存関係
└── README.md
```

## 成功基準

- [ ] Whisperで日本語音声認識が動作
- [ ] VOICEVOXで自然な音声合成
- [ ] 1秒以内の応答時間
- [ ] ウェイクワードで起動
- [ ] 簡単なコマンドの理解と実行
- [ ] 1時間以上の安定動作

## 今後の拡張

1. **ローカルLLM統合**
   - llama.cppでローカルLLM実行
   - より自然な対話の実現

2. **マルチモーダル対応**
   - カメラ入力との統合
   - ジェスチャー認識

3. **分散処理**
   - 複数のRaspberry Piでの負荷分散
   - エッジコンピューティング

## 開始手順

```bash
# リポジトリのクローン
cd /Users/kawaz/.dotfiles/local/share/repos/github.com/kawaz/voice-agent

# Python環境構築
uv venv
source .venv/bin/activate

# 依存関係インストール
uv pip install openai-whisper sounddevice numpy requests
uv pip install pvporcupine pvrecorder

# VOICEVOXダウンロード
# https://voicevox.hiroshiba.jp/

# Picovoice APIキー設定
# https://console.picovoice.ai/ でアカウント作成後、APIキー取得
export PICOVOICE_ACCESS_KEY='your-api-key-here'

# 実行
cd mvp
python main.py
```