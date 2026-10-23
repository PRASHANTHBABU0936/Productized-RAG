# 08 — Evaluation & Observability Framework

Two complementary feedback loops: an **offline** harness that scores
answer quality against a labelled dataset before a change ships, and
**online** metrics/health/audit that describe how the running system is
behaving right now.

Related: [03 async ingestion](03-async-ingestion-workflow.md) ·
[04 hybrid retrieval](04-hybrid-retrieval-strategy.md) ·
[06 security & governance](06-security-and-governance.md)

Implementation: [harness.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/evaluation/harness.py) ·
[observability.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/backend/observability.py) ·
[audit.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/backend/audit.py)

---

## 1. Offline evaluation harness

### 1.1 Why

"Did quality go up?" is unanswerable by inspection when five stages
(parse → chunk → embed → fuse → rerank) all affect the result. The
harness fixes a dataset and a tenant, runs the **same** retrieval +
generation path the API uses, and emits numbers that can be compared
across commits.

### 1.2 Dataset format

JSONL, one case per line:

```json
{"question": "What is the notice period?",
 "expected_keywords": ["30 days"],
 "expected_sources": ["Client_Contracts_Policies_and_Incident_Records.pdf"],
 "k": 6}
```

`tenant_id` (and optionally `collection_name`) may be set per line or
supplied globally. Labelling is optional per field and the harness
degrades sensibly: a case without `expected_sources` simply reports
`null` retrieval metrics instead of a misleading `0.0`, so partial
labelling does not silently deflate the aggregate.

### 1.3 Metrics

| Category | Metric | Definition |
|---|---|---|
| Retrieval | **Precision@k** | fraction of retrieved sources that are expected |
| Retrieval | **Recall@k** | fraction of expected sources that were retrieved |
| Retrieval | **MRR** | 1 / rank of the first expected source |
| Retrieval | **Hit rate** | fraction of cases with ≥1 expected source retrieved |
| Answer | **Groundedness** | lexical overlap between the answer and the exact context shown to the model |
| Answer | **Keyword hit rate** | fraction of `expected_keywords` present in the answer |
| Performance | `latency_ms` (mean, p50, p95) | end-to-end per case |
| Cost | `input_tokens`, `output_tokens`, `total_tokens` | when the model reports usage |
| Reliability | **error rate** | cases that raised |

Groundedness uses the context actually passed to the LLM, obtained via
`include_context=True` on `generate()`. That flag exists **only** for
the harness — normal API responses do not carry the context, so
evaluation does not inflate production payloads.

### 1.4 Running it

```powershell
python -m evaluation.harness `
    --dataset evaluation/dataset.sample.jsonl `
    --tenant-id <uuid>

# machine-readable report for CI
python -m evaluation.harness --dataset data.jsonl `
    --tenant-id <uuid> --json-out evaluation/report.json
```

Other flags: `--collection`, `--model`, `--limit N`. `tenant_id` may
also come from `EVAL_TENANT_ID`. The aggregate report is the summary
object; `--json-out` writes summary +
per-case rows so a CI job can assert thresholds (e.g. `recall_at_k >=
0.8`, `error_rate == 0`).

### 1.5 How it is used as a gate

Because the harness drives the real pipeline, it is the regression net
for the exact changes this architecture describes: swapping the
reranker, changing `rrf_k` or `candidate_k`, altering the caption
prompt, or changing how tables are serialized. Any of those is a
"measure, don't guess" change.

---

## 2. Online metrics

`observability.record_request(method, path, status, duration_ms)` is
called from an HTTP middleware registered with `@app.middleware("http")`
and accumulates in-process counters:

- request counts keyed by `(method, path, status_code)`,
- bounded per-endpoint latency samples (`MAX_LATENCY_SAMPLES = 2000`,
  oldest evicted first — a fixed ceiling so a long-lived process cannot
  grow without bound).

`snapshot()` derives: uptime, total requests, 4xx count, 5xx count,
error rate, and per-endpoint requests / status breakdown / latency mean,
p50, p95.

`GET /metrics?format=json|prometheus` exposes it. The Prometheus
rendering emits `mmrag_uptime_seconds` and
`mmrag_requests_total{method,path,status}` in text exposition format, so
a standard scrape config works without a client library.

**Limits, stated plainly:** metrics are **per-process and in-memory**.
They reset on restart and are not aggregated across workers, because the
API runs as a single uvicorn process today. A multi-replica deployment
needs a shared backend (Prometheus client + push/pull, or Redis/StatsD).
Endpoint labels use the raw path, so path parameters (e.g.
`/documents/status/{job_id}`) fragment cardinality — a templating step
is required before these labels are used for production alerting.

---

## 3. Health and readiness

| Endpoint | Semantics |
|---|---|
| `GET /health` | process is alive (liveness) |
| `GET /health/ready` | dependencies are usable (readiness) |

`readiness()` probes each dependency with `_probe()`, which records
latency and converts any exception into `{"status":"down","error":…}`
rather than propagating it:

| Dependency | Probe | Required? |
|---|---|---|
| `database` | `SELECT 1` via SQLAlchemy engine | ✅ |
| `redis` | `PING` with 2 s timeouts | ✅ |
| `qdrant` | `GET /collections` (with API key if set) | ✅ |
| `ollama` | `GET /api/tags` | ❌ optional |

Returning `200 {"status":"ready"}` when all required probes pass, and
`503 {"status":"degraded"}` otherwise. Ollama is deliberately **not**
required: the API can serve uploads, status and metadata without it;
only answer generation needs the model host. Coupling API readiness to a
model server would take the whole platform down for a chat-model outage.

This maps directly onto the failure that motivated the whole async
redesign — a missing Celery worker must be *detectable*, which is why
the ingestion staleness guard
([03 §4](03-async-ingestion-workflow.md)) exists alongside these probes.

---

## 4. Structured logging

All modules log through `logger.custom_logger.CustomLogger`, which emits
structured events rather than free-form strings. Because a `request_id`
/ `trace_id` cannot be recovered from prose, every log line carries an
event name and typed fields, e.g.:

```
retriever_initialized        collection_name=… embedding_model=… reranker_model=…
rrf_fusion_completed         dense_count=… sparse_count=… fused_count=…
cross_encoder_reranking_completed  candidate_count=… result_count=…
hybrid_reranking_completed   rrf_count=… final_count=… top_k=…
image_caption_generated      image_path=… vision_model=… caption_length=…
table_extracted              page_number=… rows=… columns=…
generation_completed         retrieved_documents=… used_images=…
document_processing_started  … (worker)
```

These fields are what make a retrieval-quality regression debuggable:
you can see *how many* candidates each stage produced without adding
temporary print statements.

---

## 5. Audit logging

Distinct from metrics: `audit_logs` is the **security and compliance**
record — who did what, to which resource, from which IP, when. See
[06 §6](06-security-and-governance.md). Metrics answer "is it healthy?";
audit answers "who changed it?".

---

## 6. Known limitations

- **In-memory, single-process metrics.** Reset on restart; not
  aggregated across replicas.
- **No tracing.** There is no distributed trace linking a UI request →
  API → Celery task → Qdrant call, so end-to-end latency attribution
  across the async boundary is manual.
- **No ingestion-time metrics.** Embedding throughput, vision-call
  latency and per-stage ingest duration are logged but not exported as
  time series.
- **Groundedness is lexical.** Answer↔context token overlap is a cheap
  proxy; it will not detect a confident answer that paraphrases a
  *different* passage. An LLM-as-judge or NLI-based faithfulness score
  is the upgrade path.
- **No alerting.** Metrics are exposed, not watched; no thresholds or
  paging exist yet.
- **No cost tracking beyond tokens.** Object storage, vision-model calls
  and embedder CPU time are not attributed to a tenant.
