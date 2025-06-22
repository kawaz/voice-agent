# リアルタイム音声認識の改善案

## 現状の課題

1. **長時間録音の問題**
   - 歌や連続した音声では無音がないため、長時間録音し続ける
   - 45秒の歌が終わるまで結果が表示されない

2. **リアルタイム性の欠如**
   - 録音完了後に一括処理
   - ユーザーは長時間待たされる

## 改善案

### 1. ストリーミング認識の実装

```python
class StreamingTranscriber:
    def __init__(self):
        self.buffer_duration = 3.0  # 3秒ごとに処理
        self.overlap_duration = 0.5  # 0.5秒のオーバーラップ
```

**メリット**:
- 3秒ごとに中間結果を表示
- 文脈を保つためのオーバーラップ

### 2. 段階的な実装アプローチ

#### Phase 1: 固定長チャンク（実装済み: mic_transcribe_realtime.py）
- 最大5秒で強制的に区切る
- 無音でも時間で区切る
- 音声長と処理時間を表示

#### Phase 2: オーバーラップ処理
```python
# 前のチャンクの最後と次のチャンクの最初を重複させる
prev_chunk_end = frames[-overlap_samples:]
current_chunk = prev_chunk_end + new_frames
```

#### Phase 3: 文境界検出
- 音声の振幅パターンから文の区切りを推定
- 自然な区切りで分割

### 3. UI/UXの改善

#### リアルタイム表示
```
🎤 録音中... [████████░░░░░░░░] 4.2秒
📝 認識中のテキスト: きっとどこかに答えある...
   前の結果: 生まれてきた答えが人は皆...
```

#### プログレッシブ表示
```python
def display_progressive_result(partial_text, is_final=False):
    if is_final:
        print(f"\r✅ {partial_text}")
    else:
        print(f"\r⏳ {partial_text}...", end="", flush=True)
```

### 4. 実装の優先順位

1. **すぐに実装可能**（Phase 1）✅
   - 固定長での区切り
   - 音声長の表示
   - セグメント情報の表示

2. **中期的に実装**（Phase 2）
   - オーバーラップ処理
   - スムーズな結合

3. **将来的に実装**（Phase 3）
   - 音声特徴による自然な区切り
   - 話者交代の検出

## 使用例

### 現在の改良版
```bash
uv run python mic_transcribe_realtime.py
```

特徴:
- 最大5秒で自動区切り
- 音声長と処理速度を表示
- 長い音声はセグメント表示

### 将来のストリーミング版（構想）
```python
# 3秒ごとに中間結果を表示
transcriber = StreamingTranscriber(
    chunk_duration=3.0,
    overlap=0.5,
    progressive_display=True
)
```

## パフォーマンスの考慮事項

### メモリ使用量
- チャンクサイズを小さくすることでメモリ効率向上
- オーバーラップは必要最小限に

### CPU使用率
- 並列処理で録音と認識を分離
- キューイングで効率化

### 認識精度
- 短いチャンクでは文脈が失われる可能性
- オーバーラップで補完

## まとめ

リアルタイム性を高めるには：
1. **チャンク分割**で早期フィードバック
2. **オーバーラップ**で文脈維持
3. **プログレッシブ表示**でUX向上

現在の`mic_transcribe_realtime.py`は第一段階の実装として、固定長での分割と詳細な時間表示を実現しています。