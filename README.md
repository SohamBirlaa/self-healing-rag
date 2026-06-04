# 🧠 Self-Healing RAG System

A production-grade, fully local Retrieval-Augmented Generation (RAG) system with autonomous self-healing capabilities. Built with LangGraph, Groq, BGE-M3, ChromaDB, FastAPI, and Next.js.

---

## 🚀 Live Demo

| Service | URL |
|---|---|
| **Frontend** | https://self-healing-rag.up.railway.app |
| **Backend API** | https://self-healing-rag-production-c85a.up.railway.app/docs |

---

## 🏗️ Architecture

```
User Question
      │
      ▼
  RETRIEVE          ← BGE-M3 embeddings + ChromaDB
      │
      ▼
  GENERATE          ← Groq (Llama 3.1)
      │
      ▼
   CRITIC           ← Hallucination detection + Confidence scoring
      │
   ┌──┴──────────┐
  PASS           FAIL
   │               │
  END           REWRITE      ← Query rewriting (loop prevention)
                  │
            increment_retry
                  │
              RETRIEVE       ← Retry loop (max 3)
```

### Self-Healing Flow
1. **Retrieve** — Embeds query using BGE-M3 via HuggingFace API, queries ChromaDB
> **Note:** Cross-encoder reranking (BGE Reranker Base) was implemented locally 
> for improved retrieval quality but removed in production due to Railway free 
> tier memory constraints (512MB). Distance-based scoring is used in production.
2. **Generate** — Llama 3.1 generates answer from retrieved context
3. **Critic** — Evaluates answer for groundedness and hallucination (0.0–1.0 confidence)
4. **Self-Heal** — If critic fails, rewrites query and retries (up to 3 times)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Groq API (Llama 3.1 8B Instant) |
| **Embeddings** | BGE-M3 via HuggingFace Inference API |
| **Vector DB** | ChromaDB (persistent) |
| **Orchestration** | LangGraph (cyclic state machine) |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | Next.js 16 + Tailwind CSS |
| **Deployment** | Railway (Docker) |
| **CI/CD** | GitHub Actions |
| **Testing** | Pytest (backend) + Jest (frontend) |
| **Reranker** | BGE Reranker Base (local dev) / Removed in production (memory constraints) |
---

## 📁 Project Structure

```
self-healing-rag/
│
├── backend/
│   ├── app/
│   │   ├── nodes/
│   │   │   ├── retrieve.py      # BGE-M3 embedding + ChromaDB
│   │   │   ├── generate.py      # Groq LLM answer generation
│   │   │   ├── critic.py        # Hallucination detection
│   │   │   └── rewrite.py       # Query rewriting + loop prevention
│   │   ├── utils/
│   │   │   └── logger.py        # Logging to file + console
│   │   ├── prompts/
│   │   │   └── templates.py     # All LLM prompts
│   │   ├── ingestion/
│   │   │   └── ingest.py        # Document ingestion pipeline
│   │   ├── evaluation/
│   │   │   ├── metrics.py       # Evaluation metrics
│   │   │   └── benchmark.py     # Batch evaluation runner
│   │   ├── graph.py             # LangGraph state machine
│   │   ├── state.py             # GraphState TypedDict
│   │   ├── api.py               # FastAPI REST API
│   │   └── main.py              # CLI entry point
│   ├── tests/
│   │   ├── test_retrieve.py
│   │   ├── test_generate.py
│   │   ├── test_critic.py
│   │   ├── test_rewrite.py
│   │   └── test_graph.py
│   ├── data/                    # Upload documents here
│   ├── chroma_db/               # Vector DB storage
│   ├── logs/                    # Runtime logs
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── chat/
│   │   │   └── page.tsx         # Chat interface
│   │   ├── upload/
│   │   │   └── page.tsx         # Document upload page
│   │   ├── status/
│   │   │   └── page.tsx         # DB status page
│   │   ├── components/
│   │   │   ├── ChatBox.tsx      # Main chat component
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── MetricsPanel.tsx # Pipeline metrics display
│   │   │   └── FileUpload.tsx
│   │   ├── layout.tsx           # Navbar + layout
│   │   └── page.tsx             # Landing page
│   ├── lib/
│   │   └── api.ts               # Backend API calls
│   ├── __tests__/
│   │   ├── MessageBubble.test.tsx
│   │   ├── MetricsPanel.test.tsx
│   │   ├── FileUpload.test.tsx
│   │   └── api.test.ts
│   ├── Dockerfile
│   └── package.json
│
├── .github/
│   └── workflows/
│       └── ci.yml               # CI/CD pipeline
├── docker-compose.yml
└── README.md
```

---

## ⚙️ API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Run RAG pipeline |
| `POST` | `/ingest/file` | Upload & index a file |
| `POST` | `/ingest/folder` | Ingest all files from data/ |
| `GET` | `/ingest/status` | Get total chunk count |
| `GET` | `/ingest/documents` | List indexed documents |
| `DELETE` | `/ingest/clear` | Clear ChromaDB |

---

## 🏃 Local Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (optional)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_key" > .env
echo "HF_TOKEN=your_hf_token" >> .env

# Run API
uvicorn app.api:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > .env.local

# Run dev server
npm run dev
```

### Docker (Both services)

```bash
# Create root .env
echo "GROQ_API_KEY=your_groq_key" > .env
echo "HF_TOKEN=your_hf_token" >> .env

# Build and run
docker-compose up --build
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
# 19 tests — retrieve, generate, critic, rewrite, graph
```

### Frontend Tests
```bash
cd frontend
npm test
# 20 tests — components + API functions
```

---

## 📊 Pipeline Metrics

Each chat response includes real-time metrics:

| Metric | Description |
|---|---|
| **Decision** | `PASS` or `FAIL` — critic's verdict |
| **Confidence** | 0–100% — how grounded the answer is |
| **Retries** | Number of self-healing retry attempts |
| **Retrieval Score** | Quality of retrieved documents |

---

## 🔑 Environment Variables

### Backend
```
GROQ_API_KEY    # Groq API key (free at console.groq.com)
HF_TOKEN        # HuggingFace token (free at huggingface.co)
```

### Frontend
```
NEXT_PUBLIC_API_URL    # Backend URL
```

---

## 📝 Resume Bullet

> Built and deployed a production-grade self-healing RAG system using LangGraph, Groq (Llama 3.1), BGE-M3, and ChromaDB with adaptive query rewriting, hallucination detection, confidence-based retry orchestration, REST API via FastAPI, full-stack UI with Next.js, CI/CD via GitHub Actions, and Docker-based deployment on Railway.

---

## 🗺️ Future Improvements

- [ ] Hybrid retrieval (Dense + BM25)
- [ ] LangSmith observability
- [ ] Persistent ChromaDB on cloud storage
- [ ] Streaming responses
- [ ] Multi-document comparison