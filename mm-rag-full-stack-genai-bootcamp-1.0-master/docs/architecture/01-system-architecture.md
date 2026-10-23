# 01 — System Architecture

Multimodal RAG platform: production topology, runtime flows, and component responsibilities.

Related: [02 multi-tenant data model](02-multitenant-data-model.md) ·
[03 async ingestion](03-async-ingestion-workflow.md) ·
[04 hybrid retrieval](04-hybrid-retrieval-strategy.md)

---

## 1. Component topology

```
                         ┌──────────────────────────────┐
                         │        Streamlit UI          │
                         │        (ui/app.py)           │
                         │  login · upload · poll · ask │
                         └───────────────┬──────────────┘
                                         │ HTTP (JSON / multipart)
                                         ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │                    FastAPI  (backend/main.py)                     │
   │  /auth     /documents/upload   /documents/status/{job}            │
   │  /query    /workspaces*        /documents/{id}/versions           │
   │  /audit/logs   /health  /health/ready  /metrics                   │
   │                                                                   │
   │  deps: auth (JWT) · database (SQLAlchemy) · storage · observability│
   └───────┬───────────────┬──────────────────────┬────────────────────┘
           │               │                      │
   enqueue │ task          │ metadata tx          │ store bytes
           ▼               ▼                      ▼
   ┌──────────────┐  ┌───────────────┐   ┌──────────────────────────┐
   │    Redis     │  │ PostgreSQL 16 │   │  Object storage          │
   │ broker +     │  │  :5433        │   │  (backend/storage.py)    │
   │ result       │  │  tenants…     │   │  LocalStorage | S3Storage│
   │ backend      │  │  audit_logs   │   │  raw PDFs + parsed/      │
   └──────┬───────┘  └───────▲───────┘   └──────────────────────────┘
          │ consume          │ status writes
          ▼                  │
   ┌──────────────────────────┴────────────────────────────────────────┐
   │                Celery worker  (backend/worker.py)                 │
   │  ingest_document:  parsing → chunking → indexing → ready|failed   │
   │  parse (PyMuPDF/pdfplumber/OCR) · tables · image captions (Ollama)│
   │  chunk (RecursiveCharacterTextSplitter) · embed (MiniLM 384-d)    │
   └───────────────┬──────────────────────────┬────────────────────────┘
                   │ upsert (tenant-scoped)   │ caption / chat
                   ▼                          ▼
          ┌──────────────────┐        ┌───────────────────────────┐
          │      Qdrant      │        │   Ollama (local)          │
          │  dense vectors + │        │   moondream  → image      │
          │  payload metadata│        │              captions     │
          │  (tenant_id …)   │        │   llama3.2:1b → chat      │
          └──────────────────┘        └───────────────────────────┘
```

**Read path (query):** the API process performs retrieval and generation
in-process (no worker hop), because it is latency-bound and read-only:

```
POST /query → MultimodalRAGGenerator.generate()
           → MultimodalQdrantRetriever.retrieve_hybrid()
                 dense ─┐
                        ├─► RRF ─► Cross-Encoder rerank ─► top-k
                 BM25 ──┘
           → ChatOllama(llama3.2:1b) → answer + cited sources + used images
```

**Write path (ingest):** strictly asynchronous, because it is long-running
and CPU/GPU-bound:

```
POST /documents/upload → hash → persist bytes → IngestionJob row
                       → Redis enqueue (task_id pre-generated)
Worker consumes → parses/chunks/embeds/upserts → writes status back to PG
UI polls GET /documents/status/{job_id} until ready | failed
```

---

## 2. Runtime processes

| Process | Entry point | Scale model | Notes |
|---|---|---|---|
| Streamlit UI | `streamlit run ui/app.py` | 1+ (stateless) | Talks only to the API; never touches PG/Qdrant directly |
| API | `uvicorn backend.main:app` | N (stateless) | JWT-authenticated, tenant-scoped on every request |
| Worker | `celery -A backend.worker.celery_app worker` | N | `task_acks_late`, `prefetch=1`; Windows needs `-P solo` |
| Redis | container | 1 (HA via Sentinel/cluster in prod) | Broker **and** result backend |
| PostgreSQL | `postgres:16`, host port **5433** | 1 primary + replicas | System of record for tenants/docs/jobs/audit |
| Qdrant | managed cloud or self-hosted | cluster | Vector store; payload carries all isolation metadata |
| Ollama | local service `:11434` | 1 GPU host | Vision captions (`moondream`) + chat (`llama3.2:1b`) |

---

## 3. Component responsibility matrix

| Component | Owns | Must NOT do |
|---|---|---|
| `ui/app.py` | Session state, JWT storage, upload UX, status polling, chat rendering | Direct DB/Qdrant access; synchronous ingestion calls |
| `backend/main.py` | HTTP contract, authn/authz, tenant scoping, versioning decisions, job enqueue, audit + metrics writes | Heavy parsing/embedding in the request path |
| `backend/worker.py` | Pipeline state machine, parsing/chunking/embedding/upsert, status persistence | Serve HTTP; make authorization decisions |
| `src/parsing.py` | PDF → pages/tables/images/OCR artifacts | Know about tenants or storage keys |
| `src/ingestion.py` | Artifacts → chunks → vectors → Qdrant upsert; caption generation; collection schema | Own request lifecycle or job status |
| `src/retriever.py` | Tenant-filtered dense + BM25 retrieval, RRF fusion, cross-encoder rerank, evidence guarantee | Call the LLM; write to Qdrant |
| `src/generation.py` | Context assembly, prompt construction, LLM call, citation/image surfacing | Bypass the retriever's tenant filter |
| `backend/storage.py` | Bytes in/out behind a `StorageBackend` ABC (`LocalStorage`, `S3Storage`) | Interpret document semantics |
| `backend/models.py` | Relational schema + isolation invariants | Contain business logic |
| `backend/observability.py` | Request counters/latency, readiness probes, Prometheus text | Persist anything |
| `backend/audit.py` | Append-only audit writes (never raise into request path) | Block or fail user requests |

---

## 4. Deployment view

```
                       ┌────────────┐
        HTTPS ────────►│  Ingress / │  TLS termination, rate limiting,
                       │  reverse   │  request-id injection
                       │  proxy     │
                       └─────┬──────┘
                    ┌────────┴─────────┐
                    ▼                  ▼
             ┌────────────┐    ┌────────────┐
             │ API  (N)   │    │ UI   (N)   │
             └─────┬──────┘    └────────────┘
                   │
      ┌────────────┼──────────────┬──────────────┐
      ▼            ▼              ▼              ▼
  PostgreSQL     Redis        Object store     Qdrant
                       │
                       ▼
              ┌────────────────┐        ┌──────────────┐
              │ Worker (N)     │───────►│ Ollama (GPU) │
              └────────────────┘        └──────────────┘
```

Horizontal scaling: API and UI are stateless (JWT + shared PG/Redis/Qdrant),
so both scale out freely. Workers scale out with the queue depth; keep
`prefetch_multiplier=1` so a slow GPU job cannot starve other workers.

---

## 5. Configuration surface

All runtime configuration is environment-driven (see `.env.example`):

| Var | Default | Used by |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://mmrag:…@localhost:5433/mmrag` | API, worker |
| `QDRANT_URL` / `QDRANT_API_KEY` | — (required) | ingestion, retriever |
| `QDRANT_COLLECTION_NAME` | `mm-rag-documents` | ingestion, retriever |
| `HF_EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | ingestion, retriever |
| `HF_EMBEDDING_DIMENSION` | `384` | ingestion |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | captions, chat |
| `OLLAMA_VISION_MODEL` | `moondream` | captions |
| `OLLAMA_MODEL` | `llama3.2:1b` | chat |
| `STORAGE_BACKEND` | `local` | storage (`local` \| `s3`) |
| `REDIS_URL` | `redis://localhost:6379/0` | broker, readiness |
| `JWT_SECRET` | — (required in prod) | auth |
