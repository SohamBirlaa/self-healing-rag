# """
# Rewrite Node
# ────────────
# When the critic rejects an answer, this node:
# 1. Rewrites the question to be more specific
# 2. Tracks all previous rewrites to prevent loops
# """

# from langchain_ollama import OllamaLLM
# from app.state import GraphState
# from app.prompts.templates import REWRITE_PROMPT
# from app.utils.logger import logger

# _llm = None

# def _get_llm():
#     global _llm
#     if _llm is None:
#         _llm = OllamaLLM(
#             model="llama3.2",
#             temperature=0.5
#         )
#     return _llm

# def rewrite(state: GraphState) -> dict :
#     """
#     Generates an improved version of the question.
#     Appends the old question to previous_questions to prevent loops.
#     """

#     question = state.get("rewritten_question") or state["question"]
#     previous_question = state.get("previous_questions", [])

#     #format history for the prompt

#     history_str = (
#         "\n".join(f"- {q}" for q in previous_question)
#         if previous_question
#         else "None"
#     )

#     prompt = REWRITE_PROMPT.format(
#         question=question,
#         previous_questions=history_str
#     )

#     logger.info(f"[REWRITE] Rewriting question: {question}")

#     llm = _get_llm()
#     new_question = llm.invoke(prompt).strip()

#     # Guard: if LLM returned the same question, append a nudge

#     if new_question.lower() == question.lower():
#         new_question = question + "Please provide technical details."
#         logger.warning("[REWRITE] LLM returend same question - applied fallback nudge")

#     updated_history = previous_question + [question]

#     logger.info(f"[REWRITE] New question: {new_question}")

#     return {
#         "rewritten_question" : new_question,
#         "previous_questions": updated_history
#     }

import os
from langchain_groq import ChatGroq
from app.state import GraphState
from app.prompts.templates import REWRITE_PROMPT
from app.utils.logger import logger
from dotenv import load_dotenv
load_dotenv()


_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        logger.info("Connecting to Groq (rewrite)...")
        _llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.environ.get("GROQ_API_KEY"),
            temperature=0.5
        )
    return _llm

def rewrite(state: GraphState) -> dict:
    question           = state.get("rewritten_question") or state["question"]
    previous_questions = state.get("previous_questions", [])

    history_str = (
        "\n".join(f"- {q}" for q in previous_questions)
        if previous_questions else "None"
    )

    prompt = REWRITE_PROMPT.format(
        question=question,
        previous_questions=history_str
    )

    logger.info(f"[REWRITE] Rewriting: {question}")

    llm          = _get_llm()
    new_question = llm.invoke(prompt).content.strip()   # .content — ChatGroq

    if new_question.lower() == question.lower():
        new_question = question + " Please provide technical details."
        logger.warning("[REWRITE] Same question returned — fallback applied.")

    updated_history = previous_questions + [question]

    logger.info(f"[REWRITE] New question: {new_question}")

    return {
        "rewritten_question": new_question,
        "previous_questions": updated_history
    }