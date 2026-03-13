# src/analytics.py
import json
import openai
import os
from src.prompts import resume_summary_prompt, interview_questions_prompt


def get_resume_analysis(resume_text: str, client: openai.OpenAI) -> dict:
    """
    Run full resume analysis — summary, ATS score, strengths, gaps, roles.
    Returns structured dict. Falls back to empty dict on any error.
    """
    try:
        messages = resume_summary_prompt(resume_text)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.2,
            max_tokens=800,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        return {
            "headline": "Analysis unavailable",
            "summary": "",
            "top_strengths": [],
            "areas_for_improvement": [],
            "best_fit_roles": [],
            "ats_score": 0,
            "ats_feedback": str(e)
        }


def get_interview_questions(resume_text: str, role: str, client: openai.OpenAI) -> list:
    """Generate targeted interview questions for a given role."""
    try:
        messages = interview_questions_prompt(resume_text, role)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.4,
            max_tokens=1000,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception:
        return []


def make_groq_client() -> openai.OpenAI:
    return openai.OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )