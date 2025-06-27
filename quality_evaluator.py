#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
講義修正品質評価スクリプト
"""

import json
import re
from typing import Dict, List, Tuple

def analyze_corrections(original_file: str, corrected_file: str) -> Dict:
    """修正結果の詳細分析"""
    
    try:
        # ファイル読み込み
        with open(original_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(corrected_file, 'r', encoding='utf-8') as f:
            corrected_content = f.read()
        
        # セグメント分割
        original_segments = extract_segments(original_content)
        corrected_segments = extract_segments(corrected_content)
        
        # 分析実行
        analysis = {
            'file_info': {
                'original_file': original_file,
                'corrected_file': corrected_file,
                'original_length': len(original_content),
                'corrected_length': len(corrected_content),
                'segments_count': len(original_segments)
            },
            'corrections': [],
            'statistics': {
                'total_changes': 0,
                'technical_terms': 0,
                'fillers_removed': 0,
                'punctuation_added': 0,
                'naturalness_improved': 0
            }
        }
        
        # セグメント別分析
        for i, (orig, corr) in enumerate(zip(original_segments, corrected_segments)):
            if orig['content'] != corr['content']:
                changes = identify_changes(orig['content'], corr['content'])
                analysis['corrections'].append({
                    'segment_id': i + 1,
                    'timestamp': orig.get('timestamp', 'N/A'),
                    'original': orig['content'][:100] + ('...' if len(orig['content']) > 100 else ''),
                    'corrected': corr['content'][:100] + ('...' if len(corr['content']) > 100 else ''),
                    'changes': changes,
                    'improvement_score': calculate_improvement_score(orig['content'], corr['content'])
                })
                
                # 統計更新
                analysis['statistics']['total_changes'] += len(changes)
                for change in changes:
                    if 'technical' in change['type']:
                        analysis['statistics']['technical_terms'] += 1
                    elif 'filler' in change['type']:
                        analysis['statistics']['fillers_removed'] += 1
                    elif 'punctuation' in change['type']:
                        analysis['statistics']['punctuation_added'] += 1
                    elif 'natural' in change['type']:
                        analysis['statistics']['naturalness_improved'] += 1
        
        return analysis
        
    except Exception as e:
        return {'error': f'分析エラー: {str(e)}'}

def extract_segments(content: str) -> List[Dict]:
    """セグメント抽出"""
    segments = []
    lines = content.split('\n')
    current_segment = {'timestamp': '', 'content': ''}
    
    for line in lines:
        line = line.strip()
        if re.match(r'\[\d+:\d+:\d+ - \d+:\d+:\d+\]', line):
            if current_segment['content']:
                segments.append(current_segment)
            current_segment = {'timestamp': line, 'content': ''}
        elif line:
            current_segment['content'] += line + ' '
    
    if current_segment['content']:
        segments.append(current_segment)
    
    return segments

def identify_changes(original: str, corrected: str) -> List[Dict]:
    """変更点の特定"""
    changes = []
    
    # 専門用語修正パターン
    tech_patterns = [
        (r'ベルト|ベル\s*ト', 'BERT', 'technical_term'),
        (r'ジーピーティー', 'GPT', 'technical_term'),
        (r'ラーム', 'Llama', 'technical_term'),
        (r'エルエム', 'LLM', 'technical_term')
    ]
    
    for pattern, replacement, change_type in tech_patterns:
        if re.search(pattern, original) and replacement in corrected:
            changes.append({
                'type': change_type,
                'description': f'{pattern} → {replacement}',
                'impact': 'high'
            })
    
    # フィラー除去
    filler_patterns = [r'えー+', r'あのー+', r'なんか\s+']
    for pattern in filler_patterns:
        if re.search(pattern, original) and not re.search(pattern, corrected):
            changes.append({
                'type': 'filler_removal',
                'description': f'フィラー "{pattern}" 除去',
                'impact': 'medium'
            })
    
    # 句読点追加
    original_punct = len(re.findall(r'[。、！？]', original))
    corrected_punct = len(re.findall(r'[。、！？]', corrected))
    if corrected_punct > original_punct:
        changes.append({
            'type': 'punctuation_added',
            'description': f'句読点 {corrected_punct - original_punct} 個追加',
            'impact': 'medium'
        })
    
    return changes

def calculate_improvement_score(original: str, corrected: str) -> float:
    """改善スコア計算"""
    score = 0.0
    
    # 長さの適正化（大幅な削減/追加は減点）
    length_ratio = len(corrected) / max(len(original), 1)
    if 0.8 <= length_ratio <= 1.2:
        score += 0.2
    
    # 専門用語の正確性
    tech_terms = ['BERT', 'GPT', 'Llama', 'LLM', 'Transformer']
    for term in tech_terms:
        if term in corrected:
            score += 0.1
    
    # フィラーの除去
    fillers = ['えー', 'あのー', 'なんか']
    filler_count_orig = sum(original.count(f) for f in fillers)
    filler_count_corr = sum(corrected.count(f) for f in fillers)
    if filler_count_corr < filler_count_orig:
        score += 0.2
    
    # 句読点の適正さ
    punct_density = len(re.findall(r'[。、]', corrected)) / max(len(corrected.split()), 1)
    if 0.1 <= punct_density <= 0.3:
        score += 0.2
    
    # 自然さ（語尾の適正化）
    proper_endings = ['ます', 'です', 'である', 'した']
    for ending in proper_endings:
        if ending in corrected:
            score += 0.05
    
    return min(score, 1.0)

def generate_report(analysis: Dict) -> str:
    """レポート生成"""
    if 'error' in analysis:
        return f"❌ {analysis['error']}"
    
    report = f"""
🎓 講義修正品質分析レポート
{'=' * 50}

📁 ファイル情報:
  • 元ファイル: {analysis['file_info']['original_file']}
  • 修正ファイル: {analysis['file_info']['corrected_file']}
  • 文字数変化: {analysis['file_info']['original_length']:,} → {analysis['file_info']['corrected_length']:,}
  • 処理セグメント数: {analysis['file_info']['segments_count']}

📊 修正統計:
  • 総修正回数: {analysis['statistics']['total_changes']}
  • 専門用語修正: {analysis['statistics']['technical_terms']}
  • フィラー除去: {analysis['statistics']['fillers_removed']}
  • 句読点追加: {analysis['statistics']['punctuation_added']}
  • 自然化修正: {analysis['statistics']['naturalness_improved']}

🔍 修正詳細:
"""
    
    for correction in analysis['corrections'][:5]:  # 最初の5件表示
        report += f"""
  📍 セグメント {correction['segment_id']} {correction['timestamp']}
     改善スコア: {correction['improvement_score']:.3f}
     修正前: {correction['original']}
     修正後: {correction['corrected']}
     変更内容: {len(correction['changes'])}件の修正
"""
    
    if len(analysis['corrections']) > 5:
        report += f"\n  ... 他 {len(analysis['corrections']) - 5} セグメントも修正済み\n"
    
    # 総合評価
    avg_score = sum(c['improvement_score'] for c in analysis['corrections']) / max(len(analysis['corrections']), 1)
    report += f"""
🏆 総合評価:
  • 平均改善スコア: {avg_score:.3f} / 1.000
  • 修正効果: {'優秀' if avg_score > 0.7 else '良好' if avg_score > 0.5 else '要改善'}
  • 推奨: {'実用レベル' if avg_score > 0.6 else '調整推奨'}
"""
    
    return report

def main():
    """メイン実行"""
    import sys
    
    if len(sys.argv) < 3:
        print("使用方法: python3 quality_evaluator.py original_file corrected_file")
        return
    
    original_file = sys.argv[1]
    corrected_file = sys.argv[2]
    
    print("🔍 修正品質分析を開始...")
    analysis = analyze_corrections(original_file, corrected_file)
    
    report = generate_report(analysis)
    print(report)
    
    # 結果をJSONファイルにも保存
    with open('correction_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print("\n💾 詳細分析結果を 'correction_analysis.json' に保存しました")

if __name__ == "__main__":
    main()
