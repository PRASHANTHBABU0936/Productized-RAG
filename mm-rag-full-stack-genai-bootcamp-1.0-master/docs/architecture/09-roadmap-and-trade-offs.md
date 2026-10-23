# 09 — Phased Roadmap & Trade-offs

Where the system is, what was deliberately deferred, and the order in
which the remaining work should be tackled — with the reasoning behind
each trade-off, not just a task list.

Related: [01 architecture](01-system-architecture.md) ·
[06 security](06-security-and-governance.md) ·
[08 evaluation](08-evaluation-and-observability.md)

---

## 1. Where the system is

| Capability | State | Where |
|---|---|---|
| Multimodal parse (text, OCR, tables, images) | ✅ done | [05](05-image-and-table-intelligence.md) |
| Tenant-aware ingestion → Qdrant | ✅ done | [02](02-multitenant-data-model.md) |
| Async ingestion (API → Redis → Celery → Qdrant) | ✅ done | [03](03-async-ingestion-workflow.md) |
| Ingestion state machine + staleness guard | ✅ done | [03](03-async-ingestion-workflow.md) |
| Hybrid retrieval + RRF + cross-encoder rerank | ✅ done | [04](04-hybrid-retrieval-strategy.md) |
| Vision captions for images | ✅ done | [05](05-image-and-table-intelligence.md) |
| Workspaces, roles, per-workspace permissions | ✅ done | [02](02-multitenant-data-model.md) |
| Document versioning + hash dedup | ✅ done | [07](07-versioning-and-incremental-ingestion.md) |
| Object storage abstraction (local / S3) | ✅ done | [07](07-versioning-and-incremental-ingestion.md) |
| Legacy point migration tool | ✅ done | [07](07-versioning-and-incremental-ingestion.md) |
| Offline evaluation harness | ✅ done | [08](08-evaluation-and-observability.md) |
| Metrics, health, readiness, audit log | ✅ done | [08](08-evaluation-and-observability.md), [06](06-security-and-governance.md) |
| Architecture documentation (01–09) | ✅ done | this folder |

The end-to-end path — **upload → queue → parse → embed → index →
hybrid retrieve → grounded answer**, tenant-scoped at every step — is
implemented and verified.

---

## 2. Deliberate deferrals

Each of these is a decision, not an oversight. The pattern is the same:
the simplest thing that is *correct* was chosen, and the scale-out path
is named.

| Deferral | Chosen instead | Why | Upgrade path |
|---|---|---|---|
| Native image vectors (CLIP/SigLIP) | vision caption embedded as text | one embedding space, one index, no extra model or vector type | add a second named vector or multivector (ColPali-style) |
| Persistent sparse index (SPLADE) | per-query BM25 over tenant-scoped candidates | correctness first; BM25 recompute is acceptable at current corpus size | Qdrant sparse vectors |
| Distributed tracing | structured logs + per-endpoint metrics | no collector in the stack yet | OpenTelemetry across API + worker |
| Multi-replica metrics | in-process counters | single uvicorn process today | Prometheus client + shared registry |
| LLM-as-judge evaluation | lexical groundedness | no judge-model budget/latency in eval loop | NLI or judge model, sampled |
| Refresh tokens / SSO | 60-min JWT | smallest correct auth | refresh + denylist, then OIDC/SCIM |
| Rate limiting | none | not yet internet-facing | token bucket at the edge and per route |
| Soft delete | hard delete with cascade | simpler invariants | tombstone + purge job |

---

## 3. Prioritised backlog

### P0 — correctness and production safety

1. **Set `JWT_SECRET_KEY` and fail fast when it is the default.** The
   fallback secret in
   [auth.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/backend/auth.py)
   allows token forgery if a deployment forgets it. Guard at startup.
2. **Rate limit `/auth/login` and `/query`.** Login is the classic
   credential-stuffing target; `/query` consumes an LLM and is a cost
   amplifier.
3. **Add CORS allow-list.** No `CORSMiddleware` exists, so a browser
   client is blocked by default. Required before the React/Next.js UI.

### P1 — scale and operability

4. Run **≥2 Celery workers** and move metrics/tracing to a shared
   backend; today both metrics and workers are single-instance.
5. **Restrict or authenticate `/metrics`** — it currently leaks endpoint
   inventory and latency.
6. **Reranker as a service** with batching; it is the CPU bottleneck in
   the query path.
7. **Alerting** on `error_rate`, p95 query latency, ingestion failures
   and the readiness probe — the metrics exist but nothing watches them.

### P2 — capability

8. **React/Next.js frontend** on top of the existing API (upload,
   status polling, chat, workspace management). The API is already the
   contract; the Streamlit UI is a thin client.
9. **Connectors + scheduled sync** (Drive/SharePoint/S3 bucket) using
   the existing hash comparison to enqueue only changed files.
10. **Native image retrieval** (CLIP/multivector) to close the
    caption-fidelity gap in [05 §5](05-image-and-table-intelligence.md).
11. **Per-tenant quotas** (documents, storage, tokens) for noisy-
    neighbour and cost control.

### P3 — enterprise

12. SSO/OIDC + SCIM, refresh tokens, MFA.
13. Soft delete + restore, "roll back to version N".
14. LLM-as-judge / NLI faithfulness scoring in the eval harness.
15. Per-tenant cost attribution (storage, vision calls, tokens).

---

## 4. Trade-offs, explicitly

**Async ingestion vs. simplicity.** A synchronous path would be ~50
lines less code but blocks the UI, loses progress, and cannot retry.
The cost is a Redis dependency, a state machine, a staleness guard and
the "no worker running" failure mode — all of which had to be built and
are now documented in [03](03-async-ingestion-workflow.md). Correct for
any real corpus.

**Hybrid + rerank vs. latency.** Three stages cost more than dense-only
(`retrieve_hybrid` runs two retrievals plus a cross-encoder pass). The
`retrieval_mode="dense"` escape hatch exists for latency-sensitive
callers, and the harness quantifies what hybrid buys — so the trade-off
is measurable rather than assumed.

**Captions vs. native image vectors.** Captions reuse the existing text
pipeline: no second model, no second index, retrievable by natural
language immediately. The cost is fidelity — the caption is a lossy
summary. Chosen because it makes images *actually reachable today*
rather than designing a cross-modal store that is not yet built.

**Tables as whole units vs. chunked.** Tables are never split, so a
large table consumes more of the context budget, but rows stay attached
to their headers. Chunking a table would produce unrecoverable
fragments. Correctness won over token efficiency.

**Deterministic point IDs vs. version-keyed vectors.** Keying points to
the logical document makes re-index idempotent (safe under at-least-once
delivery) and prevents vector accumulation, at the cost of historical
vectors: superseded revisions' vectors are replaced. The alternative —
version-namespaced IDs — would preserve history but leave stale chunks
retrievable unless every query filtered on `is_current`. Chosen
simplicity, documented the limitation ([07 §7](07-versioning-and-incremental-ingestion.md)).

**Fail-closed tenant filtering vs. recall.** Legacy points without
`tenant_id` are invisible rather than guessed at. This trades recall for
the guarantee that a cross-tenant leak is impossible, which is the right
direction for the risk — and the migration tool recovers the recall
safely.

**In-memory metrics vs. infrastructure.** No Prometheus server or
collector is required to get visibility, which keeps the stack small
and the metrics useful today. The cost is that metrics do not survive
restart or aggregate across replicas — acceptable at one process,
insufficient at many.

**PostgreSQL + Qdrant dual write vs. single store.** Metadata lives in
PostgreSQL (transactions, constraints, joins) and vectors in Qdrant
(ANN search). Ordering (commit PG *before* enqueue) and idempotency
(deterministic point IDs) are what keep the two consistent without
distributed transactions.

---

## 5. Definition of done for the current phase

- [x] Upload returns immediately; UI polls and reaches `ready` or
      `failed` — never hangs.
- [x] A queued job with no worker is reported `failed` after 300 s.
- [x] Every Qdrant point carries `tenant_id`, `document_id` and, when
      scoped, `workspace_id`.
- [x] Cross-tenant retrieval is impossible by construction.
- [x] Re-uploading identical bytes creates no new version and no new
      vectors; changed bytes create a new version and replace vectors.
- [x] Hybrid retrieval (dense + BM25 → RRF → cross-encoder) is wired
      into answer generation.
- [x] Tables and images are retrievable and can be force-included.
- [x] Raw PDFs and artifacts sit behind a storage abstraction.
- [x] Precision/Recall/MRR/groundedness/latency/token/error metrics are
      reportable offline, and requests/health/audit are observable
      online.
- [x] The architecture is documented end to end (01–09).

Open items are the P0–P3 backlog above; none of them block the
documented end-to-end flow.
