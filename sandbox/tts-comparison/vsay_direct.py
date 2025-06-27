#!/usr/bin/env python3
"""
vsay direct - VOICEVOXを直接利用する音声合成
元のvsayの実装
"""
import sys
import requests
import subprocess
import argparse
import json

def speak(text, speaker=3, speed=1.2):
    """VOICEVOXで即座に音声を再生"""
    try:
        # クエリ生成
        params = {'text': text, 'speaker': speaker}
        query_response = requests.post(
            'http://localhost:50021/audio_query',
            params=params,
            timeout=5.0
        )
        audio_query = query_response.json()
        
        # 高速化設定
        audio_query['speedScale'] = speed
        audio_query['pauseLength'] = 0.1
        audio_query['pauseLengthScale'] = 0.3
        
        # 音声合成
        synthesis_response = requests.post(
            'http://localhost:50021/synthesis',
            params={'speaker': speaker},
            json=audio_query,
            headers={'Content-Type': 'application/json'},
            timeout=10.0
        )
        
        # 一時ファイル経由で再生（afplayはパイプ非対応）
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(synthesis_response.content)
            temp_path = f.name
        
        subprocess.run(['afplay', temp_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.unlink(temp_path)
        
    except requests.exceptions.ConnectionError:
        print("エラー: VOICEVOXエンジンが起動していません", file=sys.stderr)
        # VOICEVOXがインストールされているか確認
        from pathlib import Path
        if not Path("voicevox_engine").exists():
            # 標準入力が端末でない場合（パイプ等）は自動セットアップをスキップ
            if not sys.stdin.isatty():
                print("\nVOICEVOXがインストールされていません", file=sys.stderr)
                print("セットアップ: vsay engine setup", file=sys.stderr)
                print("起動: vsay engine start", file=sys.stderr)
                sys.exit(1)
            
            print("\nVOICEVOXがインストールされていません。セットアップしますか？ (y/N)", file=sys.stderr)
            response = input().strip().lower()
            if response in ['y', 'yes']:
                print("\nセットアップを実行します...", file=sys.stderr)
                subprocess.run(['uv', 'run', 'python', 'voicevox_manager.py', 'setup'])
                sys.exit(0)
            else:
                print("セットアップ: vsay engine setup", file=sys.stderr)
                print("起動: vsay engine start", file=sys.stderr)
                sys.exit(1)
        else:
            print("起動: vsay engine start", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

def main(args):
    if not args.text:
        # 標準入力から読む
        text = sys.stdin.read().strip()
    else:
        text = ' '.join(args.text)
    
    if text:
        speak(text, args.speaker, args.rate)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='VOICEVOXで音声合成（直接実行）')
    parser.add_argument('text', nargs='*', help='読み上げるテキスト')
    parser.add_argument('-s', '--speaker', type=int, default=3, help='話者ID (デフォルト: 3=ずんだもん)')
    parser.add_argument('-r', '--rate', type=float, default=1.2, help='話速 (デフォルト: 1.2)')
    args = parser.parse_args()
    main(args)