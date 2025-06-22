# OpenWakeWord セットアップガイド

## 必要な環境

- Python 3.8以上
- macOS、Linux、またはWindows
- マイク（内蔵またはUSB）

## インストール手順

### 1. プロジェクトのセットアップ

```bash
cd sandbox/openwakeword
# 依存関係のインストール（pyproject.tomlから自動的に）
uv sync
```

### 2. 追加パッケージ（オプション）

グラフ表示機能を使う場合（既に開発用依存関係に含まれています）：
```bash
uv add --dev matplotlib
```

音声ファイル処理を行う場合：
```bash
uv add librosa
```

## 動作確認

### 基本テスト

```bash
# OpenWakeWordが正しくインストールされているか確認
uv run python test_basic.py
```

期待される出力：
- OpenWakeWordのバージョン
- 利用可能なモデルリスト
- モデルロードの成功
- 推論時間の測定結果

### マイクテスト

```bash
# マイクの動作確認
uv run python test_microphone.py --list-devices
```

マイクが表示されない場合：
- macOS: システム環境設定 > セキュリティとプライバシー > マイク
- Windows: 設定 > プライバシー > マイク
- Linux: `arecord -l` でデバイスを確認

## トラブルシューティング

### ImportError: No module named 'openwakeword'

```bash
# 仮想環境が有効化されているか確認
which python  # .venv/bin/python が表示されるべき

# 再インストール
uv pip install --force-reinstall openwakeword
```

### マイクが認識されない

macOSの場合：
```bash
# ターミナルにマイクアクセス権限を付与
# システム環境設定 > セキュリティとプライバシー > プライバシー > マイク
# Terminal.app または iTerm.app にチェック
```

### portaudioエラー

macOSの場合：
```bash
brew install portaudio
```

Linuxの場合：
```bash
sudo apt-get install portaudio19-dev
```

### CPU使用率が高い

`continuous_detection.py` の実行時：
```bash
# 推論頻度を下げる（精度とのトレードオフ）
uv run python continuous_detection.py --inference-period 0.16
```

## 初回実行時の注意

1. **モデルのダウンロード**: 初回実行時は自動的にモデルがダウンロードされます（数MB）
2. **マイク権限**: 初回実行時にマイクへのアクセス許可を求められます
3. **キャッシュ**: モデルは `~/.cache/openwakeword/` に保存されます

## 推奨設定

### 開発環境

```bash
# デバッグモードで実行（スコア表示）
uv run python test_microphone.py --debug

# 閾値を調整（デフォルト: 0.5）
uv run python test_microphone.py --threshold 0.6
```

### 本番環境

```bash
# バッファリング付き連続検出
uv run python continuous_detection.py --pre-buffer 1.5 --post-buffer 3.0
```

## 次のステップ

1. `test_microphone.py` でウェイクワード検出を体験
2. `custom_threshold.py` で最適な閾値を見つける
3. `continuous_detection.py` で実用的な実装を確認
4. Whisperと統合して完全な音声アシスタントを構築