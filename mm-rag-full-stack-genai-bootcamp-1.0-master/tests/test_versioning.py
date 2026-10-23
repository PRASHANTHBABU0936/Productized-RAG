"""Document versioning and duplicate-detection tests."""

from backend.models import Document


def _upload(client, headers, data, filename="contract.pdf"):
    return client.post(
        "/documents/upload",
        headers=headers,
        files={"file": (filename, data, "application/pdf")},
    )


def _mark_ready(session_factory, document_id):
    session = session_factory()
    try:
        document = session.get(Document, document_id)
        document.status = "ready"
        session.commit()
    finally:
        session.close()


def test_unchanged_reupload_is_skipped(client, auth_headers, pdf_bytes, session_factory):
    headers = auth_headers()
    first = _upload(client, headers, pdf_bytes).json()
    _mark_ready(session_factory, first["document_id"])

    second = _upload(client, headers, pdf_bytes).json()

    assert second["duplicate"] is True
    assert second["version_number"] == 1
    assert second["document_id"] == first["document_id"]


def test_changed_content_creates_new_version(client, auth_headers, pdf_bytes):
    headers = auth_headers()
    first = _upload(client, headers, pdf_bytes).json()
    second = _upload(client, headers, pdf_bytes + b"% rev2").json()

    assert second["version_number"] == 2
    assert second["document_id"] == first["document_id"]
    assert second["file_hash"] != first["file_hash"]


def test_unchanged_reupload_of_unindexed_document_is_reprocessed(
    client, auth_headers, pdf_bytes
):
    """Same bytes but the document never reached 'ready': not a duplicate."""
    headers = auth_headers()
    first = _upload(client, headers, pdf_bytes).json()
    second = _upload(client, headers, pdf_bytes).json()

    assert second.get("duplicate") is not True
    assert second["version_number"] == 2


def test_version_history_is_ordered_and_marks_current(
    client, auth_headers, pdf_bytes
):
    headers = auth_headers()
    first = _upload(client, headers, pdf_bytes).json()
    _upload(client, headers, pdf_bytes + b"% rev2")

    history = client.get(
        f"/documents/{first['document_id']}/versions", headers=headers
    )
    assert history.status_code == 200

    body = history.json()
    assert body["total"] == 2
    assert body["filename"] == "contract.pdf"

    newest, oldest = body["versions"]
    assert newest["version_number"] == 2
    assert newest["is_current"] is True
    assert oldest["version_number"] == 1
    assert oldest["is_current"] is False


def test_version_history_is_tenant_isolated(client, auth_headers, pdf_bytes):
    owner = auth_headers("vowner@example.com")
    document_id = _upload(client, owner, pdf_bytes).json()["document_id"]

    intruder = auth_headers("vintruder@example.com")
    response = client.get(
        f"/documents/{document_id}/versions", headers=intruder
    )
    assert response.status_code == 404
