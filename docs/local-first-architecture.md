# ローカルファースト アーキテクチャ設計

## 概要

プライバシー保護とオフライン動作を重視し、すべての処理をローカルで完結させるアーキテクチャを設計します。

## 技術選定（ローカル完結版）

### 1. 音声認識

#### 選定: OpenAI Whisper（ローカル版）
- **メリット**:
  - 完全オフライン動作
  - 高い認識精度（特に日本語）
  - 無料・オープンソース
  - APIキー不要
- **実装方法**:
  - Python: `whisper` パッケージ
  - C++: `whisper.cpp`（より高速）
  - Node.js: `whisper-node`（whisper.cppのバインディング）
- **モデルサイズ**:
  - tiny: 39MB（最速、精度低）
  - base: 74MB（バランス型）
  - small: 244MB（高精度）
  - medium: 769MB（より高精度）

#### リアルタイム処理の実現
```python
# ストリーミング処理の例
import whisper
import numpy as np
import sounddevice as sd
from queue import Queue

model = whisper.load_model("base")
audio_queue = Queue()

def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

# 1秒ごとに処理
def process_audio():
    audio_buffer = []
    while True:
        if not audio_queue.empty():
            audio_buffer.append(audio_queue.get())
            if len(audio_buffer) >= 16:  # 1秒分
                audio = np.concatenate(audio_buffer)
                result = model.transcribe(audio, language='ja')
                print(result["text"])
                audio_buffer = audio_buffer[-8:]  # 0.5秒重複
```

### 2. ウェイクワード検出

#### 選定: OpenWakeWord
- **メリット**:
  - 完全オープンソース（Apache 2.0）
  - ローカル動作
  - カスタムウェイクワード作成可能
  - 無料
- **日本語対応**:
  - デフォルトモデルは英語のみ
  - カスタムモデルで日本語ウェイクワード作成可能

#### 代替案: Porcupine（無料枠）
- 3ユーザーまで無料
- 日本語含む17言語対応
- より高精度だがAPIキー必要

### 3. 音声合成

#### 選定: VOICEVOX（日本語特化）
- **メリット**:
  - 完全無料・オープンソース
  - 高品質な日本語音声
  - ローカル動作
  - 複数の話者選択可能
- **実装**:
  ```python
  import requests
  import json
  import simpleaudio as sa
  
  # VOICEVOXエンジンをローカルで起動
  # テキストから音声合成
  text = "こんにちは"
  response = requests.post(
      "http://localhost:50021/audio_query",
      params={"text": text, "speaker": 1}
  )
  query = response.json()
  
  response = requests.post(
      "http://localhost:50021/synthesis",
      params={"speaker": 1},
      json=query
  )
  
  # 音声再生
  audio = sa.play_buffer(
      response.content,
      num_channels=1,
      bytes_per_sample=2,
      sample_rate=24000
  )
  ```

#### 代替案: edge-tts（Microsoft Edge の TTS）
- ローカル処理（ただし初回はモデルダウンロード）
- 多言語対応
- 無料

### 4. システムアーキテクチャ

```
┌─────────────────────────────────────────┐
│         ローカル音声エージェント           │
├─────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐   │
│  │ OpenWakeWord │    │   Whisper    │   │
│  │  (常時待機)   │    │ (音声認識)   │   │
│  └──────┬──────┘    └──────┬──────┘   │
│         │ 検出              │ テキスト    │
│         ▼                   ▼           │
│  ┌─────────────────────────────────┐   │
│  │      インテントエンジン            │   │
│  │  (ローカルLLM or ルールベース)    │   │
│  └──────────────┬──────────────────┘   │
│                 │ アクション             │
│                 ▼                       │
│  ┌─────────┐  ┌─────────┐  ┌────────┐│
│  │ VOICEVOX │  │家電制御  │  │その他   ││
│  │(音声合成) │  │  API    │  │サービス ││
│  └─────────┘  └─────────┘  └────────┘│
└─────────────────────────────────────────┘
```

## 実装プラン

### フェーズ1: 基本機能（1週間）
1. Whisperによる音声認識
2. VOICEVOXによる音声合成
3. 簡単なコマンド認識（ルールベース）

### フェーズ2: ウェイクワード（1週間）
1. OpenWakeWordの導入
2. カスタムウェイクワード作成
3. 常時待機モードの実装

### フェーズ3: 高度な機能（2週間）
1. ローカルLLM導入（llama.cpp等）
2. 家電制御API連携
3. プラグインシステム

## ハードウェア要件

### 開発環境（macOS）
- メモリ: 8GB以上
- ストレージ: 10GB以上（モデル用）

### 本番環境（Raspberry Pi）
- モデル: Raspberry Pi 4（4GB以上）
- ストレージ: 32GB以上
- 音声デバイス: ReSpeaker 2-Mics Pi HAT

## パフォーマンス最適化

### 1. モデル選択
- Whisper: "base"モデルで開始（74MB）
- 精度が必要な場合のみ"small"へ

### 2. 並列処理
- ウェイクワード検出: 専用スレッド
- 音声認識: メインスレッド
- 音声合成: 非同期処理

### 3. メモリ管理
- 音声バッファサイズの最適化
- モデルの遅延ロード
- 不要なモデルのアンロード

## プライバシーとセキュリティ

1. **データ保存なし**: 音声データは処理後即座に破棄
2. **ネットワーク分離**: 基本機能はインターネット不要
3. **ローカル処理**: すべての音声処理はデバイス内で完結
4. **オプトイン**: クラウド機能は明示的に有効化

## 開発開始手順

```bash
# Python環境構築（uv使用）
uv venv
source .venv/bin/activate

# 必要なパッケージ
uv pip install openai-whisper
uv pip install sounddevice numpy
uv pip install requests  # VOICEVOX用

# VOICEVOXのダウンロードと起動
# https://voicevox.hiroshiba.jp/ からダウンロード

# Whisperモデルのダウンロード（初回のみ）
python -c "import whisper; whisper.load_model('base')"
```

## まとめ

このアーキテクチャにより：
- 完全なオフライン動作
- プライバシー保護
- 無料での実装
- 日本語対応
- リアルタイム処理

が実現できます。