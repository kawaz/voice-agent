# 音声認識エンジンの検討タスク

音声認識エンジンについて検討し、docs/speech-recognition-engine-comparison.md に検討結果をまとめてください。

## 検討項目

1. **主要な音声認識エンジンの比較**
   - Web Speech API
   - OpenAI Whisper (ローカル/API)
   - Google Speech-to-Text API
   - Azure Speech Services
   - Amazon Transcribe
   - Julius (オープンソース)

2. **比較観点**
   - 日本語認識精度
   - リアルタイム性（遅延）
   - オフライン動作の可否
   - 消費リソース（CPU/メモリ）
   - 実装の容易さ
   - コスト（初期/運用）
   - ストリーミング対応
   - カスタマイズ性

3. **実装サンプル**
   - 各エンジンの簡単な実装例を含める
   - 必要なセットアップ手順

4. **推奨事項**
   - MVP用の推奨
   - 本番環境用の推奨
   - Raspberry Pi用の推奨