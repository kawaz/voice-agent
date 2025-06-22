# 話者分離（Speaker Diarization）の実装案

## 概要

複数人の会話を「誰が話したか」で分離・ラベル付けする技術です。

## 実装可能な方法

### 1. pyannote.audio を使用（推奨）
```python
from pyannote.audio import Pipeline
import whisper

# 話者分離パイプライン
diarization = Pipeline.from_pretrained("pyannote/speaker-diarization")

# 話者ごとのタイムスタンプを取得
diarization_result = diarization("audio.wav")

# Whisperと組み合わせ
for turn, _, speaker in diarization_result.itertracks(yield_label=True):
    # その区間の音声を抽出
    audio_segment = extract_audio(start=turn.start, end=turn.end)
    
    # Whisperで文字起こし
    text = whisper_model.transcribe(audio_segment)
    
    print(f"[{speaker}] {text}")
```

**出力例**:
```
[SPEAKER_00] こんにちは、今日の会議を始めます
[SPEAKER_01] はい、よろしくお願いします
[SPEAKER_00] まず最初の議題ですが...
[SPEAKER_02] すみません、ちょっと質問があります
```

### 2. 簡易的な実装（エネルギーベース）
```python
class SimpleSpeakerDetector:
    def __init__(self):
        self.speaker_profiles = {}
        
    def analyze_voice_features(self, audio):
        # 音声の特徴を抽出
        pitch = self.extract_pitch(audio)
        energy = self.extract_energy(audio)
        mfcc = self.extract_mfcc(audio)
        
        return {
            'pitch': pitch,
            'energy': energy,
            'mfcc': mfcc
        }
    
    def identify_speaker(self, features):
        # 既知の話者と比較
        best_match = None
        min_distance = float('inf')
        
        for speaker_id, profile in self.speaker_profiles.items():
            distance = self.calculate_distance(features, profile)
            if distance < min_distance:
                min_distance = distance
                best_match = speaker_id
                
        # 新しい話者の場合
        if min_distance > threshold:
            new_speaker_id = f"話者{len(self.speaker_profiles) + 1}"
            self.speaker_profiles[new_speaker_id] = features
            return new_speaker_id
            
        return best_match
```

### 3. リアルタイム話者分離の実装案

```python
class RealtimeSpeakerDiarization:
    def __init__(self):
        self.whisper_model = whisper.load_model("small")
        self.diarization_buffer = []
        self.speaker_embeddings = {}
        
    def process_chunk(self, audio_chunk):
        # 1. 話者の特徴を抽出
        speaker_features = self.extract_speaker_features(audio_chunk)
        
        # 2. 話者を識別
        speaker_id = self.identify_or_create_speaker(speaker_features)
        
        # 3. 文字起こし
        text = self.whisper_model.transcribe(audio_chunk, language="ja")
        
        # 4. 結果を返す
        return {
            'speaker': speaker_id,
            'text': text['text'],
            'timestamp': time.time()
        }
```

## 実装の課題と解決策

### 課題1: リアルタイム性
- **問題**: 話者分離は計算量が多い
- **解決**: 
  - 音声を小さなチャンクで処理
  - 話者変更の検出に注力

### 課題2: 精度
- **問題**: 短い発話では話者識別が困難
- **解決**:
  - 複数の特徴量を組み合わせ
  - 文脈情報を活用

### 課題3: 同時発話
- **問題**: 複数人が同時に話すと分離困難
- **解決**:
  - 音源分離技術の併用
  - 発話の重なりを検出して警告

## 実用的な実装例

```python
def transcribe_with_speakers(audio_file):
    """話者分離付き文字起こし"""
    
    # 1. 話者分離
    from pyannote.audio import Pipeline
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
    diarization = pipeline(audio_file)
    
    # 2. Whisperモデル
    model = whisper.load_model("small")
    
    # 3. 話者ごとに処理
    results = []
    for segment, _, speaker in diarization.itertracks(yield_label=True):
        # 音声を抽出
        audio_segment = extract_audio_segment(
            audio_file, 
            start=segment.start, 
            end=segment.end
        )
        
        # 文字起こし
        transcript = model.transcribe(audio_segment, language="ja")
        
        results.append({
            'speaker': speaker,
            'start': segment.start,
            'end': segment.end,
            'text': transcript['text']
        })
    
    return results
```

## 必要なライブラリ

```bash
# 話者分離
uv add pyannote.audio

# 音声処理
uv add librosa soundfile

# 機械学習
uv add torch torchaudio
```

## デモ出力イメージ

```
=== 会議の文字起こし ===
[00:00] 話者A: 今日の会議を始めさせていただきます
[00:05] 話者B: よろしくお願いします
[00:08] 話者C: 遅れてすみません
[00:10] 話者A: では最初の議題について...
[00:15] 話者B: ちょっと質問があるのですが
[00:18] 話者A: はい、どうぞ
[00:20] 話者B: この資料の3ページ目なんですけど...
```

## まとめ

話者分離は可能ですが、実装には以下の選択肢があります：

1. **高精度だが複雑**: pyannote.audio（要Hugging Faceトークン）
2. **シンプルだが限定的**: エネルギー/ピッチベース
3. **バランス型**: 両者の組み合わせ

用途に応じて選択することをお勧めします。