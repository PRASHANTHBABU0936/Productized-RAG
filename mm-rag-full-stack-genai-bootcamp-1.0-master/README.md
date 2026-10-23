# Multimodal RAG — Production-Grade Full-Stack Application

A multi-tenant, asynchronous, multimodal Retrieval-Augmented Generation system.
Documents are uploaded through a Streamlit UI, ingested by a Celery worker,
indexed in Qdrant with strict tenant isolation, and answered by a local LLM
using hybrid (dense + sparse) retrieval with cross-encoder reranking and
citations.

```
Streamlit UI ──HTTP──▶ FastAPI backend ──▶ PostgreSQL (metadata, auth, jobs)
                             │
                             ├──▶ Redis (Celery broker/result)
                             │        └──▶ Celery worker ──▶ Qdrant (vectors)
                             │                                   ▲
                             └──▶ retrieval ◀── Ollama (chat + vision) ┘
```

Design docs: `docs/architecture/01-system-architecture.md` …
`09-roadmap-and-trade-offs.md`. Implementation status:
`docs/IMPLEMENTATION_STATUS.md`.

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit (`ui/app.py`) |
| API | FastAPI + Uvicorn (`backend/main.py`) |
| Auth / RBAC | JWT (HS256), tenants / workspaces / memberships (`backend/auth.py`) |
| Metadata store | PostgreSQL (SQLAlchemy), default port **5433** |
| Queue | Redis + Celery 5.x (`backend/worker.py`) |
| Vector store | Qdrant (`metadata.tenant_id` filter enforced in-query) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (384-d) |
| Sparse | BM25 (`rank_bm25`), fused with dense via RRF (k=60) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| LLM | Ollama — `llama3.2:1b` (chat), `moondream` (vision captions) |
| Object storage | Local filesystem (default) or any S3-compatible store |

Python 3.11+ (developed on 3.11). Dependencies are pre-provisioned in `.venv`.

---

## Prerequisites

- PostgreSQL reachable at the `DATABASE_URL` (default
  `postgresql+psycopg://mmrag:mmrag_password@localhost:5433/mmrag`).
- Redis at `REDIS_URL` (default `redis://localhost:6379/0`).
- A Qdrant instance (`QDRANT_URL` + `QDRANT_API_KEY`).
- Ollama at `OLLAMA_BASE_URL` (default `http://localhost:11434`) with the chat
  and vision models pulled:
  `ollama pull llama3.2:1b` and `ollama pull moondream`.
- (Optional) Tesseract OCR for scanned PDFs — see Troubleshooting.

## Configuration

Copy `.env.example` to `.env` and fill in values. Key variables:

```dotenv
DATABASE_URL=postgresql+psycopg://mmrag:mmrag_password@localhost:5433/mmrag
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=<at least 32 random characters>
QDRANT_URL=<your qdrant url>
QDRANT_API_KEY=<your qdrant key>
QDRANT_COLLECTION_NAME=mm-rag-local
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.2:1b
OLLAMA_VISION_MODEL=moondream
STORAGE_BACKEND=local
STORAGE_ROOT=
MM_RAG_API_URL=http://localhost:8000
```

`JWT_SECRET_KEY` must be set to a strong value — the app refuses to start
authentication with a missing, placeholder, or short (<32 char) secret.
Never commit `.env`.

---

## Setup and run

Run each command from the repository root.

```powershell
# 1. Initialize database schema
.\.venv\Scripts\python.exe -m backend.init_db

# 2. Start the API (http://127.0.0.1:8000)
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# 3. Start the Celery worker (separate terminal; solo pool on Windows)
.\.venv\Scripts\python.exe -m celery -A backend.worker.celery_app worker `
    --loglevel=info --pool=solo --concurrency=1 `
    --without-gossip --without-mingle --without-heartbeat

# 4. Start the UI (http://127.0.0.1:8502)
.\.venv\Scripts\python.exe -m streamlit run ui/app.py `
    --server.address 127.0.0.1 --server.port 8502 --server.fileWatcherType none
```

Open the UI, register an account, upload a PDF, and watch the ingestion stages
(`uploaded → parsing → chunking → indexing → ready`) before asking questions.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The suite runs with no external services: it uses in-memory SQLite, mocks the
Celery dispatch, and stubs the LLM. Integration checks against real
PostgreSQL / Redis / Qdrant / Ollama are run manually (see
`docs/IMPLEMENTATION_STATUS.md`).

## Evaluation

```powershell
.\.venv\Scripts\python.exe -m evaluation.harness `
    --dataset evaluation/dataset.sample.jsonl `
    --tenant-id <your-tenant-uuid> `
    --json-out evaluation/report.json
```

Reports precision@k, recall@k, MRR, hit rate, groundedness, keyword hit rate,
latency and token usage.

---

## Troubleshooting

- **Ingestion fails trying to reach `http://127.0.0.1:9000/...`** — the storage
  backend is pointed at an unreachable S3/MinIO endpoint. Set
  `STORAGE_BACKEND=local` (default) in `.env`, or configure a reachable
  `S3_ENDPOINT_URL`.
- **Worker never consumes tasks / hangs at `mingle`** — on Windows use the solo
  pool and disable gossip/mingle/heartbeat (see the worker command above).
- **Ollama: `unable to allocate CPU buffer`** — not enough free RAM for the
  model. Stop idle API/UI processes before batch ingestion, or add memory.
- **Scanned PDFs return little/no text** — Tesseract is not installed
  (`image_ocr_failed` in logs). Install Tesseract and set `TESSERACT_PATH`.
- **`401` on login after a restart** — ensure only one API process is bound to
  port 8000, then retry.

## Repository layout

```text
backend/      FastAPI app, auth, models, storage, Celery worker, observability
src/          RAG pipeline: parsing, ingestion, retrieval, generation
ui/           Streamlit frontend
prompt_library/  Prompt templates
evaluation/   Offline evaluation harness, dataset, reports
docs/         Architecture design docs + IMPLEMENTATION_STATUS.md
tests/        pytest suite (SQLite, mocked Celery/LLM)
data/         Local uploads + metrics (default storage root)
```
