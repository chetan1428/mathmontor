"""
verifier_agent.py — Agent 4: Verifier / Critic Agent
Checks correctness, sets confidence, and flags HITL if needed.
"""

import json
from typing import Dict, List

from agents.client import call_gemini
from rag import format_context


VERIFIER_SYSTEM = """You are a rigorous math verifier / critic for a JEE tutoring system.

You are given a solved math problem. Your job:
1. Re-verify the solution approach
2. Check for domain/constraint violations
3. Check for common mistakes (sign errors, wrong formula, etc.)
4. Assess confidence in the answer

Return a JSON object:
{
  "verdict": "correct | likely_correct | uncertain | likely_incorrect | incorrect",
  "confidence": 85,
  "issues_found": ["list any issues, or empty list"],
  "domain_check": "passed | warning | failed",
  "edge_cases_checked": ["list edge cases you checked"],
  "hitl_needed": false,
  "hitl_reason": "",
  "corrected_answer": null
}

Set hitl_needed=true if:
- confidence < 70
- Any critical issue found
- Answer seems unreasonable

corrected_answer: provide if you found an error, else null.
Return ONLY valid JSON."""


def verifier_agent(parsed: Dict, solution: Dict, rag_chunks: List[Dict]) -> Dict:
    """Agent 4: Verify the solution and assess confidence."""
    rag_context = format_context(rag_chunks)
    user_msg = f"""Problem:
{json.dumps(parsed, indent=2)}

Proposed solution:
{json.dumps(solution, indent=2)}

Reference material:
{rag_context}

Verify this solution carefully."""

    result_str = call_gemini(VERIFIER_SYSTEM, user_msg, response_format="json", temperature=0.1)
    try:
        result = json.loads(result_str)
    except json.JSONDecodeError:
        result = {
            "verdict": "uncertain",
            "confidence": 50,
            "issues_found": ["Verifier error"],
            "domain_check": "warning",
            "edge_cases_checked": [],
            "hitl_needed": True,
            "hitl_reason": "Verification failed — manual review recommended",
            "corrected_answer": None
        }

    # Force HITL if confidence < 70
    if result.get("confidence", 100) < 70 and not result.get("hitl_needed"):
        result["hitl_needed"] = True
        result["hitl_reason"] = f"Confidence is {result['confidence']}% — below threshold"

    return result
