# Voice Agent

音声認識を使った家電操作デバイスの開発プロジェクト

## 概要

常時音声認識を行い、音声コマンドで家電操作や各種サービスとの連携を行うエージェントシステムです。

## 機能

- 常時音声認識（ウェイクワード対応）
- 家電操作（NatureRemo/SwitchBot API連携）
- 天気情報の音声応答
- TODOリスト管理
- カレンダー連携
- アラーム設定

## プロジェクト構造

```
voice-agent/
├── docs/               # プロジェクトドキュメント
│   ├── README.md      # ドキュメント一覧と構成
│   └── ...            # 各種設計書・仕様書（15+ files）
├── sandbox/           # 実験的実装・技術検証
│   ├── openwakeword/  # ウェイクワード検出の検証
│   └── whisper/       # 音声認識エンジンの検証
├── mvp/               # MVP実装
├── src/               # 本実装（予定）
└── tasks/             # 開発タスク管理
```

## 開発フェーズ

1. **フェーズ1（MVP）**: 音声認識 → 文字起こし → 音声読み上げ ← 現在ここ
2. **フェーズ2**: 家電操作機能の実装
3. **フェーズ3**: 外部サービス連携

## セットアップ

```bash
# MVPの実行
cd mvp
npm install
npm start
```

## ドキュメント

主要なドキュメント：
- [開発計画書](docs/development-plan.md)
- [システムアーキテクチャ](docs/architecture.md)
- [MVP実装計画](docs/mvp-implementation-plan.md)
- [開発ガイドライン](docs/development-guidelines.md)

すべてのドキュメントは [docs/README.md](docs/README.md) を参照してください。

## 技術検証

サンドボックスでの検証結果：
- [OpenWakeWord検証](sandbox/openwakeword/) - ウェイクワード検出
- [Whisper検証](sandbox/whisper/) - 音声認識エンジン