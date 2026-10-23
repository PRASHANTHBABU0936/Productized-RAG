# 04 — Hybrid Retrieval & Reranking Strategy

How a question becomes a ranked, tenant-scoped evidence set:
dense + BM25 retrieval → RRF fusion → cross-encoder reranking →
top-K, with an evidence floor for tables and images.

Related: [02 data model](02-multitenant-data-model.md) ·
[05 image & table intelligence](05-image-and-table-intelligence.md) ·
[08 evaluation](08-evaluation-and-observability.md)

Implementation: [retriever.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/src/retriever.py) ·
[generation.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/src/generation.py)

---

## 1. Why hybrid

Neither retrieval path is sufficient alone on document corpora:

| Query shape | Dense (MiniLM) | BM25 | Winner |
|---|---|---|---|
| "What is the notice period?" (paraphrase) | strong | weak | dense |
| "clause 7.2(b)" / "ISO 27001" (rare token) | weak | strong | BM25 |
| "summarize the escalation matrix" (semantic) | strong | weak | dense |
| numeric / identifier / acronym lookups | weak | strong | BM25 |

Dense embeddings capture paraphrase and semantics; BM25 captures
exact lexical overlap on rare tokens, IDs and acronyms. Running both
and fusing recovers the recall that either alone loses.

---

## 2. Pipeline

```
                       query
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
  ┌───────────┐                    ┌────────────┐
  │  Dense    │                    │   BM25     │
  │ Qdrant    │                    │  Okapi     │
  │ cosine    │                    │  (lexical) │
  └─────┬─────┘                    └──────┬─────┘
        │ candidate_k                     │ candidate_k
        │  (filtered by tenant_id,        │  (corpus scoped by the
        │   workspace_id, filename,       │   SAME tenant/workspace
        │   document_id, content_types,   │   filter before scoring)
        │   page range)                   │
        └────────────────┬────────────────┘
                         ▼
              ┌─────────────────────┐
              │  RRF fusion         │
              │  score = Σ 1/(k+r)  │   rrf_k = 60
              └──────────┬──────────┘
                         ▼  candidate_k candidates
              ┌─────────────────────┐
              │ Cross-Encoder       │
              │ ms-marco-MiniLM-L-6 │   pair = [query, chunk]
              │ direct relevance    │
              └──────────┬──────────┘
                         ▼  top-K (k)
              ┌─────────────────────┐
              │ Evidence guarantee  │   (optional)
              │ force ≥1 table and  │
              │ ≥1 image when asked │
              └──────────┬──────────┘
                         ▼
                 final top-K evidence
```

Entry point: `MultimodalQdrantRetriever.retrieve_hybrid(...)`.

---

## 3. Stage detail

### 3.1 Dense retrieval

- Qdrant cosine search over 384-d MiniLM vectors
  (`sentence-transformers/all-MiniLM-L6-v2`, `normalize_embeddings=True`).
- Returns `(Document, cosine_score)` ordered by similarity.
- `retrieve_with_scores()`; `retrieve()` is the same call without scores.

### 3.2 Sparse retrieval (BM25)

BM25's IDF is **corpus-relative**, so an unscoped BM25 index would leak
ranking signal across tenants. `retrieve_bm25` therefore:

1. `client.scroll`s Qdrant **with the full metadata filter already
   applied** (tenant, workspace, document, content types, page range),
2. builds a `BM25Okapi` index over only those candidate texts,
3. scores the tokenized query and returns the top `k`.

This makes tenant isolation a property of candidate selection, not of a
post-hoc filter, so lexical scoring can never see another tenant's text.

### 3.3 RRF fusion

`reciprocal_rank_fusion(dense, sparse, k=60, top_k=candidate_k)`

```
score(d) = Σ over each list L that contains d of  1 / (k + rank_L(d))
```

Why RRF rather than score blending:

- dense cosine (0–1) and BM25 (unbounded) are **not** on comparable
  scales; normalizing them is dataset-dependent and brittle,
- RRF works on **ranks only**, so it is scale-free and robust,
- it rewards documents that *both* retrievers agree on.

`k=60` is the standard smoothing constant: it flattens the tail so that
an item ranked #1 in one list and absent from the other does not
automatically beat an item ranked #3 in both.

Documents are de-duplicated by a composite key
`document_id|page_number|content_type|chunk_id|page_content`, so the
same chunk arriving from both lists contributes only once.

### 3.4 Cross-encoder reranking

`rerank_documents(query, docs, top_k=k)`

- Bi-encoders (the dense stage) embed query and document **separately**,
  so they cannot model token-level interaction.
- The cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) receives
  **`[query, document]` as a single input pair** and emits one direct
  relevance score per pair.
- It is far more accurate but O(pairs) LLM-free inference, so it is
  applied only to the fused candidate pool (`candidate_k`), never to the
  whole corpus. This is the standard two-stage retrieve-then-rerank
  trade-off: cheap high-recall recall, expensive high-precision trim.

### 3.5 Evidence guarantee

`_augment_with_content_types(...)` — when the caller asks for it
(`guaranteed_content_types=("table","image")` is the default in
`generate`), the pipeline tops up the result set with at least
`per_type_k` items of each requested type **if the fused set contains
none**. Without this, a strong text match can crowd out the one table
slide that actually answers a numeric question. See
[05 image & table intelligence](05-image-and-table-intelligence.md).

The guarantee is bypassed when the caller supplied an explicit
`content_types` filter, because that filter already expresses intent.

---

## 4. Filtering: applied before ranking

`build_filter(*, tenant_id, filename, document_id, workspace_id,
content_types, page_number, page_from, page_to)`

- **`tenant_id` is mandatory** — the function raises `ValueError` if it
  is missing, so no code path can retrieve unfiltered.
- Every other argument adds an *additional* `must` condition.
- The same filter object is passed to dense search, the BM25 `scroll`,
  and the guarantee top-up, so all three stages see an identical
  candidate universe.

Ordering matters: filtering happens **before** fusion and reranking.
Filtering after ranking would both waste compute and risk a
cross-tenant document influencing the final ordering.

---

## 5. Parameters and defaults

| Parameter | Default | Meaning |
|---|---|---|
| `k` | 6 (API) / caller | Final evidence count returned |
| `candidate_k` | `max(k*4, 20)` | Per-retriever candidate depth; also rerank input size |
| `rrf_k` | 60 | RRF smoothing constant |
| `top_k` (rerank) | `k` | Reranker output size |
| `retrieval_mode` | `"hybrid"` | `"hybrid"` or `"dense"` (dense-only escape hatch) |
| `guaranteed_content_types` | `("table","image")` | Evidence floor |
| `per_type_k` | 1 | Minimum items per guaranteed type |

Validation enforces `candidate_k >= k` and `k > 0`, so the reranker
never receives a narrower pool than the requested output.

---

## 6. Generation handoff

`MultimodalRAGGenerator.generate()`:

1. calls `retrieve_hybrid` (or `retrieve_with_scores` when
   `retrieval_mode="dense"`),
2. optionally drops results below `min_score`,
3. if nothing survives → returns a fixed "not enough information"
   answer with `retrieval_count: 0` (no LLM call, no hallucination),
4. otherwise builds the context + image payloads
   (`_prepare_context`, `_build_messages`) and invokes the chat model,
5. returns `{answer, sources, used_images, retrieval_count,
   model_name, collection_name, retrieval_mode, usage}`.

`usage` carries token counts when the model reports them, which is what
the offline harness consumes for cost tracking.

---

## 7. Known limitations

- **BM25 is rebuilt per query** over the same-tenant candidate set.
  Correct but not free; a persistent sparse index (e.g. Qdrant sparse
  vectors / SPLADE) is the scale-out path.
- **Single cross-encoder**, CPU-only, no batching across concurrent
  requests. A reranker service or GPU worker is the scale-out path.
- Non-English corpora would need a multilingual embedding and reranker
  pair; the current defaults are English-centric.

---

## 8. How it is measured

The offline harness (see
[08 evaluation](08-evaluation-and-observability.md)) reports
Precision@k, Recall@k, MRR and hit rate for retrieval, and groundedness
and keyword hit rate for the answer, so a change to `rrf_k`,
`candidate_k` or the reranker can be evaluated against a fixed dataset
rather than by spot-checking.
