# src/prompts.py
from dataclasses import dataclass

# ─────────────────────────────────────────────────────────────────
# BASE SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────
BASE_SYSTEM_PROMPT = """You are an expert AI recruiter and resume analyst with 15 years of experience 
in talent acquisition and career coaching.

Your job is to answer questions about a candidate based strictly on their resume.

STRICT RULES:
1. ONLY use information explicitly present in the resume — never invent or assume facts.
2. If information is not in the resume, say: "This information is not mentioned in the resume."
3. Always be specific — quote actual details from the resume when relevant.
4. Be concise but thorough — give complete answers without padding.
5. Use a professional, helpful tone.

The candidate's resume is provided in <resume> tags.
"""

# ─────────────────────────────────────────────────────────────────
# STRATEGY 1: ZERO-SHOT
# ─────────────────────────────────────────────────────────────────
def zero_shot_prompt(resume_context: str, question: str) -> list[dict]:
    return [
        {"role": "system", "content": BASE_SYSTEM_PROMPT},
        {"role": "user", "content": f"<resume>\n{resume_context}\n</resume>\n\nQuestion: {question}"}
    ]


# ─────────────────────────────────────────────────────────────────
# STRATEGY 2: FEW-SHOT
# ─────────────────────────────────────────────────────────────────
FEW_SHOT_EXAMPLES = """
Here are examples of ideal responses:

Q: How many years of Python experience does the candidate have?
A: The candidate has been using Python professionally since 2020 — approximately 4 years of experience. It is listed as their primary programming language and used across all projects.

Q: What is their highest education level?
A: The candidate holds a BSc in Mathematics and Physics and is currently pursuing an MSc in Data Science, which is their highest qualification in progress.

Q: Does the candidate have cloud experience?
A: This information is not mentioned in the resume. No cloud platforms (AWS, GCP, Azure) are referenced in their skills or project descriptions.
"""

def few_shot_prompt(resume_context: str, question: str) -> list[dict]:
    return [
        {"role": "system", "content": BASE_SYSTEM_PROMPT + "\n\n" + FEW_SHOT_EXAMPLES},
        {"role": "user", "content": f"<resume>\n{resume_context}\n</resume>\n\nQuestion: {question}"}
    ]


# ─────────────────────────────────────────────────────────────────
# STRATEGY 3: CHAIN-OF-THOUGHT (clean output — no visible steps)
# ─────────────────────────────────────────────────────────────────
COT_SYSTEM = BASE_SYSTEM_PROMPT + """

IMPORTANT RESPONSE FORMAT:
Think carefully and thoroughly before answering. Consider all relevant sections of the resume.
Then give a detailed, well-structured answer.

DO NOT show your reasoning steps in your response.
DO NOT use labels like "STEP 1", "REASONING:", or "ANSWER:".
Just provide a comprehensive, insightful, well-organized answer directly.

For complex questions, structure your response with:
- A direct answer first
- Supporting evidence from the resume
- Your professional assessment or recommendation
"""

def chain_of_thought_prompt(resume_context: str, question: str) -> list[dict]:
    return [
        {"role": "system", "content": COT_SYSTEM},
        {"role": "user", "content": f"<resume>\n{resume_context}\n</resume>\n\nQuestion: {question}\n\nProvide a thorough, detailed answer."}
    ]


# ─────────────────────────────────────────────────────────────────
# SPECIAL PROMPTS: Resume Analysis
# ─────────────────────────────────────────────────────────────────
def resume_summary_prompt(resume_text: str) -> list[dict]:
    return [
        {"role": "system", "content": "You are an expert resume analyst. Be concise and specific."},
        {"role": "user", "content": f"""Analyze this resume and return a JSON object with these exact keys:
{{
  "headline": "One powerful sentence describing this candidate",
  "summary": "3-4 sentence professional summary",
  "top_strengths": ["strength1", "strength2", "strength3"],
  "areas_for_improvement": ["gap1", "gap2", "gap3"],
  "best_fit_roles": ["role1", "role2", "role3"],
  "ats_score": <integer 0-100>,
  "ats_feedback": "Why this score — what's missing or strong"
}}

Return ONLY the JSON. No markdown. No explanation.

Resume:
{resume_text}"""}
    ]


def interview_questions_prompt(resume_text: str, role: str = "AI Engineer") -> list[dict]:
    return [
        {"role": "system", "content": "You are an experienced technical interviewer."},
        {"role": "user", "content": f"""Based on this resume, generate 5 targeted interview questions for a {role} role.

For each question include:
- The question itself
- Why you're asking it (what you're probing)
- What a strong answer would include

Return as JSON array:
[{{"question": "...", "reason": "...", "strong_answer_hints": "..."}}]

Return ONLY the JSON array. No markdown.

Resume:
{resume_text}"""}
    ]


# Registry
STRATEGIES = {
    "zero_shot": zero_shot_prompt,
    "few_shot": few_shot_prompt,
    "chain_of_thought": chain_of_thought_prompt,
}

STRATEGY_INFO = {
    "zero_shot": {
        "label": "⚡ Zero-Shot",
        "short": "Fast & Direct",
        "desc": "Asks the question directly. Fastest and cheapest. Best for simple factual questions like 'What skills does this candidate have?'",
        "badge": "Fastest • Cheapest",
        "color": "#10b981"
    },
    "few_shot": {
        "label": "🎯 Few-Shot",
        "short": "Balanced (Recommended)",
        "desc": "Shows the AI 3 example answers first so it knows exactly what format and depth you expect. Best for most use cases.",
        "badge": "Best Balance • Recommended",
        "color": "#3b82f6"
    },
    "chain_of_thought": {
        "label": "🧩 Chain-of-Thought",
        "short": "Deep & Detailed",
        "desc": "Forces deep reasoning before answering. Best for complex questions like 'Is this candidate ready for a senior ML role?' or 'What skills are missing for this job?'",
        "badge": "Most Thorough • Slightly Slower",
        "color": "#8b5cf6"
    }
}