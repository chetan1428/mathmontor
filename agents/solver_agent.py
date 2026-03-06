"""
solver_agent.py — Agent 3: Solver Agent + SymPy Tool
Solves math problems using RAG + SymPy + Gemini.
"""

import json
import re
from typing import Dict, List, Optional

from agents.client import call_gemini
from rag import format_context

# Optional: sympy for symbolic math
try:
    import sympy as sp
    from sympy.parsing.sympy_parser import parse_expr
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False


# ─────────────────────────────────────────────
# SymPy Tool
# ─────────────────────────────────────────────

def try_sympy_solve(problem_text: str, parsed: Dict) -> Optional[str]:
    """
    Attempt to solve the problem symbolically with SymPy.
    Returns a string answer or None if it can't solve it.
    """
    if not HAS_SYMPY:
        return None
    try:
        # Ask Gemini to write SymPy code for the problem
        code_prompt = f"""Write Python SymPy code to solve this math problem.
Problem: {problem_text}

Requirements:
- Use sympy library
- Store the final answer in a variable called `result`
- result should be a string representation of the answer
- Do NOT use print() — just assign to result
- Keep it simple and safe (no loops > 1000, no eval of user input)
- If the problem asks to solve an equation, use sp.solve()
- If derivative, use sp.diff()
- If limit, use sp.limit()
- If integral, use sp.integrate()

Return ONLY the Python code, no explanation, no markdown fences."""

        code = call_gemini("You are a Python/SymPy code generator.", code_prompt, temperature=0.1)
        # Clean code fences if present
        code = re.sub(r'^```python\n?', '', code, flags=re.MULTILINE)
        code = re.sub(r'^```\n?', '', code, flags=re.MULTILINE)
        code = code.strip()

        # Execute in sandboxed namespace
        namespace = {"sp": sp, "symbols": sp.symbols, "result": None}
        exec(code, namespace)  # noqa: S102
        result = namespace.get("result")
        if result is not None:
            return str(result)
    except Exception as e:
        return None
    return None


# ─────────────────────────────────────────────
# Agent 3: Solver Agent
# ─────────────────────────────────────────────

SOLVER_SYSTEM = """You are an expert JEE mathematics solver — precise, methodical, and correct.

You are given:
- A structured math problem
- Relevant reference material (RAG context)
- Similar solved problems from memory
- Solution strategy (route)

Your task: Solve the problem completely and correctly.

Return a JSON object:
{
  "answer": "the final answer (clear, concise)",
  "solution_steps": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "working": "detailed mathematical working",
  "answer_type": "numerical | algebraic | set | interval | boolean | proof",
  "units": "",
  "sympy_verified": false
}

Be rigorous. Show all key steps. Do not skip algebra. Return ONLY valid JSON."""


def solver_agent(parsed: Dict, route: Dict, rag_chunks: List[Dict],
                 memory_context: str = "") -> Dict:
    """Agent 3: Solve the problem using RAG + SymPy + Gemini."""
    problem_text = parsed.get("problem_text", "")

    # Try SymPy first for symbolic route
    sympy_answer = None
    if route.get("route") == "symbolic" and HAS_SYMPY:
        sympy_answer = try_sympy_solve(problem_text, parsed)

    # Build context
    rag_context = format_context(rag_chunks)
    user_msg = f"""Problem (structured):
{json.dumps(parsed, indent=2)}

Solution strategy: {route.get('route')} | Difficulty: {route.get('difficulty')}
Estimated steps: {route.get('estimated_steps')}

Reference material:
{rag_context}
"""
    if memory_context:
        user_msg += f"\n{memory_context}"
    if sympy_answer:
        user_msg += f"\n\nSymPy computed answer (use as verification): {sympy_answer}"

    result_str = call_gemini(SOLVER_SYSTEM, user_msg, response_format="json", temperature=0.1)
    try:
        result = json.loads(result_str)
    except json.JSONDecodeError:
        result = {
            "answer": "Could not compute answer",
            "solution_steps": ["Error in solver"],
            "working": result_str,
            "answer_type": "unknown",
            "units": "",
            "sympy_verified": False
        }

    if sympy_answer:
        result["sympy_answer"] = sympy_answer
        result["sympy_verified"] = True

    return result
