# 改訂版MVP実装計画

## Web Speech API制限を踏まえた方針変更

Web Speech APIの60秒制限とヘッドレス環境での制約により、MVPの実装方針を見直します。

## 新しいMVPアプローチ

### オプション1: Electron + Web Speech API（デモ用）
- **用途**: 短期間のデモンストレーション
- **実装**: Electronアプリとして実装（GUI必須）
- **制限対応**: 60秒ごとの自動再起動実装
- **メリット**: 実装が簡単、すぐに動作確認可能
- **デメリット**: 24時間運用は現実的でない

### オプション2: Node.js + Google Speech-to-Text API（推奨）
- **用途**: 実用的なMVP
- **実装**: Node.jsサーバーとして実装
- **メリット**: 
  - ヘッドレス環境で動作
  - 24時間連続運用可能
  - ストリーミング対応
- **デメリット**: 
  - APIキー設定が必要
  - 月60分以降は有料

### オプション3: Python + Whisper API（バランス型）
- **用途**: コスト重視のMVP
- **実装**: Pythonスクリプト
- **メリット**:
  - 低コスト（$0.006/分）
  - 高精度
  - ヘッドレス対応
- **デメリット**:
  - リアルタイム性が低い

## 推奨MVP実装計画

### フェーズ1: Google Speech-to-Text APIでの基本実装
1. Node.jsプロジェクトセットアップ
2. Google Cloud認証設定
3. ストリーミング音声認識実装
4. 音声合成（Google TTS）実装
5. 基本的なWebインターフェース

### フェーズ2: ローカル処理への移行準備
1. 音声認識エンジンの抽象化
2. Whisperローカル版のテスト
3. ウェイクワード機能の追加

### 実装構成

```
voice-agent/
├── server/
│   ├── index.js          # メインサーバー
│   ├── speech/
│   │   ├── recognition.js # 音声認識（Google STT）
│   │   └── synthesis.js   # 音声合成（Google TTS）
│   └── audio/
│       └── stream.js      # 音声ストリーム処理
├── client/
│   ├── index.html        # Webインターフェース
│   └── app.js            # クライアントロジック
└── config/
    └── google-cloud.json  # 認証情報

```

## 開発ステップ

### 1. 環境準備
```bash
# Google Cloud CLIのインストール
brew install google-cloud-sdk

# プロジェクト作成
cd mvp
npm init -y
npm install @google-cloud/speech @google-cloud/text-to-speech
npm install express socket.io
npm install node-record-lpcm16  # 音声録音用
```

### 2. Google Cloud設定
- Google Cloud Consoleでプロジェクト作成
- Speech-to-Text APIとText-to-Speech APIを有効化
- サービスアカウントキーの作成
- 環境変数設定

### 3. 基本実装
- 音声ストリーミング録音
- リアルタイム文字起こし
- テキスト読み上げ
- WebSocketでクライアント連携

## 成功基準（改訂版）

- [ ] Google Speech-to-Text APIで音声認識できる
- [ ] リアルタイムで文字起こしが表示される
- [ ] 認識したテキストを音声で読み上げる
- [ ] 1時間以上の連続動作が可能
- [ ] ヘッドレス環境で動作する

## コスト見積もり

- 開発段階: 月60分まで無料
- 本番運用: 
  - 1日1時間使用: 約$30/月
  - 24時間連続: 約$700/月
  
→ ローカルWhisperへの移行が必須