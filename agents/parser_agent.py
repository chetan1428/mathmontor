"""
parser_agent.py — Agent 1: Parser Agent
Cleans input and extracts structured math problem.
"""

import json
from typing import Dict

from agents.client import call_gemini


PARSER_SYSTEM = """You are a mathematical problem parser for a JEE-level math tutoring system.

Your job is to clean and structure a raw math problem input (which may come from OCR, speech-to-text, or direct text).

Return a JSON object with EXACTLY these fields:
{
  "problem_text": "clean, complete, unambiguous statement of the math problem",
  "topic": "one of: algebra | probability | calculus | linear_algebra",
  "subtopic": "specific subtopic e.g. quadratic equations, limits, matrix inverse",
  "variables": ["list", "of", "unknown", "variables"],
  "given_values": {"key": "value pairs of given quantities"},
  "constraints": ["any domain or boundary constraints"],
  "question_type": "one of: solve | prove | find | simplify | optimize | evaluate",
  "needs_clarification": false,
  "clarification_reason": ""
}

Set needs_clarification=true if:
- The problem is incomplete or ambiguous
- Key information is missing
- There are conflicting statements

Return ONLY valid JSON. No explanation, no markdown, no code fences."""


def parser_agent(raw_input: str, memory_context: str = "") -> Dict:
    """
    Agent 1: Parse raw input into structured problem format.
    """
    user_msg = f"Raw input to parse:\n{raw_input}"
    if memory_context:
        user_msg += f"\n\nContext from memory (similar past problems):\n{memory_context}"

    result_str = call_gemini(PARSER_SYSTEM, user_msg, response_format="json")
    try:
        result = json.loads(result_str)
    except json.JSONDecodeError:
        # Fallback: basic structure
        result = {
            "problem_text": raw_input,
            "topic": "algebra",
            "subtopic": "unknown",
            "variables": [],
            "given_values": {},
            "constraints": [],
            "question_type": "solve",
            "needs_clarification": True,
            "clarification_reason": "Could not parse the problem structure. Please review."
        }
    return result
