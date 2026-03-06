"""
intent_router_agent.py — Agent 2: Intent Router Agent
Classifies topic and chooses solution strategy.
"""

import json
from typing import Dict

from agents.client import call_gemini


ROUTER_SYSTEM = """You are a math problem routing agent for a JEE tutoring system.

Given a structured math problem (JSON), decide the best solution strategy.

Return a JSON object with:
{
  "route": "one of: symbolic | numeric | conceptual",
  "reasoning": "brief reason for the route choice",
  "tools_needed": ["list of tools: sympy, calculator, definition_lookup"],
  "difficulty": "easy | medium | hard",
  "estimated_steps": 3
}

Route meanings:
- symbolic: exact algebraic/symbolic solution using SymPy is feasible
- numeric: numerical computation needed, or symbolic too complex
- conceptual: theorem application, proof, or conceptual explanation

Return ONLY valid JSON."""


def intent_router_agent(parsed: Dict) -> Dict:
    """Agent 2: Route the problem to the right solver strategy."""
    user_msg = f"Problem to route:\n{json.dumps(parsed, indent=2)}"
    result_str = call_gemini(ROUTER_SYSTEM, user_msg, response_format="json")
    try:
        result = json.loads(result_str)
    except json.JSONDecodeError:
        result = {
            "route": "conceptual",
            "reasoning": "Default fallback routing",
            "tools_needed": [],
            "difficulty": "medium",
            "estimated_steps": 4
        }
    return result
