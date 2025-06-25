# ドキュメント一覧

このディレクトリには、Voice Agentプロジェクトの各種ドキュメントが含まれています。

## ドキュメント一覧

### 🎯 プロジェクト計画
- [`final-implementation-plan.md`](final-implementation-plan.md) - 最終実装計画 ⭐️
- [`mvp-implementation-status.md`](mvp-implementation-status.md) - MVP実装状況

### 🏗️ アーキテクチャ
- [`architecture.md`](architecture.md) - システムアーキテクチャ
- [`local-first-architecture.md`](local-first-architecture.md) - ローカルファーストアーキテクチャ
- [`cross-platform-consideration.md`](cross-platform-consideration.md) - Cross-Platform Considerations (English)

### 🔧 技術仕様
- [`technical-decisions.md`](technical-decisions.md) - 技術選定の決定事項 ⭐️
- [`speech-recognition-engine-comparison.md`](speech-recognition-engine-comparison.md) - 音声認識エンジン比較 🎤
- [`sandbox-findings.md`](sandbox-findings.md) - サンドボックス検証結果まとめ 🧪

### 🎙️ ウェイクワード関連
- [`porcupine-setup-guide.md`](porcupine-setup-guide.md) - Porcupineセットアップガイド ⭐️
- [`custom-wake-word-guide.md`](custom-wake-word-guide.md) - カスタムウェイクワードガイド
- [`custom-wake-word-implementation-guide.md`](custom-wake-word-implementation-guide.md) - カスタムウェイクワード実装ガイド
- [`wake-word-detection-comparison.md`](wake-word-detection-comparison.md) - ウェイクワード検出比較
- [`wake-word-detection-technical-overview.md`](wake-word-detection-technical-overview.md) - ウェイクワード検出技術概要
- [`wake-word-design.md`](wake-word-design.md) - ウェイクワードの設計
- [`wake-word-low-power-recommendations.md`](wake-word-low-power-recommendations.md) - 低消費電力ウェイクワード推奨事項

### 📚 開発ガイド
- [`development-guidelines.md`](development-guidelines.md) - 開発ガイドライン（サンドボックス管理、作業日誌含む） 📝
- [`git-workflow.md`](git-workflow.md) - Gitワークフロー（複数エージェント協働） 🆕
- [`language-specific-guidelines.md`](language-specific-guidelines.md) - 言語別開発ガイドライン ⭐️
- [`uv-migration-guide.md`](uv-migration-guide.md) - uv移行ガイド（pip→uv add） 🆕
- [`documentation-standards.md`](documentation-standards.md) - ドキュメント作成標準
- [`notification-guide.md`](notification-guide.md) - 通知実装ガイド

### 📓 その他
- [`work-logs/`](work-logs/) - AIの作業日誌（率直な思考プロセスの記録） 🆕
- [`archive/`](archive/) - アーカイブされた古いドキュメント（歴史的価値）

## ドキュメントの読み方

### 初めての方
1. [`final-implementation-plan.md`](final-implementation-plan.md) でプロジェクトの全体像を把握
2. [`technical-decisions.md`](technical-decisions.md) で技術選定の理由を理解
3. [`mvp-implementation-status.md`](mvp-implementation-status.md) で現在の実装状況を確認

### 開発に参加する方
1. [`development-guidelines.md`](development-guidelines.md) で開発ルールを確認
2. [`git-workflow.md`](git-workflow.md) でGitの使い方を理解
3. [`language-specific-guidelines.md`](language-specific-guidelines.md) で言語別の注意点を確認

### 特定の技術について知りたい方
- 音声認識: [`speech-recognition-engine-comparison.md`](speech-recognition-engine-comparison.md)
- ウェイクワード: [`porcupine-setup-guide.md`](porcupine-setup-guide.md)
- サンドボックス検証結果: [`sandbox-findings.md`](sandbox-findings.md)

## 更新頻度

- 🔴 **高頻度更新**: implementation-status, work-logs
- 🟡 **中頻度更新**: technical-decisions, sandbox-findings
- 🟢 **低頻度更新**: architecture, guidelines

## 凡例

- 🎤 音声関連
- 🧪 実験・検証
- 📝 ガイドライン・手順
- 🆕 最近追加/更新
- ⭐️ 重要度高