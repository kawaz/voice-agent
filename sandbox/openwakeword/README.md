# OpenWakeWord サンドボックス

OpenWakeWordの動作確認環境です。

## 現在の状況

OpenWakeWordのv0.6.0では、モデルファイルの配布形式が変更されており、プリトレーニング済みモデルが自動的にダウンロードされない問題があります。

### 動作確認済みのプログラム

- `test_audio_monitor.py` - 音声入力モニタリング（OpenWakeWordなし）
- `simple_test.py` - 基本的な音声録音テスト

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

- `test_basic.py` - OpenWakeWordの基本的な動作確認
- `test_microphone.py` - マイク入力でのウェイクワード検出
- `test_multiple_wakewords.py` - 複数ウェイクワード同時検出
- `continuous_detection.py` - 連続検出デモ（実用的な例）
- `custom_threshold.py` - 閾値調整のテスト
- `requirements.txt` - 必要なパッケージリスト

## 使い方

### 1. 基本的なテスト

```bash
# 利用可能なモデルの確認
uv run python test_basic.py

# 音声ファイルでのテスト（準備中）
uv run python test_audio_file.py test_audio.wav
```

### 2. マイク入力でのリアルタイム検出

```bash
# デフォルトのウェイクワード（"alexa"）で検出
uv run python test_microphone.py

# カスタムウェイクワードを指定
uv run python test_microphone.py --model hey_jarvis

# 閾値を調整（デフォルト: 0.5）
uv run python test_microphone.py --threshold 0.7
```

### 3. 複数ウェイクワード検出

```bash
# 複数のウェイクワードを同時に検出
uv run python test_multiple_wakewords.py
```

### 4. 連続検出デモ

```bash
# 実用的な連続検出（バッファリング付き）
uv run python continuous_detection.py
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