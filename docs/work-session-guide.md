# 作業セッションガイド

このドキュメントは、新規セッションで作業を開始する際の標準的な手順をまとめたものです。

## 🚀 作業開始時の手順

### 1. 現在のブランチとworktreeの確認

```bash
# 現在どこにいるか確認
pwd

# mainブランチにいる場合は、必ずworktreeに移動！
# worktreeの一覧を確認
git worktree list

# 既存のworktreeがある場合
cd .worktrees/feature-xxx/

# 新規worktreeが必要な場合
git worktree add .worktrees/feature-new-feature -b feature-new-feature
cd .worktrees/feature-new-feature/
```

### 2. CLAUDE.mdの確認

```bash
# 必ず最初にCLAUDE.mdを読む
cat CLAUDE.md

# 関連ドキュメントも確認
ls docs/
```

### 3. 作業状況の把握

```bash
# gitの状態確認
git status

# 前回の作業内容を確認
ls docs/work-logs/

# サンドボックスの確認（ある場合）
ls sandbox/
```

### 4. TodoListの確認・作成

必ずTodoReadツールで既存のタスクを確認し、新規タスクがあればTodoWriteで追加する。

## 🏁 作業完了時の手順

### 1. サンドボックスの整理

```bash
# サンドボックス内で作業した場合
cd sandbox/your-work/

# ディレクトリ構造を整理
mkdir -p archive working

# テスト・デモファイルをアーカイブ
mv test_*.py demo_*.py archive/

# 中間ファイルをworkingに移動
mv *_old.py *_backup.py working/

# 本番用ファイルのみを残す
ls -la
```

### 2. ドキュメントの作成・更新

```bash
# 作業日誌を作成
# ファイル名: YYYYMMDD-brief-description.md
vim docs/work-logs/20250627-tts-implementation.md

# 技術ドキュメントの更新（必要に応じて）
vim docs/technical-decisions.md
```

### 3. コミットの準備

```bash
# 変更内容の確認
git status
git diff

# 不要なファイルの削除
rm -rf tmp/ cache/ *.log

# .gitignoreの確認・更新
cat .gitignore
```

### 4. テストの実行（ある場合）

```bash
# lintやtypecheckがある場合
npm run lint
npm run typecheck

# Pythonプロジェクトの場合
uv run pytest
```

### 5. ドキュメント整合性チェック

```bash
# ドキュメントのリンク切れチェック
# docs/README.md内のリンクを確認
grep -o '\[.*\]([^)]*\.md)' docs/README.md | while read link; do
  file=$(echo $link | sed 's/.*(\(.*\))/\1/')
  [ ! -f "docs/$file" ] && echo "リンク切れ: $file"
done

# CLAUDE.md内のリンクを確認
grep -o '\[.*\](docs/[^)]*\.md)' CLAUDE.md | while read link; do
  file=$(echo $link | sed 's/.*(\(.*\))/\1/')
  [ ! -f "$file" ] && echo "リンク切れ: $file"
done

# 新規ドキュメントの確認
# docs/内の.mdファイルでREADME.mdに記載されていないものを探す
find docs -name "*.md" -not -path "docs/work-logs/*" -not -path "docs/archive/*" | while read file; do
  basename=$(basename "$file")
  grep -q "$basename" docs/README.md || echo "未記載: $file"
done
```

### 6. 最終確認とコミット

```bash
# 全体の状態確認
git status

# コミット（必要に応じて）
git add .
git commit -m "feat: 実装内容の簡潔な説明"
```

## ⚠️ 重要な注意事項

### worktreeを使う理由

- **mainブランチを汚さない**: 実験的な作業はworktreeで
- **並行作業が可能**: 複数のエージェントが同時に作業可能
- **切り替えが簡単**: ブランチ間の移動が高速

### よくある間違い

1. **mainブランチで直接作業してしまう**
   - 必ずworktreeを使用する
   - `pwd`で現在地を確認

2. **CLAUDE.mdを読まずに作業開始**
   - プロジェクト固有のルールがある
   - 必ず最初に確認

3. **作業日誌を書かない**
   - 次のエージェントが状況を把握できない
   - 簡潔でも良いので必ず記録

4. **サンドボックスを整理しない**
   - 大量のテストファイルが残る
   - archive/working構造を活用

## 📝 チェックリスト

### 作業開始時
- [ ] worktreeに移動した
- [ ] CLAUDE.mdを読んだ
- [ ] 関連ドキュメントを確認した
- [ ] TodoListを確認した
- [ ] git statusで状態を確認した

### 作業完了時
- [ ] サンドボックスを整理した
- [ ] 作業日誌を作成した
- [ ] 不要ファイルを削除した
- [ ] テストを実行した（ある場合）
- [ ] ドキュメント整合性チェックを実行した
- [ ] 新規ドキュメントがCLAUDE.md/README.mdにリンクされている
- [ ] git statusで最終確認した