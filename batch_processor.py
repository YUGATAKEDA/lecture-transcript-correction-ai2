#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
講義書き起こし修正AI - バッチ処理版
複数ファイルの一括処理機能
"""

import os
import glob
import time
import json
from nova_system import NovaCorrector

class BatchProcessor:
    """バッチ処理システム"""
    
    def __init__(self, enable_llm=True):
        self.corrector = NovaCorrector()
        self.corrector.enable_llm = enable_llm
        if not enable_llm:
            self.corrector.bedrock_client = None
    
    def process_directory(self, input_dir, output_dir=None):
        """ディレクトリ内の全txtファイルを処理"""
        if not output_dir:
            output_dir = input_dir + "_corrected"
        
        # 出力ディレクトリ作成
        os.makedirs(output_dir, exist_ok=True)
        
        # txtファイル一覧取得
        txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
        
        if not txt_files:
            print(f"❌ {input_dir} にtxtファイルが見つかりません")
            return
        
        print(f"📁 バッチ処理開始: {len(txt_files)}ファイル")
        print(f"📂 入力: {input_dir}")
        print(f"📂 出力: {output_dir}")
        print("=" * 50)
        
        total_segments = 0
        total_cost = 0
        all_results = []
        
        for i, file_path in enumerate(txt_files, 1):
            filename = os.path.basename(file_path)
            print(f"\n📄 [{i}/{len(txt_files)}] 処理中: {filename}")
            
            try:
                # ファイル読み込み
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 修正実行
                start_time = time.time()
                results = self.corrector.process_segments_enhanced(content)
                end_time = time.time()
                
                # 結果保存
                output_filename = filename.replace('.txt', '_corrected.txt')
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    for result in results:
                        f.write(f"[{result['start_time']} - {result['end_time']}]\n")
                        f.write(f"{result['corrected']}\n\n")
                
                # 統計更新
                segments = len(results)
                avg_quality = sum(r['quality'] for r in results) / segments if segments > 0 else 0
                llm_used = sum(1 for r in results if r['llm_used'])
                
                total_segments += segments
                all_results.extend(results)
                
                print(f"   ✅ 完了: {segments}セグメント, 品質{avg_quality:.3f}, LLM使用{llm_used}回")
                print(f"   ⏱️  処理時間: {end_time-start_time:.1f}秒")
                
            except Exception as e:
                print(f"   ❌ エラー: {e}")
        
        # 全体統計表示
        self.show_batch_summary(all_results, total_segments)
        
        # 統計JSONファイル作成
        self.save_batch_stats(all_results, output_dir)
    
    def show_batch_summary(self, all_results, total_segments):
        """バッチ処理結果サマリー表示"""
        if not all_results:
            return
        
        total_cost = self.corrector.total_cost * 150
        avg_quality = sum(r['quality'] for r in all_results) / len(all_results)
        llm_usage = sum(1 for r in all_results if r['llm_used'])
        high_quality = sum(1 for r in all_results if r['quality'] > 0.7)
        
        print(f"\n🎉 バッチ処理完了サマリー")
        print("=" * 40)
        print(f"📊 総セグメント数: {total_segments}")
        print(f"🧠 LLM使用回数: {llm_usage}")
        print(f"📈 平均品質スコア: {avg_quality:.3f}")
        print(f"⭐ 高品質セグメント: {high_quality}/{total_segments} ({high_quality/total_segments*100:.1f}%)")
        print(f"💰 総推定コスト: ¥{total_cost:.2f}")
        print(f"📥 入力トークン: {self.corrector.total_input_tokens}")
        print(f"📤 出力トークン: {self.corrector.total_output_tokens}")
    
    def save_batch_stats(self, all_results, output_dir):
        """統計情報をJSONで保存"""
        stats = {
            'total_segments': len(all_results),
            'llm_usage': sum(1 for r in all_results if r['llm_used']),
            'average_quality': sum(r['quality'] for r in all_results) / len(all_results) if all_results else 0,
            'high_quality_count': sum(1 for r in all_results if r['quality'] > 0.7),
            'total_cost_jpy': self.corrector.total_cost * 150,
            'input_tokens': self.corrector.total_input_tokens,
            'output_tokens': self.corrector.total_output_tokens,
            'processing_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        stats_file = os.path.join(output_dir, 'batch_statistics.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"📋 統計ファイル保存: {stats_file}")

def main():
    """メイン関数"""
    import sys
    
    print("🎓 講義書き起こし修正AI - バッチ処理版")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("📋 使用方法:")
        print("  python3 batch_processor.py <入力ディレクトリ> [出力ディレクトリ] [--no-llm]")
        print("")
        print("例:")
        print("  python3 batch_processor.py lecture_files")
        print("  python3 batch_processor.py lecture_files corrected_files")
        print("  python3 batch_processor.py lecture_files --no-llm")
        return
    
    input_dir = sys.argv[1]
    output_dir = None
    enable_llm = True
    
    # 引数解析
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == '--no-llm':
            enable_llm = False
        elif not arg.startswith('--') and not output_dir:
            output_dir = arg
    
    if not os.path.exists(input_dir):
        print(f"❌ ディレクトリが見つかりません: {input_dir}")
        return
    
    print(f"🧠 LLM機能: {'有効' if enable_llm else '無効'}")
    
    # バッチ処理実行
    processor = BatchProcessor(enable_llm=enable_llm)
    processor.process_directory(input_dir, output_dir)

if __name__ == "__main__":
    main()
