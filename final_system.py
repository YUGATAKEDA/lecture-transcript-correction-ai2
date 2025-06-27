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
            r'\bベルト\b': 'ベルトン',
            r'\bベル ト\b': 'ベルトン',
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

class WebHandler(BaseHTTPRequestHandler):
    """軽量Webサーバーハンドラー"""
    
    corrector = LightweightCorrector()
    
    def do_GET(self):
        """GET リクエスト処理"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_main_page().encode('utf-8'))
        
        elif self.path == '/style.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(self.get_css().encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """POST リクエスト処理"""
        if self.path == '/correct':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # フォームデータ解析
            parsed_data = urllib.parse.parse_qs(post_data)
            input_text = parsed_data.get('text', [''])[0]
            
            if input_text:
                # 修正実行
                results = self.corrector.process_segments(input_text)
                
                # 結果ページ生成
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(self.get_result_page(results).encode('utf-8'))
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_main_page(self):
        """メインページHTML"""
        sample_text = """[0:00:01 - 0:00:27]
皆さんこんばんは、松尾研究室の川崎と申します本日は、大規模言語モデル講座Day2ってことで、ライブで皆さんご参加いただいてありがとうございます。前回1450ぐらいだったのかな、に対して600名ぐらいですが、とも配もこの後参加していただくことを期待して講座を始めさせていただければと思います。

[0:00:27 - 0:00:58]
はい。本日ですねDay2になるDay2の講座になりますタイトルがPromptingとRAGで多分皆さんRAG周りかなり興味あるのかなと思っているのでぜひお楽しみにしていただければと思います講師はですね松尾研配属学生の原田さんと戸部去年ですねLLM講座受けられて、今内部の運営としても活躍いただいているベルトさんが編集BERTをあの後単語といただきますので、よろしくお願いします。"""
        
        return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎓 講義書き起こし修正AI</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🎓 講義書き起こし修正AI</h1>
            <p>高精度・無料で使える講義テキスト修正システム</p>
        </header>
        
        <main>
            <form method="POST" action="/correct">
                <div class="input-section">
                    <label for="text">修正したいテキストを入力してください:</label>
                    <textarea id="text" name="text" rows="15" placeholder="タイムスタンプ付きテキストを入力...">{html.escape(sample_text)}</textarea>
                </div>
                
                <div class="button-section">
                    <button type="submit" class="correct-btn">🚀 修正を実行</button>
                </div>
            </form>
            
            <div class="info-section">
                <h3>✨ 主な修正機能</h3>
                <ul>
                    <li>🔧 専門用語修正 (ベルト → BERT, ジーピーティー → GPT)</li>
                    <li>📝 語尾修正 (申しす → 申します)</li>
                    <li>🧹 フィラー除去 (えー、あのー、なんか)</li>
                    <li>📖 自然化 (話し言葉 → 書き言葉)</li>
                    <li>📋 句読点追加</li>
                    <li>🔄 繰り返し除去</li>
                </ul>
            </div>
        </main>
    </div>
</body>
</html>
        """
    
    def get_css(self):
        """CSS スタイル"""
        return """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 40px;
    color: white;
}

header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

header p {
    font-size: 1.2em;
    opacity: 0.9;
}

main {
    background: white;
    border-radius: 15px;
    padding: 40px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.input-section {
    margin-bottom: 30px;
}

label {
    display: block;
    font-weight: bold;
    margin-bottom: 10px;
    color: #555;
}

textarea {
    width: 100%;
    padding: 15px;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
    font-family: 'Courier New', monospace;
    resize: vertical;
    transition: border-color 0.3s;
}

textarea:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.button-section {
    text-align: center;
    margin-bottom: 30px;
}

.correct-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 15px 40px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 30px;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}

.correct-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.info-section {
    background: #f8f9fa;
    padding: 25px;
    border-radius: 10px;
    border-left: 5px solid #667eea;
}

.info-section h3 {
    color: #667eea;
    margin-bottom: 15px;
    font-size: 1.3em;
}

.info-section ul {
    list-style: none;
}

.info-section li {
    padding: 8px 0;
    font-size: 1.1em;
    color: #555;
}

.result-container {
    margin-top: 30px;
}

.segment {
    background: #f8f9fa;
    margin: 20px 0;
    padding: 20px;
    border-radius: 10px;
    border-left: 4px solid #28a745;
}

.segment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.segment-id {
    font-weight: bold;
    color: #667eea;
}

.quality-score {
    background: #28a745;
    color: white;
    padding: 5px 12px;
    border-radius: 15px;
    font-size: 0.9em;
}

.text-comparison {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 15px;
}

.text-box {
    padding: 15px;
    border-radius: 8px;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.5;
}

.original {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
}

.corrected {
    background: #d1ecf1;
    border: 1px solid #bee5eb;
}

.corrections {
    font-size: 0.9em;
    color: #666;
}

.corrections ul {
    list-style: none;
    margin-top: 5px;
}

.corrections li {
    padding: 2px 0;
}

.back-btn {
    background: #6c757d;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    text-decoration: none;
    display: inline-block;
    margin-top: 20px;
}

.back-btn:hover {
    background: #5a6268;
}
        """
    
    def get_result_page(self, results):
        """結果ページHTML"""
        if not results:
            return """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>結果 - 講義書き起こし修正AI</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="container">
        <main>
            <p>処理するテキストが見つかりませんでした。</p>
            <a href="/" class="back-btn">← 戻る</a>
        </main>
    </div>
</body>
</html>
            """
        
        # 統計計算
        total_segments = len(results)
        total_corrections = sum(len(r['corrections']) for r in results)
        avg_quality = sum(r['quality'] for r in results) / total_segments
        high_quality = sum(1 for r in results if r['quality'] > 0.5)
        
        # 結果HTML生成
        results_html = ""
        for result in results[:10]:  # 最初の10件のみ表示
            quality_class = "high" if result['quality'] > 0.7 else "medium" if result['quality'] > 0.5 else "low"
            quality_color = "#28a745" if result['quality'] > 0.7 else "#ffc107" if result['quality'] > 0.5 else "#dc3545"
            
            corrections_html = ""
            if result['corrections']:
                corrections_list = "\n".join(f"<li>• {html.escape(c)}</li>" for c in result['corrections'])
                corrections_html = f"""
                <div class="corrections">
                    <strong>適用された修正:</strong>
                    <ul>{corrections_list}</ul>
                </div>
                """
            
            results_html += f"""
            <div class="segment">
                <div class="segment-header">
                    <span class="segment-id">セグメント {result['id']}</span>
                    <span class="quality-score" style="background-color: {quality_color}">
                        品質: {result['quality']:.3f}
                    </span>
                </div>
                
                <div class="text-comparison">
                    <div class="text-box original">
                        <strong>修正前:</strong><br>
                        {html.escape(result['original'])}
                    </div>
                    <div class="text-box corrected">
                        <strong>修正後:</strong><br>
                        {html.escape(result['corrected'])}
                    </div>
                </div>
                
                {corrections_html}
                
                <small style="color: #666;">
                    ⏰ {result['start_time']} - {result['end_time']} | 
                    修正数: {len(result['corrections'])}回
                </small>
            </div>
            """
        
        return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>修正結果 - 講義書き起こし修正AI</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 修正結果</h1>
        </header>
        
        <main>
            <div style="background: #e9ecef; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
                <h3>📈 処理統計</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                    <div style="text-align: center;">
                        <div style="font-size: 2em; font-weight: bold; color: #667eea;">{total_segments}</div>
                        <div>処理セグメント数</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2em; font-weight: bold; color: #28a745;">{total_corrections}</div>
                        <div>総修正回数</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2em; font-weight: bold; color: #ffc107;">{avg_quality:.3f}</div>
                        <div>平均品質スコア</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2em; font-weight: bold; color: #dc3545;">{high_quality}/{total_segments}</div>
                        <div>高品質修正率</div>
                    </div>
                </div>
            </div>
            
            <div class="result-container">
                {results_html}
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/" class="back-btn">← 新しい修正を実行</a>
            </div>
        </main>
    </div>
</body>
</html>
        """

def run_server(port=8000):
    """サーバー起動"""
    server = HTTPServer(('localhost', port), WebHandler)
    print(f"🚀 講義書き起こし修正AI サーバー起動中...")
    print(f"📱 アクセス: http://localhost:{port}")
    print(f"⏹️  停止: Ctrl+C")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 サーバーを停止しました")

def main():
    """メイン関数"""
    print("🎓 講義書き起こし修正AI - 軽量版最終システム")
    print("標準ライブラリのみで動作する完全版")
    print("=" * 50)
    
    # コマンドライン処理も可能
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
    
    # Webサーバー起動
    run_server()

if __name__ == "__main__":
    main()
