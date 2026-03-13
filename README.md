# 🧠 ResumeAI — Intelligent Resume Analyzer

An AI-powered resume analysis chatbot built with LLaMA 3.1 (via Groq), 
Streamlit, and advanced prompt engineering.

## 🚀 Live Demo
[[Link will go here after deployment](https://resume-ai-chatb0t.streamlit.app/)]

## ✨ Features
- PDF resume upload with automatic text extraction
- 3 prompting strategies: Zero-Shot, Few-Shot, Chain-of-Thought
- ATS compatibility scoring
- Resume strengths & improvement areas
- Best-fit role recommendations
- Interview question generator
- Per-query cost and latency tracking

## 🏗 Architecture
User → PDF Upload → PyMuPDF extraction → ResumeLoader (section parser)
     → Prompt Strategy (zero/few/CoT) → Groq LLaMA 3.1 → Structured Response

## 📊 Benchmark Results
| Strategy | Avg Quality | Avg Tokens | Avg Latency | Cost/Query |
|---|---|---|---|---|
| chain_of_thought | 0.60 | 533 | 2140ms | $0.000700 |
| few_shot | 0.45 | 390 | 337ms | $0.000400 |
| zero_shot | 0.45 | 224 | 305ms | $0.000200 |

## 🛠 Tech Stack
- **LLM**: LLaMA 3.1 8B via Groq API
- **Framework**: Streamlit
- **PDF Parsing**: PyMuPDF (fitz)
- **Prompt Engineering**: Zero-shot, Few-shot, Chain-of-Thought
- **Token Counting**: tiktoken

## ⚡ Run Locally
```bash
git clone https://github.com/YOUR_USERNAME/resume-ai-chatbot
cd resume-ai-chatbot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your Groq API key
python3 -m streamlit run app.py
```

## 📁 Project Structure
```
resume-ai-chatbot/
├── src/
│   ├── chatbot.py       # Core LLM chat logic + memory
│   ├── loader.py        # Resume parser + section extractor
│   ├── prompts.py       # All prompt strategies
│   ├── functions.py     # OpenAI function calling
│   ├── evaluator.py     # Benchmark harness
│   └── analytics.py     # ATS scoring + interview prep
├── data/
│   ├── sample_resume.txt
│   └── test_questions.json
├── app.py               # Streamlit UI
├── benchmark.py         # CLI benchmark runner
└── requirements.txt
```

