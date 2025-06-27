#!/bin/bash

# ドキュメント整合性チェックスクリプト

echo "=== ドキュメント整合性チェック ==="
echo

# 色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# エラーカウンタ
errors=0

# 1. docs/README.md内のリンクチェック
echo "📄 docs/README.md のリンクチェック..."
grep -o '\[[^]]*\]([^)]*\.md)' docs/README.md | while IFS= read -r match; do
    file=$(echo "$match" | sed 's/.*(\([^)]*\))/\1/')
    if [[ ! -f "docs/$file" ]]; then
        echo -e "${RED}❌ リンク切れ: $file${NC}"
        ((errors++))
    fi
done

# 2. CLAUDE.md内のリンクチェック
echo
echo "📄 CLAUDE.md のリンクチェック..."
grep -o '\[[^]]*\](docs/[^)]*\.md)' CLAUDE.md | while IFS= read -r match; do
    file=$(echo "$match" | sed 's/.*(\([^)]*\))/\1/')
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}❌ リンク切れ: $file${NC}"
        ((errors++))
    fi
done

# 3. 未記載ドキュメントのチェック
echo
echo "📁 docs/ 内の未記載ドキュメントチェック..."
while IFS= read -r file; do
    basename=$(basename "$file")
    if ! grep -q "$basename" docs/README.md; then
        echo -e "${YELLOW}⚠️  README.md未記載: $file${NC}"
        ((errors++))
    fi
done < <(find docs -name "*.md" -not -name "README.md" -not -path "docs/work-logs/*" -not -path "docs/archive/*")

# 4. 新規に作成されたファイルの確認
echo
echo "🆕 最近作成/更新されたドキュメント（24時間以内）..."
find docs -name "*.md" -mtime -1 -not -path "docs/work-logs/*" | while read -r file; do
    echo -e "${GREEN}✅ $file${NC}"
done

# 結果サマリー
echo
echo "=== チェック結果 ==="
if [ $errors -eq 0 ]; then
    echo -e "${GREEN}✅ すべてのドキュメントが整合性を保っています${NC}"
else
    echo -e "${RED}❌ $errors 個の問題が見つかりました${NC}"
fi

exit $errors