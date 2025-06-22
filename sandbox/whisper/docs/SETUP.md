# Whisper環境のセットアップ手順

## 必要なツール・ライブラリ

### 1. システムレベルの依存関係

```bash
# macOS用 - Homebrewでインストール
brew install portaudio  # PyAudioのビルドに必要
brew install ffmpeg     # Whisperの音声処理に必要
```

### 2. Python環境のセットアップ

```bash
# 依存関係のインストール（pyproject.tomlから自動的に）
uv sync

# 追加のパッケージが必要な場合
uv add package-name
```

### 3. インストール済みパッケージ

以下のパッケージが自動的にインストールされます：

- openai-whisper (20240930)
- numpy (2.2.6)
- torch (2.7.1) - 約65.5MB
- pyaudio (0.2.14)
- その他の依存関係（tqdm, regex, tiktoken など）

### 4. Whisperモデルのダウンロード

初回実行時に自動的にダウンロードされます：

- tiny: 39MB
- base: 74MB （推奨）
- small: 244MB
- medium: 769MB
- large: 1.5GB

モデルは `~/.cache/whisper/` に保存されます。

## トラブルシューティング

### PyAudioのインストールエラー

```
fatal error: 'portaudio.h' file not found
```

この場合は、portaudioをインストール：

```bash
brew install portaudio
```

### マイクのアクセス権限

macOSでは初回実行時にマイクへのアクセス許可を求められます。
システム設定 > プライバシーとセキュリティ > マイク で許可してください。

## 使用例

```bash
# マイク入力でリアルタイム認識
uv run python mic_transcribe.py

# 音声ファイルの文字起こし
uv run python simple_transcribe.py audio.mp3
```