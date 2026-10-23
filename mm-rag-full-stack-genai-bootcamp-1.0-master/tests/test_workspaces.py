"""Workspace and permission (RBAC) tests."""

from backend.models import Membership, User


def _upload(client, headers, data, workspace_id=None):
    data_fields = {"workspace_id": workspace_id} if workspace_id else None
    return client.post(
        "/documents/upload",
        headers=headers,
        data=data_fields,
        files={"file": ("contract.pdf", data, "application/pdf")},
    )


def _demote(session_factory, email, role="member"):
    session = session_factory()
    try:
        user = session.query(User).filter(User.email == email).first()
        membership = (
            session.query(Membership)
            .filter(Membership.user_id == user.id)
            .first()
        )
        membership.role = role
        session.commit()
    finally:
        session.close()


def test_workspace_lifecycle(client, auth_headers):
    headers = auth_headers()

    created = client.post(
        "/workspaces", headers=headers, json={"name": "Team Alpha"}
    )
    assert created.status_code == 200, created.text
    workspace_id = created.json()["id"]

    listing = client.get("/workspaces", headers=headers).json()
    assert listing["total"] == 1
    assert listing["workspaces"][0]["id"] == workspace_id
    assert listing["workspaces"][0]["document_count"] == 0


def test_workspace_document_count(client, auth_headers, pdf_bytes):
    headers = auth_headers()
    workspace_id = client.post(
        "/workspaces", headers=headers, json={"name": "Team Beta"}
    ).json()["id"]

    _upload(client, headers, pdf_bytes, workspace_id=workspace_id)

    listing = client.get("/workspaces", headers=headers).json()
    assert listing["workspaces"][0]["document_count"] == 1


def test_permission_grant_and_revoke(client, auth_headers):
    headers = auth_headers()
    workspace_id = client.post(
        "/workspaces", headers=headers, json={"name": "Team Gamma"}
    ).json()["id"]

    granted = client.post(
        f"/workspaces/{workspace_id}/permissions",
        headers=headers,
        json={"level": "read", "role": "member"},
    )
    assert granted.status_code == 200, granted.text
    permission_id = granted.json()["id"]

    listed = client.get(
        f"/workspaces/{workspace_id}/permissions", headers=headers
    ).json()
    assert listed["total"] == 1

    revoked = client.delete(
        f"/workspaces/{workspace_id}/permissions/{permission_id}",
        headers=headers,
    )
    assert revoked.status_code == 200
    assert revoked.json()["deleted"] is True

    after = client.get(
        f"/workspaces/{workspace_id}/permissions", headers=headers
    ).json()
    assert after["total"] == 0


def test_permission_requires_exactly_one_target(client, auth_headers):
    headers = auth_headers()
    workspace_id = client.post(
        "/workspaces", headers=headers, json={"name": "Team Delta"}
    ).json()["id"]

    response = client.post(
        f"/workspaces/{workspace_id}/permissions",
        headers=headers,
        json={"level": "read"},
    )
    assert response.status_code == 400


def test_permission_level_is_validated(client, auth_headers):
    headers = auth_headers()
    workspace_id = client.post(
        "/workspaces", headers=headers, json={"name": "Team Epsilon"}
    ).json()["id"]

    response = client.post(
        f"/workspaces/{workspace_id}/permissions",
        headers=headers,
        json={"level": "superuser", "role": "member"},
    )
    assert response.status_code == 422


def test_non_admin_cannot_create_workspace(
    client, auth_headers, session_factory
):
    headers = auth_headers("member@example.com")
    _demote(session_factory, "member@example.com", role="member")

    response = client.post(
        "/workspaces", headers=headers, json={"name": "Should Fail"}
    )
    assert response.status_code == 403


def test_workspace_access_is_tenant_isolated(client, auth_headers):
    owner = auth_headers("wsowner@example.com")
    workspace_id = client.post(
        "/workspaces", headers=owner, json={"name": "Private"}
    ).json()["id"]

    intruder = auth_headers("wsintruder@example.com")
    response = client.post(
        f"/workspaces/{workspace_id}/permissions",
        headers=intruder,
        json={"level": "read", "role": "member"},
    )
    assert response.status_code == 404
