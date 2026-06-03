# """
# Retrieve Node
# ─────────────
# 1. Embeds the current question using BGE-M3
# 2. Queries ChromaDB for the top-k most similar chunks
# 3. Reranks results using a cross-encoder
# 4. Stores documents + retrieval_score in state
# """
 
# import chromadb
# from FlagEmbedding import FlagModel
# from sentence_transformers import CrossEncoder
# from app.state import GraphState
# from app.utils.logger import logger
 
 
# # ── Lazy-loaded singletons (loaded once, reused across calls) ─────────────────
# _embedder = None
# _reranker = None
# _collection = None

# def _get_embedder():
#     global _embedder
#     if _embedder is None:
#         logger.info("Loading BGG -M3 embedder...")
#         _embedder = FlagModel(
#             "BAAI/bge-m3",
#             use_fp16=True
#         )
#     return _embedder

# def _get_reranker():
#     global _reranker
#     if _reranker is None:
#         logger.info("Loading BGE reranker...")
#         _reranker = CrossEncoder("BAAI/bge-reranker-base")
#     return _reranker

# def _get_collection():
#     # ✅ Fix — cache mat karo, har baar fresh lo
#     client = chromadb.PersistentClient(path="./chroma_db")
#     return client.get_or_create_collection("documents")

# # node function===================

# def retrieve(state: GraphState) -> dict:
#     """
#     Uses rewritten_question if available, otherwise falls back to question.
#     Returns updated documents and retrieval_score.
#     """

#     query = state.get("rewritten_question") or state["question"]
#     logger.info(f"[RETRIEVE] Query: {query}")

#     embedder = _get_embedder()
#     reranker = _get_reranker()
#     colllection = _get_collection()

#     # 1. embed query
#     query_embedding = embedder.encode([query])[0].tolist()

#     # 2. query chromadb - fetch top 10 candidates
#     results = colllection.query(
#         query_embeddings=[query_embedding],
#         n_results=min(10, colllection.count() or 1)
#     )

#     raw_docs = results["documents"][0]
#     distances = results["distances"][0]

#     if not raw_docs:
#         logger.warning("[RETRIEVE] No documents found in ChromaDB")
#         return{
#             "documents": [],
#             "retrieval": 0.0
#         }
    
#     # 3. Rerank - cross-encoder scores each (quesry, docs) pair
#     pairs = [[query, doc] for doc in raw_docs]
#     rerank_scores = reranker.predict(pairs).tolist()

#     # 4. sort by reranker score descending , keep top 5
#     ranked = sorted(
#         zip(raw_docs, rerank_scores),
#         key=lambda x: x[1],
#         reverse=True
#     )[:5]

#     top_docs = [doc for doc, _ in ranked]
#     top_scores = [score for _, score in ranked]

#     # normalise retrieval score to 0-1 range (sigmoid like)
#     import math
#     avg_raw = sum(top_scores) / len(top_scores)
#     retrieval_score = round(1 / (1 + math.exp(-avg_raw)), 4)

#     logger.info(f"[RETRIEVE] {len(top_docs)} docs retrieved. score: {retrieval_score}")
    
#     return {
#         "documents": top_docs,
#         "retrieval_score": retrieval_score
#     }


import os
import math
import chromadb
from sentence_transformers import CrossEncoder
from huggingface_hub import InferenceClient
from app.state import GraphState
from app.utils.logger import logger
from dotenv import load_dotenv
load_dotenv()


# ── Singletons ─────────────────────────────────────────────────────────────────

_reranker  = None
_hf_client = None


def _get_hf_client():
    global _hf_client
    if _hf_client is None:
        logger.info("Connecting to HuggingFace Inference API...")
        _hf_client = InferenceClient(
            token=os.environ.get("HF_TOKEN")
        )
    return _hf_client


def _get_reranker():
    global _reranker
    if _reranker is None:
        logger.info("Loading BGE reranker...")
        _reranker = CrossEncoder("BAAI/bge-reranker-base")
    return _reranker


def _get_collection():
    client = chromadb.PersistentClient(path="./chroma_db")
    return client.get_or_create_collection("documents")


# ── Node function ──────────────────────────────────────────────────────────────

def retrieve(state: GraphState) -> dict:
    query = state.get("rewritten_question") or state["question"]
    logger.info(f"[RETRIEVE] Query: {query}")

    hf_client  = _get_hf_client()
    reranker   = _get_reranker()
    collection = _get_collection()

    # 1. HuggingFace API se embedding lo
    embedding = hf_client.feature_extraction(
        text=query,
        model="BAAI/bge-m3"
    )

    # List mein convert karo
    if hasattr(embedding, "tolist"):
        query_embedding = embedding.tolist()
    else:
        query_embedding = list(embedding)

    # Flatten karo agar nested list hai
    if isinstance(query_embedding[0], list):
        query_embedding = query_embedding[0]

    # 2. ChromaDB query
    count = collection.count()
    if count == 0:
        logger.warning("[RETRIEVE] ChromaDB empty.")
        return {"documents": [], "retrieval_score": 0.0}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(10, count)
    )

    raw_docs  = results["documents"][0]
    distances = results["distances"][0]

    if not raw_docs:
        return {"documents": [], "retrieval_score": 0.0}

    # 3. Rerank
    pairs         = [[query, doc] for doc in raw_docs]
    rerank_scores = reranker.predict(pairs).tolist()

    ranked = sorted(
        zip(raw_docs, rerank_scores),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    top_docs   = [doc for doc, _ in ranked]
    top_scores = [score for _, score in ranked]

    avg_raw          = sum(top_scores) / len(top_scores)
    retrieval_score  = round(1 / (1 + math.exp(-avg_raw)), 4)

    logger.info(f"[RETRIEVE] {len(top_docs)} docs. Score: {retrieval_score}")

    return {
        "documents":       top_docs,
        "retrieval_score": retrieval_score
    }