from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


# --------------------------------------------------
# Tenants
# --------------------------------------------------

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan",
    )



# --------------------------------------------------
# Users
# --------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        unique=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


# --------------------------------------------------
# Memberships
# --------------------------------------------------

class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="member",
    )

    user: Mapped["User"] = relationship(
        back_populates="memberships",
    )

    tenant: Mapped["Tenant"] = relationship(
        back_populates="memberships",
    )


# --------------------------------------------------
# Documents
# --------------------------------------------------

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    workspace_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("workspaces.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
    )

    file_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    file_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
    )

    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    ingestion_jobs: Mapped[list["IngestionJob"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )

    versions: Mapped[list["DocumentVersion"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentVersion.version_number",
    )


# --------------------------------------------------
# Workspaces
# --------------------------------------------------

class Workspace(Base):
    """Logical grouping of documents inside a tenant."""

    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    permissions: Mapped[list["Permission"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )


# --------------------------------------------------
# Permissions
# --------------------------------------------------

class Permission(Base):
    """
    Grant of a permission level to a user or a role on a workspace.

    Exactly one of ``user_id`` / ``role`` is expected to be set:
    a role grant applies to every member with that role.
    """

    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    workspace_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    role: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="read",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    workspace: Mapped["Workspace"] = relationship(
        back_populates="permissions",
    )


# --------------------------------------------------
# Document Versions
# --------------------------------------------------

class DocumentVersion(Base):
    """
    Immutable record of one uploaded revision of a document.

    ``Document`` keeps pointing at the current revision so retrieval and
    tenant scoping are unaffected; this table preserves the full history
    and is what incremental re-ingestion is driven from.
    """

    __tablename__ = "document_versions"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "version_number",
            name="uq_document_version",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
    )

    file_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    file_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    size_bytes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="uploaded",
    )

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_by: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    document: Mapped["Document"] = relationship(
        back_populates="versions",
    )

# --------------------------------------------------
# Ingestion Jobs
# --------------------------------------------------

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    celery_task_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
    )

    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    document: Mapped["Document"] = relationship(
        back_populates="ingestion_jobs",
    )


# --------------------------------------------------
# Audit Log
# --------------------------------------------------

class AuditLog(Base):
    """Append-only record of security-relevant tenant activity."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    user_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    resource_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    detail: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )