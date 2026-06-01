# """
# Critic Node
# ───────────
# Evaluates the generated answer for:
#   - Groundedness (is it backed by the context?)
#   - Hallucination (did the LLM invent facts?)
#   - Confidence (0.0 – 1.0)
 
# Sets state["decision"] = "PASS" or "FAIL"
# Sets state["confidence_score"] = float
# """

# import re
# from langchain_ollama import OllamaLLM
# from app.state import GraphState
# from app.prompts.templates import CRITIC_PROMPT
# from app.utils.logger import logger

# _llm = None

# def _get_llm():
#     global _llm
#     if _llm is None:
#         _llm = OllamaLLM(
#             model="llama3.2",
#             temperature=0.0
#         )
#     return _llm
    

# def _parse_critic_response(response: str) -> tuple:

#     decision   = "FAIL"
#     confidence = 0.0
#     reason     = "Could not parse."

#     # lowercase karke dhundo — case insensitive
#     response_lower = response.lower()

#     if "decision: pass" in response_lower:
#         decision = "PASS"
#     elif "decision: fail" in response_lower:
#         decision = "FAIL"

#     # confidence number dhundo anywhere in response
#     import re
#     match = re.search(r"confidence[:\s]+([0-9.]+)", response_lower)
#     if match:
#         try:
#             confidence = min(max(float(match.group(1)), 0.0), 1.0)
#         except ValueError:
#             confidence = 0.0

#     # reason dhundo
#     for line in response.splitlines():
#         if "reason" in line.lower():
#             reason = line.split(":", 1)[-1].strip()
#             break

#     return decision, confidence, reason
    

# def critic(state: GraphState) -> dict:
#     """
#     Runs the critic LLM and returns decision + confidence_score.
#     """
 
#     question  = state.get("rewritten_question") or state["question"]
#     documents = state.get("documents", [])
#     answer    = state.get("answer", "")
 
#     if not answer:
#         logger.warning("[CRITIC] Empty answer received. Auto-FAIL.")
#         return {"decision": "FAIL", "confidence_score": 0.0}
 
#     context = "\n\n---\n\n".join(documents) if documents else "No context available."
 
#     prompt = CRITIC_PROMPT.format(
#         context=context,
#         question=question,
#         answer=answer
#     )
 
#     logger.info("[CRITIC] Evaluating answer...")
 
#     llm      = _get_llm()
#     response = llm.invoke(prompt)
 
#     decision, confidence, reason = _parse_critic_response(response)
 
#     logger.info(
#         f"[CRITIC] Decision: {decision} | "
#         f"Confidence: {confidence} | "
#         f"Reason: {reason}"
#     )
 
#     return {
#         "decision":         decision,
#         "confidence_score": confidence
#     }



import re
import os
from langchain_groq import ChatGroq
from app.state import GraphState
from app.prompts.templates import CRITIC_PROMPT
from app.utils.logger import logger
from dotenv import load_dotenv
load_dotenv()


_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        logger.info("Connecting to Groq (critic)...")
        _llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.environ.get("GROQ_API_KEY"),
            temperature=0.0
        )
    return _llm

def _parse_critic_response(response: str) -> tuple:
    decision   = "FAIL"
    confidence = 0.0
    reason     = "Could not parse."

    response_lower = response.lower()

    if "decision: pass" in response_lower:
        decision = "PASS"
    elif "decision: fail" in response_lower:
        decision = "FAIL"

    match = re.search(r"confidence[:\s]+([0-9.]+)", response_lower)
    if match:
        try:
            confidence = min(max(float(match.group(1)), 0.0), 1.0)
        except ValueError:
            confidence = 0.0

    for line in response.splitlines():
        if "reason" in line.lower():
            reason = line.split(":", 1)[-1].strip()
            break

    return decision, confidence, reason

def critic(state: GraphState) -> dict:
    question  = state.get("rewritten_question") or state["question"]
    documents = state.get("documents", [])
    answer    = state.get("answer", "")

    if not answer:
        logger.warning("[CRITIC] Empty answer. Auto-FAIL.")
        return {"decision": "FAIL", "confidence_score": 0.0}

    context = "\n\n---\n\n".join(documents) if documents else "No context."

    prompt = CRITIC_PROMPT.format(
        context=context,
        question=question,
        answer=answer
    )

    logger.info("[CRITIC] Evaluating answer...")
    llm      = _get_llm()
    response = llm.invoke(prompt).content    # .content — ChatGroq

    decision, confidence, reason = _parse_critic_response(response)

    logger.info(f"[CRITIC] Decision: {decision} | Confidence: {confidence} | Reason: {reason}")

    return {
        "decision":         decision,
        "confidence_score": confidence
    }