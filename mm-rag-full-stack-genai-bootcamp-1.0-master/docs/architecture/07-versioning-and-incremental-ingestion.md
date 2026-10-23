# 07 — Versioning & Incremental Ingestion Strategy

How a document can be re-uploaded, superseded, deduplicated and
re-indexed without duplicating vectors, orphaning versions or leaking
across tenants.

Related: [02 data model](02-multitenant-data-model.md) ·
[03 async ingestion](03-async-ingestion-workflow.md) ·
[04 hybrid retrieval](04-hybrid-retrieval-strategy.md)

Implementation: [main.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/backend/main.py) ·
[ingestion.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/src/ingestion.py) ·
[migrate_legacy_points.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/backend/migrate_legacy_points.py)

---

## 1. Two identities: logical document vs. file revision

A user thinks in one document ("the contract") that changes over time.
The system models that with two levels:

| Concept | Table | Stability | Meaning |
|---|---|---|---|
| **Logical document** | `documents` | one row per (tenant, workspace?, filename) | the thing users cite and query |
| **Revision** | `document_versions` | one row per upload | an immutable snapshot of the bytes |

`documents` keeps the *current* revision's pointers (`stored_filename`,
`file_path`, `file_hash`, `status`), so listing and status queries stay
single-row and cheap. `document_versions` keeps the full history with
`UNIQUE(document_id, version_number)` and exactly one row flagged
`is_current`.

The critical consequence: **the Qdrant point identity is keyed to the
logical document, not the revision** (see §3). Re-uploading a changed
file therefore *replaces* the document's vectors instead of
accumulating a second copy.

---

## 2. Upload resolution algorithm

On `POST /documents/upload` the API hashes the bytes first:
`file_hash = sha256(contents).hexdigest()`.

```
resolve logical document
    tenant_id == caller's tenant
    AND filename == original filename
    AND (workspace_id == given workspace, if any)
        │
        ├─ found ──► load current version (is_current == True)
        │               │
        │               ├─ current.file_hash == new hash
        │               │  AND document.status == "ready"
        │               │        │
        │               │        └─► DUPLICATE
        │               │              • delete the redundant uploaded bytes
        │               │              • return duplicate=True, status=ready
        │               │              • no new version, no Celery task, no re-embed
        │               │
        │               └─ otherwise ──► NEW VERSION
        │                      • version_number = current.version_number + 1
        │                      • all prior versions: is_current = False
        │                      • document pointers → new revision
        │                      • document.status = "uploaded", error = None
        │
        └─ not found ──► NEW DOCUMENT: version_number = 1
```

Points worth noting:

- **Empty file rejected before hashing** — nothing is written on a bad
  request.
- **The duplicate check requires `status == "ready"`.** A previous
  upload that *failed* has the same hash but no indexed vectors, so it
  must be re-ingested rather than short-circuited. The hash alone is not
  a sufficient duplicate key; hash **and** successful indexing is.
- **The redundant upload is deleted** from object storage, so a
  duplicate costs bandwidth, not storage.
- **Version numbers never reuse values**, even after deletions, because
  they are derived from the current maximum, not from a row count.

---

## 3. Vector identity and replacement

`_point_id(...)` builds a deterministic `uuid5` from:

```
tenant_id | document_id | source | page_number
| content_type | table_index | image_index | chunk_index
```

and upserts with `replace_existing` semantics after
`_delete_existing_document(tenant_id, document_id)`, which deletes
**only** points matching *both* that `tenant_id` and that `document_id`.

Consequences:

- **Idempotent re-index.** Re-running the same ingestion twice produces
  the same point IDs, so the result converges rather than duplicating.
  This is what makes the at-least-once Celery delivery guarantee safe
  ([03 §5](03-async-ingestion-workflow.md)).
- **No cross-tenant deletion.** A tenant can only ever delete points
  carrying its own `tenant_id`, even if it uploads a file whose name,
  and therefore whose derived `document_id`, coincide with another
  tenant's.
- **No cross-document deletion.** Both keys are required, so re-indexing
  document A cannot touch document B.
- **Content changes replace, not merge.** Because the key does not
  include the file hash, a new revision overwrites the old points. That
  is intentional — stale chunks from a superseded revision must not
  remain retrievable.

---

## 4. Storage keys

Object storage is namespaced by function, not by tenant (tenant scoping
is enforced in PostgreSQL and Qdrant payloads):

| Key | Produced by | Contents |
|---|---|---|
| `uploads/<uuid4hex>_<safe_name>.pdf` | `upload_key()` | raw uploaded PDF |
| `parsed/<stem>/…` | `parsed_prefix(stem)` | parser artifacts (page images, table/image records, JSON) |

The `<uuid4hex>_` prefix guarantees uniqueness even when two tenants
upload same-named files, and the `stem` linkage keeps an artifact set
tied to the exact revision that produced it. Backends are pluggable
(`STORAGE_BACKEND=local|s3`) behind `StorageBackend`; `localize()`
materialises an object to a local path when a parser needs a real file,
which is what the worker uses (`storage.localize(key, suffix=".pdf")`).

---

## 5. Full lifecycle

| Event | `documents` | `document_versions` | Qdrant | Object storage |
|---|---|---|---|---|
| First upload | new row, `status=uploaded` | v1, `is_current=True` | — | `uploads/…` + `parsed/…` |
| → ready | `status=ready` | v1 `status=ready` | points added | artifacts persisted |
| Identical re-upload | unchanged | unchanged | untouched | **new bytes deleted** |
| Changed re-upload | pointers → v2, `status=uploaded` | v2 current, v1 `is_current=False` | v2 points replace v1 | v2 PDF + artifacts added |
| Re-upload after failure | `status=uploaded`, `error=None` | new version | points (re)written | retried |
| Delete document | rows removed (cascade) | removed | points deleted by `tenant_id + document_id` | artifacts removed under parsed prefix |

Cross-tenant deletion is impossible by construction: every Qdrant
delete requires both keys, and both are derived from the authenticated
identity.

---

## 6. Legacy points

Points written before tenant tagging existed have no
`metadata.tenant_id`. Because `build_filter` mandates that condition,
they are **invisible to all queries** — fail-closed, which is the right
default but silently loses recall.

`backend/migrate_legacy_points.py` repairs them **in place**:

- it never deletes a collection and never recreates one,
- it supports `--dry-run` to report what it *would* change,
- it reports counts so the operation is auditable.

This is the deliberate alternative to the common "drop and re-index
everything" shortcut, which would destroy data and invalidate point
IDs.

---

## 7. Content-hash provenance

`metadata.file_sha256` is a declared Qdrant payload index **and is
populated**: the worker passes `documents.file_hash` into
`ingest_pdf(..., file_sha256=…)`, which attaches it to every point's
metadata. A point can therefore be traced to the exact bytes that
produced it from the vector store alone, without a PostgreSQL join —
useful for audits and for detecting points that belong to a superseded
revision.

Note that the hash is **not** part of the point ID. It is provenance
metadata, not identity: re-ingesting changed content overwrites the
previous points (see §3) rather than creating hash-keyed siblings.

---

## 8. Known limitations

- **Version history is metadata-only.** Superseded revisions keep their
  file path and hash, but their parsed artifacts and vectors are
  replaced. Answering "what did v1 say?" would require re-parsing v1.
  Keeping per-version vectors (namespace the point ID by version) is the
  natural extension.
- **Deletion is not soft.** There is no tombstone/undo; a delete
  cascades. A soft-delete + purge job is the safer enterprise pattern.
- **No automatic change detection.** Re-ingestion is user-driven. A
  connector-based sync (see [09](09-roadmap-and-trade-offs.md)) would
  compare hashes on a schedule and enqueue only changed files — the
  hash infrastructure to do it already exists.
- **Version listing is read-only.** `GET /documents/{id}/versions`
  exposes history but there is no "roll back to v1" endpoint; the
  rollback path today is to re-upload the older bytes.
