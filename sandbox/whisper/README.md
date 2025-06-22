# Whisper サンドボックス

OpenAI Whisperの動作確認環境です。

## セットアップ

```bash
# システムの依存関係
brew install portaudio  # PyAudioのビルドに必要
brew install ffmpeg     # Whisperの音声処理に必要

# 依存関係のインストール（pyproject.tomlから）
uv sync
```

## 現在のファイル構成

### メインプログラム
- `mic_transcribe_auto.py` - 🎯 **推奨** 最適化された自動音声認識
- `mic_transcribe_continuous_debug.py` - デバッグ版（音量レベル確認用）
- `simple_transcribe.py` - 音声ファイルの簡単な文字起こしツール

### ドキュメント
- `DEVELOPMENT_HISTORY.md` - 開発過程の詳細な記録
- `FINDINGS.md` - 音声認識の検証結果と知見
- `SETUP.md` - 詳細なセットアップ手順

### アーカイブ
- `archive/` - 開発過程の各バージョンを時系列で保存

## 使い方

### 1. マイク入力で自動音声認識（推奨）

```bash
uv run python mic_transcribe_auto.py
```

話すと自動的に録音が開始され、話し終わると認識結果が表示されます。

### 2. 音声ファイルの文字起こし

```bash
# デフォルト（baseモデル）で文字起こし
uv run python simple_transcribe.py your_audio.mp3

# smallモデルを使用
uv run python simple_transcribe.py your_audio.mp3 small
```

### 3. 音量レベルの確認（環境調整用）

```bash
uv run python mic_transcribe_continuous_debug.py
```

マイクの音量レベルがリアルタイムで表示されます。

## Whisperの特徴

- **完全オフライン**: インターネット接続不要
- **多言語対応**: 日本語を含む多数の言語をサポート
- **複数のモデルサイズ**:
  - tiny (39MB): 最速、精度は低め
  - base (74MB): バランス型
  - small (244MB): 高精度 ← 現在の推奨
  - medium (769MB): より高精度
  - large (1.5GB): 最高精度

## 注意事項

- 初回実行時はモデルのダウンロードに時間がかかります
- macOSでは初回実行時にマイクへのアクセス許可が必要です
- モデルは `~/.cache/whisper/` に保存されます

## 開発履歴

詳細な開発過程と知見については `DEVELOPMENT_HISTORY.md` を参照してください。