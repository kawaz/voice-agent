# Cross-Platform Considerations: macOS and Raspberry Pi

## Overview

This document outlines considerations for running the voice agent on both macOS and Raspberry Pi platforms. It covers platform-specific challenges, abstraction strategies, performance considerations, and hardware requirements.

## 目次

1. [プラットフォーム依存の抽象化](#プラットフォーム依存の抽象化)
2. [Raspberry Piのパフォーマンス考慮事項](#raspberry-piのパフォーマンス考慮事項)
3. [ハードウェア要件](#ハードウェア要件)
4. [デプロイ方法の違い](#デプロイ方法の違い)
5. [推奨Raspberry Piモデル](#推奨raspberry-piモデル)
6. [マイクとスピーカーの選択](#マイクとスピーカーの選択)
7. [開発環境のセットアップ](#開発環境のセットアップ)

## プラットフォーム依存の抽象化

### オーディオI/Oレイヤー

最も大きなプラットフォームの違いはオーディオ処理です：

#### macOS
- **ネイティブサポート**: Core Audioフレームワーク
- **Web API**: Web Speech API（ブラウザベース）
- **ライブラリ**: PortAudio、Python実装用のPyAudio
- **レイテンシ**: 適切に設定すれば一般的に低い

#### Raspberry Pi
- **ALSA**: Advanced Linux Sound Architecture（低レベル）
- **PulseAudio**: 高レベルオーディオサーバー
- **ライブラリ**: ALSAバックエンドを使用したPortAudio
- **課題**: ドライバー設定、ハードウェア固有の問題

#### 抽象化戦略
```typescript
interface AudioInterface {
  initialize(): Promise<void>;
  startRecording(): Promise<AudioStream>;
  stopRecording(): Promise<void>;
  playAudio(buffer: AudioBuffer): Promise<void>;
}

// プラットフォーム固有の実装
class MacOSAudioInterface implements AudioInterface { }
class RaspberryPiAudioInterface implements AudioInterface { }
```

### 音声認識の抽象化

#### macOSのオプション
- Web Speech API（ブラウザ）
- Whisper API（クラウド）
- ローカルWhisper（CPU/GPUアクセラレーション）
- Google Cloud Speech-to-Text

#### Raspberry Piのオプション
- Whisper Tiny/Baseモデル（ローカル）
- Julius（軽量、オフライン）
- Pocketsphinx（非常に軽量）
- クラウドAPI（ネットワーク依存）

#### 抽象化戦略
```typescript
interface SpeechRecognizer {
  initialize(config: RecognizerConfig): Promise<void>;
  recognize(audio: AudioStream): Promise<TranscriptionResult>;
  destroy(): Promise<void>;
}

// 設定可能な実装
const recognizer = createRecognizer(platform, {
  offline: isRaspberryPi,
  modelSize: isRaspberryPi ? 'tiny' : 'large'
});
```

### ウェイクワード検出の抽象化

異なるバックエンドを持つプラットフォーム非依存インターフェース：

```typescript
interface WakeWordDetector {
  initialize(wakeWords: string[]): Promise<void>;
  startListening(): Promise<void>;
  onWakeWord(callback: (word: string) => void): void;
}
```

## Raspberry Piのパフォーマンス考慮事項

### CPUとメモリの制約

#### モデル選択ガイドライン
| コンポーネント | macOS | Raspberry Pi 4 | Raspberry Pi 3B+ | Pi Zero 2 W |
|----------------|-------|----------------|------------------|-------------|
| Whisperモデル | Large/Medium | Base/Small | Tiny | Tiny（制限付き） |
| ウェイクワード | 任意 | Porcupine/Picovoice | Porcupine | 最小限のみ |
| 同時プロセス | 無制限 | 3-4 | 2-3 | 1-2 |
| RAM使用量目標 | < 4GB | < 2GB | < 1GB | < 512MB |

### パフォーマンス最適化戦略

#### 1. オーディオ処理
- **バッファサイズ**: Piでは大きめのバッファ（512-1024サンプル vs macOSの256）
- **サンプルレート**: Piでは16kHz、macOSでは44.1kHzを検討
- **ビット深度**: Piでは16ビットで十分

#### 2. モデル最適化
- **量子化**: 可能な限りINT8量子化モデルを使用
- **モデルプルーニング**: 不要なレイヤーを削除
- **キャッシング**: 認識結果の積極的なキャッシング

#### 3. リソース管理
```python
# 例：CPU負荷に基づく適応的品質
async def adaptive_recognition():
    cpu_usage = get_cpu_usage()
    if cpu_usage > 80:
        switch_to_cloud_api()
    elif cpu_usage > 60:
        use_smaller_model()
    else:
        use_optimal_model()
```

### 熱管理
- CPU温度の監視
- 70°Cでのスロットリング実装
- 24時間稼働にはパッシブ/アクティブ冷却を検討

## ハードウェア要件

### macOS要件
- **最小**: MacBook Air M1またはIntel i5
- **推奨**: M1 Pro/MaxまたはIntel i7
- **RAM**: 最小8GB、推奨16GB
- **ストレージ**: モデルと依存関係用に10GB
- **マイク**: 内蔵またはUSB（任意の品質）

### Raspberry Pi要件

#### 最小構成
- **モデル**: Raspberry Pi 3B+
- **RAM**: 1GB
- **ストレージ**: 16GB SDカード（Class 10）
- **電源**: 2.5A電源
- **冷却**: ヒートシンク必須

#### 推奨構成
- **モデル**: Raspberry Pi 4（4GB/8GB）
- **RAM**: 最小4GB
- **ストレージ**: 32GB SDカードまたはUSB経由のSSD
- **電源**: 3A電源（公式）
- **冷却**: アクティブ冷却（ファン）

#### 追加ハードウェア
- **オーディオHAT**: より良い音質のため
- **RTCモジュール**: オフラインでの時刻管理
- **UPS**: 電源の安定性

## デプロイ方法の違い

### macOSデプロイ

#### 開発
```bash
# リポジトリのクローン
git clone https://github.com/kawaz/voice-agent
cd voice-agent

# Install dependencies
npm install

# 開発サーバーの実行
npm run dev
```

#### 本番環境
```bash
# アプリケーションのビルド
npm run build

# オプション1：サービスとして実行
npm run start

# オプション2：macOSアプリとしてパッケージ化
npm run package:macos
```

### Raspberry Piデプロイ

#### 初期セットアップ
```bash
# システムの更新
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y nodejs npm python3-pip portaudio19-dev

# オーディオセットアップ
sudo apt install -y alsa-utils pulseaudio
```

#### アプリケーションデプロイ
```bash
# クローンとセットアップ
git clone https://github.com/kawaz/voice-agent
cd voice-agent

# Pi固有のフラグでインストール
npm install --build-from-source

# Pi用に設定
cp config/raspberry-pi.json config/local.json

# systemdサービスのセットアップ
sudo cp deploy/voice-agent.service /etc/systemd/system/
sudo systemctl enable voice-agent
sudo systemctl start voice-agent
```

#### Dockerデプロイ（推奨）
```dockerfile
# Dockerfile.pi
FROM balenalib/raspberry-pi-debian:bullseye

RUN apt-get update && apt-get install -y \
    nodejs npm python3-pip portaudio19-dev \
    alsa-utils pulseaudio

WORKDIR /app
COPY . .
RUN npm install --production

CMD ["npm", "start"]
```

```bash
# ビルドと実行
docker build -f Dockerfile.pi -t voice-agent-pi .
docker run -d --device /dev/snd --restart unless-stopped voice-agent-pi
```

## 推奨Raspberry Piモデル

### 本番使用

#### Raspberry Pi 4（8GB） - 最良の選択
- **長所**: 
  - 大きなモデルに十分なRAM
  - クアッドコア1.5GHzプロセッサ
  - 高速ストレージ用USB 3.0
  - ギガビットイーサネット
- **短所**: 高い消費電力（3A必要）
- **ユースケース**: ローカル処理を備えたフル機能の音声エージェント

#### Raspberry Pi 4（4GB） - 良いバランス
- **長所**: 
  - 良好な価格/性能比
  - ほとんどの音声タスクを十分処理
  - 8GBモデルより低コスト
- **短所**: 大きなモデルでのマルチタスキングが制限される
- **ユースケース**: 標準的な音声エージェントデプロイ

### 開発/テスト

#### Raspberry Pi 3B+
- **長所**: 
  - 広く入手可能
  - 低い消費電力
  - 基本的なテストに適切
- **短所**: 
  - 軽量モデルに限定
  - 処理が遅い
- **ユースケース**: 開発と軽量デプロイ

### 非推奨

#### Raspberry Pi Zero 2 W
- リアルタイム音声処理には制限が多すぎる
- ウェイクワード検出ノードのみを検討

#### Raspberry Pi Pico
- マイクロコントローラーであり、このアプリケーションには不適切

## マイクとスピーカーの選択

### USBマイク（推奨）

#### 予算オプション：Kinobo Akiro
- **価格**: 約$15-20
- **長所**: プラグアンドプレイ、無指向性
- **短所**: 基本的な品質
- **プラットフォーム**: macOSとPiの両方で動作

#### ミドルレンジ：Blue Snowball iCE
- **価格**: 約$40-50
- **長所**: 良好な品質、カーディオイドパターン
- **短所**: 大きなサイズ
- **プラットフォーム**: 両プラットフォームで優れた性能

#### プレミアム：Audio-Technica ATR2100x-USB
- **価格**: 約$70-80
- **長所**: プロフェッショナル品質、複数パターン
- **プラットフォーム**: 高品質認識に理想的

### I2Sマイク（Raspberry Pi専用）

#### SeeedStudio ReSpeaker 2-Mics Pi HAT
- **価格**: 約$15-20
- **長所**: 
  - デュアルマイクアレイ
  - 内蔵アルゴリズム
  - LEDインジケーター
- **セットアップ**:
  ```bash
  git clone https://github.com/respeaker/seeed-voicecard
  cd seeed-voicecard
  sudo ./install.sh
  ```

#### Adafruit I2S MEMSマイク
- **価格**: 約$10-15
- **長所**: 非常にコンパクト、低消費電力
- **短所**: I2S設定が必要

### スピーカー

#### USBスピーカー
- **推奨**: 任意のUSB 2.0電源スピーカー
- **例**: Creative Pebble（$25-30）
- **セットアップ**: 両プラットフォームでプラグアンドプレイ

#### 3.5mmオーディオ
- **macOS**: 内蔵または任意の3.5mmスピーカー
- **Raspberry Pi**: 良好な電源が必要
- **注意**: Piの3.5mm出力品質は変動する

#### I2SオーディオDAC
- **例**: HiFiBerry DAC+
- **長所**: 高品質オーディオ出力
- **セットアップ**: デバイスツリーオーバーレイ設定が必要

### Bluetoothオーディオ
- **長所**: ワイヤレス、便利
- **短所**: 
  - レイテンシの問題
  - 接続の安定性
  - 消費電力
- **推奨**: リアルタイム音声対話には避ける

## 開発環境のセットアップ

### macOS開発環境

#### 前提条件
```bash
# Homebrewのインストール
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Node.jsとPythonのインストール
brew install node python@3.11

# オーディオライブラリのインストール
brew install portaudio

# 開発ツールのインストール
brew install git wget
```

#### IDEセットアップ
```bash
# VS Codeと拡張機能
brew install --cask visual-studio-code

# 拡張機能のインストール
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension ms-vscode.vscode-typescript-next
```

### Raspberry Pi開発環境

#### オプション1：Pi上での直接開発

```bash
# SSHの有効化
sudo systemctl enable ssh
sudo systemctl start ssh

# 開発ツールのインストール
sudo apt install -y git vim build-essential

# Node.jsのインストール（NodeSource経由）
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Pythonとオーディオライブラリ
sudo apt install -y python3-pip python3-venv
sudo apt install -y portaudio19-dev python3-pyaudio
```

#### オプション2：クロスプラットフォーム開発

##### macOS上でのセットアップ
```bash
# クロスコンパイルツールのインストール
brew install arm-linux-gnueabihf-binutils

# リモート開発のセットアップ
npm install -g remote-sync
```

##### VS Codeリモート開発
1. "Remote - SSH"拡張機能をインストール
2. PiへのSSH接続を設定
3. macOS上で開発、Pi上で実行

#### オプション3：Docker開発

```bash
# macOS上 - ARM用ビルド
docker buildx build --platform linux/arm/v7 -t voice-agent-pi .

# Piへ転送
docker save voice-agent-pi | ssh pi@raspberrypi docker load
```

### テストフレームワーク

#### ユニットテスト
```bash
# 両プラットフォームで同じ
npm test
```

#### 統合テスト
```javascript
// platform-test.js
const platform = process.platform === 'darwin' ? 'macos' : 'linux';
const audioTests = require(`./tests/${platform}/audio`);
```

#### ハードウェアインループテスト
```bash
# Raspberry Pi専用
sudo npm run test:hardware
```

### デバッグツール

#### macOS
- Chrome DevTools（Webインターフェース用）
- アクティビティモニタ（リソース使用状況）
- Console.app（システムログ）

#### Raspberry Pi
- `htop` - プロセス監視
- `vcgencmd` - ハードウェア監視
- `journalctl` - システムログ
- `alsamixer` - オーディオデバッグ

### パフォーマンスプロファイリング

#### macOS
```bash
# CPUプロファイリング
npm run profile:cpu

# メモリプロファイリング
npm run profile:memory
```

#### Raspberry Pi
```bash
# リソース監視
./scripts/monitor-pi.sh

# 熱スロットリングのチェック
vcgencmd measure_temp
vcgencmd get_throttled
```

## まとめ

音声エージェントをmacOSとRaspberry Piの両方で正常に実行するには、プラットフォームの違いを慎重に検討する必要があります。主な戦略には以下が含まれます：

1. **プラットフォーム固有のコードを早期に抽象化**する
2. ハードウェア機能に基づいて**適切なモデルを選択**する
3. Raspberry Pi向けに**積極的に最適化**する
4. ターゲットハードウェアで**徹底的にテスト**する
5. ユースケースに基づいて**デプロイ戦略を計画**する

適切な抽象化と最適化により、同じコードベースで両プラットフォームを効果的にサポートし、良好なパフォーマンスとユーザーエクスペリエンスを維持できます。