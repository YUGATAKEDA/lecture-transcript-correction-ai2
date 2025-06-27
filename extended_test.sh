#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
講義書き起こし修正AI - 簡易Webインターフェース
"""

import json
import html
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from nova_system import NovaCorrector

class WebHandler(BaseHTTPRequestHandler):
    """Webサーバーハンドラー"""
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_main_page().encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/correct':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            parsed_data = urllib.parse.parse_qs(post_data)
            input_text = parsed_data.get('text', [''])[0]
            enable_llm = 'enable_llm' in parsed_data
            
            if input_text:
                # 修正実行
                corrector = NovaCorrector()
                if not enable_llm:
                    # LLM無効の場合はルールベースのみ
                    corrector.bedrock_client = None
                
                results = []
                segments = input_text.split('\n\n')
                
                for i, segment in enumerate(segments):
                    if segment.strip():
                        if enable_llm:
                            corrected, corrections, quality = corrector.enhanced_correct_text(segment.strip())
                            llm_used = any('LLM' in c for c in corrections)
                        else:
                            corrected, corrections, quality = corrector.rule_corrector.correct_text(segment.strip())
                            llm_used = False
                        
                        results.append({
                            'id': i + 1,
                            'original': segment.strip(),
                            'corrected': corrected,
                            'corrections': corrections,
                            'quality': quality,
                            'llm_used': llm_used
                        })
                
                # 統計計算
                total_cost = corrector.total_cost * 150 if enable_llm else 0
                avg_quality = sum(r['quality'] for r in results) / len(results) if results else 0
                llm_count = sum(1 for r in results if r['llm_used'])
                
                # 結果ページ生成
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(self.get_result_page(results, {
                    'total_cost': total_cost,
                    'avg_quality': avg_quality,
                    'llm_count': llm_count,
                    'total_segments': len(results)
                }).encode('utf-8'))
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_main_page(self):
        """メインページHTML"""
        return """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎓 講義書き起こし修正AI</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1000px; margin: 0 auto; 
            background: white; border-radius: 10px; 
            padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 { 
            color: #667eea; text-align: center; margin-bottom: 30px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center; color: #666; margin-bottom: 30px;
            font-size: 1.2em;
        }
        .settings {
            background: #f8f9fa; padding: 20px; border-radius: 8px;
            margin-bottom: 20px; border-left: 4px solid #667eea;
        }
        .settings label {
            display: flex; align-items: center; font-weight: bold;
            color: #555; cursor: pointer;
        }
        .settings input[type="checkbox"] {
            margin-right: 10px; transform: scale(1.2);
        }
        .settings small {
            display: block; margin-top: 8px; color: #666;
            font-style: italic;
        }
        textarea { 
            width: 100%; height: 300px; padding: 15px;
            border: 2px solid #ddd; border-radius: 8px;
            font-family: 'Courier New', monospace; font-size: 14px;
            resize: vertical;
        }
        textarea:focus {
            outline: none; border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; padding: 15px 30px;
            font-size: 18px; font-weight: bold; border-radius: 25px;
            cursor: pointer; display: block; margin: 20px auto;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .features {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin-top: 30px;
        }
        .feature {
            background: #f8f9fa; padding: 20px; border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .feature h3 { color: #667eea; margin-bottom: 15px; }
        .feature ul { list-style: none; padding: 0; }
        .feature li { 
            padding: 5px 0; color: #555; position: relative; padding-left: 20px;
        }
        .feature li:before {
            content: "✓"; position: absolute; left: 0; color: #28a745;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 講義書き起こし修正AI</h1>
        <div class="subtitle">Nova Micro統合 - 高精度修正システム</div>
        
        <form method="POST" action="/correct">
            <div class="settings">
                <label>
                    <input type="checkbox" name="enable_llm" checked>
                    🧠 Nova Micro LLM機能を有効にする（高精度修正）
                </label>
                <small>※ 複雑な文脈修正にのみ使用。推定コスト: 10-20円/2時間講義</small>
            </div>
            
            <textarea name="text" placeholder="修正したいテキストを入力してください...

例：
皆さんこんばんは、松尾研究室の川崎と申します本日は、大規模言語モデル講座Day2ってことで、ライブで皆さんご参加いただいてありがとうございます。

講師はですね松尾研配属学生の原田さんと戸部去年ですねLLM講座受けられて、今内部の運営としても活躍いただいているベルトさんが編集BERTをあの後単語といただきますので、よろしくお願いします。

帰漏らしたりとかエポックの方からちょっと簡易回のお話をそれからバットいうか、申しすれば、お腹切り取りたいところとしてはですね、円周部分に力を入れて松尾岩澤研からベルトンさんがスレッド1質問でGoogleコラボを使った課題をお願いしたいと思います。"></textarea>
            
            <button type="submit" class="btn">🚀 修正を実行</button>
        </form>
        
        <div class="features">
            <div class="feature">
                <h3>🔧 ルールベース修正</h3>
                <ul>
                    <li>専門用語修正 (BERT, GPT, LLM)</li>
                    <li>語尾修正 (申します, ございます)</li>
                    <li>フィラー除去 (えー, あのー)</li>
                    <li>句読点の自動挿入</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>🧠 LLM文脈修正</h3>
                <ul>
                    <li>複雑な誤認識修正</li>
                    <li>人名・組織名の正確化</li>
                    <li>文脈依存の語句修正</li>
                    <li>自然な表現への変換</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>📊 性能・コスト</h3>
                <ul>
                    <li>品質スコア大幅向上</li>
                    <li>超低コスト（1円/3セグメント）</li>
                    <li>高速処理（1秒以下）</li>
                    <li>効率的なLLM使用判定</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
        """
    
    def get_result_page(self, results, stats):
        """結果ページHTML"""
        results_html = ""
        for result in results:
            status_color = "#667eea" if result['llm_used'] else "#28a745"
            status_text = "🧠 LLM" if result['llm_used'] else "⚙️ Rule"
            
            corrections_html = ""
            if result['corrections']:
                corrections_list = "\n".join(f"<li>{html.escape(c)}</li>" for c in result['corrections'])
                corrections_html = f"<ul>{corrections_list}</ul>"
            
            results_html += f"""
            <div style="background: #f8f9fa; margin: 15px 0; padding: 20px; border-radius: 8px; border-left: 4px solid {status_color};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <strong>セグメント {result['id']}</strong>
                    <div style="display: flex; gap: 10px;">
                        <span style="background: {status_color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8em;">{status_text}</span>
                        <span style="background: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8em;">品質: {result['quality']:.3f}</span>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 10px;">
                    <div style="background: #fff3cd; padding: 10px; border-radius: 5px; border: 1px solid #ffeaa7;">
                        <strong>修正前:</strong><br>
                        <span style="font-family: monospace; font-size: 14px;">{html.escape(result['original'])}</span>
                    </div>
                    <div style="background: #d1ecf1; padding: 10px; border-radius: 5px; border: 1px solid #bee5eb;">
                        <strong>修正後:</strong><br>
                        <span style="font-family: monospace; font-size: 14px;">{html.escape(result['corrected'])}</span>
                    </div>
                </div>
                
                {f'<div style="font-size: 0.9em; color: #666;"><strong>適用修正:</strong> {corrections_html}</div>' if corrections_html else ''}
            </div>
            """
        
        return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>修正結果 - 講義書き起こし修正AI</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 1200px; margin: 0 auto; 
            background: white; border-radius: 10px; 
            padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        h1 {{ color: #667eea; text-align: center; margin-bottom: 30px; }}
        .stats {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px; margin-bottom: 30px;
        }}
        .stat {{
            text-align: center; background: #f8f9fa; padding: 15px;
            border-radius: 8px; border-top: 4px solid #667eea;
        }}
        .stat-value {{ font-size: 1.8em; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #666; font-size: 0.9em; }}
        .back-btn {{
            background: #6c757d; color: white; border: none;
            padding: 10px 20px; border-radius: 5px; text-decoration: none;
            display: inline-block; margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 修正結果</h1>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{stats['total_segments']}</div>
                <div class="stat-label">処理セグメント</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats['llm_count']}</div>
                <div class="stat-label">LLM使用</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats['avg_quality']:.3f}</div>
                <div class="stat-label">平均品質</div>
            </div>
            <div class="stat">
                <div class="stat-value">¥{stats['total_cost']:.2f}</div>
                <div class="stat-label">推定コスト</div>
            </div>
        </div>
        
        <div class="results">
            {results_html}
        </div>
        
        <div style="text-align: center;">
            <a href="/" class="back-btn">← 新しい修正を実行</a>
        </div>
    </div>
</body>
</html>
        """

def main():
    try:
        server = HTTPServer(('localhost', 8000), WebHandler)
        print("🚀 Webサーバー起動中...")
        print("📱 アクセス: http://localhost:8000")
        print("⏹️  停止: Ctrl+C")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 サーバーを停止しました")

if __name__ == "__main__":
    main()
