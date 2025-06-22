# Whisperサンドボックス

OpenAI Whisperを使った音声認識の実験と実装を行うサンドボックスです。

## 📁 ディレクトリ構成

```
whisper/
├── README.md                         # このファイル
├── SETUP.md                         # 環境構築手順
├── pyproject.toml                   # uvプロジェクト設定
├── uv.lock                         # 依存関係ロックファイル
├── .python-version                 # Python 3.11指定
│
├── mic_transcribe_final.py          # 🎯 最終実装版（マルチレベル認識）
├── mic_transcribe_auto.py           # マイク入力の自動認識（シンプル版）
├── mic_transcribe_continuous_debug.py # デバッグ用（音量レベル表示）
├── simple_transcribe.py             # 音声ファイルの文字起こし
│
├── archive/                         # 開発過程のアーカイブ
│   ├── README.md                    # アーカイブの説明
│   └── YYYYMMDDTHHSS-*.py          # タイムスタンプ付き過去バージョン
│
└── ドキュメント/
    ├── NEXT_IMPROVEMENTS.md         # 今後の改善案
    ├── REALTIME_IMPROVEMENTS.md     # リアルタイム性能向上の検討
    └── SPEAKER_DIARIZATION.md       # 話者分離技術の調査
```

## 🚀 クイックスタート

### 1. 環境構築
```bash
# システムの依存関係
brew install portaudio ffmpeg

# Python依存関係のインストール
uv sync
```

### 2. 使い方

#### マイク入力のリアルタイム認識（推奨）
```bash
# 最終実装版（マルチレベル認識） - 最高精度
uv run python mic_transcribe_final.py

# シンプル版（軽量）
uv run python mic_transcribe_auto.py

# デバッグ版（音量調整用）
uv run python mic_transcribe_continuous_debug.py
```

#### 音声ファイルの文字起こし
```bash
uv run python simple_transcribe.py audio.mp3
```

## 🎯 どのファイルを使うべきか？

### 本番利用
- **`mic_transcribe_final.py`** - 最も高精度な実装
  - マルチレベル認識（3秒/8秒/20秒/無音区切り）
  - 誤認識対策済み
  - カラーコード表示

### テスト・開発
- **`mic_transcribe_auto.py`** - シンプルで理解しやすい
  - 基本的な無音検出
  - 軽量な実装

### トラブルシューティング
- **`mic_transcribe_continuous_debug.py`** - 音量レベルの確認
  - リアルタイム音量メーター
  - 閾値調整の参考に

## 📊 パフォーマンス

| ファイル | 精度 | 処理速度 | メモリ使用量 | 用途 |
|---------|------|----------|-------------|------|
| final.py | ★★★★★ | ★★★☆☆ | 約800MB | 本番利用 |
| auto.py | ★★★☆☆ | ★★★★★ | 約500MB | 軽量版 |
| debug.py | ★★★☆☆ | ★★★★☆ | 約500MB | デバッグ |

## 🔧 カスタマイズ

### 音声検出閾値の調整
```python
# mic_transcribe_auto.py 内
self.silence_threshold = 250  # 環境に応じて調整
```

### モデルサイズの変更
```python
# どのファイルでも共通
model_name = "small"  # tiny, base, small, medium, large
```

## ⚠️ 注意事項

- 初回実行時はモデルのダウンロードに時間がかかります
- macOSでは初回実行時にマイクへのアクセス許可が必要です
- モデルは `~/.cache/whisper/` に保存されます

## 📚 関連ドキュメント

- 技術的な知見: `/docs/sandbox-findings.md`
- 環境構築の詳細: `SETUP.md`
- 今後の改善案: `NEXT_IMPROVEMENTS.md`