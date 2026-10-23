"""
Append-only audit trail for tenant activity.

Every security-relevant action (authentication, upload, ingestion
status change, query, permission change) is recorded with the acting
user, tenant, resource and client IP so a tenant admin can answer
"who did what, when".

``record`` never raises: an audit failure must not break the request
path. Failures are logged instead.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from backend.models import AuditLog

from logger.custom_logger import CustomLogger


logger = CustomLogger().get_logger(__name__)


def client_ip(request: Any) -> str | None:
    """Best-effort client IP, honouring reverse-proxy headers."""
    if request is None:
        return None

    forwarded = request.headers.get("x-forwarded-for")

    if forwarded:
        return forwarded.split(",")[0].strip()

    if request.client is not None:
        return request.client.host

    return None


def record(
    db: Session,
    *,
    action: str,
    tenant_id: str | None,
    user_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    detail: str | None = None,
    request: Any = None,
) -> None:
    """Persist one audit entry. Never raises."""
    try:
        db.add(
            AuditLog(
                tenant_id=str(tenant_id) if tenant_id else "unknown",
                user_id=str(user_id) if user_id else None,
                action=action,
                resource_type=resource_type,
                resource_id=(
                    str(resource_id) if resource_id else None
                ),
                detail=detail,
                ip_address=client_ip(request),
            )
        )
        db.commit()

    except Exception as exc:  # noqa: BLE001
        db.rollback()

        logger.warning(
            "audit_record_failed",
            action=action,
            error=str(exc),
        )
