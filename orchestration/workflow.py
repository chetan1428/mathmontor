"""
pipeline.py — Main Pipeline Orchestrator (LangGraph)
Runs the full 5-agent pipeline end-to-end using LangGraph.
"""

import os
from typing import Dict, TypedDict, Any, List

from langgraph.graph import StateGraph, START, END

from memory import find_similar, format_memory_context
from rag import retrieve
from agents.parser_agent import parser_agent
from agents.intent_router_agent import intent_router_agent
from agents.solver_agent import solver_agent
from agents.verifier_agent import verifier_agent
from agents.explainer_agent import explainer_agent


class GraphState(TypedDict):
    """The unified state object passed between nodes."""
    raw_input: str
    input_type: str
    
    memory_context: str
    similar_problems: List[Dict]
    
    parsed: Dict[str, Any]
    rag_chunks: List[Dict]
    routing: Dict[str, Any]
    solution: Dict[str, Any]
    verification: Dict[str, Any]
    explanation: Dict[str, Any]
    
    final_answer: str
    confidence: int
    hitl_needed: bool
    hitl_reason: str
    
    trace: List[Dict[str, Any]]


def node_memory(state: GraphState) -> Dict:
    raw_input = state["raw_input"]
    trace = state.get("trace", [])
    
    trace.append({"agent": "Memory", "status": "searching similar problems..."})
    similar = find_similar(raw_input, top_k=3)
    memory_context = format_memory_context(similar)
    trace[-1]["status"] = f"found {len(similar)} similar problems"
    
    return {
        "similar_problems": similar,
        "memory_context": memory_context,
        "trace": trace
    }


def node_parser(state: GraphState) -> Dict:
    raw_input = state["raw_input"]
    memory_context = state.get("memory_context", "")
    trace = state.get("trace", [])
    
    trace.append({"agent": "Parser Agent", "status": "running..."})
    parsed = parser_agent(raw_input, memory_context)
    trace[-1]["status"] = f"topic={parsed.get('topic')} | needs_clarification={parsed.get('needs_clarification')}"
    trace[-1]["output"] = parsed
    
    return {"parsed": parsed, "trace": trace}


def node_rag(state: GraphState) -> Dict:
    parsed = state.get("parsed", {})
    raw_input = state.get("raw_input", "")
    trace = state.get("trace", [])
    
    trace.append({"agent": "RAG Retrieval", "status": "fetching context..."})
    rag_query = parsed.get("problem_text", raw_input)
    rag_chunks = retrieve(rag_query, top_k=3)
    trace[-1]["status"] = f"retrieved {len(rag_chunks)} chunks"
    trace[-1]["chunks"] = rag_chunks
    
    return {"rag_chunks": rag_chunks, "trace": trace}


def node_router(state: GraphState) -> Dict:
    parsed = state.get("parsed", {})
    trace = state.get("trace", [])
    
    trace.append({"agent": "Intent Router", "status": "routing..."})
    routing = intent_router_agent(parsed)
    trace[-1]["status"] = f"route={routing.get('route')} | difficulty={routing.get('difficulty')}"
    trace[-1]["output"] = routing
    
    return {"routing": routing, "trace": trace}


def node_solver(state: GraphState) -> Dict:
    parsed = state.get("parsed", {})
    routing = state.get("routing", {})
    rag_chunks = state.get("rag_chunks", [])
    memory_context = state.get("memory_context", "")
    trace = state.get("trace", [])
    
    trace.append({"agent": "Solver Agent", "status": "solving..."})
    solution = solver_agent(parsed, routing, rag_chunks, memory_context)
    trace[-1]["status"] = f"answer={str(solution.get('answer', ''))[:80]}"
    trace[-1]["output"] = solution
    
    return {"solution": solution, "trace": trace}


def node_verifier(state: GraphState) -> Dict:
    parsed = state.get("parsed", {})
    solution = state.get("solution", {})
    rag_chunks = state.get("rag_chunks", [])
    trace = state.get("trace", [])
    
    trace.append({"agent": "Verifier Agent", "status": "verifying..."})
    verification = verifier_agent(parsed, solution, rag_chunks)
    trace[-1]["status"] = (
        f"verdict={verification.get('verdict')} | "
        f"confidence={verification.get('confidence')}% | "
        f"hitl={verification.get('hitl_needed')}"
    )
    trace[-1]["output"] = verification
    
    final_answer = verification.get("corrected_answer") or solution.get("answer", "")
    
    return {
        "verification": verification,
        "final_answer": final_answer,
        "confidence": verification.get("confidence", 0),
        "hitl_needed": verification.get("hitl_needed", False),
        "hitl_reason": verification.get("hitl_reason", ""),
        "trace": trace
    }


def node_explainer(state: GraphState) -> Dict:
    parsed = state.get("parsed", {})
    solution = state.get("solution", {})
    verification = state.get("verification", {})
    rag_chunks = state.get("rag_chunks", [])
    trace = state.get("trace", [])
    
    trace.append({"agent": "Explainer Agent", "status": "generating explanation..."})
    explanation = explainer_agent(parsed, solution, verification, rag_chunks)
    trace[-1]["status"] = "explanation ready"
    trace[-1]["output"] = {"key_formulas": explanation.get("key_formulas"), "topic_tags": explanation.get("topic_tags")}
    
    return {"explanation": explanation, "trace": trace}


# Build the Graph
workflow = StateGraph(GraphState)

workflow.add_node("memory", node_memory)
workflow.add_node("parser", node_parser)
workflow.add_node("rag", node_rag)
workflow.add_node("router", node_router)
workflow.add_node("solver", node_solver)
workflow.add_node("verifier", node_verifier)
workflow.add_node("explainer", node_explainer)

workflow.add_edge(START, "memory")
workflow.add_edge("memory", "parser")
workflow.add_edge("parser", "rag")
workflow.add_edge("rag", "router")
workflow.add_edge("router", "solver")
workflow.add_edge("solver", "verifier")
workflow.add_edge("verifier", "explainer")
workflow.add_edge("explainer", END)

app_graph = workflow.compile()


def run_pipeline(
    raw_input: str,
    input_type: str = "text",
    api_key: str = None
) -> Dict:
    """
    Full 5-agent pipeline orchestrated with LangGraph.
    
    Args:
        raw_input: the problem text
        input_type: 'text' | 'image' | 'audio'
        api_key: optional override for GEMINI_API_KEY

    Returns:
        Full result dict with all agent outputs (compatible with previous structure).
    """
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

    initial_state = {
        "raw_input": raw_input,
        "input_type": input_type,
        "trace": []
    }
    
    final_state = app_graph.invoke(initial_state)
    
    # Return output in the exact same format as before so the UI doesn't break
    return dict(final_state)


if __name__ == "__main__":
    # Quick smoke test
    import sys
    key = sys.argv[1] if len(sys.argv) > 1 else os.getenv("GEMINI_API_KEY")
    if not key:
        print("Usage: python -m agents.pipeline YOUR_API_KEY")
        sys.exit(1)
    os.environ["GEMINI_API_KEY"] = key
    result = run_pipeline("Solve: 2x² - 5x + 3 = 0", "text")
    print("Answer:", result.get("final_answer"))
    print("Confidence:", result.get("confidence"))
    print("HITL needed:", result.get("hitl_needed"))
