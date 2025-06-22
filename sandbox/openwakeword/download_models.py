#!/usr/bin/env python3
"""
OpenWakeWordのモデルをダウンロードするスクリプト
"""

import os
import requests
from pathlib import Path

def download_models():
    """プリトレーニング済みモデルのダウンロード"""
    import openwakeword
    
    # OpenWakeWordのパッケージディレクトリを取得
    package_dir = Path(openwakeword.__file__).parent
    models_dir = package_dir / "resources" / "models"
    
    print(f"モデルディレクトリ: {models_dir}")
    
    # ディレクトリが存在しない場合は作成
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # GitHubからモデルをダウンロード
    base_url = "https://github.com/dscripka/openWakeWord/raw/main/openwakeword/resources/models/"
    
    models = {
        "alexa": "alexa_v0.1.tflite",
        "hey_jarvis": "hey_jarvis_v0.1.tflite", 
        "hey_mycroft": "hey_mycroft_v0.1.tflite",
        "hey_rhasspy": "hey_rhasspy_v0.1.tflite"
    }
    
    print("\n利用可能なモデル:")
    for name, filename in models.items():
        print(f"  - {name} ({filename})")
    
    print("\nONNXモデルの確認...")
    
    # ONNXモデルの確認
    onnx_models = list(models_dir.glob("*.onnx"))
    if onnx_models:
        print("見つかったONNXモデル:")
        for model in onnx_models:
            print(f"  - {model.name}")
    else:
        print("ONNXモデルが見つかりません")
        
        # openWakeWordの最新バージョンのモデルをチェック
        print("\n最新のモデルリストを確認中...")
        import openwakeword.model
        
        # プリトレーニング済みモデルのパスを確認
        try:
            from openwakeword.model import PRETRAINED_MODEL_PATHS
            print("\nプリトレーニング済みモデル:")
            for name, path in PRETRAINED_MODEL_PATHS.items():
                print(f"  {name}: {path}")
        except ImportError:
            print("PRETRAINED_MODEL_PATHSが見つかりません")

def test_simple_model():
    """シンプルなモデルテスト"""
    print("\n=== シンプルなモデルテスト ===")
    
    try:
        # デフォルトのモデルでテスト
        from openwakeword.model import Model
        
        # 明示的にpretrained_model_pathsを空にして、エラーを回避
        model = Model(pretrained_model_paths=[], custom_model_paths=[])
        print("✓ 空のモデルの初期化に成功")
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        
    # 利用可能なモデルを確認
    print("\n利用可能なプリトレーニング済みモデルを確認中...")
    try:
        import openwakeword.utils
        # モデルのダウンロードを試みる
        from openwakeword import utils
        
        # get_pretrained_modelsがあるか確認
        if hasattr(utils, 'get_pretrained_model_paths'):
            models = utils.get_pretrained_model_paths()
            print("プリトレーニング済みモデル:")
            for name, path in models.items():
                print(f"  {name}: {path}")
                
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    download_models()
    test_simple_model()