"""API-level tests: auth, upload validation, job status, and query.

Celery and the LLM generator are mocked, so no Redis/Qdrant/Ollama is
required. The real end-to-end path is covered by the smoke script.
"""

from datetime import datetime, timedelta, timezone

import pytest

from backend.models import IngestionJob


def _patch_celery(monkeypatch, status="PENDING", result=None):
    from backend import main as main_module

    class _FakeResult:
        def __init__(self, *args, **kwargs):
            self.status = status
            self.result = result

        def successful(self):
            return self.status == "SUCCESS"

    monkeypatch.setattr(main_module, "AsyncResult", _FakeResult)


def _upload(client, headers, data, filename="contract.pdf"):
    return client.post(
        "/documents/upload",
        headers=headers,
        files={"file": (filename, data, "application/pdf")},
    )


def _set_job(
    session_factory,
    job_id,
    *,
    status=None,
    created_at=None,
    updated_at=None,
):
    session = session_factory()
    try:
        job = session.get(IngestionJob, job_id)
        if status is not None:
            job.status = status
        if created_at is not None:
            job.created_at = created_at
        if updated_at is not None:
            job.updated_at = updated_at
        session.commit()
    finally:
        session.close()


# ---------------------------------------------------------------------
# Health / auth
# ---------------------------------------------------------------------


def test_health_is_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_register_login_me_flow(client):
    register = client.post(
        "/auth/register",
        json={"email": "flow@example.com", "password": "password123"},
    )
    assert register.status_code in (200, 201), register.text
    user = register.json()["user"]
    assert user["email"] == "flow@example.com"
    assert user["tenant_id"]
    assert user["role"] in {"owner", "admin", "member", "viewer"}

    login = client.post(
        "/auth/login",
        json={"email": "flow@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me.status_code == 200
    assert me.json()["email"] == "flow@example.com"


def test_duplicate_registration_conflicts(client):
    payload = {"email": "dupe@example.com", "password": "password123"}
    client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)
    assert second.status_code == 409


def test_short_password_rejected(client):
    response = client.post(
        "/auth/register",
        json={"email": "short@example.com", "password": "abc"},
    )
    assert response.status_code == 422


def test_login_with_wrong_password_is_unauthorized(client):
    client.post(
        "/auth/register",
        json={"email": "right@example.com", "password": "password123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "right@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_login_with_unknown_user_is_unauthorized(client):
    response = client.post(
        "/auth/login",
        json={"email": "ghost@example.com", "password": "password123"},
    )
    assert response.status_code == 401


def test_protected_endpoint_requires_token(client):
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_forged_token_is_rejected(client):
    import jwt

    forged = jwt.encode({"sub": "someone"}, "not-the-real-secret", algorithm="HS256")
    response = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {forged}"}
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------
# Upload validation
# ---------------------------------------------------------------------


def test_upload_requires_authentication(client, pdf_bytes):
    response = client.post(
        "/documents/upload",
        files={"file": ("contract.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code in (401, 403)


def test_upload_rejects_non_pdf(client, auth_headers):
    response = client.post(
        "/documents/upload",
        headers=auth_headers(),
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_upload_rejects_empty_file(client, auth_headers):
    response = _upload(client, auth_headers(), b"")
    assert response.status_code == 400


def test_upload_rejects_oversized_file(client, auth_headers):
    oversized = b"0" * (25 * 1024 * 1024 + 1)
    response = _upload(client, auth_headers(), oversized)
    assert response.status_code == 413


def test_upload_rejects_unknown_workspace(client, auth_headers):
    response = client.post(
        "/documents/upload",
        headers=auth_headers(),
        data={"workspace_id": "does-not-exist"},
        files={"file": ("contract.pdf", b"%PDF-1.4 minimal", "application/pdf")},
    )
    assert response.status_code == 404


def test_upload_creates_document_job_and_version(client, auth_headers, pdf_bytes):
    response = _upload(client, auth_headers(), pdf_bytes)
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["status"] == "uploaded"
    assert body["version_number"] == 1
    assert body["job_id"]
    assert body["document_id"]
    assert len(body["file_hash"]) == 64


# ---------------------------------------------------------------------
# Job status: authorization + staleness guards
# ---------------------------------------------------------------------


def test_status_unknown_job_is_404(client, auth_headers):
    response = client.get(
        "/documents/status/does-not-exist", headers=auth_headers()
    )
    assert response.status_code == 404


def test_status_is_tenant_isolated(client, auth_headers, pdf_bytes):
    owner = auth_headers("owner@example.com")
    job_id = _upload(client, owner, pdf_bytes).json()["job_id"]

    intruder = auth_headers("intruder@example.com")
    response = client.get(
        f"/documents/status/{job_id}", headers=intruder
    )
    assert response.status_code == 403


def test_young_unclaimed_job_reports_queued(
    client, auth_headers, pdf_bytes, monkeypatch
):
    _patch_celery(monkeypatch, status="PENDING")
    job_id = _upload(client, auth_headers(), pdf_bytes).json()["job_id"]

    body = client.get(
        f"/documents/status/{job_id}", headers=auth_headers()
    ).json()
    assert body["status"] == "queued"


def test_stale_unclaimed_job_fails(
    client, auth_headers, pdf_bytes, session_factory, monkeypatch
):
    _patch_celery(monkeypatch, status="PENDING")
    headers = auth_headers()
    job_id = _upload(client, headers, pdf_bytes).json()["job_id"]

    old = datetime.now(timezone.utc) - timedelta(seconds=3600)
    _set_job(session_factory, job_id, created_at=old, updated_at=old)

    body = client.get(
        f"/documents/status/{job_id}", headers=headers
    ).json()
    assert body["status"] == "failed"
    assert "worker" in body["error"].lower()


def test_stalled_mid_pipeline_job_fails(
    client, auth_headers, pdf_bytes, session_factory, monkeypatch
):
    """A worker that dies during 'parsing' must not stall the UI forever."""
    _patch_celery(monkeypatch, status="STARTED")
    headers = auth_headers()
    payload = _upload(client, headers, pdf_bytes).json()

    old = datetime.now(timezone.utc) - timedelta(seconds=3600)
    _set_job(
        session_factory,
        payload["job_id"],
        status="parsing",
        created_at=old,
        updated_at=old,
    )

    body = client.get(
        f"/documents/status/{payload['job_id']}", headers=headers
    ).json()
    assert body["status"] == "failed"
    assert "parsing" in body["error"]


def test_active_parsing_job_stays_in_progress(
    client, auth_headers, pdf_bytes, session_factory, monkeypatch
):
    """A recently updated in-progress job must be left alone."""
    _patch_celery(monkeypatch, status="STARTED")
    headers = auth_headers()
    payload = _upload(client, headers, pdf_bytes).json()

    _set_job(session_factory, payload["job_id"], status="parsing")

    body = client.get(
        f"/documents/status/{payload['job_id']}", headers=headers
    ).json()
    assert body["status"] == "parsing"


def test_successful_celery_result_marks_job_ready(
    client, auth_headers, pdf_bytes, monkeypatch
):
    _patch_celery(monkeypatch, status="SUCCESS", result={"chunks": 4})
    headers = auth_headers()
    payload = _upload(client, headers, pdf_bytes).json()

    body = client.get(
        f"/documents/status/{payload['job_id']}", headers=headers
    ).json()
    assert body["status"] == "ready"


# ---------------------------------------------------------------------
# Query endpoint
# ---------------------------------------------------------------------


class _FakeGenerator:
    def generate(self, **kwargs):
        return {
            "query": kwargs["query"],
            "answer": "Grounded answer [contract.pdf p.1].",
            "sources": [
                {
                    "citation": "[contract.pdf p.1]",
                    "filename": "contract.pdf",
                    "page_number": 1,
                    "content_type": "text",
                }
            ],
            "used_images": [],
            "retrieval_count": 1,
            "model_name": "fake-model",
            "collection_name": "test-collection",
            "retrieval_mode": "hybrid",
            "usage": {
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
            },
        }


def test_query_requires_authentication(client):
    response = client.post("/query", json={"question": "What is X?"})
    assert response.status_code in (401, 403)


def test_query_rejects_empty_question(client, auth_headers):
    response = client.post(
        "/query", headers=auth_headers(), json={"question": ""}
    )
    assert response.status_code == 422


def test_query_rejects_blank_question(client, auth_headers):
    response = client.post(
        "/query", headers=auth_headers(), json={"question": "   "}
    )
    assert response.status_code == 400


def test_query_returns_grounded_answer(client, auth_headers, monkeypatch):
    from backend import main as main_module

    monkeypatch.setattr(main_module, "get_generator", lambda: _FakeGenerator())

    response = client.post(
        "/query",
        headers=auth_headers(),
        json={"question": "What is this document about?", "k": 3},
    )
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["answer"].startswith("Grounded answer")
    assert body["retrieval_count"] == 1
    assert body["sources"][0]["citation"] == "[contract.pdf p.1]"
    assert body["retrieval_mode"] == "hybrid"
