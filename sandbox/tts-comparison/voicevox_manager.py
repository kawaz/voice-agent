#!/usr/bin/env python3
"""
VOICEVOX マネージャー
VOICEVOXエンジンの起動・停止・管理を簡単に行うためのツール
"""
import subprocess
import requests
import time
import os
import sys
import signal
from pathlib import Path
import atexit

class VoiceVoxManager:
    def __init__(self, engine_path=None, port=50021):
        self.port = port
        self.engine_path = engine_path or self.find_engine_path()
        self.process = None
        
        # 終了時の処理を登録
        atexit.register(self.stop)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def find_engine_path(self):
        """VOICEVOXエンジンのパスを自動検出"""
        possible_paths = [
            Path("voicevox_engine"),
            Path("voicevox_engine-macos-arm64-0.23.1"),
            Path("voicevox_engine-macos-x64-0.23.1"),
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "run").exists():
                return path
        
        return None
    
    def is_installed(self):
        """VOICEVOXエンジンがインストールされているか確認"""
        return self.engine_path is not None and self.engine_path.exists()
    
    def is_running(self):
        """VOICEVOXエンジンが起動しているか確認"""
        try:
            response = requests.get(f'http://localhost:{self.port}/version', timeout=1)
            return response.status_code == 200
        except:
            return False
    
    def start(self, wait=True, timeout=30):
        """VOICEVOXエンジンを起動"""
        if not self.is_installed():
            print("エラー: VOICEVOXエンジンが見つかりません")
            print("まず './setup_voicevox_manual.sh' を実行してください")
            return False
        
        if self.is_running():
            print("VOICEVOXエンジンは既に起動しています")
            return True
        
        run_path = self.engine_path / "run"
        print(f"VOICEVOXエンジンを起動中... ({run_path})")
        
        try:
            # エンジンを起動
            self.process = subprocess.Popen(
                [str(run_path), "--port", str(self.port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            if wait:
                # 起動を待つ
                for i in range(timeout):
                    if self.is_running():
                        print(f"\n✓ VOICEVOXエンジンが起動しました (ポート: {self.port})")
                        print(f"  API Docs: http://localhost:{self.port}/docs")
                        return True
                    print(".", end="", flush=True)
                    time.sleep(1)
                
                print("\nエラー: 起動タイムアウト")
                self.stop()
                return False
            
            return True
            
        except Exception as e:
            print(f"エラー: {e}")
            return False
    
    def stop(self):
        """VOICEVOXエンジンを停止"""
        if self.process:
            print("\nVOICEVOXエンジンを停止中...")
            self.process.terminate()
            self.process.wait()
            self.process = None
            print("停止しました")
    
    def restart(self):
        """VOICEVOXエンジンを再起動"""
        self.stop()
        time.sleep(1)
        return self.start()
    
    def _signal_handler(self, signum, frame):
        """シグナルハンドラー"""
        print("\n終了シグナルを受信しました")
        self.stop()
        sys.exit(0)
    
    def test_synthesis(self, text="こんにちは、私はずんだもんなのだ！"):
        """音声合成のテスト"""
        if not self.is_running():
            print("エラー: VOICEVOXエンジンが起動していません")
            return False
        
        try:
            # 音声合成
            params = {'text': text, 'speaker': 3}  # 3 = ずんだもん
            query_response = requests.post(
                f'http://localhost:{self.port}/audio_query',
                params=params
            )
            
            synthesis_response = requests.post(
                f'http://localhost:{self.port}/synthesis',
                params={'speaker': 3},
                json=query_response.json(),
                headers={'Content-Type': 'application/json'}
            )
            
            # 保存
            output_file = "outputs/voicevox_test.wav"
            with open(output_file, 'wb') as f:
                f.write(synthesis_response.content)
            
            print(f"✓ テスト音声を生成しました: {output_file}")
            print(f"  テキスト: {text}")
            return True
            
        except Exception as e:
            print(f"エラー: {e}")
            return False
    
    def interactive_mode(self):
        """対話モード"""
        if not self.is_running():
            if not self.start():
                return
        
        print("\n=== VOICEVOX 対話モード ===")
        print("テキストを入力すると音声を生成します")
        print("終了: quit, exit, q")
        print("話者変更: speaker <ID>")
        print()
        
        speaker_id = 3  # デフォルト: ずんだもん
        
        while True:
            try:
                text = input("> ").strip()
                
                if text.lower() in ['quit', 'exit', 'q']:
                    break
                
                if text.startswith('speaker '):
                    try:
                        speaker_id = int(text.split()[1])
                        print(f"話者IDを {speaker_id} に変更しました")
                        continue
                    except:
                        print("使用方法: speaker <ID>")
                        continue
                
                if not text:
                    continue
                
                # 音声合成
                params = {'text': text, 'speaker': speaker_id}
                query_response = requests.post(
                    f'http://localhost:{self.port}/audio_query',
                    params=params
                )
                
                synthesis_response = requests.post(
                    f'http://localhost:{self.port}/synthesis',
                    params={'speaker': speaker_id},
                    json=query_response.json(),
                    headers={'Content-Type': 'application/json'}
                )
                
                # 保存と再生
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_file = f"outputs/voicevox_{timestamp}.wav"
                with open(output_file, 'wb') as f:
                    f.write(synthesis_response.content)
                
                print(f"✓ 保存: {output_file}")
                
                # macOSの場合は自動再生（オプション）
                if sys.platform == 'darwin':
                    subprocess.run(['afplay', output_file])
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"エラー: {e}")
        
        print("\n対話モードを終了します")

def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='VOICEVOX マネージャー')
    parser.add_argument('command', nargs='?', default='help',
                       choices=['start', 'stop', 'restart', 'status', 'test', 'interactive', 'help'],
                       help='実行するコマンド')
    parser.add_argument('--port', type=int, default=50021,
                       help='使用するポート (デフォルト: 50021)')
    
    args = parser.parse_args()
    
    manager = VoiceVoxManager(port=args.port)
    
    if args.command == 'start':
        manager.start()
        print("\nCtrl+C で停止します")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    
    elif args.command == 'stop':
        manager.stop()
    
    elif args.command == 'restart':
        manager.restart()
    
    elif args.command == 'status':
        if manager.is_installed():
            print(f"✓ VOICEVOXエンジンはインストール済み: {manager.engine_path}")
        else:
            print("✗ VOICEVOXエンジンが見つかりません")
        
        if manager.is_running():
            print(f"✓ VOICEVOXエンジンは起動中 (ポート: {manager.port})")
        else:
            print("✗ VOICEVOXエンジンは停止中")
    
    elif args.command == 'test':
        if not manager.is_running():
            print("エンジンを起動します...")
            if not manager.start():
                return
        manager.test_synthesis()
    
    elif args.command == 'interactive':
        manager.interactive_mode()
    
    else:  # help
        print("使用方法: python voicevox_manager.py [コマンド]")
        print()
        print("コマンド:")
        print("  start       - VOICEVOXエンジンを起動")
        print("  stop        - VOICEVOXエンジンを停止")
        print("  restart     - VOICEVOXエンジンを再起動")
        print("  status      - 状態を確認")
        print("  test        - 音声合成のテスト")
        print("  interactive - 対話モード")
        print("  help        - このヘルプを表示")
        print()
        print("オプション:")
        print("  --port PORT - 使用するポート (デフォルト: 50021)")

if __name__ == "__main__":
    main()