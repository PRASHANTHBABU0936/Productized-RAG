# 06 — Security & Governance Plan

Authentication, authorisation, tenant isolation, input validation,
auditability and the operational controls around them. Each section
states what is **implemented today** and what is **planned**, so the
gap is explicit rather than implied.

Related: [02 data model](02-multitenant-data-model.md) ·
[07 versioning](07-versioning-and-incremental-ingestion.md) ·
[09 roadmap](09-roadmap-and-trade-offs.md)

Implementation: [auth.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/backend/auth.py) ·
[main.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/backend/main.py) ·
[audit.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/backend/audit.py)

---

## 1. Authentication

| Property | Value | Status |
|---|---|---|
| Scheme | JWT Bearer (`HTTPBearer`) | ✅ |
| Algorithm | `HS256` | ✅ |
| Subject claim | `sub = user_id` | ✅ |
| Expiry | `exp`, 60 minutes | ✅ |
| Password storage | `pwdlib.PasswordHash.recommended()` (Argon2id family) | ✅ |
| Refresh tokens | — | ❌ planned |
| Token revocation / denylist | — | ❌ planned |
| MFA | — | ❌ planned |

Registration (`POST /auth/register`) creates, atomically:

1. a `tenants` row (the isolation boundary),
2. a `users` row with a hashed password (`is_active=True`),
3. a `memberships` row linking them with role **`owner`**.

Duplicate emails are rejected with `409` **before** any row is written.
Email is always lower-cased, so case cannot be used to fork identity.

Login issues a token carrying only `sub` and `exp`. **No tenant or role
is embedded in the token** — that is deliberate (see §3).

---

## 2. Request authentication flow

`get_current_user` is the single authentication dependency used by every
protected route:

```
Authorization: Bearer <jwt>
        │
        ├─ decode (signature + exp verified)  ── fail ─► 401 "Invalid or expired token"
        │
        ├─ load users.sub                       ── fail ─► 401 "User not found"
        │
        └─ load memberships for that user       ── fail ─► 403 "User has no tenant membership"
                    │
                    ▼
        {"id", "email", "tenant_id", "role"}
```

`GET /auth/me` returns exactly that object, so clients never guess their
scope.

---

## 3. Tenant isolation (the core guarantee)

Isolation is enforced by **derivation, not by assertion**. The tenant is
never read from a request body, query parameter or header:

- `tenant_id` comes from `memberships.tenant_id` for the authenticated
  user, resolved server-side on every request.
- Every relational read filters on it: documents, ingestion jobs,
  workspaces, permissions, audit logs.
- **Vector reads**: `build_filter()` raises `ValueError` when
  `tenant_id` is absent, and always injects
  `metadata.tenant_id == <tenant>` as a `must` condition. There is no
  code path that queries Qdrant without it.
- **Lexical reads**: BM25 candidates are selected by scrolling Qdrant
  *with that same filter*, so an unscoped corpus never exists.
- **Fusion/reranking**: both operate on already-filtered lists.
- **Legacy points** without `tenant_id` are fail-closed — invisible to
  every query — and are repaired in place by
  `backend/migrate_legacy_points.py` (never by deleting a collection).

A cross-tenant read would require the membership row itself to be wrong,
which is a database-integrity problem, not an application-logic one.

---

## 4. Authorisation

Two independent layers.

### 4.1 Tenant roles (`memberships.role`)

`owner` · `admin` · `member`, with `ADMIN_ROLES = {"owner","admin"}`.

| Operation | Required |
|---|---|
| Register / login / `/auth/me` | any authenticated user |
| Upload, query, status, own documents | any member |
| `GET /documents/{id}/versions` | member with access to the document |
| `POST /workspaces` | `owner` or `admin` |
| `POST/GET/DELETE …/permissions` | `owner` or `admin` |
| `GET /audit/logs` | `owner` or `admin` |

### 4.2 Workspace permissions

`PERMISSION_LEVELS = {read:1, write:2, admin:3}`. A grant targets
**exactly one** of `user_id` (direct) or `role` (applies to all holders
of that role). `effective_level()` returns the maximum level across
direct and role grants:

```
effective_level(user, workspace)
    = max(level(p) for p in permissions where
          p.workspace_id == workspace.id
          and (p.user_id == user.id or p.role == user.role))
```

Numeric ordering means "does this grant satisfy a `write`
requirement?" is a single comparison (`level >= 2`) rather than a set
membership test, which stays correct when new levels are inserted.

### 4.3 Resource ownership on read

Reads are authorised per resource, not per route: the status endpoint
loads the job's document and returns `403` when
`document.tenant_id != current_user.tenant_id`; workspace lookups use
`_get_workspace(db, id, tenant_id)` which `404`s on cross-tenant ids
(404 rather than 403 so existence is not disclosed).

---

## 5. Input validation & upload safety

| Control | Implementation | Status |
|---|---|---|
| Extension allow-list | `.pdf` only → `400` | ✅ |
| Empty payload | rejected → `400` | ✅ |
| Size ceiling | 25 MB → `413` | ✅ |
| Filename sanitisation | `Path(file.filename).name`; stored as `<uuid4hex>_<name>` | ✅ |
| Filename collision | uuid prefix makes stored names unique | ✅ |
| Workspace ownership | optional `workspace_id` verified against the caller's tenant → `404` | ✅ |
| Path traversal | keys are composed from the sanitised basename, never from raw input | ✅ |
| Query length | `Field(min_length=1, max_length=5000)` | ✅ |
| `k` bounds | `ge=1, le=20` | ✅ |
| Permission `level` | `pattern="^(read\|write\|admin)$"` | ✅ |
| Rate limiting | — | ❌ planned |
| Virus / content-type scan | — | ❌ planned |

Validation happens **before** any storage write or task enqueue, so a
rejected upload leaves no trace to clean up.

---

## 6. Audit trail

`audit.record(db, action=…, tenant_id=…, user_id=…, resource_type=…,
resource_id=…, detail=…, request=…)` appends to `audit_logs`.

Design properties:

- **Append-only** — entries are written, never updated or deleted.
- **Never raises** — failures are caught, rolled back and logged as
  `audit_record_failed`. Auditing must not break the operation it
  observes, and a silent audit gap must not become an outage.
- **Tenant-scoped reads** — `/audit/logs` filters on
  `tenant_id = current_user["tenant_id"]` and requires an admin role.
- Records `ip_address` (via `client_ip(request)`) and `created_at`.

Events captured include registrations, logins, document uploads (with
`version=` and `sha256=<12 hex prefix>` in `detail`), queries (including
the `workspace_id` scope used) and permission changes.

---

## 7. Secrets & configuration governance

All secrets and endpoints are environment variables, never literals:

| Variable | Purpose | Risk if defaulted |
|---|---|---|
| `JWT_SECRET_KEY` | token signing | **critical** — falls back to `"change-this-secret-in-production"`; must be set in any real deployment |
| `DATABASE_URL` | PostgreSQL | credentials in URL |
| `QDRANT_URL` / `QDRANT_API_KEY` | vector store | remote data plane |
| `S3_ACCESS_KEY_ID` / `S3_SECRET_ACCESS_KEY` | object storage | bucket access |
| `OLLAMA_BASE_URL` | model host | — |

The JWT default is safe for local development and **unsafe in
production**; it is the single highest-priority configuration item in
[09 roadmap](09-roadmap-and-trade-offs.md).

---

## 8. Observability surface & exposure

`GET /metrics` (`json` or `prometheus`) and `GET /health`,
`/health/ready` are currently **unauthenticated**, which is normal for
cluster-internal probes but means they must not be published directly to
the internet. `/health/ready` discloses dependency names and, for
Qdrant/Ollama, the collection and model lists. Restricting these to an
internal network or requiring authentication for the detailed variants
is a planned hardening step.

---

## 9. Governance controls to add

| Control | Why | Priority |
|---|---|---|
| Set `JWT_SECRET_KEY`; rotate on schedule | prevents token forgery | P0 |
| Rate limiting on `/auth/login` and `/query` | credential stuffing / cost abuse | P0 |
| Refresh tokens + revocation denylist | 60-min sessions are user-hostile and unrevocable | P1 |
| CORS allow-list | no `CORSMiddleware` is configured today; browsers will be blocked once a React/Next.js UI is added | P1 |
| Restrict or authenticate `/metrics` | information disclosure | P1 |
| Malware scanning on upload | untrusted PDFs | P2 |
| Per-tenant quotas (docs, tokens, storage) | noisy-neighbour and cost control | P2 |
| Audit retention & export policy | compliance | P2 |
| Field-level encryption / KMS for secrets | defence in depth | P3 |
| SSO / OIDC + SCIM provisioning | enterprise onboarding | P3 |
