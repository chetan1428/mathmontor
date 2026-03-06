"""
explainer_agent.py — Agent 5: Explainer / Tutor Agent
Generates student-friendly step-by-step explanations.
"""

import json
from typing import Dict, List

from agents.client import call_gemini
from rag import format_context


EXPLAINER_SYSTEM = """You are an encouraging, expert math tutor helping JEE students.

You are given a solved problem. Your task: produce a clear, student-friendly explanation.

CRITICAL FORMATTING REQUIREMENTS:
- You MUST format your explanation strictly step-by-step.
- Use distinct headings or numbered lists for each step (e.g., "### Step 1: ...", "### Step 2: ...").
- You MUST insert double line breaks (`\n\n`) between each step so they appear as separate paragraphs in the UI, NOT a single wall of text.
- Explain the WHY behind each step, not just the what.
- Use simple language suitable for a 17-year-old student.
- Highlight key formulas used (wrap in **formula**).
- End with a brief summary / key takeaway.
- Use LaTeX notation for math: $formula$ inline, $$formula$$ for display.

Return a JSON object:
{
  "explanation": "full markdown explanation with numbered steps",
  "key_formulas": ["list of main formulas used"],
  "common_mistakes": ["mistakes students make on this type"],
  "similar_problem_hint": "a similar practice problem suggestion",
  "difficulty_rating": "easy | medium | hard",
  "topic_tags": ["topic1", "topic2"]
}

Return ONLY valid JSON."""


def explainer_agent(parsed: Dict, solution: Dict, verification: Dict,
                    rag_chunks: List[Dict]) -> Dict:
    """Agent 5: Generate student-friendly step-by-step explanation."""
    # Use corrected answer if verifier found one
    final_answer = verification.get("corrected_answer") or solution.get("answer")
    rag_context = format_context(rag_chunks[:2])  # Limit context for explainer

    user_msg = f"""Problem: {parsed.get('problem_text')}
Topic: {parsed.get('topic')} — {parsed.get('subtopic')}

Final Answer: {final_answer}

Solution steps:
{chr(10).join(solution.get('solution_steps', []))}

Working:
{solution.get('working', '')}

Reference material (use for accurate explanations):
{rag_context}

Verification notes:
- Verdict: {verification.get('verdict')}
- Issues found: {', '.join(verification.get('issues_found', [])) or 'none'}

Generate a complete, encouraging explanation for a JEE student."""

    result_str = call_gemini(EXPLAINER_SYSTEM, user_msg, response_format="json", temperature=0.3)
    try:
        result = json.loads(result_str)
    except json.JSONDecodeError:
        result = {
            "explanation": result_str,
            "key_formulas": [],
            "common_mistakes": [],
            "similar_problem_hint": "",
            "difficulty_rating": "medium",
            "topic_tags": [parsed.get("topic", "math")]
        }
    return result
