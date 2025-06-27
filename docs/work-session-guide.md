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

### 5. 作業中のコミット習慣

**重要**: 作業が完了してからまとめてコミットするのではなく、適切な単位で作業しながらコミットする。

```bash
# ❌ 悪い例：全ての作業が終わってから
git add -A
git commit -m "feat: 大量の変更をまとめてコミット"

# ✅ 良い例：機能単位でコミット
# 1. 新機能のコア実装
git add src/new_feature.py
git commit -m "feat: 新機能のコア実装を追加"

# 2. テストを追加
git add tests/test_new_feature.py
git commit -m "test: 新機能のテストを追加"

# 3. ドキュメント更新
git add docs/new_feature.md
git commit -m "docs: 新機能のドキュメントを追加"
```

#### コミットのタイミング
- 新しい関数/クラスを実装したら → コミット
- 既存コードの重要な修正をしたら → コミット
- テストを追加/修正したら → コミット
- ドキュメントを更新したら → コミット
- 設定ファイルを変更したら → コミット

#### 1Password承認待ちの対処
```bash
# 1分以上応答がない場合は承認ダイアログを確認
timeout 60 git commit -m "メッセージ" || say "1Passwordの承認を確認してください"
```

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
# ファイル名: YYYYMMDDTHHMM-brief-description.md
vim docs/work-logs/20250627T1445-tts-implementation.md

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

### 6. 最終確認

```bash
# 全体の状態確認
git status

# コミット漏れがないか確認
# （作業中に適切にコミットしていれば、ここでの作業は最小限）
git log --oneline -10
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

5. **作業完了後にまとめてコミット**
   - 後からコミット分割を考えるのは非効率
   - 作業しながら適切な単位でコミット
   - 「言われなくても」自然にコミットする習慣を

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