# 改善版Voice Agentアーキテクチャ設計

## 設計方針

1. **疎結合**: 各サービスが独立して動作
2. **メッセージング**: Queueベースの非同期通信
3. **拡張性**: 新機能の追加が容易
4. **効率性**: リソースの適切な共有

## システム構成

```
┌─────────────────────────────────────────────────────┐
│                   Controller                         │
│  (全体調整・状態管理・メッセージルーティング)           │
└─────────────────┬───────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┬─────────────┐
    │             │             │             │             │
┌───▼───┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
│ Wake   │   │Whisper  │   │Command  │   │Speech   │   │Display  │
│ Word   │   │Service  │   │Processor│   │Output   │   │Service  │
│Service │   │         │   │(将来)   │   │(将来)   │   │(将来)   │
└────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
```

## メッセージ定義

### 1. WakeWordDetectedMessage
```python
{
    "type": "wake_word_detected",
    "timestamp": float,
    "wake_word": {
        "name": str,
        "language": str,
        "confidence": float
    }
}
```

### 2. StartTranscriptionMessage
```python
{
    "type": "start_transcription",
    "timestamp": float,
    "timeout": float  # 最大録音時間
}
```

### 3. TranscriptionResultMessage
```python
{
    "type": "transcription_result",
    "timestamp": float,
    "text": str,
    "language": str,
    "duration": float,
    "confidence": float
}
```

### 4. ProcessCommandMessage
```python
{
    "type": "process_command",
    "timestamp": float,
    "text": str,
    "context": dict
}
```

### 5. SpeakMessage
```python
{
    "type": "speak",
    "timestamp": float,
    "text": str,
    "voice": str,
    "priority": int
}
```

## サービス詳細設計

### Controller

**責務**:
- 各サービスの起動・停止
- メッセージのルーティング
- 全体の状態管理
- エラーハンドリング

**実装**:
```python
class Controller:
    def __init__(self):
        self.services = {}
        self.message_queue = asyncio.Queue()
        self.state = ControllerState.IDLE
    
    async def start(self):
        # 各サービスを起動
        await self._start_services()
        # メッセージループを開始
        await self._message_loop()
    
    async def _message_loop(self):
        while self.running:
            message = await self.message_queue.get()
            await self._route_message(message)
```

### WakeWordService

**責務**:
- 複数言語のウェイクワード検出
- 検出時のController通知
- CPU使用率の最小化

**実装**:
```python
class WakeWordService(BaseService):
    def __init__(self, controller_queue):
        self.controller_queue = controller_queue
        self.detectors = {}  # 言語別検出器
    
    async def process_audio(self, audio_frame):
        for lang, detector in self.detectors.items():
            if result := detector.process(audio_frame):
                await self._notify_detection(result)
    
    async def _notify_detection(self, result):
        message = WakeWordDetectedMessage(
            wake_word=result,
            timestamp=time.time()
        )
        await self.controller_queue.put(message)
```

### WhisperService

**責務**:
- 音声の文字起こし
- バッファリングと効率的な処理
- 結果のController通知

**実装**:
```python
class WhisperService(BaseService):
    def __init__(self, controller_queue):
        self.controller_queue = controller_queue
        self.model = None  # 遅延ロード
        self.is_active = False
    
    async def start_transcription(self):
        self.is_active = True
        # モデルのロード（初回のみ）
        if not self.model:
            self.model = await self._load_model()
        # 録音と認識を開始
        result = await self._transcribe()
        # 結果を送信
        await self._send_result(result)
```

## 実装ステップ

### Phase 1: 基本構造（現在）
1. メッセージングシステムの実装
2. Controller基盤の作成
3. 既存機能のサービス化

### Phase 2: サービス実装
1. WakeWordServiceの実装
2. WhisperServiceの実装
3. 統合テスト

### Phase 3: 拡張（将来）
1. CommandProcessorの追加
2. SpeechOutputの追加
3. DisplayServiceの追加

## 設定管理

### 環境変数
```bash
# 基本設定
VOICE_AGENT_LOG_LEVEL=INFO
VOICE_AGENT_DATABASE_PATH=./data/voice_agent.db

# サービス別設定
WAKE_WORD_SENSITIVITY=0.5
WHISPER_MODEL=small
WHISPER_LANGUAGE=ja
```

### 設定ファイル（config.yaml）
```yaml
controller:
  message_queue_size: 1000
  shutdown_timeout: 30

services:
  wake_word:
    languages:
      - ja
      - en
    sensitivity: 0.5
  
  whisper:
    model: small
    language: ja
    num_workers: 2
```

## エラーハンドリング

1. **サービスレベル**: 各サービス内でエラーをキャッチ
2. **Controller レベル**: サービス障害の検出と回復
3. **グレースフルシャットダウン**: 全サービスの安全な停止

## パフォーマンス考慮

1. **非同期処理**: asyncioによる効率的な並行処理
2. **リソース共有**: Whisperモデルの単一インスタンス
3. **バッファリング**: 音声データの効率的な処理
4. **遅延ロード**: 必要時のみリソースを確保

## テスト戦略

1. **単体テスト**: 各サービスの個別テスト
2. **統合テスト**: メッセージフローのテスト
3. **負荷テスト**: 並行処理のパフォーマンス確認