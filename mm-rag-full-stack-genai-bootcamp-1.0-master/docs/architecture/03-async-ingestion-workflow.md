# 03 — Async Ingestion Workflow & State Machine

Why ingestion is asynchronous, how a job's state advances, and how the
system avoids the "loading forever" failure mode.

Related: [01 architecture](01-system-architecture.md) ·
[07 versioning](07-versioning-and-incremental-ingestion.md) ·
[08 observability](08-evaluation-and-observability.md)

---

## 1. Why asynchronous

Parsing a PDF, running OCR, calling a vision model for every image and
computing embeddings is seconds-to-minutes of CPU/GPU work. Doing it
inside the upload request would:

- hold an HTTP connection open and time out behind a proxy,
- block a Streamlit script run so the UI cannot repaint,
- make retries duplicate work,
- couple API availability to model availability.

The upload endpoint therefore does only cheap, synchronous work
(hash → persist bytes → write metadata → enqueue) and returns
immediately with a `job_id`.

---

## 2. Sequence

```
UI                API                     Redis             Worker              PG        Qdrant
│                  │                        │                 │                 │           │
│ POST /documents/upload (multipart)        │                 │                 │           │
├─────────────────►│                        │                 │                 │           │
│                  │ sha256(contents)       │                 │                 │           │
│                  │ storage.save_bytes()   │                 │                 │           │
│                  │ INSERT document/version/job ─────────────────────────────► │           │
│                  │ commit  ◄──────────────────────────────────────────────── │           │
│                  │ apply_async(task_id)   │                 │                 │           │
│                  ├───────────────────────►│                 │                 │           │
│ 200 {job_id, document_id, version_number} │                 │                 │           │
│◄─────────────────┤                        │                 │                 │           │
│                  │                        │  consume task   │                 │           │
│                  │                        ├────────────────►│                 │           │
│                  │                        │                 │ parsing         │           │
│                  │                        │                 ├────────────────►│           │
│ GET /documents/status/{job_id}  (poll)    │                 │ chunking        │           │
├─────────────────►│                        │                 ├────────────────►│           │
│                  │ AsyncResult.status     │                 │ indexing        │           │
│                  │ sync job/document      │                 │ ├── embed ──────┼──────────►│
│◄─────────────────┤ {status: "indexing"}   │                 │ │   upsert ─────┼──────────►│
│ ... poll ...     │                        │                 │ ready           │           │
│◄─────────────────┤ {status: "ready"}      │                 ├────────────────►│           │
```

---

## 3. State machine

```
            ┌──────────┐
     upload │ uploaded │
            └────┬─────┘
                 │ worker picks up the task
                 ▼
            ┌──────────┐
            │ parsing  │  PyMuPDF / pdfplumber / OCR / table extraction
            └────┬─────┘
                 ▼
            ┌──────────┐
            │ chunking │  split + image captioning + metadata assembly
            └────┬─────┘
                 ▼
            ┌──────────┐
            │ indexing │  embed (MiniLM 384-d) + Qdrant upsert
            └────┬─────┘
                 ▼
            ┌──────────┐
            │  ready   │  terminal ✓
            └──────────┘

     any stage ──► ┌──────────┐
                   │  failed  │  terminal ✗  (error message persisted)
                   └──────────┘
```

Intermediate stages are written by the **worker** through
`set_stage(stage, error=None)`, which updates the `ingestion_jobs` row,
the `documents` row **and** the current `document_versions` row in one
commit. The UI therefore sees real progress, not a single blocking call.

`parsing` is set by the worker before it starts, and `chunking` /
`indexing` arrive through `progress_callback` from
`MultimodalDocumentIngestion`.

---

## 4. Status resolution (API side)

`GET /documents/status/{job_id}` merges persisted state with the Celery
result, because Celery's `PENDING` is ambiguous — it means both "queued,
not started" and "unknown task id".

```
celery_status = AsyncResult(job.celery_task_id).status

SUCCESS   → job.status = ready
FAILURE   → job.status = failed,  job.error = str(result)
STARTED   → keep whatever stage the worker wrote (parsing/chunking/indexing)
other*    → still queued?
              age = now − job.created_at
              age > STALE_JOB_SECONDS (300s)
                    → failed  ("No Celery worker picked up this job …")
              else  → queued
```

This staleness guard is what stops the UI from polling forever when no
worker is running (a real failure mode observed in development).

The endpoint is tenant-authorised: it loads the job's document and
returns `403` if `document.tenant_id != current_user.tenant_id`.

---

## 5. Delivery guarantees

| Concern | Mechanism |
|---|---|
| At-least-once delivery | `task_acks_late=True` — the task is acked only after it finishes |
| No head-of-line blocking | `worker_prefetch_multiplier=1` — one job per worker slot |
| Progress visibility | `task_track_started=True` |
| Result retention | `result_expires = 24h` |
| Idempotent re-index | deterministic point IDs; `replace_existing` deletes only the same `tenant_id + document_id` |
| Broker restart safety | `broker_connection_retry_on_startup=True` |
| PG-before-Redis ordering | the job row is committed **before** `apply_async`, so the worker can always find it |

Because tasks are at-least-once, `ingest_document` must be safe to run
twice for the same `document_id`: it is, since upserts are keyed by
deterministic point IDs and the delete is scoped to
`tenant_id + document_id`.

---

## 6. Failure handling

| Failure | Detection | Outcome |
|---|---|---|
| Model/parse error | exception inside the task | `except` → `db.rollback()` → `set_stage("failed", str(exc))` → re-raise |
| Worker never starts | staleness guard in the status endpoint | `failed` after 300 s |
| API dies after enqueue | job row already committed | worker still completes; UI resumes polling |
| Duplicate upload of identical bytes | `current_version.file_hash == sha256` and `status == ready` | short-circuit, no new version, redundant upload deleted |
| Unsupported / oversized file | request validation | `400` / `413`, nothing enqueued |

The worker cleans its scratch directory in a `finally` block, so failed
runs do not leak temporary files.

---

## 7. Operational commands

```powershell
# API
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Worker  (Windows requires the solo pool)
python -m celery -A backend.worker.celery_app worker -P solo -l info

# Schema
python -m backend.init_db
```

Readiness (database, redis, qdrant required; ollama optional):

```
GET /health/ready   → 200 {"status":"ready", "checks":{...}}
                    → 503 {"status":"degraded", ...}
```
