#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定ファイル生成スクリプト
"""

import json
import os

def create_config_file():
    """設定ファイル作成"""
    config = {
        "system": {
            "name": "講義書き起こし修正AI",
            "version": "1.0",
            "enable_llm": True,
            "aws_region": "us-east-1",
            "model_id": "amazon.nova-micro-v1:0"
        },
        "correction_settings": {
            "enable_tech_terms": True,
            "enable_ending_fixes": True,
            "enable_filler_removal": True,
            "enable_naturalization": True,
            "enable_punctuation": True,
            "enable_repetition_removal": True
        },
        "llm_settings": {
            "temperature": 0.1,
            "top_p": 0.9,
            "max_tokens": 1000,
            "use_threshold": 0.5
        },
        "cost_settings": {
            "max_cost_per_session": 100.0,
            "alert_threshold": 50.0,
            "cost_tracking": True
        },
        "output_settings": {
            "save_original": True,
            "save_corrections_log": True,
            "save_statistics": True,
            "output_format": "txt"
        },
        "custom_patterns": {
            "tech_terms": {
                "ベルトン": "ベルトン",
                "松尾研": "松尾研究室",
                "岩澤研": "岩澤研究室"
            },
            "organization_names": {
                "松尾岩澤研": "松尾・岩澤研"
            },
            "product_names": {
                "Googleコラボ": "Google Colab"
            }
        }
    }
    
    config_file = "correction_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 設定ファイル作成: {config_file}")
    print("📝 設定をカスタマイズできます")
    
    return config_file

def load_config(config_file="correction_config.json"):
    """設定ファイル読み込み"""
    if not os.path.exists(config_file):
        print(f"⚠️  設定ファイルが見つかりません。デフォルト設定を作成します。")
        create_config_file()
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 設定ファイル読み込み: {config_file}")
        return config
    except Exception as e:
        print(f"❌ 設定ファイル読み込みエラー: {e}")
        return None

def show_config_help():
    """設定ファイルのヘルプ表示"""
    help_text = """
🔧 設定ファイル (correction_config.json) の説明

【system】- システム全般設定
- enable_llm: LLM機能の有効/無効
- aws_region: AWS Bedrockのリージョン
- model_id: 使用するモデルID

【correction_settings】- 修正機能設定
- enable_tech_terms: 専門用語修正
- enable_ending_fixes: 語尾修正
- enable_filler_removal: フィラー除去
- enable_naturalization: 自然化
- enable_punctuation: 句読点追加
- enable_repetition_removal: 繰り返し除去

【llm_settings】- LLM詳細設定
- temperature: 創造性レベル (0.0-1.0)
- top_p: 確率カットオフ (0.0-1.0) 
- max_tokens: 最大出力トークン数
- use_threshold: LLM使用判定閾値

【cost_settings】- コスト管理
- max_cost_per_session: セッション最大コスト
- alert_threshold: アラート閾値
- cost_tracking: コスト追跡有効化

【custom_patterns】- カスタム修正パターン
- tech_terms: 専門用語辞書
- organization_names: 組織名辞書
- product_names: 製品名辞書

📝 設定変更後は、システムを再起動してください。
    """
    print(help_text)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        show_config_help()
    else:
        create_config_file()
        print("\n📋 設定ファイルヘルプ表示:")
        print("python3 config_system.py --help")
