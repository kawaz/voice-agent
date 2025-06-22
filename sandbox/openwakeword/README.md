# OpenWakeWord サンドボックス

OpenWakeWordの動作確認環境です。

## 現在の状況

OpenWakeWordのv0.6.0では、モデルファイルの配布形式が変更されており、プリトレーニング済みモデルが自動的にダウンロードされない問題があります。

### 動作する主要プログラム

- `continuous_detection.py` - 実用的な連続検出実装（Whisper統合準備済み）
- `custom_threshold.py` - 最適な閾値を見つけるための調整ツール

### 解決方法（検討中）

1. **tflite-runtimeのインストール**（ARM系プロセッサ向け）
2. **カスタムモデルの作成**
3. **古いバージョンのOpenWakeWordを使用**

## セットアップ

```bash
# 依存関係のインストール（pyproject.tomlから）
uv sync
```

## ファイル構成

```
openwakeword/
├── continuous_detection.py      # 🎯 実用的な連続検出（バッファリング付き）
├── custom_threshold.py          # 閾値調整ツール（リアルタイムグラフ表示）
├── download_models.py           # モデルダウンロードユーティリティ
├── pyproject.toml              # プロジェクト設定と依存関係
├── uv.lock                     # 依存関係のロックファイル
│
├── archive/                    # アーカイブされた開発・実験ファイル
│   ├── 20250623T020005-test_basic.py          # 基本動作確認
│   ├── 20250623T020005-test_microphone.py     # マイク入力検出テスト
│   ├── 20250623T020005-test_multiple_wakewords.py  # 複数ウェイクワード
│   ├── 20250623T020005-test_audio_monitor.py  # 音声モニター（VADなし）
│   ├── 20250623T020005-test_with_predownloaded.py  # モデル確認テスト
│   ├── 20250623T020005-simple_test.py         # シンプルな録音テスト
│   ├── 20250623T020005-wake_word_demo.py      # デモ用簡易版
│   └── 20250623T020005-wake_word_easy.py      # 超簡易版（教育用）
│
└── docs/                       # ドキュメント
    ├── SETUP.md               # 詳細なセットアップガイド
    ├── FINDINGS.md            # 技術検証の詳細結果
    └── SUMMARY.md             # 検証サマリー
```

## 使い方

### 1. 連続検出（推奨）

```bash
# 実用的な連続検出（バッファリング付き）
uv run python continuous_detection.py

# オプション指定
uv run python continuous_detection.py --pre-buffer 1.5 --post-buffer 3.0
```

### 2. 閾値調整ツール

```bash
# リアルタイムで閾値を調整（グラフ表示）
uv run python custom_threshold.py
```

## OpenWakeWordの特徴

- **完全オープンソース**: Apache 2.0ライセンス
- **無料**: 商用利用も可能
- **軽量**: 組み込みデバイスでも動作
- **カスタマイズ可能**: 独自のウェイクワード作成可能

## プリトレーニング済みモデル

利用可能なモデル:
- `alexa` - "Alexa"を検出
- `hey_jarvis` - "Hey Jarvis"を検出
- `hey_mycroft` - "Hey Mycroft"を検出
- `hey_rhasspy` - "Hey Rhasspy"を検出

## トラブルシューティング

### マイクが認識されない場合

```bash
# macOSの場合、マイク権限を確認
# システム環境設定 > セキュリティとプライバシー > プライバシー > マイク

# 利用可能なオーディオデバイスを確認
uv run python -c "import sounddevice as sd; print(sd.query_devices())"
```

### CPU使用率が高い場合

`continuous_detection.py`の`INFERENCE_PERIOD`を調整してください（デフォルト: 0.08秒）。

## 次のステップ

1. カスタムウェイクワードの作成（日本語対応）
2. Whisperとの統合（ウェイクワード検出後に音声認識）
3. 省電力化の最適化