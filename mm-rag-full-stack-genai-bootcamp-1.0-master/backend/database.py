import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# --------------------------------------------------
# Database configuration
# --------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://mmrag:mmrag_password@localhost:5433/mmrag",
)


# --------------------------------------------------
# Database engine
# --------------------------------------------------

_engine_kwargs: dict = {"pool_pre_ping": True}

if DATABASE_URL.startswith("postgresql"):
    # Bound the connect attempt. A wedged Docker port proxy keeps 5433 in
    # LISTEN and accepts the TCP connection but never answers, so an unbounded
    # connect() blocks /health/ready for minutes and the app looks dead.
    _engine_kwargs["connect_args"] = {"connect_timeout": 10}
    _engine_kwargs["pool_timeout"] = 10

engine = create_engine(DATABASE_URL, **_engine_kwargs)


# --------------------------------------------------
# Session factory
# --------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# --------------------------------------------------
# Base model
# --------------------------------------------------

class Base(DeclarativeBase):
    pass


# --------------------------------------------------
# Database session dependency
# --------------------------------------------------

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()