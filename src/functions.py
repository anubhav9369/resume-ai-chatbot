# src/functions.py
import json
import openai
from typing import Any


# ─────────────────────────────────────────────────────
# TOOL DEFINITIONS (JSON Schema format)
# ─────────────────────────────────────────────────────
EXTRACT_PROFILE_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_candidate_profile",
        "description": "Extract structured profile data from a resume",
        "parameters": {
            "type": "object",
            "properties": {
                "full_name": {
                    "type": "string",
                    "description": "Candidate full name"
                },
                "email": {
                    "type": ["string", "null"],
                    "description": "Email address if present"
                },
                "total_experience_years": {
                    "type": "number",
                    "description": "Estimated total years of professional experience"
                },
                "top_skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Top 5-8 technical skills"
                },
                "education_level": {
                    "type": "string",
                    "enum": ["High School", "Bachelor", "Master", "PhD", "Unknown"],
                    "description": "Highest education level"
                },
                "current_or_recent_role": {
                    "type": "string",
                    "description": "Most recent job title"
                },
                "is_suitable_for_ml_role": {
                    "type": "boolean",
                    "description": "Does this candidate have ML/AI background?"
                }
            },
            "required": ["full_name", "top_skills", "education_level"]
        }
    }
}


def extract_structured_profile(resume_text: str, client: openai.OpenAI) -> dict[str, Any]:
    """
    Use function calling to extract structured data from resume.
    Returns a clean Python dict — no regex, no parsing.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract structured information from the resume. Be precise and conservative."
            },
            {
                "role": "user",
                "content": f"Extract profile data from this resume:\n\n{resume_text}"
            }
        ],
        tools=[EXTRACT_PROFILE_TOOL],
        tool_choice={"type": "function", "function": {"name": "extract_candidate_profile"}}
    )

    # The LLM is forced to call our function — extract the arguments
    tool_call = response.choices[0].message.tool_calls[0]
    profile = json.loads(tool_call.function.arguments)
    return profile


def format_profile_as_markdown(profile: dict) -> str:
    """Format extracted profile for display in UI."""
    skills = ', '.join(profile.get('top_skills', []))
    return f'''
    ## 📋 Candidate Profile (Auto-extracted)

    | Field | Value |
    |-------|-------|
    | Name | {profile.get('full_name', 'N/A')} |
    | Current Role | {profile.get('current_or_recent_role', 'N/A')} |
    | Experience | {profile.get('total_experience_years', 'N/A')} years |
    | Education | {profile.get('education_level', 'N/A')} |
    | ML Background | {'Yes' if profile.get('is_suitable_for_ml_role') else 'No'} |
    | Top Skills | {skills} |
    '''
