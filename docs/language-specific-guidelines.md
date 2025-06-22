# 言語別開発ガイドライン

> **最終更新**: 2025-06-22
> **カテゴリ**: Guide
> **関連文書**: [開発ガイドライン](development-guidelines.md), [ドキュメント作成標準](documentation-standards.md)

## 概要

このドキュメントでは、各プログラミング言語を使用する際の標準的な開発手法、ツール、注意事項をまとめています。

## Python

### パッケージ管理

**🚫 使用禁止**:
```bash
pip install package  # ❌ グローバル環境を汚染
uv pip install package  # ❌ 古い方法
```

**✅ 推奨: uvの新しいコマンドを使用**:
```bash
# プロジェクトの初期化（pyproject.tomlを作成）
uv init

# パッケージの追加（pyproject.tomlに記録される）
uv add package

# 開発用依存関係の追加
uv add --dev pytest black flake8

# 特定バージョンの指定
uv add "package>=2.0"

# 既存のrequirements.txtがある場合の移行
uv add -r requirements.txt

# 依存関係の同期（他の開発者がプロジェクトをクローンした場合）
uv sync
```

### プロジェクト構造

```
project/
├── .venv/              # uvが作成する仮想環境（gitignore）
├── pyproject.toml      # プロジェクト設定と依存関係（uvが管理）
├── uv.lock            # 依存関係のロックファイル
├── src/               # ソースコード
├── tests/             # テストコード
└── README.md          # プロジェクト説明
```

**注**: `requirements.txt`は過去の方法。`uv`は`pyproject.toml`で依存関係を管理します。

### コード実行

```bash
# スクリプトの実行
uv run python script.py

# モジュールとして実行
uv run python -m module_name
```

### よくある間違いと対策

| 間違い | 正しい方法 | 理由 |
|--------|------------|------|
| `pip install package` | `uv add package` | uvでの統一管理 |
| `uv pip install package` | `uv add package` | 新しいAPIを使用 |
| `pip freeze > requirements.txt` | `uv`が自動で`uv.lock`を管理 | 自動化された依存関係管理 |
| `python script.py` | `uv run python script.py` | 仮想環境の自動アクティベート |
| グローバルインストール | プロジェクトごとの環境 | 依存関係の衝突回避 |

## JavaScript/TypeScript

### パッケージ管理

**✅ 推奨: npm（またはpnpm/yarn）**:
```bash
# 初期化
npm init -y

# パッケージのインストール
npm install package

# 開発用依存関係
npm install --save-dev package

# グローバルインストールは最小限に
npm install -g package  # 必要な場合のみ
```

### プロジェクト構造

```
project/
├── node_modules/       # 依存関係（gitignore）
├── package.json        # プロジェクト設定
├── package-lock.json   # 依存関係のロック
├── tsconfig.json      # TypeScript設定
├── src/               # ソースコード
├── dist/              # ビルド出力（gitignore）
└── tests/             # テストコード
```

### スクリプト定義

```json
{
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "build": "tsc",
    "test": "jest",
    "lint": "eslint src/**/*.js"
  }
}
```

## Go

### モジュール管理

```bash
# モジュールの初期化
go mod init github.com/user/project

# 依存関係の追加（自動）
go get package@version

# 依存関係の整理
go mod tidy
```

### プロジェクト構造

```
project/
├── go.mod             # モジュール定義
├── go.sum             # 依存関係のチェックサム
├── cmd/               # 実行可能ファイル
│   └── app/
│       └── main.go
├── internal/          # 内部パッケージ
├── pkg/               # 公開パッケージ
└── tests/             # テストコード
```

## Rust

### プロジェクト管理

```bash
# 新規プロジェクト
cargo new project_name

# ビルド
cargo build

# 実行
cargo run

# テスト
cargo test
```

### プロジェクト構造

```
project/
├── Cargo.toml         # プロジェクト設定
├── Cargo.lock         # 依存関係のロック
├── src/
│   ├── main.rs       # エントリーポイント
│   └── lib.rs        # ライブラリコード
├── tests/            # 統合テスト
└── target/           # ビルド出力（gitignore）
```

## 共通の原則

### 1. 環境分離

- **本番環境と開発環境を分離**: 設定ファイルを使い分ける
- **仮想環境の使用**: 言語固有のツールを活用
- **環境変数の活用**: `.env`ファイルと`dotenv`ライブラリ

### 2. 依存関係管理

- **ロックファイルをコミット**: 再現可能なビルドを保証
- **最小限の依存関係**: 必要なものだけをインストール
- **定期的な更新**: セキュリティパッチの適用

### 3. コード品質

```bash
# 各言語のリンター/フォーマッター
Python: uv run black . && uv run ruff check
JavaScript: npm run lint && npm run format
Go: go fmt ./... && golangci-lint run
Rust: cargo fmt && cargo clippy
```

### 4. テスト

```bash
# 各言語のテスト実行
Python: uv run pytest
JavaScript: npm test
Go: go test ./...
Rust: cargo test
```

### 5. uvを使った開発フロー（Python）

```bash
# 1. プロジェクト初期化
uv init my-project
cd my-project

# 2. 依存関係の追加
uv add fastapi uvicorn
uv add --dev pytest black ruff

# 3. コードの実行
uv run python main.py
uv run uvicorn main:app --reload

# 4. テストとリント
uv run pytest
uv run black .
uv run ruff check

# 5. 他の開発者がクローンした場合
git clone <repo>
cd <repo>
uv sync  # すべての依存関係を自動インストール
```

## サンドボックスでの注意事項

### Python サンドボックス

```bash
# 新規プロジェクトの場合
cd sandbox/my-experiment
uv init
uv add numpy pandas  # 必要なパッケージを追加
uv run python main.py

# 既存のrequirements.txtがある場合
cd sandbox/existing-project
uv init
uv add -r requirements.txt  # 既存の依存関係を移行
uv run python main.py
```

### 環境のクリーンアップ

```bash
# Python
rm -rf .venv

# Node.js
rm -rf node_modules package-lock.json

# Go
go clean -modcache

# Rust
cargo clean
```

## エディタ設定

### VS Code推奨拡張機能

**Python**:
- Python
- Pylance
- Black Formatter

**JavaScript/TypeScript**:
- ESLint
- Prettier
- TypeScript

**共通**:
- EditorConfig
- GitLens

### .editorconfig

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4

[*.{js,ts,json}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

## まとめ

各言語には固有のベストプラクティスがありますが、共通して重要なのは：

1. **環境の分離と再現性**
2. **標準的なツールチェーンの使用**
3. **一貫性のあるプロジェクト構造**

特にPythonでは`uv`を使用することで、環境管理が簡潔かつ確実になります。