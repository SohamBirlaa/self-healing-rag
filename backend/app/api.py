"""
FastAPI Backend — Self-Healing RAG
───────────────────────────────────
Run:    uvicorn app.api:app --reload
Docs:   http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
import chromadb
import uuid

from app.graph import graph
from app.ingestion.ingest import ingest, load_documents, SPLITTER, CHROMA_DIR
from app.utils.logger import logger
#from FlagEmbedding import FlagModel
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
load_dotenv()


# ── App initialize ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="SELF HEALING RAG API",
    description="LangGraph + Llama3.2 + BGE-M3 + ChromaDB",
    version="1.0.0"
)


# ── CORS Setup ─────────────────────────────────────────────────────────────────
# Next.js (port 3000) ko Backend (port 8000) se baat karne deta hai

app.add_middleware(
    CORSMiddleware,
    #allow_origins=["*"],        # production mein ["http://localhost:3000"] karo
    allow_origins=[
        "https://self-healing-rag.up.railway.app",
        "https://skillful-patience-production.up.railway.app",
        "*"  # development ke liye
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Embedder ────────────────────────────────────────────────────────────
# Server start hote hi ek baar load hoga — har request pe nahi
# Isse OOM (Out of Memory) error nahi aayega

print("[STARTUP] Loading BGE-M3 embedder...")
#embedder = FlagModel("BAAI/bge-m3", use_fp16=True)
hf_client = InferenceClient(token=os.environ.get("HF_TOKEN"))
print("[STARTUP] Embedder ready ")


# ── Pydantic Models ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    decision: str
    confidence: float
    retries: int
    retrieval_score: float

class IngestStatusResponse(BaseModel):
    total_chunks: int
    message: str

class DocumentsResponse(BaseModel):
    documents: list[str]
    total: int


# ── Helper ─────────────────────────────────────────────────────────────────────

def get_chroma_collection():
    """ChromaDB collection return karta hai."""
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection("documents")


# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════


# ── 1. Root ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Self-Healing RAG API",
        "docs": "http://127.0.0.1:8000/docs"
    }


# ── 2. Health Check ────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """API alive hai ya nahi check karo."""
    return {"status": "ok", "message": "Self-Healing RAG API is running"}


# ── 3. Chat ────────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    RAG pipeline run karo.
    Question bhejo → Documents retrieve → Answer generate → Critic validate
    Fail hone pe → Rewrite → Retry (max 3 baar)
    """

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question empty nahi ho sakta."
        )

    logger.info(f"[API] /chat → {request.question}")

    initial_state = {
        "question":           request.question,
        "rewritten_question": "",
        "previous_questions": [],
        "documents":          [],
        "answer":             "",
        "decision":           "",
        "retry_count":        0,
        "retrieval_score":    0.0,
        "confidence_score":   0.0
    }

    result = graph.invoke(initial_state)

    return ChatResponse(
        answer          = result.get("answer", ""),
        decision        = result.get("decision", "UNKNOWN"),
        confidence      = result.get("confidence_score", 0.0),
        retries         = result.get("retry_count", 0),
        retrieval_score = result.get("retrieval_score", 0.0)
    )


# ── 4. File Upload & Ingest ────────────────────────────────────────────────────

@app.post("/ingest/file")
async def ingest_file(file: UploadFile = File(...)):
    """
    Ek file upload karo aur ChromaDB mein index karo.
    Supported: .txt, .pdf, .docx, .md
    """

    # File name valid hai?
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file name.")

    # File type check
    ALLOWED_EXTENSIONS = {".txt", ".pdf", ".md", ".docx"}
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' allowed nahi hai. Sirf {ALLOWED_EXTENSIONS} allowed hain."
        )

    # File data/ folder mein save karo
    save_path = os.path.join("./data", file.filename)
    os.makedirs("./data", exist_ok=True)

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)   # file stream copy karo
    except Exception as e:
        logger.error(f"[API] File save failed: {str(e)}")
        raise HTTPException(status_code=500, detail="File disk pe save nahi ho saki.")
    finally:
        await file.close()      # stream hamesha close karo — memory leak rokta hai

    logger.info(f"[API] File saved: {file.filename}")

    # ChromaDB mein index karo
    try:
        collection = get_chroma_collection()

        # Load aur chunk karo
        docs   = load_documents(save_path)
        chunks = SPLITTER.split_documents(docs)

        if not chunks:
            raise HTTPException(status_code=400, detail="did not get any content from file.")

        # Embed karo — global embedder use ho raha hai (load nahi hoga dobara)
        texts      = [chunk.page_content for chunk in chunks]
        metadatas  = [
            {
                "source": file.filename,
                "page":   str(chunk.metadata.get("page", 0))
            }
            for chunk in chunks
        ]
        #embeddings = embedder.encode(texts).tolist()
        raw_embeddings = hf_client.feature_extraction(
            text=texts,
            model="BAAI/bge-m3"
        )
        if hasattr(raw_embeddings, "tolist"):
            embeddings = raw_embeddings.tolist()
        else:
            embeddings = list(raw_embeddings)
        ids        = [str(uuid.uuid4()) for _ in texts]

        # Store karo
        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        logger.info(f"[API] {len(chunks)} chunks indexed from {file.filename}")

        return {
            "message":  f"'{file.filename}' successfully indexed.",
            "chunks":   len(chunks),
            "filename": file.filename
        }

    except HTTPException:
        raise       # HTTPException ko directly re-raise karo
    except Exception as e:
        logger.error(f"[API] Ingestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


# ── 5. Folder Ingest ───────────────────────────────────────────────────────────

@app.post("/ingest/folder")
def ingest_folder():
    """data/ folder ki saari files ChromaDB mein index karo."""

    logger.info("[API] /ingest/folder called")

    try:
        ingest()
        collection   = get_chroma_collection()
        total        = collection.count()

        return {
            "message":      "Folder successfully ingested.",
            "total_chunks": total
        }

    except Exception as e:
        logger.error(f"[API] Folder ingestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 6. Ingest Status ───────────────────────────────────────────────────────────

@app.get("/ingest/status", response_model=IngestStatusResponse)
def ingest_status():
    """ChromaDB mein total indexed chunks count karo."""

    collection   = get_chroma_collection()
    total_chunks = collection.count()

    return IngestStatusResponse(
        total_chunks = total_chunks,
        message      = f"{total_chunks} chunks indexed at ChromaDB."
    )


# ── 7. Indexed Documents List ─────────────────────────────────────────────────

@app.get("/ingest/documents", response_model=DocumentsResponse)
def list_documents():
    """Saare indexed document names return karo."""

    collection = get_chroma_collection()
    results    = collection.get(include=["metadatas"])

    # Unique file names nikalo
    sources = set()
    for metadata in results.get("metadatas", []):
        if metadata and "source" in metadata:
            sources.add(metadata["source"])

    source_list = sorted(list(sources))

    return DocumentsResponse(
        documents = source_list,
        total     = len(source_list)
    )


# ── 8. Clear ChromaDB ─────────────────────────────────────────────────────────

@app.delete("/ingest/clear")
def clear_documents():
    """
    ChromaDB se saare documents delete karo.
    Yeh action reversible nahi hai!
    """

    logger.warning("[API] /ingest/clear called — deleting all documents")

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    client.delete_collection("documents")
    client.get_or_create_collection("documents")

    return {"message": "All documents are deleted. chromadb is empty"}