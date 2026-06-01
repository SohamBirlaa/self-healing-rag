# """
# Document Ingestion
# ──────────────────
# Loads .txt, .pdf, or .md files from the /data folder,
# splits them into chunks, embeds with BGE-M3, and stores in ChromaDB.
 
# Usage:
#     python -m app.ingestion.ingest
# """

# import os
# import uuid
# import chromadb
# from FlagEmbedding import FlagModel
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import(
#     TextLoader,
#     PyPDFLoader,
#     Docx2txtLoader,
# )
# from app.utils.logger import logger

# #config=========

# CHUNK_SIZE = 512
# CHUNK_OVERLAP = 64
# DATA_DIR = "./data"
# CHROMA_DIR = "./chroma_db"

# SPLITTER = RecursiveCharacterTextSplitter(
#     chunk_size=CHUNK_SIZE,
#     chunk_overlap=CHUNK_OVERLAP,
#     separators=["\n\n", "\n", " ", ""]
# )

# #file loader======================

# def load_documents(filepath: str):
#     """
#     Load a file using the appropriate LangChain loader.
#     Returns a list of LangChain Document objects.
#     """

#     ext = os.path.splitext(filepath)[1].lower()

#     if ext ==".pdf":
#         loader = PyPDFLoader(filepath)

#     elif ext in (".txt", ".md"):
#         loader = TextLoader(filepath, encoding="utf-8")

#     elif ext == ".docx":
#         loader = Docx2txtLoader(filepath)

#     else:
#         logger.warning(f"[INGEST] Unsupported file type: {ext} - skipping {filepath}")
#         return []
    
#     return loader.load()


# # main ingestion function=========

# def ingest():
#     logger.info(f"[INGEST] Starting ingestion")

#     # load BGE M3 embedder
#     logger.info(f"[INGEST] loading BGE-M3 embedder")
#     embedder = FlagModel("BAAI/bge-m3", use_fp16=True)

#     #connect to chromadb
#     client = chromadb.PersistentClient(path=CHROMA_DIR)
#     collection = client.get_or_create_collection("documents")

#     #scan data/ folder
#     files = [
#         f for f in os.listdir(DATA_DIR)
#         if os.path.isfile(os.path.join(DATA_DIR, f))
#     ]

#     if not files:
#         logger.warning(f"[INGEST] No files found in {DATA_DIR}/ - add some documentsfirst")
#         print(f"\n No files found in {DATA_DIR}/\n")
#         return
    
#     total_chunks = 0

#     for filename in files:
#         filepath = os.path.join(DATA_DIR, filename)
#         logger.info(f"[INGEST] loading: {filename}")

#         # 1. loading file --> langchain documents
#         docs = load_documents(filepath)
#         if not docs:
#             continue

#         # 2. split into chunks (respects word/sentence boundaries)
#         chunks = SPLITTER.split_documents(docs)

#         if not chunks:
#             logger.warning(f"[INGEST] No chunks produced from {filename}")
#             continue

#         logger.info(f"[INGEST] {len(chunks)} chunks from {filename}")

#         # 3. extract text and metadata from each chunk

#         texts = [chunk.page_content for chunk in chunks]
#         metadatas = [
#             {
#                 "source":filename,
#                 "page": str(chunk.metadata.get("page", 0))
#             }
#             for chunk in chunks
#         ]

#         # 4. Embed all chunks in one batch
#         embeddings = embedder.encode(texts).tolist()

#         # 5. store in chromadb
#         ids = [str(uuid.uuid4()) for _ in texts]

#         collection.add(
#             ids=ids,
#             documents=texts,
#             embeddings=embeddings,
#             metadatas=metadatas
#         )

#         total_chunks += len(texts)
#         print(f"{filename} -> {len(texts)} chunks indexed")

#     logger.info(f"[INGEST] Done. {total_chunks} total chunks stored.")
#     print(f"\n Ingestion complete — {total_chunks} chunks stored in ChromaDB.\n")
 
 
# if __name__ == "__main__":
#     ingest()

"""
Document Ingestion
──────────────────
Loads .txt, .pdf, or .md files from the /data folder,
splits them into chunks, embeds with HuggingFace API (BGE-M3), and stores in ChromaDB.

Usage:
    python -m app.ingestion.ingest
"""

import os
import uuid
import chromadb
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
)
from app.utils.logger import logger

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────

CHUNK_SIZE    = 512
CHUNK_OVERLAP = 64
DATA_DIR      = "./data"
CHROMA_DIR    = "./chroma_db"

SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", " ", ""]
)

# ── File Loader ────────────────────────────────────────────────────────────────

def load_documents(filepath: str):
    """
    Load a file using the appropriate LangChain loader.
    Returns a list of LangChain Document objects.
    """

    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(filepath)

    elif ext in (".txt", ".md"):
        loader = TextLoader(filepath, encoding="utf-8")

    elif ext == ".docx":
        loader = Docx2txtLoader(filepath)

    else:
        logger.warning(f"[INGEST] Unsupported file type: {ext} — skipping {filepath}")
        return []

    return loader.load()


# ── Main Ingestion Function ────────────────────────────────────────────────────

def ingest():
    logger.info("[INGEST] Starting ingestion...")

    # HuggingFace API client — BGE-M3 embeddings
    logger.info("[INGEST] Connecting to HuggingFace API (BGE-M3)...")
    hf_client = InferenceClient(token=os.environ.get("HF_TOKEN"))

    # Connect to ChromaDB
    client     = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection("documents")

    # Scan data/ folder
    files = [
        f for f in os.listdir(DATA_DIR)
        if os.path.isfile(os.path.join(DATA_DIR, f))
    ]

    if not files:
        logger.warning(f"[INGEST] No files found in {DATA_DIR}/")
        print(f"\n  No files found in {DATA_DIR}/\n")
        return

    total_chunks = 0

    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        logger.info(f"[INGEST] Loading: {filename}")

        # 1. Load file → LangChain Documents
        docs = load_documents(filepath)
        if not docs:
            continue

        # 2. Split into chunks
        chunks = SPLITTER.split_documents(docs)

        if not chunks:
            logger.warning(f"[INGEST] No chunks from {filename}")
            continue

        logger.info(f"[INGEST] {len(chunks)} chunks from {filename}")

        # 3. Extract text and metadata
        texts     = [chunk.page_content for chunk in chunks]
        metadatas = [
            {
                "source": filename,
                "page":   str(chunk.metadata.get("page", 0))
            }
            for chunk in chunks
        ]

        # 4. Embed using HuggingFace API (BGE-M3)
        # Batch embedding — ek baar mein sab chunks
        raw_embeddings = hf_client.feature_extraction(
            text=texts,
            model="BAAI/bge-m3"
        )

        # Numpy array → list convert karo
        if hasattr(raw_embeddings, "tolist"):
            embeddings = raw_embeddings.tolist()
        else:
            embeddings = list(raw_embeddings)

        # 5. Store in ChromaDB
        ids = [str(uuid.uuid4()) for _ in texts]

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        total_chunks += len(texts)
        print(f" {filename} → {len(texts)} chunks indexed")

    logger.info(f"[INGEST] Done. {total_chunks} total chunks stored.")
    print(f"\n Ingestion complete — {total_chunks} chunks stored in ChromaDB.\n")


if __name__ == "__main__":
    ingest()