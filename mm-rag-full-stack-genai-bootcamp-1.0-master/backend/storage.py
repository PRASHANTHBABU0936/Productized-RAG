"""
Object storage abstraction for raw uploads and parsed artifacts.

Default backend is the local filesystem (``data/``). Setting
``STORAGE_BACKEND=s3`` switches to any S3-compatible object store
(AWS S3, MinIO, Cloudflare R2, ...) using boto3.

Keys are caller-defined, relative, POSIX-style strings, e.g.
``uploads/<stored_filename>`` or ``parsed/<stem>/tables.json``.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STORAGE_ROOT = PROJECT_ROOT / "data"


def upload_key(stored_filename: str) -> str:
    """Storage key for an uploaded PDF."""
    return f"uploads/{Path(stored_filename).name}"


def parsed_prefix(stem: str) -> str:
    """Storage prefix for the parsed artifacts of an upload."""
    return f"parsed/{stem}"


class StorageBackend(ABC):
    """Minimal object-store contract shared by local and S3 backends."""

    @abstractmethod
    def save_bytes(self, key: str, data: bytes) -> str:
        """Persist ``data`` under ``key`` and return the key."""

    @abstractmethod
    def load_bytes(self, key: str) -> bytes:
        """Return the bytes stored under ``key``."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Whether ``key`` exists in the store."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete ``key`` if present (never raises if missing)."""

    @abstractmethod
    def localize(self, key: str, *, suffix: str = "") -> Path:
        """
        Return a local filesystem path containing the object's bytes.

        For the local backend this is the real file; for S3 a temporary
        file is downloaded and returned.
        """

    @abstractmethod
    def save_directory(self, local_dir: Path, prefix: str) -> list[str]:
        """Upload every file in ``local_dir`` under ``prefix``."""


class LocalStorage(StorageBackend):
    """Filesystem-backed storage rooted at ``STORAGE_ROOT``."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.root / key.lstrip("/\\")

    def save_bytes(self, key: str, data: bytes) -> str:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def load_bytes(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def exists(self, key: str) -> bool:
        return self._path(key).exists()

    def delete(self, key: str) -> None:
        path = self._path(key)

        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink(missing_ok=True)

    def localize(self, key: str, *, suffix: str = "") -> Path:
        return self._path(key)

    def save_directory(self, local_dir: Path, prefix: str) -> list[str]:
        keys: list[str] = []
        base = Path(local_dir)

        for file_path in sorted(base.rglob("*")):
            if not file_path.is_file():
                continue

            relative = file_path.relative_to(base).as_posix()
            key = f"{prefix.rstrip('/')}/{relative}"
            self.save_bytes(key, file_path.read_bytes())
            keys.append(key)

        return keys


class S3Storage(StorageBackend):
    """S3-compatible storage (AWS S3, MinIO, R2)."""

    def __init__(
        self,
        *,
        bucket: str,
        endpoint_url: str | None = None,
        region: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        try:
            import boto3
        except ImportError as exc:  # noqa: BLE001
            raise RuntimeError(
                "STORAGE_BACKEND=s3 requires the 'boto3' package "
                "(pip install boto3)."
            ) from exc

        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except Exception:  # noqa: BLE001
            self.client.create_bucket(Bucket=self.bucket)

    def save_bytes(self, key: str, data: bytes) -> str:
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
        )
        return key

    def load_bytes(self, key: str) -> bytes:
        response = self.client.get_object(
            Bucket=self.bucket,
            Key=key,
        )
        return response["Body"].read()

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:  # noqa: BLE001
            return False

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def localize(self, key: str, *, suffix: str = "") -> Path:
        data = self.load_bytes(key)
        file_descriptor, temp_path = tempfile.mkstemp(
            suffix=suffix or Path(key).suffix
        )

        with os.fdopen(file_descriptor, "wb") as handle:
            handle.write(data)

        return Path(temp_path)

    def save_directory(self, local_dir: Path, prefix: str) -> list[str]:
        keys: list[str] = []
        base = Path(local_dir)

        for file_path in sorted(base.rglob("*")):
            if not file_path.is_file():
                continue

            relative = file_path.relative_to(base).as_posix()
            key = f"{prefix.rstrip('/')}/{relative}"
            self.save_bytes(key, file_path.read_bytes())
            keys.append(key)

        return keys


_storage: StorageBackend | None = None


def _build_storage() -> StorageBackend:
    backend = (os.getenv("STORAGE_BACKEND") or "local").strip().lower()

    if backend == "s3":
        return S3Storage(
            bucket=os.getenv("S3_BUCKET") or "mm-rag-documents",
            endpoint_url=os.getenv("S3_ENDPOINT_URL"),
            region=os.getenv("S3_REGION"),
            access_key=os.getenv("S3_ACCESS_KEY_ID"),
            secret_key=os.getenv("S3_SECRET_ACCESS_KEY"),
        )

    return LocalStorage(
        Path(os.getenv("STORAGE_ROOT") or DEFAULT_STORAGE_ROOT)
    )


def get_storage() -> StorageBackend:
    """Return the process-wide storage backend (lazily created)."""
    global _storage

    if _storage is None:
        _storage = _build_storage()

    return _storage
