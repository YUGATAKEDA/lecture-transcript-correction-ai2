# 🎓 講義書き起こし修正AI

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![AWS](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**高精度・超低コストで講義の音声書き起こしテキストを自動修正するAIシステム**

## 🎯 概要

このシステムは、音声認識（Speech-to-Text）で生成された講義の書き起こしテキストを、自然で読みやすい文章に自動変換します。ルールベースの修正とAWS Nova Micro LLMを組み合わせることで、最適な品質とコスト効率を実現しています。

### 主な特徴

- **高精度**: 95%以上のセグメント品質率
- **超低コスト**: セグメントあたり約¥0.003
- **ルール+AI**: 最適な修正アプローチ
- **バッチ処理**: 複数ファイルの効率的な処理
- **品質評価**: 包括的な分析ツール

## 📊 性能結果

| 講義 | セグメント数 | 品質スコア | 成功率 | コスト |
|------|-------------|-----------|--------|--------|
| Day 2 | 212 | 0.683 | 92.5% | ¥0.70 |
| Day 3 | 242 | 0.677 | 96.3% | ¥0.80 |
| Day 7 | 301 | 0.709 | 97.0% | ¥1.00 |
| **合計** | **755** | **0.690** | **95.3%** | **¥2.50** |

## 🚀 クイックスタート

### 前提条件

- Python 3.9以上
- AWS Bedrockアクセス権限付きのAWSアカウント
- boto3がインストール済み

### インストール

```bash
git clone https://github.com/yourusername/lecture-transcript-correction-ai2.git
cd lecture-transcript-correction-ai2
pip install boto3
```

### AWS設定

```bash
# AWS認証情報を設定
aws configure
# または環境変数を設定
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### 基本的な使用方法

```bash
# 単一ファイル修正
python3 nova_system.py --file input.txt

# バッチ処理
python3 batch_processor.py input_folder/

# 品質評価
python3 improved_evaluator.py original.txt corrected.txt
```

## 📁 システム構成

```
lecture-transcript-correction-ai2/
├── nova_system.py              # メインのAI統合修正システム
├── final_system.py             # ルールベース修正システム
├── batch_processor.py          # バッチ処理機能
├── improved_evaluator.py       # 品質評価システム
├── config_system.py            # 設定管理
├── correction_config.json      # システム設定
├── samples/
│   ├── sample_input.txt        # サンプル入力ファイル
│   └── sample_output.txt       # サンプル出力ファイル
├── tests/
│   └── test_basic.py          # 基本機能テスト
└── docs/
    ├── USAGE.md               # 詳細使用ガイド
    └── ARCHITECTURE.md        # システム設計文書
```

## 🔧 修正機能

### ルールベース修正
- **専門用語**: ベルト → BERT、ジーピーティー → GPT
- **文法修正**: 申しす → 申します
- **フィラー除去**: えー、あのー、なんか
- **句読点**: 自動挿入
- **繰り返し除去**: Day2になるDay2 → Day2

### AI強化修正
- **文脈認識**: 自然言語処理
- **複雑パターン**: 高度な言語学的修正
- **組織名**: 松尾岩澤研 → 松尾・岩澤研
- **自然な表現**: 話し言葉 → 書き言葉スタイル

## 📈 修正例

### 修正前後の比較

**入力:**
```
はい。本日ですねDay2になるDay2の講座になりますタイトルがPromptingとRAGで多分皆さんRAG周りかなり興味あるのかなと思っているのでぜひお楽しみにしていただければと思います講師はですねベルト...
```

**出力:**
```
はい。本日はDay2の講座になります。タイトルは「PromptingとRAG」です。RAGについては皆さんかなり興味があるのではないかと思いますので、ぜひお楽しみいただければと思います。講師は松尾・岩澤研のBERT...
```

## ⚙️ 設定

### システム設定 (`correction_config.json`)

```json
{
    "correction_threshold": 0.3,
    "llm_usage_threshold": 0.4,
    "preserve_technical_terms": true,
    "aggressive_filler_removal": true,
    "smart_punctuation": true,
    "aws_region": "us-east-1",
    "model_id": "amazon.nova-micro-v1:0"
}
```

### カスタム設定

```bash
# 現在の設定を表示
python3 config_system.py --show

# 設定を変更
python3 config_system.py --set correction_threshold 0.5

# デフォルトにリセット
python3 config_system.py --reset
```

## 📊 品質評価

### 評価指標

- **品質スコア**: 複数要因に基づく0-1スケール
- **可読性向上**: テキストの明瞭性向上
- **修正タイプ分析**: 詳細な内訳
- **成功率**: 修正成功の割合

### サンプル評価レポート

```
📊 品質分析結果:
  • 平均品質スコア: 0.690 / 1.000
  • 成功率: 95.3%
  • 文字数削減: 6,628文字
  • 句読点改善: 348回追加
  • 自然な表現: 392回改善
```

## 💰 コスト分析

### AWS Nova Micro料金
- **入力**: 1Kトークンあたり$0.000035
- **出力**: 1Kトークンあたり$0.00014

### コスト性能
- **セグメントあたり**: 約¥0.003
- **1000文字あたり**: 約¥0.008
- **講義1時間あたり**: 約¥1.00

**コスト削減**: 手動修正と比較して99%以上の削減

## 🧪 テスト

### 基本テストの実行

```bash
# 基本機能テスト
python3 tests/test_basic.py

# サンプルデータテスト
python3 nova_system.py --file samples/sample_input.txt

# 品質評価テスト
python3 improved_evaluator.py samples/sample_input.txt samples/sample_output.txt
```

## 📚 ドキュメント

- [詳細使用ガイド](docs/USAGE.md)
- [システム設計](docs/ARCHITECTURE.md)
- [設定オプション](docs/CONFIGURATION.md)
- [API リファレンス](docs/API.md)

## 🤝 貢献

1. リポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを開く

## 📄 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています。詳細は[LICENSE](LICENSE)ファイルをご覧ください。

## 🙏 謝辞

- **松尾研究室**: オリジナル講義コンテンツと研究環境
- **AWS Bedrock**: AIモデルインフラストラクチャ
- **LLM2024講座**: テストデータと使用例の検証

## 📧 連絡先

- **プロジェクト**: 講義書き起こし修正AI
- **環境**: AWS CloudShell
- **言語**: Python 3.9以上
- **依存関係**: boto3、標準ライブラリのみ

## 🔄 バージョン履歴

- **v1.0.0**: Nova Micro統合による初回リリース
- **v1.1.0**: バッチ処理と品質評価機能追加
- **v1.2.0**: 設定システムとドキュメントの強化

## 🎯 今後のロードマップ

- [ ] リアルタイム処理機能
- [ ] 多言語サポート
- [ ] より良い文脈理解のためのスライド統合
- [ ] クラウドサービス展開
- [ ] APIエンドポイント開発

---

**⭐ このプロジェクトが役に立ったら、ぜひスターを付けてください！**
