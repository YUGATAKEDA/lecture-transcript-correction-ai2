#!/bin/bash

echo "🎓 講義書き起こし修正AI - Nova Micro統合版 セットアップ"
echo "========================================================"

# プロジェクトディレクトリ作成
mkdir -p lecture-correction-ai
cd lecture-correction-ai

echo "📄 既存の軽量版システムを配置中..."

# 既存システム（Document 3から）を配置
cat > final_system.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
講義書き起こし修正AI - 軽量版最終システム
標準ライブラリのみで動作する完全版
"""

import re
import json
import html
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import webbrowser
from typing import List, Dict, Tuple

class LightweightCorrector:
    """軽量版コレクター"""
    
    def __init__(self):
        self.load_patterns()
    
    def load_patterns(self):
        """修正パターン読み込み"""
        self.tech_terms = {
            r'\bベルト\b': 'BERT',
            r'\bベル ト\b': 'BERT',
            r'\bジーピーティー\b': 'GPT',
            r'\bラーム\b': 'Llama',
            r'\bエルエム\b': 'LLM',
            r'\b松尾研\b(?!究室)': '松尾研究室',
            r'とも配も': 'ともかく',
            r'編集BERT': 'BERT',
            r'あの後単語': '後ほど',
        }
        
        self.ending_fixes = {
            r'申しす(?=\s|$)': '申します',
            r'ございす(?=\s|$)': 'ございます',
            r'思いす(?=\s|$)': '思います',
            r'りがとうございす': 'ありがとうございます',
        }
        
        self.naturalness_rules = [
            (r'だったのかな[、。]', 'でした。'),
            (r'あるのかなと思', 'あると思'),
            (r'かなというふう', 'かと思'),
            (r'っていう', 'という'),
            (r'だったりとか', 'や'),
        ]
        
        self.filler_patterns = [
            (r'\s*[えあ]+ー*\s*', ' '),
            (r'\s*あのー*\s*', ' '),
            (r'なんか\s+', ''),
        ]
        
        self.punctuation_rules = [
            (r'申します([あ-んA-Za-z])', r'申します。\1'),
            (r'ございます([あ-んA-Za-z])', r'ございます。\1'),
            (r'思います([あ-んA-Za-z])', r'思います。\1'),
        ]
        
        self.repetition_patterns = [
            (r'\b(\w+)になる\1\b', r'\1'),
            (r'\b(\w+)\s+\1(?=\s)', r'\1'),
        ]
    
    def correct_text(self, text: str) -> Tuple[str, List[str], float]:
        """テキスト修正"""
        corrected = text
        corrections_log = []
        
        # 1. 専門用語修正
        for pattern, replacement in self.tech_terms.items():
            if re.search(pattern, corrected):
                corrected = re.sub(pattern, replacement, corrected)
                corrections_log.append(f"専門用語: {replacement}")
        
        # 2. 語尾修正
        for pattern, replacement in self.ending_fixes.items():
            if re.search(pattern, corrected):
                corrected = re.sub(pattern, replacement, corrected)
                corrections_log.append(f"語尾修正: {replacement}")
        
        # 3. 繰り返し修正
        for pattern, replacement in self.repetition_patterns:
            if re.search(pattern, corrected):
                corrected = re.sub(pattern, replacement, corrected)
                corrections_log.append("繰り返し除去")
        
        # 4. フィラー除去
        for pattern, replacement in self.filler_patterns:
            if re.search(pattern, corrected):
                corrected = re.sub(pattern, replacement, corrected)
                corrections_log.append("フィラー除去")
        
        # 5. 自然化
        for pattern, replacement in self.naturalness_rules:
            if re.search(pattern, corrected):
                corrected = re.sub(pattern, replacement, corrected)
                corrections_log.append("自然化")
        
        # 6. 句読点
        for pattern, replacement in self.punctuation_rules:
            if re.search(pattern, corrected):
                corrected = re.sub(pattern, replacement, corrected)
                corrections_log.append("句読点追加")
        
        # 7. クリーンアップ
        corrected = re.sub(r'\s{2,}', ' ', corrected)
        corrected = re.sub(r'\s*([。、！？])', r'\1', corrected)
        corrected = corrected.strip()
        
        # 品質スコア計算（簡易版）
        quality = min(1.0, len(corrections_log) / 5 + 0.3)
        
        return corrected, corrections_log, quality
    
    def process_segments(self, text: str) -> List[Dict]:
        """セグメント処理"""
        segments = re.split(r'(\[\d+:\d+:\d+ - \d+:\d+:\d+\])', text)
        results = []
        
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
                    
                    # 修正実行
                    corrected, corrections, quality = self.correct_text(content)
                    
                    results.append({
                        'id': len(results) + 1,
                        'start_time': start_time,
                        'end_time': end_time,
                        'original': content,
                        'corrected': corrected,
                        'corrections': corrections,
                        'quality': quality
                    })
        
        return results

def main():
    """メイン関数"""
    print("🎓 講義書き起こし修正AI - 軽量版最終システム")
    print("標準ライブラリのみで動作する完全版")
    print("=" * 50)
    
    # コマンドライン処理
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == '--file':
            if len(sys.argv) > 2:
                filename = sys.argv[2]
                corrector = LightweightCorrector()
                
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    print(f"📂 ファイル処理: {filename}")
                    results = corrector.process_segments(content)
                    
                    # 結果を保存
                    output_file = filename.replace('.txt', '_corrected.txt')
                    with open(output_file, 'w', encoding='utf-8') as f:
                        for result in results:
                            f.write(f"[{result['start_time']} - {result['end_time']}]\n")
                            f.write(f"{result['corrected']}\n\n")
                    
                    print(f"✅ 修正完了: {output_file}")
                    print(f"📊 処理統計: {len(results)}セグメント, "
                          f"平均品質{sum(r['quality'] for r in results)/len(results):.3f}")
                    
                except FileNotFoundError:
                    print(f"❌ ファイルが見つかりません: {filename}")
                return

if __name__ == "__main__":
    main()
