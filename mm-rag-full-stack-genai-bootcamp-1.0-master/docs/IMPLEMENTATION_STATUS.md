# Implementation Status

Productionizing the Multimodal RAG application. This is the single
implementation checklist; it is updated as features are implemented and
verified. Status values: **PASS**, **PARTIAL**, **BLOCKED**, **FAIL**,
**NOT REQUIRED**.

Last updated: 2026-10-22

---

## 1. Verification evidence (real runs)

| Check | Command / artefact | Result |
|---|---|---|
| Unit + integration suite | `python -m pytest -q` | **75 passed** (62 prior + 13 new OCR tests), 2 benign warnings, 39.41s |
| Live health | `GET /health` | `{"status":"healthy"}` |
| Live readiness | `GET /health/ready` | database/redis/qdrant/ollama all `up` |
| Live ingestion (real pipeline) | eager `mm_rag.ingest_document` task | parsed 1 page, **4 chunks indexed**, DB → `ready` |
| Live hybrid retrieval (own tenant) | `docs_retrieved_with_scores` | dense=4, sparse=4, RRF fused=4, reranked 4 |
| Live tenant isolation | same query, foreign `tenant_id` | `result_count=0` |
| Live grounded answer | `llama3.2:1b` + citations | grounded summary + 4 `PSNB_MIAMIN.pdf` citations |
| Live image ingestion | `Client_Contracts...pdf` | 13 images detected, **13/13 captioned** by `moondream`, indexed as `content_type=image` |
| Live table ingestion | `Client_Contracts...pdf` | **16 tables** extracted and indexed as `content_type=table` (Markdown) |
| Live multimodal retrieval | Qdrant payload distribution | `page_text_plus_ocr`=27, `table`=16, `image`=13 (56 points) |
| Live table query | `similarity_search("table of performance metrics...")` | top-5 = **5× `table`** |
| Live image query | `similarity_search("diagram of the neural network architecture")` | top-5 = image, table, image, image, text |
| Offline eval harness | `evaluation/report.after2.json` | precision 0.972, recall 1.0, MRR 1.0, hit 1.0, groundedness 0.826, errors 0 |
| Live EasyOCR fallback (scanned/image path) | sample PNG, Tesseract absent | Tesseract → 0 chars (`image_ocr_failed`); EasyOCR → 43 chars, `ocr_easyocr_fallback_used`; reader reused (`gpu=False`) |

Test layers: `tests/` uses in-memory SQLite + mocked Celery dispatch + stubbed
LLM (**mocked**); the live rows above ran against real PostgreSQL, Redis,
Qdrant and Ollama (**integration**).

---

## 2. Requirements A–I

| # | Requirement | Status | Evidence / notes |
|---|---|---|---|
| A | Backend / service separation | **PASS** | `backend/` (FastAPI API, models, auth, storage, worker, observability) is independent of `ui/` (Streamlit) and `src/` (pipeline). UI talks to the API over HTTP (`MM_RAG_API_URL`). See `docs/architecture/01-system-architecture.md`. |
| B | Async ingestion (Celery + Redis) | **PASS** | `backend/worker.py` `mm_rag.ingest_document`; state machine `uploaded → parsing → chunking → indexing → ready\|failed` (+`retrying`). Verified live (task received + full run) and in `tests/test_api.py`. |
| C | Multi-tenant auth / RBAC, filters inside retrieval | **PASS** | JWT (`backend/auth.py`) rejects missing/placeholder/<32-char secrets; tenant filter is mandatory in `src/retriever.py::build_filter` (`metadata.tenant_id`). RBAC `PERMISSION_LEVELS={read:1,write:2,admin:3}`. Isolation proven live (`result_count=0` for a foreign tenant) and in `tests/test_retrieval.py`, `tests/test_workspaces.py`. |
| D | Hybrid retrieval (dense + sparse RRF) + rerank + citations | **PASS** | Dense `all-MiniLM-L6-v2` + BM25 fused by RRF (k=60), then cross-encoder `ms-marco-MiniLM-L-6-v2`. Answers return `sources` with `filename`/`content_type`/`score`. Verified live and via `evaluation/report.after2.json`. |
| E | Multimodal image retrieval | **PASS** | `src/ingestion.py` captions every extracted image with Ollama `moondream` and embeds the caption with MiniLM (`_enrich_image_document`). Verified live on `Client_Contracts...pdf`: 13/13 images captioned (`image_searchable=True`), and a natural-language diagram query retrieves `image` chunks. No OCR dependency for retrieval. |
| F | Table intelligence | **PASS** | `src/parsing.py::extract_tables` + `create_langchain_documents` index each table as structured Markdown (`content_type=table`, with `table_index`/`row_count`/`column_count`/`headers`). Verified live: 16 tables extracted and indexed; the table-targeted query returned 5/5 `table` chunks. |
| G | Versioning / incremental ingestion | **PASS** | Logical `Document` vs `DocumentVersion`; `file_sha256` dedup + supersede on re-upload; unchanged+ready → `duplicate=True`. `tests/test_versioning.py` (5 tests) + `tests/test_storage.py`. |
| H | Evaluation + observability | **PASS** | `evaluation/harness.py` (precision/recall/MRR/hit/groundedness/keyword/latency/tokens, `--json-out`); `GET /metrics` (json + Prometheus); `GET /health`, `/health/ready`; audit log `GET /audit/logs` (owner/admin). |
| I | Product capabilities | **PASS** | Multi-workspace tenancy, per-user JWT auth, permission grants, document version history, upload status polling, grounded Q&A — all in `backend/main.py` and `ui/app.py`. |

---

## 3. Nine-phase roadmap

Detailed in `docs/architecture/09-roadmap-and-trade-offs.md`. Progress:

| Phase | Scope | Status |
|---|---|---|
| 1 | V1 RAG pipeline (parse → embed → Qdrant → answer) | **PASS** |
| 2 | Multi-document ingestion + auth | **PASS** |
| 3 | Async ingestion / storage abstraction / PostgreSQL | **PASS** |
| 4 | Tenants / workspaces / RBAC | **PASS** |
| 5 | Hybrid retrieval (RRF + reranking) | **PASS** |
| 6 | Improved multimodal (image captions, table Markdown) | **PASS** |
| 7 | Evaluation + observability | **PASS** |
| 8 | Production API / frontend hardening | **PASS** (rate-limiting/tracing to add) |
| 9 | Enterprise integrations & billing | **NOT REQUIRED** (out of scope per brief) |

---

## 4. Known limitations / deferred

- **Tesseract OCR not installed → covered by the EasyOCR fallback.**
  `_run_tesseract_ocr` now returns `""` and logs `image_ocr_failed` instead of
  aborting; the cached, CPU-only EasyOCR reader then recovers the text
  (`ocr_easyocr_fallback_used`). `winget` is unavailable on this host, so a
  Tesseract system install was not possible; install Tesseract and set
  `TESSERACT_PATH` to make Tesseract the working *primary* engine (EasyOCR then
  only runs when Tesseract yields fewer than `OCR_FALLBACK_MIN_CHARS`=8 chars).
- **Ollama memory ceiling.** Under concurrent load (`llama3.2:1b` +
  `moondream` + embedding models) the local Ollama server can fail to allocate
  CPU buffers (`unable to allocate CPU buffer`). Mitigation: stop idle
  Streamlit/API processes before batch runs, or raise available RAM. During the
  multimodal verification, 1 of 2 caption attempts on the large paper PDF
  failed for this reason but the document was preserved and the run continued.
- **Legacy points.** Pre-tenant Qdrant points are handled by
  `backend/migrate_legacy_points.py`; not run here to avoid touching existing data.
- **`keyword_hit_rate` 0.5** in the sample evaluation reflects strict
  substring matching on a tiny 6-case dataset, not a retrieval defect.

---

## 5. Root cause fixed: storage blocker

Ingestion previously failed trying to reach `http://127.0.0.1:9000/mm-rag-documents`
(an unreachable MinIO/S3 endpoint). Root cause: `.env` was configured with
`STORAGE_BACKEND=s3` and a dead `S3_ENDPOINT_URL`. Fix: use the supported,
already-implemented local backend — `STORAGE_BACKEND=local` (S3 block left
commented in `.env`, never printed). No MinIO installed, no Qdrant replaced,
no data deleted.

---

## 6. EasyOCR fallback integration

EasyOCR was added as an **alternative to** Tesseract, keeping Tesseract as the
primary engine. Only `src/parsing.py`, `tests/test_ocr.py` (new) and
`.env.example` changed; the PDF parser, table extraction, image captioning,
chunking, embeddings, Qdrant indexing, Celery ingestion, citations and
multi-tenant security are untouched.

### Installation

```
python -m pip install easyocr          # resolved to easyocr 1.7.2
```

- Python 3.11.15; `easyocr 1.7.2`.
- Pulled in `torchvision 0.29.1+cpu` (EasyOCR requires `torchvision>=0.5`);
  **torch stayed `2.14.1+cpu`** (no reinstall/upgrade), `numpy 2.4.6` unchanged.
- CPU-only inference (`gpu=False`); models (`craft` detector + `english_g2`
  recognizer, ~100 MB) download once on first use and are cached under
  `~/.EasyOCR/model`.

### Behaviour

| Item | Value |
|---|---|
| `get_easyocr_reader()` | process-wide lazy singleton behind a `threading.Lock`; built **once per worker process**, `gpu=False` |
| `easyocr_extract_text(path)` | `reader.readtext(detail=0, paragraph=True)`; returns `""` on any failure — never raises |
| `run_ocr_on_image(path)` | Tesseract first; EasyOCR fallback when Tesseract `< OCR_FALLBACK_MIN_CHARS` (8) |
| Page-level OCR gating | full-page OCR runs **only** when selectable text `< PAGE_TEXT_MIN_CHARS` (40) — i.e. scanned pages |
| Env flags | `EASYOCR_ENABLED` (default `true`), `EASYOCR_LANGUAGES` (default `en`) |

Graceful failure: a missing Tesseract binary is logged (`image_ocr_failed`) and
tolerated; a missing/disabled/failing EasyOCR returns `None`/`""` and is cached
(`_EASYOCR_INIT_FAILED`) so ingestion is never interrupted.

### Verified evidence

- `tests/test_ocr.py` — **13 tests, all passing**: reader reuse (single init),
  disabled-via-env, init-failure caching, language parsing, empty-on-failure,
  segment joining, Tesseract-first precedence, EasyOCR fallback, both-fail,
  fallback-worse-than-Tesseract, and page-level gating (skip vs run).
- Full suite: `python -m pytest -q` → **75 passed**.
- Live sample image (text rendered with PIL, Tesseract absent on host):
  Tesseract → 0 chars; EasyOCR → 43 chars
  (`Invoice Number 12345\nMultimodal RAG EaSyCCR`, minor misread of the default
  font); `ocr_easyocr_fallback_used` emitted; `get_easyocr_reader()` returned the
  same object across calls (reader reuse confirmed).

### Remaining issues

- Live verification required a machine with enough free RAM (torch + models);
  on hosts under heavy load the run can fail with `MemoryError`/OpenBLAS
  allocation errors. Set `OMP_NUM_THREADS=1`/`OPENBLAS_NUM_THREADS=1` on
  low-memory hosts.
- Default PIL font is low-resolution and produced one misread character
  (`EasyOCR` → `EaSyCCR`); real scanned documents render at higher DPI.
- EasyOCR currently runs only for the fallback path; if Tesseract is later
  installed it becomes primary automatically and EasyOCR only fills the gaps.

---

## 7. Stabilization: crashes, duplicate processes, "app unavailable"

All four reported symptoms were traced to evidence, fixed with minimal changes,
and re-verified end to end on 2026-10-22.

### Root causes

| # | Symptom | Root cause | Fix |
|---|---|---|---|
| 1 | Process dies with `0xc0000005` (`c10.dll`, `VCRUNTIME140.dll`) | Two complete CPython installs on PATH. `where python` resolves to **Python 3.14** (torch 2.11.0, no easyocr); the project is pinned to `.venv` **Python 3.11.15** (torch 2.14.1+cpu, easyocr 1.7.2). Loading a second native torch stack kills the process with no Python traceback. `__pycache__` contained both `cpython-311` and `cpython-314` bytecode as proof of mixed-interpreter runs. | `commands.ps1` resolves `.venv\Scripts\python.exe` by absolute path and asserts the version prefix is `3.11` **and** `sys.executable` is inside the project before any launch. |
| 2 | High memory / needless torch loading | `backend/main.py` and `ui/app.py` imported the parsing/ingestion/generation pipeline at module import. | Imports are now lazy. Verified by import probe: `torch_loaded=False`, `easyocr_loaded=False`, `cv2_loaded=False`. |
| 3 | **"App becomes unavailable"** | When the Docker Desktop engine wedges it keeps 5433/6379 in `LISTEN` via `wslrelay` + `com.docker.backend` as a dead port proxy. TCP connects succeed but nothing ever answers. `check_database()` used `engine.connect()` with **no timeout**, so `/health/ready` blocked **261 s** and the UI appeared dead. | `backend/database.py` now sets `connect_args={"connect_timeout": 10}` and `pool_timeout=10` for postgres URLs, so the probe fails fast and visibly instead of hanging. |
| 4 | Duplicate services | A second `start` launched another API/worker/UI; the copy failed to bind its port and left a stale pid file. Three Redis containers (`mmrag-redis`, `mm-rag-redis`, `pipeline-redis`) and two Postgres instances were also found on the host. | `Get-LiveServicePid` + an early return make `start` idempotent; `Stop-AppService` removes stale pid files and tolerates `taskkill` "not found" on stderr. Compose declares named volumes only, so it can never adopt or replace the existing containers. |
| 5 | Ingestion stays `queued` forever | A native crash or an external kill is **not** a Python `Exception`, so `autoretry_for=(Exception,)` never fires. With `task_acks_late` the message stays unacked for the full 30-minute `visibility_timeout`. | Operational: keep the pinned-interpreter guard in place. Recovery is `.\commands.ps1 stop` then `start`; the UI is additionally rescued by `STALE_JOB_SECONDS=300`. |
| 6 | Services died with the launching shell | `Start-Process` makes the service a child of the terminal that launched it. | Services are launched through `Win32_Process.Create` (parented to `WmiPrvSE`) wrapped in `powershell -File`, so they outlive the shell. Verified: a detached heartbeat kept writing for 60 s after its launching command exited. |

### Verified evidence (this session)

| Check | Result |
|---|---|
| `GET /health` | 200 `{"status":"healthy"}` |
| `GET /health/ready` | 200 `ready` — database 5.3 ms, redis 19.2 ms, qdrant 859.8 ms (`mm-rag-documents`, `mm-rag-local`), ollama 2130.6 ms (`moondream:latest`, `llama3.2:1b`) |
| Streamlit | up on `http://127.0.0.1:8502` |
| Containers | `mm-rag-postgres` running, `mmrag-redis` running |
| Celery queue depth | 0 |
| Fresh ingestion (`PSNB_CISCNS.pdf`, 114 KB) | `uploaded → queued → ready`; 1 page parsed, **6 points indexed** into `mm-rag-local` |
| Dedup path | re-upload of identical bytes → `{"duplicate": true, "status": "ready"}`, no new job |
| Hybrid retrieval | dense=16, sparse=16, RRF fused=16 → cross-encoder rerank → **6** final, tenant-filtered |
| **End-to-end query** | `POST /query` → **200 in 22 s**, grounded answer from `llama3.2:1b`, 6 sources with citations |
| Frontend-requested context | `logs\smoke.log` ends with `RESULT: PASS` |

### Remaining constraints

- **RAM ceiling for generation (not a code defect).** With **0.6 GB free of
  15.68 GB**, Ollama returned HTTP 500:
  `ggml_backend_cpu_buffer_type_alloc_buffer: failed to allocate buffer of size 1313251456`.
  Retrieval had already succeeded in the same request. With **1.69 GB free** the
  identical query returned 200 in 22 s. `commands.ps1 doctor` and `start` now
  report free RAM and warn below 1.5 GB.
- **Docker Desktop is the least reliable component on this host.** Its engine
  wedged three times during this work (`docker ps` never returns, pipes present,
  port proxy still listening). `docker desktop restart` is unusable here
  (`Access is denied` writing `C:\Users\prash\AppData\Local\Docker\log\host`);
  recovery is to kill the Docker Desktop process tree, `wsl --shutdown`, then
  relaunch via WMI. After any engine restart the host containers come back
  `Exited (255)` and need `docker start mm-rag-postgres mmrag-redis`.
- **Leftover containers from other projects** (`mm-rag-redis` redis:7-alpine,
  `pipeline-redis` — still mapping `0.0.0.0:6379`, `pgdev`, `tech_intern-*`,
  `taskmanager_*`) were deliberately **not** removed, to honour the
  never-delete-volumes constraint. They are worth a manual review.
- **Nothing was run with bare `python`.** Always go through `commands.ps1`.
