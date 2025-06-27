# Voice Agentアーキテクチャ分析

## 現在のアーキテクチャの問題点

### 1. 現状の構成

```
main.py (VoiceAssistant)
├── MultilingualWakeWordDetector
│   ├── 日本語Porcupineインスタンス
│   └── 英語Porcupineインスタンス
├── WhisperProcessor
│   ├── ワーカー0 (Whisperモデル所有)
│   └── ワーカー1 (Whisperモデル所有)
└── AudioRecorder
```

### 2. 問題点

1. **リソースの無駄遣い**
   - Whisperモデルが2つロードされている（メモリ消費）
   - ウェイクワード検出とWhisperが密結合

2. **アーキテクチャの問題**
   - 各コンポーネントが独立していない
   - メッセージング機構がない
   - 将来の拡張が困難

3. **終了処理の問題**
   - multiprocessingのプロセスが正しく終了しない
   - Ctrl+C時にエラーが発生

## 理想のアーキテクチャ

### 1. コンポーネント構成

```
Controller (調整役)
├── WakeWordService
│   ├── LanguageDetector[ja] (Porcupine)
│   └── LanguageDetector[en] (Porcupine)
├── TranscriptionService (Whisper)
│   └── WorkerPool (共有モデル)
├── CommandProcessor (将来)
├── SpeechSynthesizer (将来)
└── DisplayService (将来)
```

### 2. メッセージフロー

```
1. WakeWordService → Controller: "wake_word_detected"
2. Controller → TranscriptionService: "start_transcription"
3. TranscriptionService → Controller: "transcription_result"
4. Controller → CommandProcessor: "process_command"
5. CommandProcessor → SpeechSynthesizer: "speak_response"
```

### 3. 各サービスの責務

#### WakeWordService
- 常時起動でウェイクワードを監視
- 検出時にControllerに通知
- CPU使用率は最小限

#### TranscriptionService
- 待機状態では音声をバッファリング（処理はしない）
- Controllerからの指示で文字起こし開始
- 結果をControllerに返す

#### Controller
- 全体の調整役
- 各サービス間のメッセージング
- 状態管理

### 4. 利点

1. **疎結合**
   - 各サービスが独立
   - テスト・開発が容易

2. **拡張性**
   - 新機能の追加が簡単
   - 既存機能への影響が最小

3. **効率性**
   - リソースの共有が適切
   - 必要な時だけ処理を実行

## 実装方針

1. **メッセージング**
   - Python標準のQueueを使用
   - 非同期処理にasyncioを活用

2. **プロセス管理**
   - グレースフルシャットダウンの実装
   - シグナルハンドリングの改善

3. **設定管理**
   - 各サービスの設定を分離
   - 環境変数での制御

## 次のステップ

1. グレースフルシャットダウンの実装
2. メッセージングシステムの設計
3. 改善版プロトタイプの実装