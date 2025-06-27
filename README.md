# 🎓 Lecture Transcript Correction AI

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![AWS](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**AI-powered system for automatically correcting speech-to-text lecture transcripts with high accuracy and ultra-low cost.**

## 🎯 Overview

This system automatically corrects speech-to-text transcripts of lectures, transforming them into natural, readable text. It combines rule-based corrections with AWS Nova Micro LLM integration for optimal quality and cost efficiency.

### Key Features

- **High Accuracy**: 95%+ segment quality rate
- **Ultra-Low Cost**: ~¥0.003 per segment
- **Rule-Based + AI**: Optimal correction approach
- **Batch Processing**: Handle multiple files efficiently
- **Quality Evaluation**: Comprehensive analysis tools

## 📊 Performance Results

| Lecture | Segments | Quality Score | Success Rate | Cost |
|---------|----------|---------------|--------------|------|
| Day 2   | 212      | 0.683         | 92.5%        | ¥0.70 |
| Day 3   | 242      | 0.677         | 96.3%        | ¥0.80 |
| Day 7   | 301      | 0.709         | 97.0%        | ¥1.00 |
| **Total** | **755** | **0.690** | **95.3%** | **¥2.50** |

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- AWS Account with Bedrock access
- boto3 installed

### Installation

```bash
git clone https://github.com/yourusername/lecture-transcript-correction-ai2.git
cd lecture-transcript-correction-ai2
pip install boto3
```

### AWS Configuration

```bash
# Configure AWS credentials
aws configure
# or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### Basic Usage

```bash
# Single file correction
python3 nova_system.py --file input.txt

# Batch processing
python3 batch_processor.py input_folder/

# Quality evaluation
python3 improved_evaluator.py original.txt corrected.txt
```

## 📁 System Architecture

```
lecture-transcript-correction-ai2/
├── nova_system.py              # Main AI-integrated correction system
├── final_system.py             # Rule-based correction system
├── batch_processor.py          # Batch processing functionality
├── improved_evaluator.py       # Quality evaluation system
├── config_system.py            # Configuration management
├── correction_config.json      # System configuration
├── samples/
│   ├── sample_input.txt        # Sample input file
│   └── sample_output.txt       # Sample output file
├── tests/
│   └── test_basic.py          # Basic functionality tests
└── docs/
    ├── USAGE.md               # Detailed usage guide
    └── ARCHITECTURE.md        # System design documentation
```

## 🔧 Correction Features

### Rule-Based Corrections
- **Technical Terms**: ベルト → BERT, ジーピーティー → GPT
- **Grammar Fixes**: 申しす → 申します
- **Filler Removal**: えー, あのー, なんか
- **Punctuation**: Automatic insertion
- **Repetition Removal**: Day2になるDay2 → Day2

### AI-Enhanced Corrections
- **Context-Aware**: Natural language processing
- **Complex Patterns**: Advanced linguistic corrections
- **Organization Names**: 松尾岩澤研 → 松尾・岩澤研
- **Natural Expression**: Conversational → Written style

## 📈 Correction Examples

### Before and After

**Input:**
```
はい。本日ですねDay2になるDay2の講座になりますタイトルがPromptingとRAGで多分皆さんRAG周りかなり興味あるのかなと思っているのでぜひお楽しみにしていただければと思います講師はですねベルト...
```

**Output:**
```
はい。本日はDay2の講座になります。タイトルは「PromptingとRAG」です。RAGについては皆さんかなり興味があるのではないかと思いますので、ぜひお楽しみいただければと思います。講師は松尾・岩澤研のBERT...
```

## ⚙️ Configuration

### System Settings (`correction_config.json`)

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

### Custom Configuration

```bash
# View current configuration
python3 config_system.py --show

# Modify settings
python3 config_system.py --set correction_threshold 0.5

# Reset to defaults
python3 config_system.py --reset
```

## 📊 Quality Evaluation

### Evaluation Metrics

- **Quality Score**: 0-1 scale based on multiple factors
- **Readability Improvement**: Text clarity enhancement
- **Correction Type Analysis**: Detailed breakdown
- **Success Rate**: Percentage of successful corrections

### Sample Evaluation Report

```
📊 Quality Analysis Results:
  • Average Quality Score: 0.690 / 1.000
  • Success Rate: 95.3%
  • Character Reduction: 6,628 characters
  • Punctuation Improvement: 348 additions
  • Natural Expression: 392 improvements
```

## 💰 Cost Analysis

### AWS Nova Micro Pricing
- **Input**: $0.000035 per 1K tokens
- **Output**: $0.00014 per 1K tokens

### Cost Performance
- **Per Segment**: ~¥0.003
- **Per 1000 Characters**: ~¥0.008
- **Per Hour of Lecture**: ~¥1.00

**Cost Reduction**: 99%+ compared to manual correction

## 🧪 Testing

### Run Basic Tests

```bash
# Basic functionality test
python3 tests/test_basic.py

# Sample data test
python3 nova_system.py --file samples/sample_input.txt

# Quality evaluation test
python3 improved_evaluator.py samples/sample_input.txt samples/sample_output.txt
```

## 📚 Documentation

- [Detailed Usage Guide](docs/USAGE.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Configuration Options](docs/CONFIGURATION.md)
- [API Reference](docs/API.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Matsuo Lab**: Original lecture content and research environment
- **AWS Bedrock**: AI model infrastructure
- **LLM2024 Course**: Test data and use case validation

## 📧 Contact

- **Project**: Lecture Transcript Correction AI
- **Environment**: AWS CloudShell
- **Language**: Python 3.9+
- **Dependencies**: boto3, standard library only

## 🔄 Version History

- **v1.0.0**: Initial release with Nova Micro integration
- **v1.1.0**: Added batch processing and quality evaluation
- **v1.2.0**: Enhanced configuration system and documentation

## 🎯 Future Roadmap

- [ ] Real-time processing capability
- [ ] Multi-language support
- [ ] Slide integration for better context
- [ ] Cloud service deployment
- [ ] API endpoint development

---

**⭐ If this project helps you, please consider giving it a star!**
