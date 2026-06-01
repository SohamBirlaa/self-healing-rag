"""
LangGraph Pipeline — Self-Healing RAG
─────────────────────────────────────
 
Flow:
  retrieve → generate → critic
                           │
               ┌───────────┼───────────┐
             PASS        RETRY        FAIL
               │            │           │
              END        rewrite       END
                            │
                     increment_retry
                            │
                         retrieve  (loop)
"""

from langgraph.graph import StateGraph, END
from app.state import GraphState
from app.nodes.retrieve import retrieve
from app.nodes.generate import generate
from app.nodes.critic import critic
from app.nodes.rewrite import rewrite
from app.utils.logger import logger

MAX_RETRIES = 3

# routin logic ========
def should_retry(state: GraphState) ->str:
    """
    Decides what to do after the critic runs.
 
    Returns
    -------
    "pass"  → answer is good, exit pipeline
    "retry" → rewrite and try again
    "fail"  → max retries hit, exit with best-effort answer
    """

    decision   = state.get("decision", "FAIL")
    confidence = state.get("confidence_score") or 0.0   # None → 0.0
    retries    = state.get("retry_count") or 0

    if decision == "PASS" and confidence >=0.7:
        logger.info(f"[ROUTER] PASS (confidence = {confidence})")
        return "pass"

    if retries >= MAX_RETRIES:
        logger.warning(f"[ROUTER] MAX RETRIES ({MAX_RETRIES}) reached exiting")
        return "fail"

    logger.info(f"[ROUTER] RETRY #{retries + 1} (confidence = {confidence})")
    
    return "retry"

def increment_retry(state: GraphState) -> dict:
    """Increments the retry counter before looping back."""
    return {"retry_count": state.get("retry_count", 0) + 1}


# build the graph=================

builder = StateGraph(GraphState)

builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_node("critic", critic)
builder.add_node("rewrite", rewrite)
builder.add_node("increment_retry", increment_retry)

# entry point

builder.set_entry_point("retrieve")


# Fixed edges
builder.add_edge("retrieve",        "generate")
builder.add_edge("generate",        "critic")
builder.add_edge("rewrite",         "increment_retry")
builder.add_edge("increment_retry", "retrieve")       # ← the retry loop
 
# Conditional routing after critic
builder.add_conditional_edges(
    "critic",
    should_retry,
    {
        "pass":  END,
        "retry": "rewrite",
        "fail":  END
    }
)
 
graph = builder.compile()

        