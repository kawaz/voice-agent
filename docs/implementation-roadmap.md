# Voice Agent実装ロードマップ

## 現在の状態

### 完了項目 ✅
1. ウェイクワード検出（Porcupine）
2. 音声認識（Whisper）
3. 多言語対応（日本語＋英語）
4. データベース記録（DuckDB）
5. グレースフルシャットダウン

### 問題点 ⚠️
1. コンポーネントが密結合
2. Whisperワーカーが複数存在（リソースの無駄）
3. メッセージング機構がない
4. 拡張が困難

## 実装計画

### Phase 1: リファクタリング準備（1-2日）
- [ ] 現在のコードをバックアップ
- [ ] テストスイートの作成
- [ ] ドキュメントの整理

### Phase 2: メッセージングシステム（2-3日）
- [ ] BaseServiceクラスの実装
- [ ] メッセージ定義（dataclass）
- [ ] Controllerの基本実装
- [ ] Queue管理システム

### Phase 3: サービス分離（3-4日）
- [ ] WakeWordServiceの実装
  - [ ] 既存のMultilingualWakeWordDetectorをラップ
  - [ ] メッセージ送信機能の追加
- [ ] WhisperServiceの実装
  - [ ] 単一モデルインスタンス化
  - [ ] 遅延ロード対応
  - [ ] メッセージベースの起動
- [ ] AudioServiceの実装
  - [ ] 録音機能の分離
  - [ ] バッファ管理

### Phase 4: 統合とテスト（2-3日）
- [ ] 全サービスの統合
- [ ] エンドツーエンドテスト
- [ ] パフォーマンステスト
- [ ] エラーハンドリングの確認

### Phase 5: 機能拡張準備（将来）
- [ ] CommandProcessorインターフェース定義
- [ ] SpeechOutputインターフェース定義
- [ ] プラグインシステムの設計

## 技術的詳細

### メッセージングパターン
```python
# Publisher-Subscriber pattern
class MessageBus:
    def __init__(self):
        self.subscribers = defaultdict(list)
    
    def subscribe(self, message_type, handler):
        self.subscribers[message_type].append(handler)
    
    async def publish(self, message):
        for handler in self.subscribers[message.type]:
            await handler(message)
```

### サービス基底クラス
```python
class BaseService(ABC):
    def __init__(self, message_bus):
        self.message_bus = message_bus
        self.running = False
    
    @abstractmethod
    async def start(self):
        pass
    
    @abstractmethod
    async def stop(self):
        pass
    
    async def send_message(self, message):
        await self.message_bus.publish(message)
```

### 段階的移行戦略

1. **並行稼働期間**
   - 新旧システムを並行して動作
   - 機能ごとに段階的に切り替え

2. **フィーチャーフラグ**
   ```python
   USE_NEW_ARCHITECTURE = os.getenv("USE_NEW_ARCHITECTURE", "false") == "true"
   ```

3. **ロールバック対応**
   - 各段階でロールバック可能な設計
   - 設定切り替えで旧システムに戻せる

## 成功指標

1. **パフォーマンス**
   - メモリ使用量: 30%削減
   - CPU使用率: 変化なし
   - レスポンス時間: 10%改善

2. **保守性**
   - コード結合度の低下
   - テストカバレッジ: 80%以上
   - 新機能追加時間: 50%削減

3. **信頼性**
   - エラー率: 現状維持
   - 復旧時間: 改善

## リスクと対策

1. **移行リスク**
   - 対策: 段階的移行、十分なテスト

2. **パフォーマンス劣化**
   - 対策: ベンチマーク、プロファイリング

3. **複雑性の増加**
   - 対策: シンプルな設計、十分なドキュメント