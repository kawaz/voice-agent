# uv移行状況

> **最終更新**: 2025-06-22
> **カテゴリ**: Planning
> **関連文書**: [uv移行ガイド](uv-migration-guide.md)

## 概要

プロジェクト全体のuv移行状況を追跡するドキュメントです。

## 移行完了 ✅

### sandbox/whisper
- [x] `pyproject.toml`作成
- [x] `uv.lock`生成
- [x] `requirements.txt`削除
- [x] README.md更新
- [x] SETUP.md更新

**変更内容**:
- `uv pip install` → `uv sync`
- 依存関係は`pyproject.toml`で管理

### sandbox/openwakeword
- [x] `pyproject.toml`作成済み
- [x] `requirements.txt`削除
- [x] README.md更新
- [x] SETUP.md更新

**変更内容**:
- 既に`pyproject.toml`が存在していた
- ドキュメントを`uv sync`使用に更新

## 移行保留 ⏸️

### mvp/
- Node.jsプロジェクトのため対象外
- `package.json`で管理

## ガイドライン更新 📝

### 更新済みドキュメント
1. **language-specific-guidelines.md**
   - `pip install` → `uv add`
   - `uv pip install` → `uv add`（非推奨として明記）
   - プロジェクト構造を更新

2. **uv-migration-guide.md**（新規作成）
   - 移行手順の詳細
   - 新旧コマンド対応表
   - よくある質問

## 今後の対応

### 新規プロジェクト
- 必ず`uv init`で開始
- `requirements.txt`は作成しない
- `pyproject.toml`で依存関係管理

### 既存プロジェクトの移行
- 実際に動作確認しながら段階的に移行
- `uv add -r requirements.txt`で既存の依存関係を移行
- 移行後は`requirements.txt`を削除

## チェックリスト

新しいPythonプロジェクトを作成する際：

- [ ] `uv init project-name`でプロジェクト作成
- [ ] `uv add package`で依存関係追加
- [ ] `uv add --dev pytest black`で開発用依存関係追加
- [ ] `uv sync`で他の開発者が環境構築
- [ ] `uv run python script.py`でスクリプト実行

## まとめ

すべてのPythonサンドボックスプロジェクトでuv移行が完了しました。今後は`uv add`を標準として使用し、`requirements.txt`は作成しません。