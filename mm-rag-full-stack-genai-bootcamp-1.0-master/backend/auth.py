from datetime import datetime, timedelta, timezone
from pathlib import Path
import os

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

# Load .env before any module-level os.getenv below, so JWT_SECRET_KEY is
# resolved from the project configuration instead of silently falling back.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


# --------------------------------------------------
# Password hashing
# --------------------------------------------------

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        password,
        hashed_password,
    )


# --------------------------------------------------
# JWT configuration
# --------------------------------------------------

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

# The value shipped in the repository. Keeping it would let anyone mint a
# token for any user id, so it is rejected outright.
INSECURE_DEFAULT_SECRET = "change-this-secret-in-production"

MIN_SECRET_LENGTH = 32


def _resolve_secret_key() -> str:
    """
    Read JWT_SECRET_KEY and refuse to start with an unsafe value.

    Failing here (at import time) is deliberate: a misconfigured secret is
    an account-takeover vulnerability, not a runtime error to recover from.
    """
    secret = (os.getenv("JWT_SECRET_KEY") or "").strip()

    if not secret:
        raise RuntimeError(
            "JWT_SECRET_KEY is not set. Generate one with "
            '`python -c "import secrets; print(secrets.token_urlsafe(64))"` '
            "and add it to .env before starting the API."
        )

    if secret == INSECURE_DEFAULT_SECRET:
        raise RuntimeError(
            "JWT_SECRET_KEY is still the insecure placeholder "
            f"'{INSECURE_DEFAULT_SECRET}'. Anyone could forge an access "
            "token for any user. Set a unique random secret in .env."
        )

    if len(secret) < MIN_SECRET_LENGTH:
        raise RuntimeError(
            f"JWT_SECRET_KEY must be at least {MIN_SECRET_LENGTH} "
            f"characters (got {len(secret)})."
        )

    return secret


JWT_SECRET_KEY = _resolve_secret_key()


# --------------------------------------------------
# JWT creation
# --------------------------------------------------

def create_access_token(
    user_id: str,
    expires_delta: timedelta | None = None,
) -> str:

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": user_id,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


# --------------------------------------------------
# JWT verification
# --------------------------------------------------

def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
    )