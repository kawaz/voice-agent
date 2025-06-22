# ドキュメント一覧

このディレクトリには、Voice Agentプロジェクトの各種ドキュメントが含まれています。

## ドキュメントの構成

### 🎯 プロジェクト計画
- [`development-plan.md`](development-plan.md) - 開発計画
- [`mvp-implementation-plan.md`](mvp-implementation-plan.md) - MVP実装計画
- [`revised-mvp-plan.md`](revised-mvp-plan.md) - 改訂版MVP計画
- [`final-implementation-plan.md`](final-implementation-plan.md) - 最終実装計画
- [`mvp-implementation-status.md`](mvp-implementation-status.md) - MVP実装状況

### 🏗️ アーキテクチャ
- [`architecture.md`](architecture.md) - システムアーキテクチャ
- [`local-first-architecture.md`](local-first-architecture.md) - ローカルファーストアーキテクチャ
- [`cross-platform-consideration.md`](cross-platform-consideration.md) - クロスプラットフォーム考慮事項

### 🔧 技術仕様
- [`technical-decisions.md`](technical-decisions.md) - 技術選定の決定事項
- [`speech-recognition-engine-comparison.md`](speech-recognition-engine-comparison.md) - 音声認識エンジン比較 🎤
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
- [`sandbox-findings.md`](sandbox-findings.md) - サンドボックス検証結果まとめ 🧪

### 🔧 実装ガイド
- [`openwakeword-guide.md`](openwakeword-guide.md) - OpenWakeWord実装ガイド
- [`custom-wake-word-implementation-guide.md`](custom-wake-word-implementation-guide.md) - カスタムウェイクワード実装ガイド

### 📋 ステータス・記録
- [`uv-migration-status.md`](uv-migration-status.md) - uv移行ステータス
- [`document-organization-plan.md`](document-organization-plan.md) - ドキュメント整理計画

### 📓 作業日誌
- [`work-logs/`](work-logs/) - AIの作業日誌（率直な思考プロセスの記録） 🆕

## ドキュメントの読み方

### 初めての方
1. [`development-plan.md`](development-plan.md) でプロジェクトの全体像を把握
2. [`technical-decisions.md`](technical-decisions.md) で技術選定の理由を理解
3. [`mvp-implementation-plan.md`](mvp-implementation-plan.md) で現在の実装状況を確認

### 開発に参加する方
1. [`development-guidelines.md`](development-guidelines.md) で開発ルールを確認
2. [`git-workflow.md`](git-workflow.md) でGitの使い方を理解
3. [`language-specific-guidelines.md`](language-specific-guidelines.md) で言語別の注意点を確認

### 特定の技術について知りたい方
- 音声認識: [`speech-recognition-engine-comparison.md`](speech-recognition-engine-comparison.md)
- ウェイクワード: [`wake-word-detection-comparison.md`](wake-word-detection-comparison.md)
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