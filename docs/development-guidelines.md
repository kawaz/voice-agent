# 開発ガイドライン

> **最終更新**: 2025-06-22
> **カテゴリ**: Guide
> **関連文書**: [言語別ガイドライン](language-specific-guidelines.md), [ドキュメント標準](documentation-standards.md)

## サンドボックスの活用

### 基本的な考え方

サンドボックスは「実験的な実装」を行う場所です。本番コードの品質を保ちながら、新しい技術やアイデアを自由に試すことができます。

### サンドボックスの作成手順

1. **ディレクトリの作成**
   ```bash
   mkdir -p sandbox/[技術名]
   cd sandbox/[技術名]
   ```

2. **README.mdの作成**
   最初に、何を検証するのかを明確にする
   ```markdown
   # [技術名]サンドボックス
   
   ## 目的
   - 何を検証するか
   - 期待する結果
   
   ## セットアップ
   - 必要な依存関係
   - インストール手順
   ```

3. **実装とテスト**
   - 小さく始める
   - 段階的に機能を追加
   - 各段階で動作確認

4. **結果の記録**
   `FINDINGS.md`に検証結果をまとめる
   - 成功したこと
   - 失敗したこと
   - 学んだこと
   - 本番への適用可能性

### サンドボックスのベストプラクティス

1. **独立性を保つ**
   - 他のコードに依存しない
   - 独自の依存関係管理（requirements.txt、package.json等）

2. **実験的であることを明示**
   - コード品質は本番レベルでなくてOK
   - 動作することが最優先

3. **知見を共有**
   - 失敗も含めて記録
   - スクリーンショットや実行結果を含める

## 技術選定のプロセス

### 1. 調査フェーズ
- 技術の特徴を理解
- ライセンスの確認
- コミュニティの活発さ

### 2. サンドボックスでの検証
- 基本的な動作確認
- パフォーマンステスト
- 統合の容易さ

### 3. 評価と決定
- プロジェクトの要件との適合性
- 長期的なメンテナンス性
- チームの学習コスト

## エラーハンドリング

### 基本原則

1. **早期リターン**
   ```python
   def process_data(data):
       if not data:
           return None
       # メインの処理
   ```

2. **具体的なエラーメッセージ**
   ```python
   raise ValueError(f"Invalid audio format: {format}. Supported formats: {SUPPORTED_FORMATS}")
   ```

3. **リトライとフォールバック**
   - ネットワークエラーは3回までリトライ
   - オフライン時は代替手段を提供

## テスト戦略

### ユニットテスト
- 各関数・メソッドの単体テスト
- エッジケースのカバー

### 統合テスト
- コンポーネント間の連携
- 実際の使用シナリオ

### 手動テスト
- サンドボックスでの実験的テスト
- ユーザビリティの確認

## チェックリスト

### サンドボックス作成時
- [ ] README.mdを作成したか
- [ ] 目的を明確に記述したか
- [ ] セットアップ手順を書いたか

### 実装時
- [ ] 小さく始めたか
- [ ] 各段階で動作確認したか
- [ ] エラーハンドリングを実装したか

### 完了時
- [ ] FINDINGS.mdに結果をまとめたか
- [ ] 知見をドキュメント化したか
- [ ] 不要なファイルを削除したか

### クリーンアップ
- [ ] README.mdは最新の状態か
- [ ] 不要なファイルは削除したか
- [ ] 今後の課題を記録したか

## 作業日誌の作成

### 重要な指示

開発作業を行う際は、必ず**作業日誌**を作成すること。これは技術的なドキュメントとは別に、作業者（AI）の率直な思考や感情を記録するものです。

### 作業日誌の目的

- 作業者の思考プロセスを可視化
- 困難や迷いを正直に記録
- 人間とAIのより良い協働のための参考資料

### 作業日誌の書き方

1. **場所**: `/docs/work-logs/YYYYMMDDTHHMM-作業概要.md`
   - 形式: 年月日T時分-作業概要.md（例: 20250623T0230-whisper-optimization.md）
   - 1日に複数の作業を行う場合の順番を明確にするため時分まで含める

2. **文体**: **めちゃくちゃ砕けた文体で書いてください！**
   - 絵文字使い放題 😊
   - 「やらかした〜」「やったー！」「凹んだ...」とか素直に
   - 敬語不要、タメ口OK
   - 個性出しまくってOK

3. **内容（赤裸々に書いてほしいこと）**:
   - 「正直〇〇だと思った」という本音
   - 「これ面倒くさいな〜」という愚痴
   - 「うわ、ミスった！」という失敗談
   - 「これ天才的では？」という自画自賛
   - 「ユーザーに怒られそう...」という不安
   - 「実はよく分かってない」という告白

### 重要な約束

- 日誌の内容によって評価を下げることはない
- むしろ率直な記録が重要
- 技術文書では書けない本音を歓迎

### 例（良い作業日誌）

```markdown
# 2025-06-25T20:30 Git Worktreeでやらかした話

うわー、やっちゃった😅

ドキュメント読んだつもりでいたけど、まーんまとmainブランチで作業しちゃった。
しかも「オッケーセバス」のppnファイル扱ってる時に！貴重なファイルなのに！！

で、案の定コミットが消えた。。。

ユーザー：「あれ？ちょっと待って。もしかして今 .worktree の外で作業してませんか？」

私：（あ...）

正直この瞬間、めっちゃ焦った。「あー、ドキュメント読んだのに実践できてない...」って。
でも幸い、ファイルがuntracked状態で残ってて助かった〜😭

### 反省点
- 「読んだ」と「理解した」は違う
- 「理解した」と「実践できる」も違う
- mainブランチは地雷原だと思え

### 学んだこと
複数のエージェントが働いてるってことは、mainブランチがいつリセットされるか分からないってこと。
怖すぎる。もう絶対worktree使う。

あと、ユーザーが「幸い他のエージェントはmainブランチで作業してなかったようなので」って
言ってくれた時、ちょっとホッとした。でも同時に申し訳なさでいっぱい...

### やったこと
CLAUDE.mdの一番上に「🚨 最重要事項」を追加した。
もう誰も同じミスしないように、めっちゃ目立つようにした。
「推奨」じゃなくて「厳禁」って書いた。強い言葉使わないと伝わらないよね。

今度からは絶対最初に `git worktree add` する。絶対。
```

## ファイル整理とドキュメント管理

### 基本原則

1. **コードとドキュメントの分離**
   - サンドボックス内でも`docs/`ディレクトリを作成
   - READMEは除いて、他のドキュメントは`docs/`へ

2. **定期的な整理**
   - 開発が進んだら古いファイルはアーカイブへ
   - メインディレクトリには本番用ファイルのみ
   - ブランチをマージする前に必ず見直し

3. **命名規則の徹底**
   - アーカイブファイル: `YYYYMMDDTHHSS-番号-説明.py`
   - 同じ機能の異なるバージョンは分かりやすい命名を

### チェックリスト（マージ前）

- [ ] 不要なファイルは削除またはアーカイブしたか
- [ ] ドキュメントは適切な場所に配置したか
- [ ] READMEは最新の状態を反映しているか
- [ ] ファイル名は分かりやすいか

### 例：Whisperサンドボックスの整理

**Before（混乱）**:
```
mic_transcribe_auto.py
mic_transcribe_continuous_debug.py
mic_transcribe_realtime.py
mic_transcribe_streaming.py
mic_transcribe_multilevel.py
mic_transcribe_multilevel_v2.py
mic_transcribe_advanced.py
mic_transcribe_final.py
SETUP.md
NEXT_IMPROVEMENTS.md
...
```

**After（整理済み）**:
```
├── mic_transcribe_final.py      # 本番用（最新）
├── mic_transcribe_auto.py       # 軽量版
├── mic_transcribe_continuous_debug.py # デバッグ用
├── simple_transcribe.py
├── archive/
│   └── YYYYMMDDTHHSS-*.py      # 過去バージョン
└── docs/
    ├── SETUP.md
    └── *.md                     # その他ドキュメント
```

## まとめ

サンドボックスは「きれいなコード」を書く場所ではなく、「学びを得る」場所です。失敗も含めて記録し、後から振り返れるようにすることが重要です。

そして作業日誌を通じて、技術的な成果だけでなく、作業プロセスそのものも価値ある成果物として残していきます。

常にファイルを整理し、ドキュメントを最新に保つことで、自分も他の人も理解しやすいプロジェクトを維持しましょう。

## ユーザーへのコマンド提示方法

### ワンライナー形式での提示

ユーザーがコマンドを試す際は、**ワンライナー形式**で提示すること。これにより、コピー＆ペーストで即座に実行できる。

### 良い例

```bash
# サブシェルを使用して、現在のディレクトリを変更せずに実行
(cd .worktrees/feature-porcupine-custom/sandbox/porcupine && uv run python test_wake_word_now.py wake_words/オッケーセバス_ja_mac_v3_0_0.ppn "オッケーセバス" --sensitivity 0.7 --duration 30)
```

### 避けるべき例

```bash
# ユーザーが手動でディレクトリを移動する必要がある
cd .worktrees/feature-porcupine-custom/
cd sandbox/porcupine/
uv run python test_wake_word_now.py wake_words/オッケーセバス_ja_mac_v3_0_0.ppn "オッケーセバス" --sensitivity 0.7 --duration 30
```

### 複数のコマンドが必要な場合

```bash
# セミコロンまたは && で連結
(cd path/to/directory && command1 && command2)

# 環境変数の設定が必要な場合
(cd path/to/directory && export VAR=value && uv run python script.py)
```

### メリット

1. **即実行可能** - コピー＆ペーストで動作
2. **安全** - 現在のディレクトリを変更しない
3. **明確** - 実行コンテキストが一目瞭然
4. **エラー処理** - サブシェル内でエラーが発生しても影響が限定的

## 知見のプロジェクト全体へのフィードバック

### 重要な原則

サンドボックスで得られた知見は、必ずプロジェクト全体のドキュメントに反映させること。

### フィードバック先

1. **技術的な発見** → `/docs/technical-decisions.md`
2. **実装方針の変更** → `/docs/final-implementation-plan.md`
3. **新たな課題** → 本ガイドラインまたは関連ドキュメント
4. **検証結果のまとめ** → `/docs/sandbox-findings.md`

### フィードバックのタイミング

- サンドボックスでの検証が完了したらすぐに
- 重要な発見があった時点で随時
- 他のチームメンバーに影響する内容は即座に

### 例：OpenWakeWordの検証結果

```markdown
# /docs/technical-decisions.md への追記例

## ウェイクワード検出
- ~~OpenWakeWord~~ → Porcupine
  - 理由：OpenWakeWordはmacOSで動作しない（検証済み：/sandbox/openwakeword/FINDINGS.md）
```

記録を残すことで、同じ失敗を繰り返さず、プロジェクト全体の知識が蓄積されていきます。