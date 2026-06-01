# """
# Generate Node
# ─────────────
# 1. Combines retrieved documents into a single context string
# 2. Calls Llama 3 via Ollama to generate an answer
# 3. Returns the answer in state
# """
 
# from langchain_ollama import OllamaLLM
# from app.state import GraphState
# from app.prompts.templates import GENERATE_PROMPT
# from app.utils.logger import logger

# # singleton LLM

# _llm = None

# def _get_llm():
#     global _llm
#     if _llm is None:
#         logger.info("Connecting to ollama (llama3.2)...")
#         _llm = OllamaLLM(
#             model="llama3.2",
#             temperature=0.1
#         )
#     return _llm


# # node function ==============

# def generate(state: GraphState) -> dict:
#     """
#     Builds a prompt from retrieved docs and runs the LLM.
#     Returns: updated answer field.
#     """

#     question = state.get("rewritten_question") or state["question"]
#     documents = state.get("documents", [])

#     if not documents:
#         logger.warning(f"[GENERATE] No documents available. Returing fallback.")
#         return {"answer" : "I coud not find relevant information to answer your question."}
    
#     context = "\n\n---\n\n".join(documents)

#     prompt = GENERATE_PROMPT.format(
#         context=context,
#         question=question
#     )

#     logger.info(f"[GENRATE] Genrate answer for : {question}")

#     llm = _get_llm()
#     answer = llm.invoke(prompt)

#     logger.info(f"[GENERATE] Answer genrated {len(answer)} chars")

#     return {"answer": answer}

from langchain_groq import ChatGroq
from app.state import GraphState
from app.prompts.templates import GENERATE_PROMPT
from app.utils.logger import logger
import os
from dotenv import load_dotenv
load_dotenv()

_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        logger.info("Connecting to Groq (llama3-8b)...")
        _llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.environ.get("GROQ_API_KEY"),
            temperature=0.1
        )
    return _llm

def generate(state: GraphState) -> dict:
    question  = state.get("rewritten_question") or state["question"]
    documents = state.get("documents", [])

    if not documents:
        logger.warning("[GENERATE] No documents available.")
        return {"answer": "I could not find relevant information to answer your question."}

    context = "\n\n---\n\n".join(documents)
    prompt  = GENERATE_PROMPT.format(context=context, question=question)

    logger.info(f"[GENERATE] Generating answer for: {question}")

    llm    = _get_llm()
    answer = llm.invoke(prompt).content   # .content — ChatGroq response

    logger.info(f"[GENERATE] Answer generated ({len(answer)} chars)")

    return {"answer": answer}