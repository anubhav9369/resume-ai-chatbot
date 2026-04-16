# 🧠 ResumeAI — Intelligent Resume Analyzer

An AI-powered resume analysis chatbot built with LLaMA 3.1 (via Groq), 
Streamlit, and advanced prompt engineering.

## 🚀 Live Demo
[[Visit Website !](https://resume-ai-chatb0t.streamlit.app/)]
<img width="1628" height="922" alt="image" src="https://github.com/user-attachments/assets/594e7841-3ba9-4939-99e7-a4de8f88bca2" />
<img width="1603" height="916" alt="image" src="https://github.com/user-attachments/assets/7f46de15-7a0f-45b5-8763-4cd6e4c1c3e7" />
<img width="1571" height="777" alt="image" src="https://github.com/user-attachments/assets/af155b0a-4769-4aa3-9872-8e3dea187193" />
<img width="1578" height="864" alt="image" src="https://github.com/user-attachments/assets/bb518070-c9b1-4aa5-a8ee-ee8cb6f8b7da" />





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



