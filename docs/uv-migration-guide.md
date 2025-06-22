# uv移行ガイド

> **最終更新**: 2025-06-22
> **カテゴリ**: Guide
> **関連文書**: [言語別開発ガイドライン](language-specific-guidelines.md)

## 概要

このドキュメントでは、既存のPythonプロジェクトを`pip`から`uv`の新しいコマンド体系に移行する方法を説明します。

## uvの新旧コマンド対応表

| 用途 | 旧方法（非推奨） | 新方法（推奨） |
|------|-----------------|---------------|
| プロジェクト初期化 | `python -m venv .venv` | `uv init` |
| パッケージ追加 | `pip install package` | `uv add package` |
| 開発用パッケージ追加 | `pip install -r requirements-dev.txt` | `uv add --dev package` |
| requirements.txtから | `pip install -r requirements.txt` | `uv add -r requirements.txt` |
| 依存関係の同期 | `pip install -r requirements.txt` | `uv sync` |
| スクリプト実行 | `python script.py` | `uv run python script.py` |

## 既存プロジェクトの移行手順

### 1. requirements.txtがある場合

```bash
# プロジェクトディレクトリに移動
cd my-project

# uvプロジェクトとして初期化
uv init

# 既存の依存関係を追加
uv add -r requirements.txt

# 開発用依存関係がある場合
uv add --dev -r requirements-dev.txt

# 古いファイルを削除（オプション）
rm requirements.txt requirements-dev.txt
```

### 2. 仮想環境のみの場合

```bash
# 既存の仮想環境を削除
rm -rf .venv venv env

# uvで再初期化
uv init

# 必要なパッケージを追加
uv add numpy pandas scikit-learn
uv add --dev pytest black ruff
```

### 3. pipenvやpoetryからの移行

```bash
# pipenvの場合
pipenv requirements > requirements.txt
uv init
uv add -r requirements.txt

# poetryの場合
poetry export -f requirements.txt > requirements.txt
uv init
uv add -r requirements.txt
```

## サンドボックスでの使用例

### 新規実験プロジェクト

```bash
cd sandbox
uv init whisper-experiment
cd whisper-experiment

# 必要なパッケージを追加
uv add openai-whisper
uv add --dev jupyterlab

# Jupyter Labを起動
uv run jupyter lab
```

### 既存サンドボックスの更新

```bash
cd sandbox/existing-project

# バックアップ（念のため）
cp requirements.txt requirements.txt.bak

# uvに移行
uv init
uv add -r requirements.txt

# 動作確認
uv run python main.py
```

## pyproject.tomlの構造

uvは`pyproject.toml`で依存関係を管理します：

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "My project description"
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "pydantic>=2.0.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
```

## よくある質問

### Q: `uv pip install`はもう使わない？

A: はい。`uv add`を使用してください。`uv pip`は互換性のために残されていますが、新しいプロジェクトでは`uv add`を推奨します。

### Q: requirements.txtは不要？

A: 基本的に不要です。uvは`pyproject.toml`と`uv.lock`で依存関係を管理します。ただし、既存プロジェクトとの互換性のために`uv pip compile`で生成できます。

### Q: 他の開発者との共有は？

A: `pyproject.toml`と`uv.lock`をコミットします。他の開発者は`uv sync`で同じ環境を再現できます。

### Q: CIでの使用は？

A: GitHub Actionsなどでも使用可能：

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v1
  
- name: Install dependencies
  run: uv sync
  
- name: Run tests
  run: uv run pytest
```

## まとめ

`uv add`を使用することで：
- より明確な依存関係管理
- 自動的なロックファイル生成
- プロジェクトごとの独立した環境
- 高速なパッケージ解決

既存プロジェクトも段階的に移行できるので、新しいプロジェクトから順次導入することを推奨します。