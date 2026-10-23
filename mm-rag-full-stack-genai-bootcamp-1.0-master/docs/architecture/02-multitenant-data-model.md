# 02 — Multi-Tenant Data Model

How tenant isolation is represented in PostgreSQL and Qdrant, and the
invariants that keep one tenant's data invisible to another.

Related: [01 system architecture](01-system-architecture.md) ·
[06 security & governance](06-security-and-governance.md)

---

## 1. Relational model (PostgreSQL)

```
        ┌─────────────┐
        │   tenants   │  id · name · created_at
        └──────┬──────┘
               │ 1
      ┌────────┴────────┬──────────────────┬─────────────────┐
      │ N               │ N                │ N               │ N
┌─────────────┐  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐
│ memberships │  │  documents  │  │  workspaces  │  │   audit_logs     │
│ user_id     │  │ tenant_id   │  │ tenant_id    │  │ tenant_id        │
│ tenant_id   │  │ workspace_id┘──┤ id           │  │ user_id (null)   │
│ role        │  │ filename    │  │ name         │  │ action           │
└──────┬──────┘  │ stored_name │  │ description  │  │ resource_type    │
       │ N       │ file_path   │  └──────┬───────┘  │ resource_id      │
┌──────┴──────┐  │ file_hash   │         │ N        │ detail           │
│    users    │  │ status      │  ┌──────┴───────┐  │ ip_address       │
│ email (uni) │  │ error       │  │ permissions  │  │ created_at       │
│ password_h  │  │ created_at  │  │ tenant_id    │  └──────────────────┘
│ is_active   │  │ updated_at  │  │ workspace_id │
└─────────────┘  └──────┬──────┘  │ user_id(null)│
                        │ 1       │ role (null)  │
              ┌─────────┴────────┐ │ level        │
              │ N                │N└──────────────┘
   ┌──────────────────┐  ┌──────────────────┐
   │ document_versions│  │  ingestion_jobs  │
   │ document_id      │  │ document_id      │
   │ version_number   │  │ celery_task_id   │
   │ stored_filename  │  │ status           │
   │ file_path        │  │ error            │
   │ file_hash        │  │ created_at       │
   │ size_bytes       │  │ updated_at       │
   │ status           │  └──────────────────┘
   │ is_current       │
   │ created_by       │
   │ created_at       │
   │ UNIQUE(doc, ver) │
   └──────────────────┘
```

### Table notes

| Table | Purpose | Key constraints |
|---|---|---|
| `tenants` | Isolation boundary; one per registered organisation | `id` UUID PK |
| `users` | Identity + credential | `email` unique, indexed |
| `memberships` | User ↔ tenant link carrying the **role** | `user_id`, `tenant_id` indexed, FK cascade |
| `workspaces` | Logical document grouping inside a tenant | `tenant_id` indexed |
| `permissions` | Per-workspace grant to a **user** or a **role** | `workspace_id`, `user_id` FKs |
| `documents` | Current revision of a logical document | `stored_filename` unique; `file_hash`, `workspace_id` indexed |
| `document_versions` | Immutable revision history | `UNIQUE(document_id, version_number)` |
| `ingestion_jobs` | One async job per upload attempt | `celery_task_id` unique |
| `audit_logs` | Append-only security trail | `tenant_id`, `user_id`, `created_at` indexed |

`document_versions` exists so `documents` can keep a single stable row
(and therefore a single stable set of Qdrant points) while still
recording every upload. See [07 versioning](07-versioning-and-incremental-ingestion.md).

---

## 2. Vector model (Qdrant)

One collection per deployment (`QDRANT_COLLECTION_NAME`, default
`mm-rag-documents`), 384-dimensional cosine vectors
(`all-MiniLM-L6-v2`, normalized).

Every point carries:

| Payload key | Type | Indexed | Purpose |
|---|---|---|---|
| `metadata.tenant_id` | keyword | ✅ | **Mandatory isolation filter** |
| `metadata.document_id` | keyword | ✅ | Point → PostgreSQL document |
| `metadata.workspace_id` | keyword | ✅ | Workspace-scoped retrieval |
| `metadata.filename` | keyword | ✅ | File-scoped retrieval / citations |
| `metadata.file_sha256` | keyword | ✅ | Content-hash provenance |
| `metadata.content_type` | keyword | ✅ | `text` · `table` · `image` · `page_text_plus_ocr` |
| `metadata.page_number` | integer | ✅ | Page filters and citations |
| `metadata.image_index` | integer | ✅ | Image identity within a page |
| `metadata.chunk_index` | integer | — | Ordering / provenance |
| `metadata.chunk_id` | keyword | — | Stable point identity |
| `metadata.table_index` | keyword/int | — | Table identity |
| `metadata.image_path` | keyword | — | Artifact location |
| `metadata.image_caption` | text | — | Vision-generated caption (searchable) |

**Point identity** is a deterministic hash of
`(document_id, tenant_id, source, page_number, content_type, chunk_index, table_index, image_index)`.
Re-ingesting the same logical document therefore *overwrites* its
points instead of duplicating them.

---

## 3. Isolation invariants

1. **Relational scoping.** Every read/write path resolves `tenant_id`
   from the JWT's membership (`get_current_user`), never from the
   request body. Filtering by `tenant_id` is applied to documents,
   jobs, workspaces, permissions and audit logs.
2. **Vector scoping.** `build_filter()` raises `ValueError` when
   `tenant_id` is missing and always injects
   `metadata.tenant_id == <tenant>` as a `must` condition.
3. **BM25 scoping.** `retrieve_bm25` cannot score an unscoped corpus:
   it first `scroll`s Qdrant *with the tenant filter* and only then
   builds the BM25 index over those candidates. Tenant isolation is
   therefore enforced **before** lexical scoring.
4. **Fusion scoping.** RRF fuses only the two already-tenant-filtered
   result lists, and the cross-encoder reranks only fused candidates —
   no un-scoped data can enter the ranking.
5. **Defensive re-check.** Retrieved documents are re-validated against
   the requested tenant before context assembly.

### Failure mode: legacy points

Points written before tenant tagging existed have no
`metadata.tenant_id`. They are invisible to every filtered query
(fail-closed). `backend/migrate_legacy_points.py` backfills them
**in place** — it never deletes a collection — and reports what it
found. See `--dry-run`.

---

## 4. Access-control model

Roles (`memberships.role`): `owner`, `admin`, `member`.
`ADMIN_ROLES = {"owner", "admin"}` gates tenant-wide operations
(workspace creation, permission administration, audit log reads).

Permission levels (`permissions.level`), ordered
`read` < `write` < `admin`:

```python
PERMISSION_LEVELS = {"read": 1, "write": 2, "admin": 3}
```

A grant targets **exactly one** of `user_id` (direct grant) or `role`
(applies to every member holding that role). `effective_level()` returns
the **maximum** level found across the user's direct and role-based
grants for a workspace.

```
effective_level(user, workspace)
    = max(level(p) for p in permissions
          where p.workspace_id == workspace.id
            and (p.user_id == user.id or p.role == user.role))
```

---

## 5. Data lifecycle

| Stage | Relational | Vector | Object storage |
|---|---|---|---|
| Upload | `documents` + `document_versions` + `ingestion_jobs` | — | raw PDF |
| Parsing | version status `parsing` | — | `parsed/<stem>/…` |
| Chunking | version status `chunking` | — | — |
| Indexing | version status `indexing` | upsert (replace same doc) | — |
| Ready | status `ready`, `is_current` on newest version | tenant-tagged points | artifacts persisted |
| Re-upload (same bytes) | no new version (`duplicate: true`) | untouched | redundant upload deleted |
| Re-upload (new bytes) | new version, `is_current` moved | points replaced | new PDF kept |

Deletion semantics: deleting a document removes its PG rows (cascade)
and its Qdrant points by `tenant_id + document_id`; the parsed
artifacts are removed under the parsed prefix. Cross-tenant deletion is
impossible by construction because both keys are required.
