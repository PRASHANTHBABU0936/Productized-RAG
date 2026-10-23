from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from uuid import uuid4
import asyncio
import hashlib
import os
import time

from dotenv import load_dotenv

# Load .env before importing modules that read configuration at import time
# (backend.auth reads JWT_SECRET_KEY, backend.storage reads the S3 settings).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends,
    Query,
    Request,
)
from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from celery.result import AsyncResult
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend import audit, observability
from backend.worker import ingest_document
from backend.database import get_db
from backend.storage import get_storage, upload_key, parsed_prefix

from backend.models import (
    AuditLog,
    Document,
    DocumentVersion,
    IngestionJob,
    Permission,
    User,
    Tenant,
    Workspace,
    Membership,
)

from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

from backend.schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
)

# src.ingestion and src.generation transitively import PyTorch (via
# sentence-transformers) and EasyOCR. Loading those native libraries into the
# always-on API process means a single native fault (a mismatched c10.dll /
# MSVC runtime from a second Python install) kills the whole service with an
# access violation and no Python traceback. The RAG pipeline is therefore
# imported lazily, where it is actually used.


# --------------------------------------------------
# Application
# --------------------------------------------------

app = FastAPI(
    title="MM-RAG API",
    description="Backend API for the MM-RAG application",
    version="1.0.0",
)


security = HTTPBearer()


# A job that no worker picks up within this window is reported as
# failed, so the UI never polls forever.
STALE_JOB_SECONDS = 300

# A job whose worker died mid-pipeline stops writing progress. When Celery
# still reports the task as running we allow a longer ceiling before
# declaring it dead, because a large PDF can legitimately spend a long time
# inside a single stage without touching the database.
STALLED_JOB_SECONDS = int(
    os.getenv("STALLED_JOB_SECONDS", "900")
)

# Stages the worker writes while a task is actively running.
IN_PROGRESS_STAGES = {"parsing", "chunking", "indexing", "retrying"}

# Statuses that mean "no worker has claimed this job yet".
UNCLAIMED_STATUSES = {None, "", "PENDING", "QUEUED", "uploaded"}


def _job_age_seconds(job: "IngestionJob", reference: datetime | None) -> float:
    """Seconds since ``reference`` (defaults to the job's creation)."""
    reference = reference or job.created_at

    if reference is not None and reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)

    if reference is None:
        return 0.0

    return (datetime.now(timezone.utc) - reference).total_seconds()


# --------------------------------------------------
# Authentication Dependency
# --------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    membership = (
        db.query(Membership)
        .filter(Membership.user_id == user.id)
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="User has no tenant membership",
        )

    return {
        "id": user.id,
        "email": user.email,
        "tenant_id": membership.tenant_id,
        "role": membership.role,
    }


# --------------------------------------------------
# Current User
# --------------------------------------------------

@app.get("/auth/me")
def auth_me(
    current_user: dict = Depends(get_current_user),
):
    return current_user


# --------------------------------------------------
# Reusable RAG components
# --------------------------------------------------

@lru_cache(maxsize=1)
def get_generator():
    # Imported on first use so PyTorch stays out of the API startup path.
    from src.generation import MultimodalRAGGenerator

    return MultimodalRAGGenerator()


# --------------------------------------------------
# Request schema
# --------------------------------------------------

class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    k: int = Field(
        default=6,
        ge=1,
        le=20,
    )

    workspace_id: str | None = Field(
        default=None,
    )


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health_check():
    """Liveness probe: the process is up."""
    return {
        "status": "healthy",
        "service": "mm-rag-backend",
    }


@app.get("/health/ready")
def readiness_check():
    """
    Readiness probe: the API can serve traffic.

    Pings every dependency (PostgreSQL, Redis, Qdrant, Ollama) so an
    orchestrator can hold traffic until the stack is actually usable.
    """
    report = observability.readiness()

    if report["status"] != "ready":
        raise HTTPException(
            status_code=503,
            detail=report,
        )

    return report


# --------------------------------------------------
# Metrics
# --------------------------------------------------

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Time every request and feed the metrics registry."""
    started = time.perf_counter()

    try:
        response = await call_next(request)

    except Exception:
        observability.record_request(
            request.method,
            request.url.path,
            500,
            (time.perf_counter() - started) * 1000.0,
        )
        raise

    # Prefer the route template (e.g. /documents/status/{job_id}) so
    # path parameters don't explode the metric cardinality.
    route = request.scope.get("route")
    path = getattr(route, "path", None) or request.url.path

    observability.record_request(
        request.method,
        path,
        response.status_code,
        (time.perf_counter() - started) * 1000.0,
    )

    return response


@app.get("/metrics")
def metrics(format: str = Query("json", pattern="^(json|prometheus)$")):
    """Request counters and latency percentiles."""
    if format == "prometheus":
        return PlainTextResponse(
            observability.render_prometheus(),
            media_type="text/plain; version=0.0.4",
        )

    return observability.snapshot()


# ==================================================
# AUTHENTICATION
# ==================================================

# --------------------------------------------------
# Register User
# --------------------------------------------------

@app.post(
    "/auth/register",
    response_model=RegisterResponse,
)
def register_user(
    request: RegisterRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    # Check whether the email is already registered
    existing_user = (
        db.query(User)
        .filter(User.email == request.email.lower())
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered",
        )

    try:
        # --------------------------------------------------
        # Create tenant/workspace
        # --------------------------------------------------

        tenant = Tenant(
            name=f"{request.email.split('@')[0]}'s Workspace"
        )

        db.add(tenant)
        db.flush()

        # --------------------------------------------------
        # Create user
        # --------------------------------------------------

        user = User(
            email=request.email.lower(),
            password_hash=hash_password(request.password),
            is_active=True,
        )

        db.add(user)
        db.flush()

        # --------------------------------------------------
        # Create membership
        # --------------------------------------------------

        membership = Membership(
            user_id=user.id,
            tenant_id=tenant.id,
            role="owner",
        )

        db.add(membership)

        # --------------------------------------------------
        # Save everything
        # --------------------------------------------------

        db.commit()

        audit.record(
            db,
            action="auth.register",
            tenant_id=tenant.id,
            user_id=user.id,
            resource_type="user",
            resource_id=user.id,
            detail=f"role={membership.role}",
            request=http_request,
        )

        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "tenant_id": tenant.id,
                "role": membership.role,
            },
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(exc)}",
        ) from exc


# --------------------------------------------------
# Login User
# --------------------------------------------------

@app.post(
    "/auth/login",
    response_model=LoginResponse,
)
def login_user(
    request: LoginRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------
    # Find user
    # --------------------------------------------------

    user = (
        db.query(User)
        .filter(User.email == request.email.lower())
        .first()
    )

    if not user:
        audit.record(
            db,
            action="auth.login_failed",
            tenant_id=None,
            detail=f"unknown email: {request.email.lower()}",
            request=http_request,
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # --------------------------------------------------
    # Resolve the tenant up front so failed attempts are
    # attributable to the right audit trail.
    # --------------------------------------------------

    membership = (
        db.query(Membership)
        .filter(Membership.user_id == user.id)
        .first()
    )

    tenant_id = membership.tenant_id if membership else None

    # --------------------------------------------------
    # Check account status
    # --------------------------------------------------

    if not user.is_active:
        audit.record(
            db,
            action="auth.login_failed",
            tenant_id=tenant_id,
            user_id=user.id,
            detail="account inactive",
            request=http_request,
        )

        raise HTTPException(
            status_code=403,
            detail="User account is inactive",
        )

    # --------------------------------------------------
    # Verify password
    # --------------------------------------------------

    if not verify_password(
        request.password,
        user.password_hash,
    ):
        audit.record(
            db,
            action="auth.login_failed",
            tenant_id=tenant_id,
            user_id=user.id,
            detail="invalid password",
            request=http_request,
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # --------------------------------------------------
    # Create JWT access token
    # --------------------------------------------------

    access_token = create_access_token(
        user_id=user.id,
    )

    audit.record(
        db,
        action="auth.login",
        tenant_id=tenant_id,
        user_id=user.id,
        resource_type="user",
        resource_id=user.id,
        request=http_request,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ==================================================
# DOCUMENT INGESTION
# ==================================================

# --------------------------------------------------
# PDF Upload + Async Ingestion API
# --------------------------------------------------

@app.post("/documents/upload")
async def upload_document(
    http_request: Request,
    file: UploadFile = File(...),
    collection_name: str | None = Form(None),
    workspace_id: str | None = Form(None),
    chunk_size: int = Form(2000),
    chunk_overlap: int = Form(120),
    replace_existing: bool = Form(True),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    if Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported",
        )

    original_filename = Path(file.filename).name

    safe_filename = f"{uuid4().hex}_{original_filename}"

    storage = get_storage()
    pdf_key = upload_key(safe_filename)
    output_prefix = parsed_prefix(Path(safe_filename).stem)

    try:
        # --------------------------------------------------
        # Read uploaded PDF
        # --------------------------------------------------

        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty",
            )

        if len(contents) > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="PDF exceeds the 25 MB limit",
            )

        # --------------------------------------------------
        # Validate the optional workspace
        # --------------------------------------------------

        if workspace_id:
            workspace = (
                db.query(Workspace)
                .filter(
                    Workspace.id == workspace_id,
                    Workspace.tenant_id == current_user["tenant_id"],
                )
                .first()
            )

            if workspace is None:
                raise HTTPException(
                    status_code=404,
                    detail="Workspace not found",
                )

        # --------------------------------------------------
        # Persist uploaded PDF to object storage
        # --------------------------------------------------

        file_hash = hashlib.sha256(contents).hexdigest()

        storage.save_bytes(pdf_key, contents)

        # --------------------------------------------------
        # Resolve the logical document.
        #
        # A re-upload of the same filename within the tenant (and
        # workspace, when given) is a new *version* of the same
        # document, not a duplicate document.
        # --------------------------------------------------

        document_query = db.query(Document).filter(
            Document.tenant_id == current_user["tenant_id"],
            Document.filename == original_filename,
        )

        if workspace_id:
            document_query = document_query.filter(
                Document.workspace_id == workspace_id
            )

        document = document_query.first()

        current_version: DocumentVersion | None = None

        if document is not None:
            current_version = (
                db.query(DocumentVersion)
                .filter(
                    DocumentVersion.document_id == document.id,
                    DocumentVersion.is_current.is_(True),
                )
                .first()
            )

            # Same bytes AND already indexed: nothing to redo.
            if (
                current_version is not None
                and current_version.file_hash == file_hash
                and document.status == "ready"
            ):
                storage.delete(pdf_key)

                return {
                    "message": "Document already ingested",
                    "document_id": document.id,
                    "version_number": current_version.version_number,
                    "duplicate": True,
                    "status": document.status,
                }

            version_number = (
                current_version.version_number + 1
                if current_version is not None
                else 1
            )

            (
                db.query(DocumentVersion)
                .filter(DocumentVersion.document_id == document.id)
                .update({"is_current": False})
            )

            # Document now points at the newest revision.
            document.stored_filename = safe_filename
            document.file_path = pdf_key
            document.file_hash = file_hash
            document.status = "uploaded"
            document.error = None

        else:
            version_number = 1

            document = Document(
                tenant_id=current_user["tenant_id"],
                workspace_id=workspace_id,
                filename=original_filename,
                stored_filename=safe_filename,
                file_path=pdf_key,
                file_hash=file_hash,
                status="uploaded",
            )

            db.add(document)
            db.flush()

        version = DocumentVersion(
            document_id=document.id,
            version_number=version_number,
            stored_filename=safe_filename,
            file_path=pdf_key,
            file_hash=file_hash,
            size_bytes=len(contents),
            status="uploaded",
            is_current=True,
            created_by=current_user["id"],
        )

        db.add(version)
        db.commit()
        db.refresh(document)
        db.refresh(version)

        # --------------------------------------------------
        # Generate Celery task ID BEFORE queueing
        # --------------------------------------------------

        celery_task_id = str(uuid4())

        # --------------------------------------------------
        # Create persistent ingestion job
        # --------------------------------------------------

        job = IngestionJob(
            document_id=document.id,
            celery_task_id=celery_task_id,
            status="uploaded",
        )

        db.add(job)

        # --------------------------------------------------
        # IMPORTANT:
        # Commit PostgreSQL BEFORE sending the task to Redis.
        # This guarantees that the Celery worker can find
        # the job when it starts.
        # --------------------------------------------------

        db.commit()
        db.refresh(job)

        # --------------------------------------------------
        # Queue Celery ingestion job
        # --------------------------------------------------

        ingest_document.apply_async(
            kwargs={
                "storage_key": pdf_key,
                "output_prefix": output_prefix,
                "collection_name": collection_name,
                "workspace_id": document.workspace_id,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "replace_existing": replace_existing,
            },
            task_id=celery_task_id,
        )

        audit.record(
            db,
            action="document.upload",
            tenant_id=current_user["tenant_id"],
            user_id=current_user["id"],
            resource_type="document",
            resource_id=document.id,
            detail=(
                f"filename={original_filename} "
                f"version={version_number} "
                f"sha256={file_hash[:12]} "
                f"bytes={len(contents)} "
                f"task_id={celery_task_id}"
            ),
            request=http_request,
        )

        return {
            "message": "Document ingestion started",
            "document_id": document.id,
            "job_id": job.id,
            "celery_task_id": celery_task_id,
            "version_id": version.id,
            "version_number": version_number,
            "file_hash": file_hash,
            "workspace_id": document.workspace_id,
            "filename": original_filename,
            "stored_filename": safe_filename,
            "tenant_id": document.tenant_id,
            "status": "uploaded",
        }

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()

        storage.delete(pdf_key)

        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue document ingestion: {str(exc)}",
        ) from exc

    finally:
        await file.close()


# --------------------------------------------------
# Document Ingestion Status API
# --------------------------------------------------

@app.get("/documents/status/{job_id}")
async def document_status(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = (
        db.query(IngestionJob)
        .filter(IngestionJob.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Ingestion job not found",
        )

    # --------------------------------------------------
    # Tenant authorization
    # --------------------------------------------------

    document = (
        db.query(Document)
        .filter(Document.id == job.document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    if document.tenant_id != current_user["tenant_id"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this document",
        )

    # --------------------------------------------------
    # Get Celery status
    # --------------------------------------------------

    celery_result = AsyncResult(
        job.celery_task_id,
        app=ingest_document.app,
    )

    # --------------------------------------------------
    # Synchronize status with Celery
    #
    # The worker owns the intermediate stages
    # (parsing / chunking / indexing). The API only resolves the
    # terminal states and fails jobs that no worker ever picked up.
    # --------------------------------------------------

    celery_status = celery_result.status

    if celery_status == "SUCCESS":
        job.status = "ready"
        job.error = None

    elif celery_status == "FAILURE":
        job.status = "failed"
        job.error = str(celery_result.result)

    elif job.status in UNCLAIMED_STATUSES:
        # Still queued: has any worker picked this up yet?
        if _job_age_seconds(job, job.created_at) > STALE_JOB_SECONDS:
            job.status = "failed"
            job.error = (
                f"No Celery worker picked up this job within "
                f"{STALE_JOB_SECONDS}s. "
                f"Check that the worker is running."
            )
        else:
            job.status = "queued"

    elif job.status in IN_PROGRESS_STAGES:
        # The worker owns this stage. If it died without writing a terminal
        # state (crash, OOM, killed container) nothing will ever advance the
        # job, so fail it instead of letting the UI poll forever.
        ceiling = (
            STALE_JOB_SECONDS
            if celery_status in {"PENDING", "REVOKED"}
            else STALLED_JOB_SECONDS
        )

        if _job_age_seconds(job, job.updated_at) > ceiling:
            stalled_stage = job.status

            job.status = "failed"
            job.error = (
                f"Ingestion stalled at '{stalled_stage}' for more than "
                f"{ceiling}s with no worker progress; the worker "
                f"appears to have stopped. Re-upload the document "
                f"to retry."
            )

    db.commit()

    # --------------------------------------------------
    # Update related document
    # --------------------------------------------------

    document.status = job.status
    document.error = job.error

    db.commit()

    # --------------------------------------------------
    # Response
    # --------------------------------------------------

    response = {
        "job_id": job.id,
        "document_id": job.document_id,
        "celery_task_id": job.celery_task_id,
        "tenant_id": document.tenant_id,
        "status": job.status,
    }

    if job.error:
        response["error"] = job.error

    if celery_result.successful():
        response["result"] = celery_result.result

    return response


# ==================================================
# RAG QUERY
# ==================================================

# --------------------------------------------------
# RAG Query API
# --------------------------------------------------

@app.post("/query")
async def query_documents(
    request: QueryRequest,
    http_request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    if request.workspace_id:
        _get_workspace(
            db,
            request.workspace_id,
            current_user["tenant_id"],
        )

    try:
        generator = get_generator()

        result = await asyncio.to_thread(
            generator.generate,
            query=question,
            tenant_id=current_user["tenant_id"],
            k=request.k,
            workspace_id=request.workspace_id,
        )

        # Persist token usage and cost so /metrics reports spend that
        # survives a restart.
        observability.record_usage(
            model=result.get("model_name"),
            usage=result.get("usage"),
        )

        audit.record(
            db,
            action="query.answer",
            tenant_id=current_user["tenant_id"],
            user_id=current_user["id"],
            resource_type="query",
            detail=(
                f"question={question[:200]} "
                f"k={request.k} "
                f"workspace_id={request.workspace_id} "
                f"retrieval_count={result.get('retrieval_count')}"
            ),
            request=http_request,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Query generation failed: {str(exc)}",
        ) from exc


# ==================================================
# AUDIT TRAIL
# ==================================================

@app.get("/audit/logs")
def list_audit_logs(
    action: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the tenant's audit trail, newest first."""
    if current_user["role"] not in {"owner", "admin"}:
        raise HTTPException(
            status_code=403,
            detail="Audit logs require the owner or admin role",
        )

    query = db.query(AuditLog).filter(
        AuditLog.tenant_id == current_user["tenant_id"]
    )

    if action:
        query = query.filter(AuditLog.action == action)

    total = query.count()

    entries = (
        query.order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "entries": [
            {
                "id": entry.id,
                "action": entry.action,
                "user_id": entry.user_id,
                "resource_type": entry.resource_type,
                "resource_id": entry.resource_id,
                "detail": entry.detail,
                "ip_address": entry.ip_address,
                "created_at": entry.created_at,
            }
            for entry in entries
        ],
    }


# ==================================================
# WORKSPACES & PERMISSIONS
# ==================================================

# Ordered from least to most privileged so a numeric comparison can
# decide whether one grant satisfies another.
PERMISSION_LEVELS = {
    "read": 1,
    "write": 2,
    "admin": 3,
}

ADMIN_ROLES = {"owner", "admin"}


class WorkspaceRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class PermissionRequest(BaseModel):
    level: str = Field(..., pattern="^(read|write|admin)$")
    user_id: str | None = None
    role: str | None = None


def _require_admin(current_user: dict) -> None:
    if current_user["role"] not in ADMIN_ROLES:
        raise HTTPException(
            status_code=403,
            detail="This action requires the owner or admin role",
        )


def _get_workspace(
    db: Session,
    workspace_id: str,
    tenant_id: str,
) -> Workspace:
    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id,
            Workspace.tenant_id == tenant_id,
        )
        .first()
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found",
        )

    return workspace


def effective_level(db: Session, current_user: dict) -> str | None:
    """
    Highest workspace permission level held by the user, or ``None``
    when the user has no explicit grant.

    An explicit ``user_id`` grant wins over a ``role`` grant of the
    same level.
    """
    grants = (
        db.query(Permission)
        .filter(
            Permission.tenant_id == current_user["tenant_id"],
            (Permission.user_id == current_user["id"])
            | (Permission.role == current_user["role"]),
        )
        .all()
    )

    if not grants:
        return None

    return max(
        (grant.level for grant in grants),
        key=lambda level: PERMISSION_LEVELS.get(level, 0),
    )


@app.post("/workspaces")
def create_workspace(
    request: WorkspaceRequest,
    http_request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)

    workspace = Workspace(
        tenant_id=current_user["tenant_id"],
        name=request.name,
        description=request.description,
    )

    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    audit.record(
        db,
        action="workspace.create",
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        resource_type="workspace",
        resource_id=workspace.id,
        detail=f"name={workspace.name}",
        request=http_request,
    )

    return {
        "id": workspace.id,
        "tenant_id": workspace.tenant_id,
        "name": workspace.name,
        "description": workspace.description,
        "created_at": workspace.created_at,
    }


@app.get("/workspaces")
def list_workspaces(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workspaces = (
        db.query(Workspace)
        .filter(
            Workspace.tenant_id == current_user["tenant_id"]
        )
        .order_by(Workspace.created_at.desc())
        .all()
    )

    document_counts = dict(
        db.query(Document.workspace_id, func.count(Document.id))
        .filter(Document.tenant_id == current_user["tenant_id"])
        .group_by(Document.workspace_id)
        .all()
    )

    return {
        "total": len(workspaces),
        "workspaces": [
            {
                "id": workspace.id,
                "name": workspace.name,
                "description": workspace.description,
                "document_count": document_counts.get(
                    workspace.id,
                    0,
                ),
                "created_at": workspace.created_at,
            }
            for workspace in workspaces
        ],
    }


@app.post("/workspaces/{workspace_id}/permissions")
def grant_permission(
    workspace_id: str,
    request: PermissionRequest,
    http_request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)

    workspace = _get_workspace(
        db,
        workspace_id,
        current_user["tenant_id"],
    )

    if (request.user_id is None) == (request.role is None):
        raise HTTPException(
            status_code=400,
            detail="Provide exactly one of user_id or role",
        )

    if request.user_id is not None:
        user = (
            db.query(User)
            .filter(User.id == request.user_id)
            .first()
        )

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        in_tenant = (
            db.query(Membership)
            .filter(
                Membership.user_id == user.id,
                Membership.tenant_id == current_user["tenant_id"],
            )
            .first()
        )

        if in_tenant is None:
            raise HTTPException(
                status_code=400,
                detail="User does not belong to this tenant",
            )

    permission = Permission(
        tenant_id=current_user["tenant_id"],
        workspace_id=workspace.id,
        user_id=request.user_id,
        role=request.role,
        level=request.level,
    )

    db.add(permission)
    db.commit()
    db.refresh(permission)

    audit.record(
        db,
        action="permission.grant",
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        resource_type="workspace",
        resource_id=workspace.id,
        detail=(
            f"level={permission.level} "
            f"user_id={permission.user_id} "
            f"role={permission.role}"
        ),
        request=http_request,
    )

    return {
        "id": permission.id,
        "workspace_id": permission.workspace_id,
        "user_id": permission.user_id,
        "role": permission.role,
        "level": permission.level,
        "created_at": permission.created_at,
    }


@app.get("/workspaces/{workspace_id}/permissions")
def list_permissions(
    workspace_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workspace = _get_workspace(
        db,
        workspace_id,
        current_user["tenant_id"],
    )

    permissions = (
        db.query(Permission)
        .filter(Permission.workspace_id == workspace.id)
        .order_by(Permission.created_at.desc())
        .all()
    )

    return {
        "workspace_id": workspace.id,
        "total": len(permissions),
        "permissions": [
            {
                "id": permission.id,
                "user_id": permission.user_id,
                "role": permission.role,
                "level": permission.level,
                "created_at": permission.created_at,
            }
            for permission in permissions
        ],
    }


@app.delete("/workspaces/{workspace_id}/permissions/{permission_id}")
def revoke_permission(
    workspace_id: str,
    permission_id: str,
    http_request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)

    workspace = _get_workspace(
        db,
        workspace_id,
        current_user["tenant_id"],
    )

    permission = (
        db.query(Permission)
        .filter(
            Permission.id == permission_id,
            Permission.workspace_id == workspace.id,
        )
        .first()
    )

    if permission is None:
        raise HTTPException(
            status_code=404,
            detail="Permission not found",
        )

    detail = (
        f"level={permission.level} "
        f"user_id={permission.user_id} "
        f"role={permission.role}"
    )

    db.delete(permission)
    db.commit()

    audit.record(
        db,
        action="permission.revoke",
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        resource_type="workspace",
        resource_id=workspace.id,
        detail=detail,
        request=http_request,
    )

    return {"deleted": True, "permission_id": permission_id}


# ==================================================
# DOCUMENT VERSIONS
# ==================================================

def _public_version(version: DocumentVersion) -> dict:
    return {
        "id": version.id,
        "document_id": version.document_id,
        "version_number": version.version_number,
        "file_hash": version.file_hash,
        "size_bytes": version.size_bytes,
        "status": version.status,
        "is_current": version.is_current,
        "created_by": version.created_by,
        "created_at": version.created_at,
    }


@app.get("/documents/{document_id}/versions")
def list_document_versions(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.tenant_id == current_user["tenant_id"],
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    versions = (
        db.query(DocumentVersion)
        .filter(DocumentVersion.document_id == document.id)
        .order_by(DocumentVersion.version_number.desc())
        .all()
    )

    return {
        "document_id": document.id,
        "filename": document.filename,
        "workspace_id": document.workspace_id,
        "total": len(versions),
        "versions": [_public_version(version) for version in versions],
    }
