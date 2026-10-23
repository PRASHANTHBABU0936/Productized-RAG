# from datetime import datetime, timezone
# from uuid import uuid4

# from sqlalchemy import DateTime, ForeignKey, String, Text
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from backend.database import Base


# # --------------------------------------------------
# # Documents
# # --------------------------------------------------

# class Document(Base):
#     __tablename__ = "documents"

#     id: Mapped[str] = mapped_column(
#         String(36),
#         primary_key=True,
#         default=lambda: str(uuid4()),
#     )

#     filename: Mapped[str] = mapped_column(
#         String(500),
#         nullable=False,
#     )

#     stored_filename: Mapped[str] = mapped_column(
#         String(500),
#         nullable=False,
#         unique=True,
#     )

#     file_path: Mapped[str] = mapped_column(
#         Text,
#         nullable=False,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         default="PENDING",
#     )

#     error: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#     )

#     ingestion_jobs: Mapped[list["IngestionJob"]] = relationship(
#         back_populates="document",
#         cascade="all, delete-orphan",
#     )


# # --------------------------------------------------
# # Ingestion Jobs
# # --------------------------------------------------

# class IngestionJob(Base):
#     __tablename__ = "ingestion_jobs"

#     id: Mapped[str] = mapped_column(
#         String(36),
#         primary_key=True,
#         default=lambda: str(uuid4()),
#     )

#     document_id: Mapped[str] = mapped_column(
#         String(36),
#         ForeignKey("documents.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     celery_task_id: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#         unique=True,
#         index=True,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         default="PENDING",
#     )

#     error: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#     )

#     document: Mapped["Document"] = relationship(
#         back_populates="ingestion_jobs",
#     )



from backend.database import Base, engine
from backend import models


def init_database():
    print("Creating database tables...")

    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully.")


if __name__ == "__main__":
    init_database()