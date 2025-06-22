# 技術的意思決定

## 概要

3つの技術検討結果を基に、音声エージェントプロジェクトの技術的な意思決定をまとめます。

## 基本方針

**ローカルファースト**: プライバシー保護とオフライン動作を重視し、可能な限りローカルで処理を完結させます。

## 1. 音声認識エンジン

### 最終選定: OpenAI Whisper（ローカル版）
- **理由**: 
  - 完全オフライン動作
  - 高い日本語認識精度
  - 無料・オープンソース
  - プライバシー保護
- **実装オプション**:
  - Python: `whisper`パッケージ
  - C++: `whisper.cpp`（高速版）
  - Node.js: `whisper-node`
- **モデル選択**:
  - 開発: baseモデル（74MB）
  - 本番: smallモデル（244MB）

### 代替案（クラウド依存を許容する場合）
- Google Speech-to-Text API（リアルタイム性重視）
- Web Speech API（ブラウザベースのデモ用）

## 2. ウェイクワード検出

### 最終選定: Picovoice Porcupine
- **理由**: 
  - 実証済みの安定性（2025年6月22日検証）
  - 日本語含む17言語対応
  - 高精度（97%以上の検出率）
  - 無料枠あり（3ユーザーまで）
- **制約**: 
  - APIキー管理が必要
  - 商用利用は有料

### 検証済み代替案
- **OpenWakeWord**（v0.6.0で検証）
  - ❌ macOSでの動作に問題あり
  - ❌ プリトレーニング済みモデルが利用不可
  - ✅ 完全オープンソースだが実用性に課題
  - 詳細: [sandbox/openwakeword/FINDINGS.md](../sandbox/openwakeword/FINDINGS.md)

### その他の選択肢
- **Whisper + VAD**（音声アクティビティ検出）
  - ウェイクワードなしで音声検出
  - 消費電力が高いが柔軟性あり

## 3. クロスプラットフォーム対応

### アーキテクチャ
- **抽象化レイヤー**: プラットフォーム依存部分を分離
- **共通コア**: TypeScript/JavaScript
- **プラットフォーム固有**: 音声I/O、システムAPI

### ハードウェア推奨構成

#### macOS開発環境
- マイク: 内蔵マイクで十分
- 追加ハードウェア: 不要

#### Raspberry Pi本番環境
- **モデル**: Raspberry Pi 4 (4GB以上)
- **マイク**: ReSpeaker 2-Mics Pi HAT
- **スピーカー**: 3.5mmジャック接続
- **電源**: 5V 3A以上

## 4. 音声合成

### 最終選定: VOICEVOX
- **理由**:
  - 完全無料・オープンソース
  - 高品質な日本語音声
  - ローカル動作
  - 複数の話者選択可能
- **代替案**: edge-tts（Microsoft Edge TTS のローカル版）

## 5. 実装アプローチ

### フェーズ1（MVP - 1週間）
1. Whisperローカル版で音声認識
2. VOICEVOXで音声合成
3. 簡単なコマンド認識（ルールベース）

### フェーズ2（ウェイクワード - 1週間）
1. OpenWakeWordの導入
2. カスタム日本語ウェイクワード作成
3. 常時待機モードの実装

### フェーズ3（高度な機能 - 2週間）
1. ローカルLLM導入（llama.cpp等）
2. 家電制御API連携
3. プラグインシステム

## 6. 開発環境セットアップ

### 必要なツール
```bash
# macOS
brew install portaudio ffmpeg

# Python環境（uv使用）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate

# 音声処理パッケージ
uv pip install openai-whisper
uv pip install sounddevice numpy
uv pip install requests  # VOICEVOX用

# Whisperモデルのダウンロード（初回のみ）
python -c "import whisper; whisper.load_model('base')"
```

### Raspberry Pi
```bash
# 音声関連
sudo apt-get install portaudio19-dev
sudo apt-get install alsa-utils

# Node.js (NodeSource)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 7. パフォーマンス目標

- **応答時間**: < 2秒（ウェイクワード検出から応答開始まで）
- **CPU使用率**: < 30%（Raspberry Pi 4、通常動作時）
- **メモリ使用量**: < 500MB
- **消費電力**: < 5W（Raspberry Pi本体含む）

## 次のステップ

1. MVPの実装開始（Web Speech API使用）
2. 基本的なUIの作成
3. 音声認識の精度テスト
4. ウェイクワード機能の追加検討