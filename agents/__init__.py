"""
agents — All 5 Agents + Pipeline Orchestrator (Package)

Agents:
  1. Parser Agent       — cleans input, extracts structured problem
  2. Intent Router      — classifies topic, chooses solution strategy
  3. Solver Agent       — solves using RAG + SymPy + Gemini
  4. Verifier Agent     — checks correctness, sets confidence / HITL flag
  5. Explainer Agent    — generates student-friendly step-by-step explanation

Pipeline: run_pipeline(raw_input, input_type) → full result dict
"""

from agents.client import get_client, call_gemini
from agents.multimodal import extract_from_image, transcribe_audio
from agents.parser_agent import parser_agent
from agents.intent_router_agent import intent_router_agent
from agents.solver_agent import solver_agent, try_sympy_solve
from agents.verifier_agent import verifier_agent
from agents.explainer_agent import explainer_agent

__all__ = [
    "get_client",
    "call_gemini",
    "extract_from_image",
    "transcribe_audio",
    "parser_agent",
    "intent_router_agent",
    "solver_agent",
    "try_sympy_solve",
    "verifier_agent",
    "explainer_agent",
]
