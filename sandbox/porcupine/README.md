# Picovoice Porcupine サンドボックス

ウェイクワード検出エンジンPorcupineの検証環境です。

## 検証結果サマリー

✅ **完全動作確認済み** (2025-06-22)
- 完全ローカル動作（APIキーは初回認証のみ）
- CPU使用率: 2.4%（実測）
- メモリ使用量: 32.5MB（実測）
- 検出精度: 高（誤検出ほぼなし）

詳細は[FINDINGS.md](FINDINGS.md)および[PERFORMANCE_RESULTS.md](PERFORMANCE_RESULTS.md)を参照。

## セットアップ

1. **APIキーの取得**
   - https://console.picovoice.ai/ でアカウント作成
   - AccessKeyを取得
   - 環境変数に設定: `export PICOVOICE_ACCESS_KEY=your-key`

2. **依存関係のインストール**
   ```bash
   uv sync
   ```

## 主要ファイル

### 実行可能なテストスクリプト

- `resource_monitor.py` - リソース使用状況モニター付きテスト（推奨）
- `test_wake_word_demo.py` - インタラクティブなウェイクワード検出デモ
- `test_custom_wake_word.py` - カスタムウェイクワードのテストツール
- `test_multiple_patterns.py` - 複数パターンの統計テスト

### ドキュメント

- `FINDINGS.md` - 技術的な検証結果
- `PERFORMANCE_RESULTS.md` - パフォーマンス測定結果
- `VALIDATION.md` - 動作確認結果
- `SETUP.md` - 詳細なセットアップ手順
- `docs/` - カスタムウェイクワード関連ドキュメント

### アーカイブ

- `archive/` - 過去のテストスクリプト（参考用）

## 使用例

### リソースモニター付きテスト（3分間）
```bash
source .envrc  # または export PICOVOICE_ACCESS_KEY=your-key
uv run python resource_monitor.py
```

### カスタムウェイクワードのテスト
```bash
# Picovoice Consoleで作成した.ppnファイルをテスト
uv run python test_custom_wake_word.py wake_words/おっけーはうす.ppn "おっけーはうす"
```

## 次のステップ

1. カスタム日本語ウェイクワードの作成（推奨: "おっけーはうす"）
2. 本番環境への統合
3. Raspberry Pi環境でのテスト