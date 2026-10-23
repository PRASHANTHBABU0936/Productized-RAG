"""
Safe migration for legacy Qdrant points that predate the current schema.

Legacy points (written before the payload contract was fixed) are missing
some of the metadata every retrieval path depends on:
``metadata.tenant_id`` (mandatory filter - without it a point is invisible),
``metadata.workspace_id`` and ``metadata.file_sha256`` (provenance and
deduplication).

They also carry a wrong ``metadata.filename``: the async worker derived it
from the *localized* artifact (``<hash>_original.pdf`` through the local
backend, a temp file through S3) instead of the name the user uploaded.
That leaks the storage key into citations and breaks any filename-based
matching (e.g. the evaluation harness' ``expected_sources``).

This tool fixes that without ever deleting the collection or rewriting
vectors. It only patches the payload of the affected points with
``set_payload``, which leaves the 384-d embeddings untouched.

Resolution order for each incomplete point:

    1. ``metadata.document_id`` matched against the PostgreSQL ``documents``
       table -> use that document's ``tenant_id``, ``workspace_id``,
       ``file_hash`` and ``filename`` (precise attribution).
    2. Otherwise fall back to ``--default-tenant-id`` / ``--workspace-id``
       (explicit opt-in).
    3. Otherwise the field is reported as *unresolved* and left untouched.

Usage:

    # Dry run (default) - reports what would change, writes nothing.
    python -m backend.migrate_legacy_points

    # Apply the backfill.
    python -m backend.migrate_legacy_points --apply

    # Also re-stamp points that already carry the fields.
    python -m backend.migrate_legacy_points --overwrite --apply
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from backend.database import SessionLocal
from backend.models import Document, DocumentVersion

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

# Payload fields this tool knows how to reconstruct from PostgreSQL.
# ``BACKFILLED_FIELDS`` are only written when absent; ``NORMALIZED_FIELDS``
# already exist but may hold a stale value that must be corrected.
BACKFILLED_FIELDS = ("tenant_id", "workspace_id", "file_sha256")
NORMALIZED_FIELDS = ("filename",)
MANAGED_FIELDS = BACKFILLED_FIELDS + NORMALIZED_FIELDS

# Documents ingested before hashing was introduced have a NULL file_hash and no
# DocumentVersion row, so the digest is recomputed from the stored upload.
STORAGE_ROOT = Path(
    os.getenv("STORAGE_ROOT") or (PROJECT_ROOT / "data")
)

# ``backend.main`` stores each upload as ``f"{uuid4().hex}_{original}"``.
_STORED_NAME_PREFIX = re.compile(r"^[0-9a-f]{32}_")


def recover_original_filename(value: str | None) -> str | None:
    """
    Peel the storage-key prefix off a legacy payload filename.

    The old worker recorded the localized artifact name instead of the
    upload name. When the owning ``documents`` row is gone this is the
    only way to recover what the user actually uploaded.
    """
    if not value:
        return None

    name = Path(str(value)).name
    match = _STORED_NAME_PREFIX.match(name)

    return name[match.end():] if match else name


def resolve_config(collection: str | None) -> tuple[str, dict[str, str], str]:
    base = (
        os.getenv("QDRANT_URL")
        or os.getenv("QDRANT_Cluster_Endpoint")
    )

    if not base:
        raise RuntimeError(
            "QDRANT_URL / QDRANT_Cluster_Endpoint must be set"
        )

    api_key = os.getenv("QDRANT_API_KEY") or ""

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
    }

    resolved_collection = (
        collection
        or os.getenv("QDRANT_COLLECTION_NAME")
        or "mm-rag-documents"
    )

    return base.rstrip("/"), headers, resolved_collection


def scroll_all(
    base: str,
    headers: dict[str, str],
    collection: str,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    offset: Any = None

    while True:
        body: dict[str, Any] = {
            "limit": 256,
            "with_payload": True,
            "with_vector": False,
        }

        if offset is not None:
            body["offset"] = offset

        response = requests.post(
            f"{base}/collections/{collection}/points/scroll",
            headers=headers,
            json=body,
            timeout=120,
        )
        response.raise_for_status()

        result = response.json()["result"]
        batch = result.get("points") or []

        if not batch:
            break

        points.extend(batch)

        if limit is not None and len(points) >= limit:
            return points[:limit]

        offset = result.get("next_page_offset")

        if offset is None:
            break

    return points


def set_payload(
    base: str,
    headers: dict[str, str],
    collection: str,
    point_id: Any,
    metadata: dict[str, Any],
) -> None:
    response = requests.post(
        f"{base}/collections/{collection}/points/payload",
        headers=headers,
        json={
            "payload": {"metadata": metadata},
            "points": [point_id],
        },
        params={"wait": "true"},
        timeout=60,
    )
    response.raise_for_status()


def hash_stored_artifact(
    file_path: str | None,
    stored_filename: str | None,
) -> str | None:
    """
    Recompute the sha256 of the stored upload.

    ``file_path`` is either an absolute path (older rows) or a storage key
    relative to the storage root. Returns ``None`` when the artifact is no
    longer on the local filesystem.
    """
    candidates: list[Path] = []

    if file_path:
        raw = Path(file_path)
        candidates.append(raw)
        candidates.append(STORAGE_ROOT / raw)

    if stored_filename:
        candidates.append(
            STORAGE_ROOT / "uploads" / Path(stored_filename).name
        )

    for candidate in candidates:
        try:
            if not candidate.is_file():
                continue

            digest = hashlib.sha256()

            with candidate.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1 << 20), b""):
                    digest.update(chunk)

            return digest.hexdigest()
        except OSError:
            continue

    return None


def build_document_metadata_map() -> dict[str, dict[str, str | None]]:
    """
    Map ``document_id`` -> the payload fields it should carry.

    ``file_hash`` lives on both ``documents`` and ``document_versions``;
    the current version is used as a fallback when the document row has
    not recorded a hash yet, and the stored upload is hashed as a last
    resort for pre-hashing-row documents.
    """
    db = SessionLocal()

    try:
        rows = db.query(
            Document.id,
            Document.tenant_id,
            Document.workspace_id,
            Document.filename,
            Document.file_hash,
            Document.file_path,
            Document.stored_filename,
        ).all()

        current_hashes = {
            str(row.document_id): row.file_hash
            for row in db.query(
                DocumentVersion.document_id,
                DocumentVersion.file_hash,
            )
            .filter(DocumentVersion.is_current.is_(True))
            .all()
        }

        metadata_map: dict[str, dict[str, str | None]] = {}

        for row in rows:
            document_id = str(row.id)

            file_sha256 = (
                row.file_hash
                or current_hashes.get(document_id)
                or hash_stored_artifact(
                    row.file_path,
                    row.stored_filename,
                )
            )

            metadata_map[document_id] = {
                "tenant_id": str(row.tenant_id) if row.tenant_id else None,
                "workspace_id": (
                    str(row.workspace_id) if row.workspace_id else None
                ),
                "file_sha256": file_sha256,
                "filename": Path(row.filename).name if row.filename else None,
            }

        return metadata_map
    finally:
        db.close()


def migrate(
    *,
    collection: str | None,
    default_tenant_id: str | None,
    workspace_id: str | None,
    overwrite: bool,
    apply: bool,
    limit: int | None,
) -> int:
    base, headers, collection_name = resolve_config(collection)

    info = requests.get(
        f"{base}/collections/{collection_name}",
        headers=headers,
        timeout=60,
    )

    if info.status_code == 404:
        print(f"collection not found: {collection_name}")
        return 1

    info.raise_for_status()
    print(
        f"collection={collection_name} "
        f"points={info.json()['result'].get('points_count')}"
    )

    document_metadata = build_document_metadata_map()
    print(f"postgres documents known: {len(document_metadata)}")

    points = scroll_all(base, headers, collection_name, limit=limit)
    print(f"scanned points: {len(points)}")

    already_complete = 0
    unchanged = 0
    missing_before = {field: 0 for field in MANAGED_FIELDS}
    filled = {field: 0 for field in MANAGED_FIELDS}
    unresolved = {field: 0 for field in MANAGED_FIELDS}
    updates: list[tuple[Any, dict[str, Any]]] = []

    for point in points:
        payload = point.get("payload") or {}
        metadata = dict(payload.get("metadata") or {})

        missing = [
            field
            for field in BACKFILLED_FIELDS
            if not metadata.get(field)
        ]

        document_id = metadata.get("document_id")
        known = (
            document_metadata.get(str(document_id))
            if document_id
            else None
        ) or {}

        # Fallbacks only ever apply to tenant/workspace; file_sha256 is
        # provenance and may only come from the owning document row.
        # filename may additionally be recovered from the storage key.
        values: dict[str, Any] = {
            "tenant_id": known.get("tenant_id") or default_tenant_id,
            "workspace_id": known.get("workspace_id") or workspace_id,
            "file_sha256": known.get("file_sha256"),
            "filename": known.get("filename")
            or recover_original_filename(metadata.get("filename")),
        }

        # Fields whose current value differs from PostgreSQL (a stale
        # localized artifact name, for instance).
        stale = [
            field
            for field in NORMALIZED_FIELDS
            if values.get(field)
            and str(metadata.get(field)) != str(values[field])
        ]

        if not missing and not stale and not overwrite:
            already_complete += 1
            continue

        for field in missing:
            missing_before[field] += 1

        for field in stale:
            missing_before[field] += 1

        new_metadata = dict(metadata)

        for field in MANAGED_FIELDS if overwrite else missing + stale:
            value = values.get(field)

            if value:
                if str(new_metadata.get(field)) != str(value):
                    new_metadata[field] = str(value)
                    filled[field] += 1
            elif not new_metadata.get(field):
                unresolved[field] += 1

        if any(
            new_metadata.get(field) != metadata.get(field)
            for field in MANAGED_FIELDS
        ):
            updates.append((point.get("id"), new_metadata))
        else:
            unchanged += 1

    print("---- migration plan ----")
    print(f"already complete (skipped): {already_complete}")
    print(f"no new values available   : {unchanged}")

    for field in MANAGED_FIELDS:
        print(
            f"  {field:<13} missing={missing_before[field]:<5} "
            f"backfilled={filled[field]:<5} unresolved={unresolved[field]}"
        )

    print(f"points to update          : {len(updates)}")

    if any(unresolved.values()):
        print(
            "hint: unresolved fields have no PostgreSQL document match; "
            "pass --default-tenant-id / --workspace-id to attribute them, "
            "or re-ingest those documents via POST /documents/upload."
        )

    if not apply:
        print("dry run: no writes performed (re-run with --apply)")
        return 0

    updated = 0
    failed = 0

    for point_id, metadata in updates:
        try:
            set_payload(
                base,
                headers,
                collection_name,
                point_id,
                metadata,
            )
            updated += 1
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"failed point {point_id}: {exc}")

    print(f"updated: {updated} | failed: {failed}")
    return 0 if failed == 0 else 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Backfill missing metadata (tenant_id, workspace_id, "
            "file_sha256) and normalize the filename on legacy Qdrant "
            "points without deleting the collection."
        )
    )
    parser.add_argument(
        "--collection",
        default=None,
        help="Qdrant collection (defaults to QDRANT_COLLECTION_NAME).",
    )
    parser.add_argument(
        "--default-tenant-id",
        default=None,
        help=(
            "Tenant to assign when the point's document_id is not "
            "present in PostgreSQL."
        ),
    )
    parser.add_argument(
        "--workspace-id",
        default=None,
        help="Optional workspace_id to stamp as well.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Also re-stamp points that already have a tenant_id.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write the changes (default is a dry run).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only scan the first N points (debugging).",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    sys.exit(migrate(**vars(parse_args())))
