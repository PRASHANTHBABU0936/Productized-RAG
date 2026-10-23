# from pathlib import Path
# from typing import Any
# import shutil
# import logging
# import tempfile

# from celery import Celery
# from sqlalchemy.orm import Session

# from backend.database import SessionLocal
# from backend.models import Document, DocumentVersion, IngestionJob
# from backend.storage import get_storage
# from src.ingestion import MultimodalDocumentIngestion


# # --------------------------------------------------
# # Celery configuration
# # --------------------------------------------------

# celery_app = Celery(
#     "mm_rag_worker",
#     broker="redis://localhost:6379/0",
#     backend="redis://localhost:6379/0",
# )

# # A worker that dies mid-task (OOM kill, container restart, SIGKILL) leaves the
# # message unacked. Redis will not redeliver it until the visibility timeout
# # elapses, so the one-hour default would keep the job stuck far longer than the
# # API's stale-job guard. 30 minutes sits comfortably above the slowest
# # legitimate single-stage run while still bounding recovery time.
# VISIBILITY_TIMEOUT_SECONDS = 30 * 60

# # Bounded retries: a transient infrastructure failure (Ollama down, Qdrant
# # timeout, worker killed) should not require a manual re-upload.
# MAX_TASK_RETRIES = 3

# celery_app.conf.update(
#     task_track_started=True,
#     task_acks_late=True,
#     # The worker acknowledges only after the task returns, so if the process is
#     # lost the message is requeued and another worker picks it up. This is what
#     # makes recovery automatic instead of waiting for the visibility timeout.
#     task_reject_on_worker_lost=True,
#     worker_prefetch_multiplier=1,
#     result_expires=24 * 60 * 60,
#     broker_connection_retry_on_startup=True,
#     broker_transport_options={
#         "visibility_timeout": VISIBILITY_TIMEOUT_SECONDS,
#     },
# )


# # --------------------------------------------------
# # Async document ingestion task
# # --------------------------------------------------

# @celery_app.task(
#     name="mm_rag.ingest_document",
#     bind=True,
#     # Exhausted retries are still surfaced as a terminal "failed" job.
#     autoretry_for=(Exception,),
#     max_retries=MAX_TASK_RETRIES,
#     retry_backoff=15,
#     retry_backoff_max=300,
#     retry_jitter=True,
# )
# def ingest_document(
#     self,
#     storage_key: str,
#     output_prefix: str | None = None,
#     collection_name: str | None = None,
#     workspace_id: str | None = None,
#     chunk_size: int = 2000,
#     chunk_overlap: int = 120,
#     replace_existing: bool = True,
# ) -> dict[str, Any]:
#     """
#     Run the ingestion pipeline as an explicit state machine:

#         uploaded -> parsing -> chunking -> indexing -> ready | failed

#     The worker owns the intermediate stages so the UI can poll
#     real progress instead of a single blocking call.
#     """

#     db: Session = SessionLocal()

#     job: IngestionJob | None = None
#     document: Document | None = None
#     version: DocumentVersion | None = None

#     local_pdf: Path | None = None
#     local_output: Path | None = None

#     def set_stage(stage: str, error: str | None = None) -> None:
#         """Persist a pipeline stage for the job, document and version."""
#         if job is not None:
#             job.status = stage
#             job.error = error
#         if document is not None:
#             document.status = stage
#             document.error = error
#         if version is not None:
#             version.status = stage
#         db.commit()

#     try:
#         # --------------------------------------------------
#         # Find the ingestion job using the Celery task ID
#         # --------------------------------------------------

#         job = (
#             db.query(IngestionJob)
#             .filter(
#                 IngestionJob.celery_task_id == self.request.id
#             )
#             .first()
#         )

#         if not job:
#             raise RuntimeError(
#                 f"Ingestion job not found for Celery task "
#                 f"{self.request.id}"
#             )

#         # --------------------------------------------------
#         # Load the PostgreSQL document
#         # --------------------------------------------------

#         document = (
#             db.query(Document)
#             .filter(Document.id == job.document_id)
#             .first()
#         )

#         if not document:
#             raise RuntimeError(
#                 f"Document not found: {job.document_id}"
#             )

#         # --------------------------------------------------
#         # Load the current document version (if versioned)
#         # --------------------------------------------------

#         version = (
#             db.query(DocumentVersion)
#             .filter(
#                 DocumentVersion.document_id == document.id,
#                 DocumentVersion.is_current.is_(True),
#             )
#             .first()
#         )

#         # --------------------------------------------------
#         # Get tenant + document identity
#         # --------------------------------------------------

#         tenant_id = str(document.tenant_id)
#         document_id = str(document.id)

#         if not tenant_id:
#             raise RuntimeError(
#                 f"Document {document_id} has no tenant_id"
#             )

#         # --------------------------------------------------
#         # Stage 1: parsing
#         # --------------------------------------------------

#         set_stage("parsing")

#         storage = get_storage()

#         # Materialize the raw PDF locally (no-op for the local backend,
#         # a download for S3/MinIO) and parse into a scratch directory.
#         local_pdf = storage.localize(storage_key, suffix=".pdf")
#         local_output = Path(
#             tempfile.mkdtemp(prefix="mmrag_parsed_")
#         )

#         ingestion = MultimodalDocumentIngestion(
#             collection_name=collection_name,
#             chunk_size=int(chunk_size),
#             chunk_overlap=int(chunk_overlap),
#         )

#         # The ingestion pipeline reports "chunking" and "indexing"
#         # back through progress_callback.
#         result = ingestion.ingest_pdf(
#             pdf_path=local_pdf,
#             output_dir=local_output,
#             tenant_id=tenant_id,
#             document_id=document_id,
#             workspace_id=workspace_id,
#             file_sha256=(
#                 str(document.file_hash)
#                 if document.file_hash
#                 else None
#             ),
#             # local_pdf is a localized artifact (`<hash>_name.pdf` for
#             # the local backend, a temp file for S3), so pass the
#             # logical upload name explicitly. Otherwise citations and
#             # the stored payload leak the artifact name.
#             filename=document.filename,
#             replace_existing=replace_existing,
#             progress_callback=set_stage,
#         )

#         # --------------------------------------------------
#         # Persist parsed artifacts to object storage
#         # --------------------------------------------------

#         if output_prefix:
#             artifact_keys = storage.save_directory(
#                 local_output,
#                 output_prefix,
#             )
#             result["artifact_keys"] = artifact_keys

#         # --------------------------------------------------
#         # Terminal stage: ready
#         # --------------------------------------------------

#         set_stage("ready")

#         return result

#     except Exception as exc:

#         # --------------------------------------------------
#         # Terminal stage: failed
#         #
#         # Never leave the UI polling forever.
#         # --------------------------------------------------

#         db.rollback()

#         if job is not None and document is None:
#             document = (
#                 db.query(Document)
#                 .filter(Document.id == job.document_id)
#                 .first()
#             )

#             if document is not None:
#                 version = (
#                     db.query(DocumentVersion)
#                     .filter(
#                         DocumentVersion.document_id == document.id,
#                         DocumentVersion.is_current.is_(True),
#                     )
#                     .first()
#                 )

#         if self.request.retries < self.max_retries:
#             # autoretry_for will schedule another attempt. Report the
#             # intermediate stage so the UI keeps polling instead of showing a
#             # failure that is about to be retried.
#             set_stage("retrying", str(exc))
#         else:
#             set_stage("failed", str(exc))

#         raise

#     finally:
#         db.close()

#         # Clean up scratch artifacts created for this task.
#         if local_output is not None:
#             shutil.rmtree(local_output, ignore_errors=True)

#         if local_pdf is not None:
#             try:
#                 temp_root = Path(tempfile.gettempdir()).resolve()

#                 if temp_root in local_pdf.resolve().parents:
#                     local_pdf.unlink(missing_ok=True)
#             except OSError:
#                 pass



















from pathlib import Path
from typing import Any
import logging
import os
import shutil
import tempfile

from celery import Celery
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# The worker runs as its own process, so it must load the same .env the API
# uses. Without this, DATABASE_URL / REDIS_URL / STORAGE_BACKEND would fall
# back to their defaults and the two services could silently drift onto
# different databases or object stores.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

from backend.database import SessionLocal
from backend.models import Document, DocumentVersion, IngestionJob
from backend.storage import get_storage
from src.ingestion import MultimodalDocumentIngestion


# --------------------------------------------------
# Logging
# --------------------------------------------------

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Celery configuration
# --------------------------------------------------

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "mm_rag_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

VISIBILITY_TIMEOUT_SECONDS = 30 * 60
MAX_TASK_RETRIES = 3

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    result_expires=24 * 60 * 60,
    broker_connection_retry_on_startup=True,
    broker_transport_options={
        "visibility_timeout": VISIBILITY_TIMEOUT_SECONDS,
    },
)


# --------------------------------------------------
# Async document ingestion task
# --------------------------------------------------

@celery_app.task(
    name="mm_rag.ingest_document",
    bind=True,
    autoretry_for=(Exception,),
    max_retries=MAX_TASK_RETRIES,
    retry_backoff=15,
    retry_backoff_max=300,
    retry_jitter=True,
)
def ingest_document(
    self,
    storage_key: str,
    output_prefix: str | None = None,
    collection_name: str | None = None,
    workspace_id: str | None = None,
    chunk_size: int = 2000,
    chunk_overlap: int = 120,
    replace_existing: bool = True,
) -> dict[str, Any]:
    """
    Run document ingestion through the following stages:

        uploaded -> parsing -> chunking -> indexing -> ready | failed

    Detailed exceptions are logged to help diagnose ingestion failures.
    """

    db: Session = SessionLocal()

    job: IngestionJob | None = None
    document: Document | None = None
    version: DocumentVersion | None = None

    local_pdf: Path | None = None
    local_output: Path | None = None

    def set_stage(stage: str, error: str | None = None) -> None:
        """Persist the current pipeline stage."""

        if job is not None:
            job.status = stage
            job.error = error

        if document is not None:
            document.status = stage
            document.error = error

        if version is not None:
            version.status = stage

        db.commit()

    try:
        # --------------------------------------------------
        # Find ingestion job
        # --------------------------------------------------

        job = (
            db.query(IngestionJob)
            .filter(
                IngestionJob.celery_task_id == self.request.id
            )
            .first()
        )

        if not job:
            raise RuntimeError(
                f"Ingestion job not found for Celery task "
                f"{self.request.id}"
            )

        # --------------------------------------------------
        # Load document
        # --------------------------------------------------

        document = (
            db.query(Document)
            .filter(Document.id == job.document_id)
            .first()
        )

        if not document:
            raise RuntimeError(
                f"Document not found: {job.document_id}"
            )

        # --------------------------------------------------
        # Load current document version
        # --------------------------------------------------

        version = (
            db.query(DocumentVersion)
            .filter(
                DocumentVersion.document_id == document.id,
                DocumentVersion.is_current.is_(True),
            )
            .first()
        )

        # --------------------------------------------------
        # Tenant and document identity
        # --------------------------------------------------

        tenant_id = str(document.tenant_id)
        document_id = str(document.id)

        if not tenant_id:
            raise RuntimeError(
                f"Document {document_id} has no tenant_id"
            )

        logger.info(
            "Starting ingestion: task_id=%s document_id=%s tenant_id=%s",
            self.request.id,
            document_id,
            tenant_id,
        )

        # --------------------------------------------------
        # Stage 1: parsing
        # --------------------------------------------------

        set_stage("parsing")

        storage = get_storage()

        local_pdf = storage.localize(
            storage_key,
            suffix=".pdf",
        )

        local_output = Path(
            tempfile.mkdtemp(prefix="mmrag_parsed_")
        )

        ingestion = MultimodalDocumentIngestion(
            collection_name=collection_name,
            chunk_size=int(chunk_size),
            chunk_overlap=int(chunk_overlap),
        )

        # --------------------------------------------------
        # Parse, chunk and index
        # --------------------------------------------------

        logger.info(
            "Starting PDF ingestion: task_id=%s document_id=%s",
            self.request.id,
            document_id,
        )

        result = ingestion.ingest_pdf(
            pdf_path=local_pdf,
            output_dir=local_output,
            tenant_id=tenant_id,
            document_id=document_id,
            workspace_id=workspace_id,
            file_sha256=(
                str(document.file_hash)
                if document.file_hash
                else None
            ),
            filename=document.filename,
            replace_existing=replace_existing,
            progress_callback=set_stage,
        )

        logger.info(
            "PDF ingestion returned successfully: "
            "task_id=%s document_id=%s",
            self.request.id,
            document_id,
        )

        # --------------------------------------------------
        # Persist parsed artifacts
        # --------------------------------------------------

        if output_prefix:
            artifact_keys = storage.save_directory(
                local_output,
                output_prefix,
            )

            result["artifact_keys"] = artifact_keys

        # --------------------------------------------------
        # Mark ready
        # --------------------------------------------------

        set_stage("ready")

        logger.info(
            "Ingestion completed: task_id=%s document_id=%s",
            self.request.id,
            document_id,
        )

        return result

    except Exception as exc:
        # --------------------------------------------------
        # Log the complete traceback
        # --------------------------------------------------

        logger.exception(
            "Document ingestion failed: "
            "task_id=%s document_id=%s retry=%s/%s error=%s",
            self.request.id,
            job.document_id if job is not None else None,
            self.request.retries,
            self.max_retries,
            exc,
        )

        db.rollback()

        # Reload document/version if needed
        if job is not None and document is None:
            document = (
                db.query(Document)
                .filter(Document.id == job.document_id)
                .first()
            )

            if document is not None:
                version = (
                    db.query(DocumentVersion)
                    .filter(
                        DocumentVersion.document_id == document.id,
                        DocumentVersion.is_current.is_(True),
                    )
                    .first()
                )

        # Update job status before Celery retries
        if self.request.retries < self.max_retries:
            set_stage("retrying", str(exc))
        else:
            set_stage("failed", str(exc))

        raise

    finally:
        db.close()

        # --------------------------------------------------
        # Clean up temporary artifacts
        # --------------------------------------------------

        if local_output is not None:
            shutil.rmtree(
                local_output,
                ignore_errors=True,
            )

        if local_pdf is not None:
            try:
                temp_root = Path(tempfile.gettempdir()).resolve()

                if temp_root in local_pdf.resolve().parents:
                    local_pdf.unlink(missing_ok=True)

            except OSError:
                logger.exception(
                    "Failed to clean temporary PDF: %s",
                    local_pdf,
                )
