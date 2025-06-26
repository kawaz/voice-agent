# Git ワークフロー

> **最終更新**: 2025-06-25
> **カテゴリ**: Guide
> **関連文書**: [開発ガイドライン](development-guidelines.md)

## 🚨 最重要ルール：mainブランチでの作業は絶対禁止！

**なぜ重要か**: 複数のAIエージェントが同時に作業しており、mainブランチで作業すると：
- 他のエージェントがリセット/プッシュして**あなたの作業が消失**
- コミット履歴が競合して**プロジェクトが壊れる**
- 実際に2025-06-25に、mainブランチでコミットが消失する事故が発生

## 概要

このプロジェクトでは複数のAIエージェントが協働作業を行うため、明確なGitワークフローを定めています。

## 基本方針

### 1. コミットの粒度
- 作業は適切な単位でコミットを作成
- 1つのコミットは1つの論理的な変更を含む
- コミットメッセージは明確で説明的に

### 2. ブランチ戦略
- 特定機能の実装や検証を行う際は**必ずブランチを作成**
- 特にsandbox内での作業は完全に独立してブランチで実施
- ブランチ名は分かりやすく（例: `feature/whisper-sandbox`, `experiment/wake-word`）

### 3. Git Worktreeの活用（必須）

#### 🔴 絶対的なルール：必ずWorktreeで作業する

**作業開始時の最初のコマンド**：
```bash
# 1. 必ずこれを最初に実行
git worktree add -b feature/your-feature-name .worktrees/your-feature-name

# 2. worktreeに移動
cd .worktrees/your-feature-name

# 3. ここから作業開始（絶対にmainブランチには戻らない）
```

#### ⚠️ 重要な注意事項

**Worktree使用時の落とし穴**：
- 現在の作業ディレクトリを常に意識すること
- `pwd`コマンドで定期的に確認

**よくある間違い**：
```bash
# ❌ 間違い: worktree内にいるのにフルパスで実行
cd .worktrees/feature-foo
uv run /.worktrees/feature-foo/program.py  # エラー！

# ✅ 正解: 相対パスで実行
cd .worktrees/feature-foo
uv run program.py
```

**過去の事例**：
> worktree内で作成したファイルを読もうとしたら見つからず、メインの作業ツリーで書き直そうとした事例がありました。
> これは作業ディレクトリの認識ミスが原因でした。

### 4. マージ方針

#### 自動マージ可能なケース
- sandboxのような完全に独立した内容
- ドキュメントの追加・更新
- 新規ファイルの追加

#### 確認が必要なケース
- 既存ファイルの大幅な変更
- アーキテクチャに関わる変更
- コンフリクトの可能性がある変更

## ワークフロー例

### 1. Sandbox実験の場合
```bash
# 1. worktreeを作成
git worktree add .worktrees/experiment-whisper -b experiment/whisper

# 2. worktreeに移動
cd .worktrees/experiment-whisper

# 3. 作業場所を確認
pwd  # 必ず確認！

# 4. 実験作業を実施
# ... sandbox/whisper/ での作業 ...

# 5. 適切な単位でコミット
git add sandbox/whisper/
git commit -m "feat(whisper): マルチレベル認識の実装"

# 6. mainにマージ（独立した内容なので確認不要）
git switch main
git merge experiment/whisper

# 7. worktreeを削除
git worktree remove .worktrees/experiment-whisper
```

### 2. 複数エージェントの協働

各エージェントは：
1. 自分の作業用worktreeを作成
2. 独立して作業を進める
3. 定期的にmainの変更を取り込む
4. 作業完了後にmainにマージ

```bash
# Agent A: Whisper実験
git worktree add .worktrees/whisper-exp -b feature/whisper

# Agent B: Wake word実験
git worktree add .worktrees/wake-word -b feature/wake-word

# それぞれ独立して作業可能
```

## チェックリスト

作業開始時：
- [ ] 適切なブランチを作成したか
- [ ] worktreeを使用する場合は作成したか
- [ ] `pwd`で作業ディレクトリを確認したか

作業中：
- [ ] 定期的に`pwd`で場所を確認しているか
- [ ] 適切な粒度でコミットしているか
- [ ] コミットメッセージは明確か

作業完了時（マージ前レビュー）：
- [ ] すべての変更をコミットしたか
- [ ] **ファイル構成は適切か（不要なファイルはないか）**
- [ ] **ドキュメントは最新の状態を反映しているか**
- [ ] **学んだことを全体のdocsに反映したか**
- [ ] マージが必要な場合、確認が必要か判断したか
- [ ] worktreeを削除したか

## マージ前レビューの重要性

ブランチをマージする前に必ず以下を確認：

### 1. ファイル整理
- 開発過程で生まれた一時的なファイルは削除
- 古いバージョンはアーカイブへ
- ドキュメントは適切な場所に

### 2. ドキュメントの更新
- READMEは現在の状態を反映
- 新機能や変更点は文書化
- リンクが正しいか確認

### 3. 知見の共有
- 個別の学びを全体のガイドラインに反映
- エラーや解決策を記録
- ベストプラクティスを更新

## まとめ

Git worktreeは複数エージェントでの協働作業に非常に有用ですが、作業ディレクトリの認識ミスに注意が必要です。
`pwd`での確認を習慣化し、安全で効率的な開発を行いましょう。

また、**マージ前のレビュー**を徹底することで、きれいで理解しやすいプロジェクトを維持できます。