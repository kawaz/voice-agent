# Voice Agentプロジェクト作業ガイド

## 🚨 最重要事項：必ずGit Worktreeで作業してください！

### ❌ 絶対にやってはいけないこと
- **mainブランチでの直接作業は厳禁です**
- mainブランチでコミットすると他のエージェントの作業と競合し、**作業が消失する事故が発生します**

### ✅ 正しい作業手順
```bash
# 1. 新しい機能の作業を始める時は必ずworktreeを作成
git worktree add -b feature/your-feature-name .worktrees/your-feature-name

# 2. worktreeに移動して作業
cd .worktrees/your-feature-name

# 3. ここで開発・テスト・コミットを行う
```

**理由**: 複数のAIエージェントが同時に作業しているため、mainブランチは予告なくリセット・変更される可能性があります。

---

このプロジェクトで作業を行う際は、必ず以下のドキュメントを参照してください。

## 🎌 言語設定
- **チャットは日本語で行ってください**

## 📚 必読ドキュメント

作業を開始する前に、`docs/`ディレクトリ内の以下のドキュメントを確認してください：

⚠️ **重要**: 以下のドキュメントは単にリストとして把握するだけでなく、**必ず各リンク先の内容を実際に読んで理解してから作業を開始してください**。指示の徹底がされていないケースが多発しています。

### 開発方針
- **[開発ガイドライン](docs/development-guidelines.md)** - サンドボックスの活用方法、作業日誌の作成など
- **[作業セッションガイド](docs/work-session-guide.md)** - 作業開始・完了時の標準手順 🆕
- **[Git ワークフロー](docs/git-workflow.md)** - 複数エージェント協働時のGit操作方法
- **[通知ガイド](docs/notification-guide.md)** - ユーザーへの通知実装ガイドライン
- **[言語別ガイドライン](docs/language-specific-guidelines.md)** - 特にPythonでの`uv`使用方法

### プロジェクト理解
- **[最終実装計画](docs/final-implementation-plan.md)** - 現在の技術スタックと実装計画
- **[技術的意思決定](docs/technical-decisions.md)** - 技術選定の根拠と決定事項
- **[MVP実装ステータス](docs/mvp-implementation-status.md)** - 現在の進捗状況
- **[TTS実装ガイド](docs/tts-implementation-guide.md)** - 音声合成の実装詳細 🆕

## 🛠️ 開発環境

### Python開発
- **必ず`uv`を使用**してパッケージ管理を行う（`pip`は使用禁止）
- 詳細は[uv移行ガイド](docs/uv-migration-guide.md)を参照

### 作業の進め方
1. **必ずGit Worktreeを作成して作業** (`.worktrees/feature-名`ディレクトリ)
2. サンドボックスで実験的な実装を行う
3. 作業日誌を`docs/work-logs/`に記録する
4. 得られた知見を全体のドキュメントに反映する

## 📋 プロジェクト情報

- **目的**: 音声認識を使った家電操作デバイスの開発
- **現在のフェーズ**: MVP実装完了（音声認識→文字起こし→読み上げ）
- **技術スタック**: 
  - 音声認識: OpenAI Whisper（ローカル版）
  - ウェイクワード: Picovoice Porcupine
  - 音声合成: edge-tts / VOICEVOX

## ⚠️ 重要な注意事項

- APIキーなどの機密情報は環境変数または.envファイルで管理
- .gitignoreに機密ファイルを必ず追加
- コミット前に必ずファイル整理とドキュメント更新を確認

詳細な情報は[docs/README.md](docs/README.md)から各ドキュメントを参照してください。