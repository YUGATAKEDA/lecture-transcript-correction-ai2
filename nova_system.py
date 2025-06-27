#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
講義書き起こし修正AI - Nova Micro統合版
既存のルールベース + Amazon Nova Micro LLM
"""

import re
import json
import boto3
import time
from typing import List, Dict, Tuple, Optional
from final_system import LightweightCorrector  # 既存システムをインポート

class NovaCorrector:
    """Amazon Nova Micro統合コレクター"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.rule_corrector = LightweightCorrector()
        self.bedrock_client = None
        self.model_id = "amazon.nova-micro-v1:0"
        
        # コスト追跡
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        
        self._init_bedrock_client()
    
    def _init_bedrock_client(self):
        """Bedrock クライアント初期化"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=self.region
            )
            print(f"✅ Bedrock クライアント初期化成功 (リージョン: {self.region})")
        except Exception as e:
            print(f"❌ Bedrock クライアント初期化失敗: {e}")
            print("ルールベースのみで動作します")
    
    def needs_llm_correction(self, text: str) -> bool:
        """LLM修正が必要かどうかを判定"""
        # LLM修正が必要なパターンを検出
        complex_patterns = [
            r'[あ-ん]{3,}も',  # 「とも配も」のような複雑な誤認識
            r'帰漏らし',      # 「聞き漏らし」の誤認識
            r'エポック',      # 人名の可能性
            r'簡易回',       # 「範囲外」の誤認識
            r'バット[^ー]',   # 「バッド」の誤認識
            r'お腹切り',     # 複雑な誤認識
            r'円周部分',     # 「演習部分」の誤認識
            r'ベルトンさん', # 人名修正
            r'松尾岩澤研',   # 組織名修正
            r'スレッド1',    # 「ワンスレッド1」
            r'Googleコラボ', # 「Google Colab」
        ]
        
        for pattern in complex_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def create_correction_prompt(self, text: str) -> str:
        """修正用プロンプト作成"""
        prompt = f"""以下は大規模言語モデル（LLM）講座の書き起こしテキストです。Speech-to-Textによる誤認識を修正して、自然で正確な日本語に直してください。

【修正ルール】
1. 専門用語・人名・組織名を正確に修正
   - 「ベルトンさん」→「ベルトンさん」（人名として適切に）
   - 「松尾岩澤研」→「松尾・岩澤研」（正式組織名）
   - 「Googleコラボ」→「Google Colab」
   - 「スレッド1」→「ワンスレッド1」

2. 音韻類似による誤認識修正
   - 「帰漏らし」→「聞き漏らし」
   - 「簡易回」→「範囲外」
   - 「バット」→「バッド」（Bad）
   - 「円周部分」→「演習部分」

3. 文脈依存の語句修正
   - 「とも配も」→「ともかく」または「この後」（文脈に応じて）
   - 「エポック」→適切な人名・用語に
   - 「お腹切り取りたい」→「可能な限り取りたい」

4. 不自然な表現の自然化
   - 話し言葉を適切な書き言葉に
   - 繰り返しや冗長表現の削除

【重要】
- 元の意味を保持すること
- 講義の内容・文脈に適した修正を行うこと
- 過度な修正は避け、必要最小限の変更に留めること

【修正対象テキスト】
{text}

【修正後】（修正されたテキストのみを出力してください）:"""
        
        return prompt
    
    def call_nova_micro(self, prompt: str) -> Optional[str]:
        """Nova Micro API呼び出し"""
        if not self.bedrock_client:
            return None
        
        try:
            # API呼び出し用のボディ準備
            body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 1000,
                    "temperature": 0.1,
                    "topP": 0.9
                }
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            
            # トークン数とコスト計算
            usage = response_body.get('usage', {})
            input_tokens = usage.get('inputTokens', 0)
            output_tokens = usage.get('outputTokens', 0)
            
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            
            # コスト計算（Nova Micro料金）
            input_cost = input_tokens * 0.000035 / 1000
            output_cost = output_tokens * 0.00014 / 1000
            call_cost = input_cost + output_cost
            self.total_cost += call_cost
            
            print(f"📊 Nova Micro呼び出し - 入力:{input_tokens}トークン, 出力:{output_tokens}トークン, コスト:¥{call_cost*150:.3f}")
            
            # レスポンステキスト抽出
            if 'output' in response_body and 'message' in response_body['output']:
                content = response_body['output']['message'].get('content', [])
                if content and len(content) > 0:
                    return content[0].get('text', '').strip()
            
            return None
            
        except Exception as e:
            print(f"❌ Nova Micro API呼び出しエラー: {e}")
            return None
    
    def enhanced_correct_text(self, text: str) -> Tuple[str, List[str], float]:
        """拡張修正（ルールベース + LLM）"""
        corrections_log = []
        
        # Phase 1: 既存ルールベース修正
        rule_corrected, rule_corrections, rule_quality = self.rule_corrector.correct_text(text)
        corrections_log.extend(rule_corrections)
        
        # Phase 2: LLM修正が必要かチェック
        if self.needs_llm_correction(rule_corrected):
            print(f"🧠 LLM修正実行中...")
            
            # Phase 3: Nova Micro修正
            prompt = self.create_correction_prompt(rule_corrected)
            llm_result = self.call_nova_micro(prompt)
            
            if llm_result and llm_result != rule_corrected:
                corrections_log.append("LLM文脈修正")
                # 品質スコア向上
                enhanced_quality = min(1.0, rule_quality + 0.3)
                return llm_result, corrections_log, enhanced_quality
        
        return rule_corrected, corrections_log, rule_quality
    
    def process_segments_enhanced(self, text: str) -> List[Dict]:
        """拡張セグメント処理"""
        segments = re.split(r'(\[\d+:\d+:\d+ - \d+:\d+:\d+\])', text)
        results = []
        
        print(f"🚀 拡張修正システム開始 - {len(segments)//2}セグメント処理")
        
        for i in range(1, len(segments), 2):
            if i + 1 < len(segments):
                timestamp = segments[i]
                content = segments[i + 1].strip()
                
                if content:
                    # タイムスタンプ抽出
                    ts_match = re.search(r'\[(\d+:\d+:\d+) - (\d+:\d+:\d+)\]', timestamp)
                    if ts_match:
                        start_time = ts_match.group(1)
                        end_time = ts_match.group(2)
                    else:
                        start_time = end_time = "00:00:00"
                    
                    # 拡張修正実行
                    corrected, corrections, quality = self.enhanced_correct_text(content)
                    
                    results.append({
                        'id': len(results) + 1,
                        'start_time': start_time,
                        'end_time': end_time,
                        'original': content,
                        'corrected': corrected,
                        'corrections': corrections,
                        'quality': quality,
                        'llm_used': any('LLM' in c for c in corrections)
                    })
        
        # コスト情報表示
        print(f"\n💰 Nova Micro使用統計:")
        print(f"   総入力トークン: {self.total_input_tokens}")
        print(f"   総出力トークン: {self.total_output_tokens}")
        print(f"   推定コスト: ¥{self.total_cost*150:.2f}")
        
        return results

def main():
    """メイン関数"""
    print("🎓 講義書き起こし修正AI - Nova Micro統合版")
    print("=" * 50)
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--file':
        if len(sys.argv) > 2:
            filename = sys.argv[2]
            
            # Nova Micro統合システム初期化
            corrector = NovaCorrector()
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"📂 ファイル処理: {filename}")
                
                # 拡張修正実行
                start_time = time.time()
                results = corrector.process_segments_enhanced(content)
                end_time = time.time()
                
                # 結果保存
                output_file = filename.replace('.txt', '_enhanced_corrected.txt')
                with open(output_file, 'w', encoding='utf-8') as f:
                    for result in results:
                        f.write(f"[{result['start_time']} - {result['end_time']}]\n")
                        f.write(f"{result['corrected']}\n\n")
                
                # 統計情報
                total_segments = len(results)
                llm_used_count = sum(1 for r in results if r['llm_used'])
                avg_quality = sum(r['quality'] for r in results) / total_segments
                
                print(f"\n✅ 拡張修正完了: {output_file}")
                print(f"📊 処理統計:")
                print(f"   セグメント数: {total_segments}")
                print(f"   LLM使用セグメント: {llm_used_count}")
                print(f"   平均品質スコア: {avg_quality:.3f}")
                print(f"   処理時間: {end_time-start_time:.1f}秒")
                print(f"   推定コスト: ¥{corrector.total_cost*150:.2f}")
                
            except FileNotFoundError:
                print(f"❌ ファイルが見つかりません: {filename}")
            except Exception as e:
                print(f"❌ エラーが発生しました: {e}")
        else:
            print("❌ ファイル名を指定してください")
            print("使用方法: python3 nova_system.py --file <filename>")
    else:
        print("📋 使用方法:")
        print("   python3 nova_system.py --file <input_file.txt>")

if __name__ == "__main__":
    main()
