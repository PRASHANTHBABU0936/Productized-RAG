"""Object-storage abstraction tests (local backend, no external services)."""

from backend.storage import (
    LocalStorage,
    get_storage,
    parsed_prefix,
    upload_key,
)


def test_key_helpers():
    assert upload_key("abc123_file.pdf") == "uploads/abc123_file.pdf"
    # Only the basename is kept, so a path cannot escape the prefix.
    assert upload_key("../../evil.pdf") == "uploads/evil.pdf"
    assert parsed_prefix("stem") == "parsed/stem"


def test_round_trip(tmp_path):
    storage = LocalStorage(tmp_path)
    key = upload_key("doc.pdf")

    assert storage.exists(key) is False
    assert storage.save_bytes(key, b"payload") == key
    assert storage.exists(key) is True
    assert storage.load_bytes(key) == b"payload"
    assert storage.localize(key) == tmp_path / "uploads" / "doc.pdf"


def test_delete_is_idempotent(tmp_path):
    storage = LocalStorage(tmp_path)
    storage.delete("uploads/missing.pdf")  # must not raise
    key = upload_key("doc.pdf")
    storage.save_bytes(key, b"x")
    storage.delete(key)
    assert storage.exists(key) is False


def test_save_directory_preserves_tree(tmp_path):
    storage = LocalStorage(tmp_path / "store")
    source = tmp_path / "artifacts"
    (source / "page_images").mkdir(parents=True)
    (source / "tables.json").write_text("[]")
    (source / "page_images" / "page_001.png").write_bytes(b"png")

    keys = storage.save_directory(source, "parsed/stem")

    assert keys == [
        "parsed/stem/page_images/page_001.png",
        "parsed/stem/tables.json",
    ]
    assert storage.load_bytes("parsed/stem/tables.json") == b"[]"


def test_absolute_key_cannot_escape_root(tmp_path):
    storage = LocalStorage(tmp_path)
    storage.save_bytes("/etc/passwd", b"nope")
    assert (tmp_path / "etc" / "passwd").read_bytes() == b"nope"


def test_get_storage_defaults_to_local_backend():
    # conftest.py pins STORAGE_BACKEND=local.
    assert isinstance(get_storage(), LocalStorage)
