"""Authentication and secret-management tests."""

import pytest

from backend import auth


def test_rejects_missing_secret(monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="not set"):
        auth._resolve_secret_key()


def test_rejects_placeholder_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "change-this-secret-in-production")
    with pytest.raises(RuntimeError, match="placeholder"):
        auth._resolve_secret_key()


def test_rejects_short_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "too-short")
    with pytest.raises(RuntimeError, match="at least"):
        auth._resolve_secret_key()


def test_accepts_strong_secret(monkeypatch):
    strong = "x" * 40
    monkeypatch.setenv("JWT_SECRET_KEY", strong)
    assert auth._resolve_secret_key() == strong


def test_password_hash_is_salted_and_verifies():
    hashed = auth.hash_password("password123")
    assert hashed != "password123"
    assert auth.verify_password("password123", hashed) is True
    assert auth.verify_password("wrong-password", hashed) is False


def test_access_token_round_trip():
    token = auth.create_access_token("user-123")
    payload = auth.decode_access_token(token)
    assert payload["sub"] == "user-123"


def test_tampered_token_is_rejected():
    token = auth.create_access_token("user-123")
    with pytest.raises(Exception):
        auth.decode_access_token(token + "tampered")


def test_token_signed_with_other_secret_is_rejected(monkeypatch):
    import jwt

    forged = jwt.encode({"sub": "victim"}, "a-different-secret", algorithm="HS256")
    with pytest.raises(Exception):
        auth.decode_access_token(forged)
