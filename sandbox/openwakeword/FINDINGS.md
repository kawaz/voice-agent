# OpenWakeWord 検証結果

## 概要

OpenWakeWordの動作検証を行った結果、以下の課題が判明しました。

## 主な課題

### 1. モデルファイルの問題

OpenWakeWord v0.6.0では：
- プリトレーニング済みモデルが自動的にダウンロードされない
- デフォルトでtflite形式のモデルを期待するが、ONNXランタイムしかインストールされていない
- `inference_framework="onnx"`を指定しても、対応するONNXモデルが存在しない

### 2. 依存関係の問題

- `tflite-runtime`は主にARM系プロセッサ（Raspberry Pi等）向け
- macOS（Intel/Apple Silicon）では`tflite-runtime`のインストールが困難
- Python 3.11との互換性問題（一部の依存関係）

## 動作確認できた機能

### 音声入力モニタリング

`test_audio_monitor.py`で以下を確認：
- マイク入力の取得 ✓
- リアルタイム音量レベル表示 ✓
- 16kHz、80msフレームでの処理 ✓

```
[██████████████████████                            ] 0.220  🟡 中音量
```

## 推奨される対応策

### 短期的対応

1. **Picovoice Porcupineの使用**
   - より成熟したウェイクワード検出ライブラリ
   - 日本語を含む多言語対応
   - 無料枠あり（3ユーザーまで）

2. **音声アクティビティ検出（VAD）での代替**
   - ウェイクワードなしで音声検出
   - Whisperと組み合わせて使用

### 長期的対応

1. **カスタムウェイクワードモデルの作成**
   - OpenWakeWordの学習機能を使用
   - 日本語ウェイクワードの作成

2. **別のオープンソース実装の検討**
   - Mycroft Precise
   - Snowboy（開発終了だが動作する）

## 技術的詳細

### OpenWakeWordのアーキテクチャ

```
音声入力 (16kHz)
    ↓
フレーム分割 (80ms = 1280サンプル)
    ↓
特徴抽出 (メルスペクトログラム)
    ↓
ニューラルネットワーク推論
    ↓
スコア出力 (0-1)
```

### 必要なリソース

- CPU: 低（1コアの10-15%程度）
- メモリ: 約100MB
- モデルサイズ: 1-5MB/モデル

## 結論

OpenWakeWordは優れたアーキテクチャを持つが、現在のバージョンではセットアップに課題がある。プロジェクトの要件を考慮すると：

1. **開発段階**: Picovoice Porcupineを推奨
2. **MVP**: VADベースの簡易実装
3. **将来**: OpenWakeWordのカスタムモデル作成

## 参考リンク

- [OpenWakeWord GitHub](https://github.com/dscripka/openWakeWord)
- [Picovoice Porcupine](https://picovoice.ai/platform/porcupine/)
- [Whisper + VAD統合例](../whisper/mic_transcribe_continuous.py)