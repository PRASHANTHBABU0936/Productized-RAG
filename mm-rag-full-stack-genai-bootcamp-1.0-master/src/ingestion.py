# # from __future__ import annotations
# # from langchain_huggingface import HuggingFaceEmbeddings
# # import os
# # import sys
# # from pathlib import Path
# # from typing import Any, Sequence
# # from uuid import NAMESPACE_URL, uuid5

# # from dotenv import load_dotenv
# # from langchain_core.documents import Document
# # from langchain_openai import OpenAIEmbeddings
# # from langchain_qdrant import QdrantVectorStore, RetrievalMode
# # from langchain_text_splitters import RecursiveCharacterTextSplitter
# # from qdrant_client import QdrantClient, models

# # PROJECT_ROOT = Path(__file__).resolve().parent.parent
# # if str(PROJECT_ROOT) not in sys.path:
# #     sys.path.insert(0, str(PROJECT_ROOT))

# # load_dotenv(PROJECT_ROOT / ".env")

# # from exception.custom_exception import DocumentPortalException
# # from logger.custom_logger import CustomLogger
# # from src.parsing import ComplexPDFParser

# # logger = CustomLogger().get_logger(__name__)



# # class MultimodalDocumentIngestion:
# #     """Parse, prepare, embed and upsert MM-RAG documents into Qdrant."""

# #     TEXT_CONTENT_TYPES = {"page_text_plus_ocr", "text"}

# #     def __init__(
# #         self,
# #         collection_name: str | None = None,
# #         chunk_size: int = 2000,
# #         chunk_overlap: int = 120,
# #         batch_size: int = 64,
# #     ) -> None:
# #                 try:
# #             self.collection_name = (
# #                 collection_name
# #                 or os.getenv("QDRANT_COLLECTION_NAME")
# #                 or "mm-rag-documents"
# #             )

# #             self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
# #             self.embedding_dimension = 384

# #             self.qdrant_url = (
# #                 os.getenv("QDRANT_URL")
# #                 or os.getenv("QDRANT_Cluster_Endpoint")
# #             )
# #             self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
# #             self.batch_size = batch_size

# #             self._validate_config()

# #             self.embeddings = HuggingFaceEmbeddings(
# #                 model_name=self.embedding_model
# #             )

# #             self.text_splitter = RecursiveCharacterTextSplitter(
# #                 chunk_size=chunk_size,
# #                 chunk_overlap=chunk_overlap,
# #                 add_start_index=True,
# #             )

# #             self.client = QdrantClient(
# #                 url=self.qdrant_url,
# #                 api_key=self.qdrant_api_key,
# #             )

# #             self._ensure_collection()

# #             self.vector_store = QdrantVectorStore(
# #                 client=self.client,
# #                 collection_name=self.collection_name,
# #                 embedding=self.embeddings,
# #                 retrieval_mode=RetrievalMode.DENSE,
# #             )

# #             logger.info(
# #                 "ingestion_initialized",
# #                 collection_name=self.collection_name,
# #                 embedding_model=self.embedding_model,
# #             )
# #         # try:
# #         #     self.collection_name = (
# #         #         collection_name
# #         #         or os.getenv("QDRANT_COLLECTION_NAME")
# #         #         or "mm-rag-documents"
# #         #     )
# #         #    self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
# #         #  self.embedding_dimension = 384

# #         #     self.qdrant_url = (
# #         #         os.getenv("QDRANT_URL")
# #         #         or os.getenv("QDRANT_Cluster_Endpoint")
# #         #     )
# #         #     self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
# #         #     self.batch_size = batch_size

# #         #     self._validate_config()

# #         #     self.embeddings = OpenAIEmbeddings(
# #         #         model=self.embedding_model,
# #         #         dimensions=self.embedding_dimension,
# #         #     )
# #         #     self.text_splitter = RecursiveCharacterTextSplitter(
# #         #         chunk_size=chunk_size,
# #         #         chunk_overlap=chunk_overlap,
# #         #         add_start_index=True,
# #         #     )
# #         #     self.client = QdrantClient(
# #         #         url=self.qdrant_url,
# #         #         api_key=self.qdrant_api_key,
# #         #     )

# #         #     self._ensure_collection()

# #         #     self.vector_store = QdrantVectorStore(
# #         #         client=self.client,
# #         #         collection_name=self.collection_name,
# #         #         embedding=self.embeddings,
# #         #         retrieval_mode=RetrievalMode.DENSE,
# #         #     )

# #         #     logger.info(
# #         #         "ingestion_initialized",
# #         #         collection_name=self.collection_name,
# #         #         embedding_model=self.embedding_model,
# #         #     )

# #         except Exception as exc:
# #             logger.exception("ingestion_initialization_failed", error=str(exc))
# #             raise DocumentPortalException(
# #                 "Failed to initialize ingestion pipeline", exc
# #             ) from exc

# #     def _validate_config(self) -> None:
# #         if not os.getenv("OPENAI_API_KEY"):
# #             raise ValueError("OPENAI_API_KEY is missing")
# #         if not self.qdrant_url:
# #             raise ValueError("QDRANT_URL is missing")
# #         if self.embedding_dimension <= 0:
# #             raise ValueError("OPENAI_EMBEDDING_DIMENSION must be positive")
# #         if self.batch_size <= 0:
# #             raise ValueError("batch_size must be positive")

# #     def _ensure_collection(self) -> None:
# #         """Create the collection and filter indexes before ingestion."""
# #         if not self.client.collection_exists(self.collection_name):
# #             self.client.create_collection(
# #                 collection_name=self.collection_name,
# #                 vectors_config=models.VectorParams(
# #                     size=self.embedding_dimension,
# #                     distance=models.Distance.COSINE,
# #                 ),
# #             )
# #             logger.info(
# #                 "qdrant_collection_created",
# #                 collection_name=self.collection_name,
# #             )

# #         info = self.client.get_collection(self.collection_name)
# #         existing_indexes = set((info.payload_schema or {}).keys())

# #         required_indexes = {
# #             "metadata.document_id": models.PayloadSchemaType.KEYWORD,
# #             "metadata.filename": models.PayloadSchemaType.KEYWORD,
# #             "metadata.file_sha256": models.PayloadSchemaType.KEYWORD,
# #             "metadata.content_type": models.PayloadSchemaType.KEYWORD,
# #             "metadata.page_number": models.PayloadSchemaType.INTEGER,
# #         }

# #         for field_name, field_schema in required_indexes.items():
# #             if field_name not in existing_indexes:
# #                 self.client.create_payload_index(
# #                     collection_name=self.collection_name,
# #                     field_name=field_name,
# #                     field_schema=field_schema,
# #                     wait=True,
# #                 )

# #     @staticmethod
# #     def _document_id(source: str) -> str:
# #         return str(uuid5(NAMESPACE_URL, f"mm-rag-document:{source}"))

# #     @staticmethod
# #     def _point_id(
# #         source: str,
# #         page_number: Any,
# #         content_type: str,
# #         chunk_index: int,
# #         table_index: Any = "",
# #         image_index: Any = "",
# #     ) -> str:
# #         identity = "|".join(
# #             [
# #                 source,
# #                 str(page_number),
# #                 content_type,
# #                 str(table_index),
# #                 str(image_index),
# #                 str(chunk_index),
# #             ]
# #         )
# #         return str(uuid5(NAMESPACE_URL, f"mm-rag-point:{identity}"))

# #     def _split(self, document: Document) -> list[Document]:
# #         content_type = str(document.metadata.get("content_type", "unknown"))
# #         if content_type in self.TEXT_CONTENT_TYPES:
# #             return self.text_splitter.split_documents([document])
# #         return [document]

# #     def prepare_documents(
# #         self,
# #         documents: Sequence[Document],
# #     ) -> tuple[list[Document], list[str]]:
# #         """Split page text, preserve tables/images, and add stable metadata."""
# #         prepared: list[Document] = []
# #         point_ids: list[str] = []

# #         for document in documents:
# #             if not document.page_content.strip():
# #                 continue

# #             for chunk_index, chunk in enumerate(self._split(document)):
# #                 content = chunk.page_content.strip()
# #                 if not content:
# #                     continue

# #                 metadata = dict(chunk.metadata)
# #                 source = str(metadata.get("source", "unknown"))
# #                 content_type = str(metadata.get("content_type", "unknown"))
# #                 page_number = metadata.get("page_number", -1)

# #                 document_id = self._document_id(source)
# #                 point_id = self._point_id(
# #                     source=source,
# #                     page_number=page_number,
# #                     content_type=content_type,
# #                     chunk_index=chunk_index,
# #                     table_index=metadata.get("table_index", ""),
# #                     image_index=metadata.get("image_index", ""),
# #                 )

# #                 metadata.update(
# #                     {
# #                         "document_id": document_id,
# #                         "filename": Path(source).name,
# #                         "chunk_index": chunk_index,
# #                         "chunk_id": point_id,
# #                     }
# #                 )

# #                 prepared.append(
# #                     Document(page_content=content, metadata=metadata)
# #                 )
# #                 point_ids.append(point_id)

# #         if not prepared:
# #             raise ValueError("No documents available for ingestion")

# #         return prepared, point_ids

# #     def _delete_existing_document(self, document_id: str) -> None:
# #         """Prevent stale/duplicate chunks when the same PDF is re-ingested."""
# #         self.client.delete(
# #             collection_name=self.collection_name,
# #             points_selector=models.FilterSelector(
# #                 filter=models.Filter(
# #                     must=[
# #                         models.FieldCondition(
# #                             key="metadata.document_id",
# #                             match=models.MatchValue(value=document_id),
# #                         )
# #                     ]
# #                 )
# #             ),
# #             wait=True,
# #         )

# #     def ingest_documents(
# #         self,
# #         documents: Sequence[Document],
# #         replace_existing: bool = True,
# #     ) -> dict[str, Any]:
# #         try:
# #             prepared, point_ids = self.prepare_documents(documents)

# #             document_ids = sorted(
# #                 {str(doc.metadata["document_id"]) for doc in prepared}
# #             )

# #             if replace_existing:
# #                 for document_id in document_ids:
# #                     self._delete_existing_document(document_id)

# #             inserted_ids: list[str] = []

# #             for start in range(0, len(prepared), self.batch_size):
# #                 end = start + self.batch_size
# #                 inserted_ids.extend(
# #                     self.vector_store.add_documents(
# #                         documents=prepared[start:end],
# #                         ids=point_ids[start:end],
# #                     )
# #                 )

# #             result = {
# #                 "collection_name": self.collection_name,
# #                 "source_document_count": len(document_ids),
# #                 "input_document_count": len(documents),
# #                 "indexed_document_count": len(prepared),
# #                 "inserted_point_count": len(inserted_ids),
# #             }

# #             logger.info("document_ingestion_completed", **result)
# #             return result

# #         except Exception as exc:
# #             logger.exception("document_ingestion_failed", error=str(exc))
# #             raise DocumentPortalException(
# #                 "Failed to ingest documents into Qdrant", exc
# #             ) from exc

# #     def ingest_pdf(
# #         self,
# #         pdf_path: str | Path,
# #         output_dir: str | Path,
# #         tesseract_path: str | None = None,
# #         replace_existing: bool = True,
# #     ) -> dict[str, Any]:
# #         """Existing parser -> document preparation -> embeddings -> Qdrant."""
# #         try:
# #             parser = ComplexPDFParser(
# #                 pdf_path=str(pdf_path),
# #                 output_dir=str(output_dir),
# #                 tesseract_path=tesseract_path,
# #             )
# #             parsed = parser.parse(save_output=True)

# #             result = self.ingest_documents(
# #                 documents=parsed["documents"],
# #                 replace_existing=replace_existing,
# #             )
# #             result.update(
# #                 {
# #                     "pdf_path": str(pdf_path),
# #                     "parsed_pages": len(parsed["pages"]),
# #                     "parsed_tables": len(parsed["tables"]),
# #                     "parsed_images": len(parsed["images"]),
# #                 }
# #             )
# #             return result

# #         except DocumentPortalException:
# #             raise
# #         except Exception as exc:
# #             logger.exception(
# #                 "pdf_ingestion_failed",
# #                 pdf_path=str(pdf_path),
# #                 error=str(exc),
# #             )
# #             raise DocumentPortalException(
# #                 "Failed to parse and ingest PDF", exc
# #             ) from exc

# #     def get_vector_store(self) -> QdrantVectorStore:
# #         return self.vector_store


# # if __name__ == "__main__":
# #     pdf_path = (
# #         PROJECT_ROOT
# #         / "data"
# #         / "Client_Contracts_Policies_and_Incident_Records.pdf"
# #     )
# #     output_dir = PROJECT_ROOT / "data" / "parsed_pdf_output"

# #     ingestion = MultimodalDocumentIngestion()
# #     result = ingestion.ingest_pdf(
# #         pdf_path=pdf_path,
# #         output_dir=output_dir,
# #         tesseract_path=os.getenv("TESSERACT_PATH") or None,
# #         replace_existing=True,
# #     )

# #     print("Ingestion completed:", result)


# from __future__ import annotations
# from langchain_huggingface import HuggingFaceEmbeddings
# import os
# import sys
# from pathlib import Path
# from typing import Any, Sequence
# from uuid import NAMESPACE_URL, uuid5

# from dotenv import load_dotenv
# from langchain_core.documents import Document
# from langchain_qdrant import QdrantVectorStore, RetrievalMode
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from qdrant_client import QdrantClient, models

# PROJECT_ROOT = Path(__file__).resolve().parent.parent
# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))

# load_dotenv(PROJECT_ROOT / ".env")

# from exception.custom_exception import DocumentPortalException
# from logger.custom_logger import CustomLogger
# from src.parsing import ComplexPDFParser

# logger = CustomLogger().get_logger(__name__)



# class MultimodalDocumentIngestion:
#     """Parse, prepare, embed and upsert MM-RAG documents into Qdrant."""

#     TEXT_CONTENT_TYPES = {"page_text_plus_ocr", "text"}

#     def __init__(
#         self,
#         collection_name: str | None = None,
#         chunk_size: int = 2000,
#         chunk_overlap: int = 120,
#         batch_size: int = 64,
#     ) -> None:
#         try:
#             self.collection_name = (
#                 collection_name
#                 or os.getenv("QDRANT_COLLECTION_NAME")
#                 or "mm-rag-documents"
#             )

#             self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
#             self.embedding_dimension = 384

#             self.qdrant_url = (
#                 os.getenv("QDRANT_URL")
#                 or os.getenv("QDRANT_Cluster_Endpoint")
#             )
#             self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
#             self.batch_size = batch_size

#             self._validate_config()

#             self.embeddings = HuggingFaceEmbeddings(
#                 model_name=self.embedding_model
#             )

#             self.text_splitter = RecursiveCharacterTextSplitter(
#                 chunk_size=chunk_size,
#                 chunk_overlap=chunk_overlap,
#                 add_start_index=True,
#             )

#             self.client = QdrantClient(
#                 url=self.qdrant_url,
#                 api_key=self.qdrant_api_key,
#             )

#             self._ensure_collection()

#             self.vector_store = QdrantVectorStore(
#                 client=self.client,
#                 collection_name=self.collection_name,
#                 embedding=self.embeddings,
#                 retrieval_mode=RetrievalMode.DENSE,
#             )

#             logger.info(
#                 "ingestion_initialized",
#                 collection_name=self.collection_name,
#                 embedding_model=self.embedding_model,
#             )

#         except Exception as exc:
#             logger.exception("ingestion_initialization_failed", error=str(exc))
#             raise DocumentPortalException(
#                 "Failed to initialize ingestion pipeline", exc
#             ) from exc

#     def _validate_config(self) -> None:
#         if not self.qdrant_url:
#             raise ValueError("QDRANT_URL is missing")
#         if self.embedding_dimension <= 0:
#             raise ValueError("embedding_dimension must be positive")
#         if self.batch_size <= 0:
#             raise ValueError("batch_size must be positive")

#     def _ensure_collection(self) -> None:
#         """Create the collection and filter indexes before ingestion."""
#         if not self.client.collection_exists(self.collection_name):
#             self.client.create_collection(
#                 collection_name=self.collection_name,
#                 vectors_config=models.VectorParams(
#                     size=self.embedding_dimension,
#                     distance=models.Distance.COSINE,
#                 ),
#             )
#             logger.info(
#                 "qdrant_collection_created",
#                 collection_name=self.collection_name,
#             )

#         info = self.client.get_collection(self.collection_name)

#         # Prevent inserting 384-dimension vectors into an incompatible collection.
#         vectors_config = info.config.params.vectors
#         existing_dimension = getattr(vectors_config, "size", None)
#         if existing_dimension is not None and existing_dimension != self.embedding_dimension:
#             raise ValueError(
#                 f"Qdrant collection '{self.collection_name}' uses "
#                 f"{existing_dimension}-dimension vectors, but "
#                 f"{self.embedding_model} produces {self.embedding_dimension}. "
#                 "Use a separate 384-dimension collection; do not delete existing data."
#             )

#         existing_indexes = set((info.payload_schema or {}).keys())

#         required_indexes = {
#             "metadata.document_id": models.PayloadSchemaType.KEYWORD,
#             "metadata.filename": models.PayloadSchemaType.KEYWORD,
#             "metadata.file_sha256": models.PayloadSchemaType.KEYWORD,
#             "metadata.content_type": models.PayloadSchemaType.KEYWORD,
#             "metadata.page_number": models.PayloadSchemaType.INTEGER,
#         }

#         for field_name, field_schema in required_indexes.items():
#             if field_name not in existing_indexes:
#                 self.client.create_payload_index(
#                     collection_name=self.collection_name,
#                     field_name=field_name,
#                     field_schema=field_schema,
#                     wait=True,
#                 )

#     @staticmethod
#     def _document_id(source: str) -> str:
#         return str(uuid5(NAMESPACE_URL, f"mm-rag-document:{source}"))

#     @staticmethod
#     def _point_id(
#         source: str,
#         page_number: Any,
#         content_type: str,
#         chunk_index: int,
#         table_index: Any = "",
#         image_index: Any = "",
#     ) -> str:
#         identity = "|".join(
#             [
#                 source,
#                 str(page_number),
#                 content_type,
#                 str(table_index),
#                 str(image_index),
#                 str(chunk_index),
#             ]
#         )
#         return str(uuid5(NAMESPACE_URL, f"mm-rag-point:{identity}"))

#     def _split(self, document: Document) -> list[Document]:
#         content_type = str(document.metadata.get("content_type", "unknown"))
#         if content_type in self.TEXT_CONTENT_TYPES:
#             return self.text_splitter.split_documents([document])
#         return [document]

#     def prepare_documents(
#         self,
#         documents: Sequence[Document],
#     ) -> tuple[list[Document], list[str]]:
#         """Split page text, preserve tables/images, and add stable metadata."""
#         prepared: list[Document] = []
#         point_ids: list[str] = []

#         for document in documents:
#             if not document.page_content.strip():
#                 continue

#             for chunk_index, chunk in enumerate(self._split(document)):
#                 content = chunk.page_content.strip()
#                 if not content:
#                     continue

#                 metadata = dict(chunk.metadata)
#                 source = str(metadata.get("source", "unknown"))
#                 content_type = str(metadata.get("content_type", "unknown"))
#                 page_number = metadata.get("page_number", -1)

#                 document_id = self._document_id(source)
#                 point_id = self._point_id(
#                     source=source,
#                     page_number=page_number,
#                     content_type=content_type,
#                     chunk_index=chunk_index,
#                     table_index=metadata.get("table_index", ""),
#                     image_index=metadata.get("image_index", ""),
#                 )

#                 metadata.update(
#                     {
#                         "document_id": document_id,
#                         "filename": Path(source).name,
#                         "chunk_index": chunk_index,
#                         "chunk_id": point_id,
#                     }
#                 )

#                 prepared.append(
#                     Document(page_content=content, metadata=metadata)
#                 )
#                 point_ids.append(point_id)

#         if not prepared:
#             raise ValueError("No documents available for ingestion")

#         return prepared, point_ids

#     def _delete_existing_document(self, document_id: str) -> None:
#         """Prevent stale/duplicate chunks when the same PDF is re-ingested."""
#         self.client.delete(
#             collection_name=self.collection_name,
#             points_selector=models.FilterSelector(
#                 filter=models.Filter(
#                     must=[
#                         models.FieldCondition(
#                             key="metadata.document_id",
#                             match=models.MatchValue(value=document_id),
#                         )
#                     ]
#                 )
#             ),
#             wait=True,
#         )

#     def ingest_documents(
#         self,
#         documents: Sequence[Document],
#         replace_existing: bool = True,
#     ) -> dict[str, Any]:
#         try:
#             prepared, point_ids = self.prepare_documents(documents)

#             document_ids = sorted(
#                 {str(doc.metadata["document_id"]) for doc in prepared}
#             )

#             if replace_existing:
#                 for document_id in document_ids:
#                     self._delete_existing_document(document_id)

#             inserted_ids: list[str] = []

#             for start in range(0, len(prepared), self.batch_size):
#                 end = start + self.batch_size
#                 inserted_ids.extend(
#                     self.vector_store.add_documents(
#                         documents=prepared[start:end],
#                         ids=point_ids[start:end],
#                     )
#                 )

#             result = {
#                 "collection_name": self.collection_name,
#                 "source_document_count": len(document_ids),
#                 "input_document_count": len(documents),
#                 "indexed_document_count": len(prepared),
#                 "inserted_point_count": len(inserted_ids),
#             }

#             logger.info("document_ingestion_completed", **result)
#             return result

#         except Exception as exc:
#             logger.exception("document_ingestion_failed", error=str(exc))
#             raise DocumentPortalException(
#                 "Failed to ingest documents into Qdrant", exc
#             ) from exc

#     def ingest_pdf(
#         self,
#         pdf_path: str | Path,
#         output_dir: str | Path,
#         tesseract_path: str | None = None,
#         replace_existing: bool = True,
#     ) -> dict[str, Any]:
#         """Existing parser -> document preparation -> embeddings -> Qdrant."""
#         try:
#             parser = ComplexPDFParser(
#                 pdf_path=str(pdf_path),
#                 output_dir=str(output_dir),
#                 tesseract_path=tesseract_path,
#             )
#             parsed = parser.parse(save_output=True)

#             result = self.ingest_documents(
#                 documents=parsed["documents"],
#                 replace_existing=replace_existing,
#             )
#             result.update(
#                 {
#                     "pdf_path": str(pdf_path),
#                     "parsed_pages": len(parsed["pages"]),
#                     "parsed_tables": len(parsed["tables"]),
#                     "parsed_images": len(parsed["images"]),
#                 }
#             )
#             return result

#         except DocumentPortalException:
#             raise
#         except Exception as exc:
#             logger.exception(
#                 "pdf_ingestion_failed",
#                 pdf_path=str(pdf_path),
#                 error=str(exc),
#             )
#             raise DocumentPortalException(
#                 "Failed to parse and ingest PDF", exc
#             ) from exc

#     def get_vector_store(self) -> QdrantVectorStore:
#         return self.vector_store


# if __name__ == "__main__":
#     pdf_path = (
#         PROJECT_ROOT
#         / "data"
#         / "Client_Contracts_Policies_and_Incident_Records.pdf"
#     )
#     output_dir = PROJECT_ROOT / "data" / "parsed_pdf_output"

#     ingestion = MultimodalDocumentIngestion()
#     result = ingestion.ingest_pdf(
#         pdf_path=pdf_path,
#         output_dir=output_dir,
#         tesseract_path=os.getenv("TESSERACT_PATH") or None,
#         replace_existing=True,
#     )

#     print("Ingestion completed:", result)


from __future__ import annotations

import base64
import os
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

import requests
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient, models

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
from src.parsing import ComplexPDFParser


logger = CustomLogger().get_logger(__name__)


class MultimodalDocumentIngestion:
    """
    Parse, prepare, embed and upsert multimodal documents into Qdrant.

    Tenant-aware ingestion:
        - Every vector contains tenant_id.
        - Every vector contains PostgreSQL document_id.
        - Existing vectors are deleted only for the same
          tenant_id + document_id combination.

    Phase 6:
        - Detect image documents.
        - Generate semantic image captions using Ollama/Moondream.
        - Add captions to searchable page_content.
        - Store caption metadata in Qdrant.
    """

    TEXT_CONTENT_TYPES = {
        "page_text_plus_ocr",
        "text",
    }

    IMAGE_CONTENT_TYPES = {
        "image",
    }

    def __init__(
        self,
        collection_name: str | None = None,
        chunk_size: int = 2000,
        chunk_overlap: int = 120,
        batch_size: int = 16,
    ) -> None:
        try:
            # ----------------------------------------------------------
            # Qdrant configuration
            # ----------------------------------------------------------
            self.collection_name = (
                collection_name
                or os.getenv("QDRANT_COLLECTION_NAME")
                or "mm-rag-documents"
            )

            # ----------------------------------------------------------
            # Embedding configuration
            # ----------------------------------------------------------
            self.embedding_model = (
                os.getenv("HF_EMBEDDING_MODEL")
                or "sentence-transformers/all-MiniLM-L6-v2"
            )

            self.embedding_dimension = int(
                os.getenv("HF_EMBEDDING_DIMENSION") or 384
            )

            # ----------------------------------------------------------
            # Qdrant connection
            # ----------------------------------------------------------
            self.qdrant_url = (
                os.getenv("QDRANT_URL")
                or os.getenv("QDRANT_Cluster_Endpoint")
            )

            self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
            self.batch_size = batch_size

            # ----------------------------------------------------------
            # Ollama vision configuration
            # ----------------------------------------------------------
            self.ollama_base_url = (
                os.getenv("OLLAMA_BASE_URL")
                or "http://localhost:11434"
            ).rstrip("/")

            self.vision_model = (
                os.getenv("OLLAMA_VISION_MODEL")
                or "moondream"
            )

            self.vision_timeout = int(
                os.getenv("OLLAMA_VISION_TIMEOUT")
                or 180
            )

            # ----------------------------------------------------------
            # Validate configuration
            # ----------------------------------------------------------
            self._validate_config()

            # ----------------------------------------------------------
            # Embeddings
            # ----------------------------------------------------------
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model,
                model_kwargs={
                    "device": "cpu",
                },
                encode_kwargs={
                    "normalize_embeddings": True,
                },
            )

            # ----------------------------------------------------------
            # Text splitter
            # ----------------------------------------------------------
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                add_start_index=True,
            )

            # ----------------------------------------------------------
            # Qdrant client
            # ----------------------------------------------------------
            self.client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key,
            timeout=120,
            )

            self._ensure_collection()

            # ----------------------------------------------------------
            # LangChain Qdrant vector store
            # ----------------------------------------------------------
            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=self.embeddings,
                retrieval_mode=RetrievalMode.DENSE,
            )

            logger.info(
                "ingestion_initialized",
                collection_name=self.collection_name,
                embedding_model=self.embedding_model,
                vision_model=self.vision_model,
            )

        except Exception as exc:
            logger.exception(
                "ingestion_initialization_failed",
                error=str(exc),
            )

            raise DocumentPortalException(
                "Failed to initialize ingestion pipeline",
                exc,
            ) from exc

    # ==================================================================
    # Configuration
    # ==================================================================

    def _validate_config(self) -> None:
        if not self.qdrant_url:
            raise ValueError("QDRANT_URL is missing")

        if self.embedding_dimension <= 0:
            raise ValueError(
                "HF_EMBEDDING_DIMENSION must be positive"
            )

        if self.batch_size <= 0:
            raise ValueError(
                "batch_size must be positive"
            )

        if not self.ollama_base_url:
            raise ValueError(
                "OLLAMA_BASE_URL is missing"
            )

        if not self.vision_model:
            raise ValueError(
                "OLLAMA_VISION_MODEL is missing"
            )

    # ==================================================================
    # Qdrant collection
    # ==================================================================

    def _ensure_collection(self) -> None:
        """
        Create the collection if required and ensure all payload
        indexes required by tenant-aware retrieval exist.
        """

        if not self.client.collection_exists(
            self.collection_name
        ):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.embedding_dimension,
                    distance=models.Distance.COSINE,
                ),
            )

            logger.info(
                "qdrant_collection_created",
                collection_name=self.collection_name,
            )

        info = self.client.get_collection(
            self.collection_name
        )

        # --------------------------------------------------------------
        # Protect the existing collection from incompatible vectors.
        # --------------------------------------------------------------
        vectors_config = info.config.params.vectors

        existing_dimension = getattr(
            vectors_config,
            "size",
            None,
        )

        if (
            existing_dimension is not None
            and existing_dimension != self.embedding_dimension
        ):
            raise ValueError(
                f"Qdrant collection '{self.collection_name}' uses "
                f"{existing_dimension}-dimension vectors, but "
                f"{self.embedding_model} produces "
                f"{self.embedding_dimension}. "
                "Use a separate compatible collection; "
                "do not delete existing data."
            )

        # --------------------------------------------------------------
        # Required payload indexes
        # --------------------------------------------------------------
        existing_indexes = set(
            (info.payload_schema or {}).keys()
        )

        required_indexes = {
            "metadata.tenant_id": (
                models.PayloadSchemaType.KEYWORD
            ),
            "metadata.document_id": (
                models.PayloadSchemaType.KEYWORD
            ),
            "metadata.workspace_id": (
                models.PayloadSchemaType.KEYWORD
            ),
            "metadata.filename": (
                models.PayloadSchemaType.KEYWORD
            ),
            "metadata.file_sha256": (
                models.PayloadSchemaType.KEYWORD
            ),
            "metadata.content_type": (
                models.PayloadSchemaType.KEYWORD
            ),
            "metadata.page_number": (
                models.PayloadSchemaType.INTEGER
            ),
            "metadata.image_index": (
                models.PayloadSchemaType.INTEGER
            ),
        }

        for field_name, field_schema in required_indexes.items():
            if field_name not in existing_indexes:
                try:
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=field_name,
                        field_schema=field_schema,
                        wait=True,
                    )
                except Exception as exc:
                    # image_index may be absent or represented as a
                    # string in some parser outputs. Do not make an
                    # existing collection unusable because of this.
                    if field_name == "metadata.image_index":
                        logger.warning(
                            "payload_index_creation_skipped",
                            field_name=field_name,
                            error=str(exc),
                        )
                    else:
                        raise

    # ==================================================================
    # Stable point IDs
    # ==================================================================

    @staticmethod
    def _point_id(
        document_id: str,
        tenant_id: str,
        source: str,
        page_number: Any,
        content_type: str,
        chunk_index: int,
        table_index: Any = "",
        image_index: Any = "",
    ) -> str:
        """
        Generate a stable UUID5 point ID.

        Tenant and PostgreSQL document IDs are included so that
        different tenants can safely upload files with identical
        filenames.
        """

        identity = "|".join(
            [
                tenant_id,
                document_id,
                source,
                str(page_number),
                content_type,
                str(table_index),
                str(image_index),
                str(chunk_index),
            ]
        )

        from uuid import NAMESPACE_URL, uuid5

        return str(
            uuid5(
                NAMESPACE_URL,
                f"mm-rag-point:{identity}",
            )
        )

    # ==================================================================
    # Phase 6 - Image semantic captioning
    # ==================================================================

    def _resolve_image_path(
        self,
        document: Document,
    ) -> Path | None:
        """
        Resolve the physical image path from parser metadata.

        The parser may expose the path through image_path, source,
        or related metadata fields.
        """

        metadata = document.metadata or {}

        candidates = [
            metadata.get("image_path"),
            metadata.get("image_file"),
            metadata.get("file_path"),
            metadata.get("source"),
        ]

        for candidate in candidates:
            if not candidate:
                continue

            candidate_path = Path(str(candidate))

            # Direct path
            if candidate_path.exists():
                return candidate_path

            # Relative to project root
            project_candidate = (
                PROJECT_ROOT / candidate_path
            )

            if project_candidate.exists():
                return project_candidate

        return None

    def _generate_image_caption(
        self,
        image_path: str | Path,
    ) -> str:
        """
        Generate a semantic caption using the local Ollama
        vision model.

        The caption is later embedded with MiniLM, allowing
        natural-language queries to retrieve images.
        """

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image file not found: {image_path}"
            )

        # --------------------------------------------------------------
        # Read and encode image
        # --------------------------------------------------------------
        with image_path.open("rb") as image_file:
            image_base64 = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        prompt = (
            "Describe this image for document search. "
            "Be factual and concise. "
            "Mention important objects, visible text, labels, "
            "diagrams, symbols, layout, people, and other "
            "visually meaningful information. "
            "If text is visible, describe or transcribe the "
            "important visible text when possible. "
            "Do not invent information that is not visible."
        )

        logger.info(
            "image_caption_generation_started",
            image_path=str(image_path),
            vision_model=self.vision_model,
        )

        response = requests.post(
            f"{self.ollama_base_url}/api/generate",
            json={
                "model": self.vision_model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False,
            },
            timeout=self.vision_timeout,
        )

        response.raise_for_status()

        result = response.json()

        caption = str(
            result.get("response", "")
        ).strip()

        if not caption:
            raise RuntimeError(
                f"Ollama vision model '{self.vision_model}' "
                "returned an empty caption"
            )

        logger.info(
            "image_caption_generated",
            image_path=str(image_path),
            vision_model=self.vision_model,
            caption_length=len(caption),
        )

        return caption

    def _enrich_image_document(
        self,
        document: Document,
    ) -> Document:
        """
        Generate and attach a semantic caption to an image
        document.

        The caption is added to page_content so that the existing
        MiniLM embedding pipeline converts the image semantics into
        a searchable vector.

        Caption metadata is also stored in the Qdrant payload.
        """

        metadata = dict(
            document.metadata or {}
        )

        content_type = str(
            metadata.get(
                "content_type",
                "",
            )
        ).strip().lower()

        # --------------------------------------------------------------
        # Not an image -> leave unchanged
        # --------------------------------------------------------------
        if content_type not in self.IMAGE_CONTENT_TYPES:
            return document

        image_path = self._resolve_image_path(
            document
        )

        # --------------------------------------------------------------
        # Image path unavailable
        # --------------------------------------------------------------
        if image_path is None:
            error_message = (
                "Could not resolve physical image path "
                "from document metadata"
            )

            logger.warning(
                "image_caption_failed",
                error=error_message,
                metadata=metadata,
            )

            metadata.update(
                {
                    "image_searchable": False,
                    "image_caption_error": error_message,
                    "image_caption_model": self.vision_model,
                    "image_caption_version": "v1",
                }
            )

            return Document(
                page_content=document.page_content,
                metadata=metadata,
            )

        # --------------------------------------------------------------
        # Generate caption
        # --------------------------------------------------------------
        try:
            caption = self._generate_image_caption(
                image_path
            )

            original_content = (
                document.page_content or ""
            ).strip()

            # ----------------------------------------------------------
            # Make image semantics part of the embedded text.
            # ----------------------------------------------------------
            enriched_content = (
                "IMAGE CAPTION:\n"
                f"{caption}\n\n"
                "IMAGE METADATA:\n"
                f"Page: "
                f"{metadata.get('page_number', 'unknown')}\n"
                f"Image Index: "
                f"{metadata.get('image_index', 'unknown')}\n"
                f"Image Path: "
                f"{image_path}\n\n"
                "PARSER CONTENT:\n"
                f"{original_content}"
            )

            metadata.update(
                {
                    "image_path": str(image_path),
                    "image_caption": caption,
                    "image_caption_model": (
                        self.vision_model
                    ),
                    "image_searchable": True,
                    "image_caption_version": "v1",
                }
            )

            return Document(
                page_content=enriched_content,
                metadata=metadata,
            )

        except Exception as exc:
            logger.warning(
                "image_caption_failed",
                image_path=str(image_path),
                error=str(exc),
            )

            # ----------------------------------------------------------
            # Do not destroy the original image document if vision
            # captioning fails.
            # ----------------------------------------------------------
            metadata.update(
                {
                    "image_path": str(image_path),
                    "image_searchable": False,
                    "image_caption_model": (
                        self.vision_model
                    ),
                    "image_caption_version": "v1",
                    "image_caption_error": str(exc),
                }
            )

            return Document(
                page_content=document.page_content,
                metadata=metadata,
            )

    # ==================================================================
    # Document splitting
    # ==================================================================

    def _split(
        self,
        document: Document,
    ) -> list[Document]:
        content_type = str(
            document.metadata.get(
                "content_type",
                "unknown",
            )
        )

        # --------------------------------------------------------------
        # Normal text is chunked.
        # --------------------------------------------------------------
        if content_type in self.TEXT_CONTENT_TYPES:
            return self.text_splitter.split_documents(
                [document]
            )

        # --------------------------------------------------------------
        # Images and tables remain as individual documents.
        # --------------------------------------------------------------
        return [document]

    # ==================================================================
    # Document preparation
    # ==================================================================

    def prepare_documents(
        self,
        documents: Sequence[Document],
        *,
        tenant_id: str,
        document_id: str,
        workspace_id: str | None = None,
        file_sha256: str | None = None,
        filename: str | None = None,
    ) -> tuple[list[Document], list[str]]:
        """
        Split text, preserve tables/images, enrich images with
        semantic captions, and attach tenant-aware metadata.

        ``filename`` overrides the logical file name stored in the
        payload. Without it the name is derived from the parser's
        ``source`` path, which for the async worker is a localized
        artifact (``<hash>_name.pdf`` or a temp file) rather than the
        name the user actually uploaded.
        """

        if not tenant_id:
            raise ValueError(
                "tenant_id is required for ingestion"
            )

        if not document_id:
            raise ValueError(
                "document_id is required for ingestion"
            )

        prepared: list[Document] = []
        point_ids: list[str] = []

        image_count = 0
        searchable_image_count = 0

        for document in documents:
            if not document.page_content.strip():
                continue

            # ----------------------------------------------------------
            # Phase 6:
            # Enrich image documents BEFORE embedding.
            # ----------------------------------------------------------
            content_type = str(
                document.metadata.get(
                    "content_type",
                    "",
                )
            ).strip().lower()

            if content_type in self.IMAGE_CONTENT_TYPES:
                image_count += 1

                document = self._enrich_image_document(
                    document
                )

                if document.metadata.get(
                    "image_searchable",
                    False,
                ):
                    searchable_image_count += 1

            # ----------------------------------------------------------
            # Split text / preserve image and table documents.
            # ----------------------------------------------------------
            for chunk_index, chunk in enumerate(
                self._split(document)
            ):
                content = (
                    chunk.page_content or ""
                ).strip()

                if not content:
                    continue

                metadata = dict(
                    chunk.metadata or {}
                )

                source = str(
                    metadata.get(
                        "source",
                        "unknown",
                    )
                )

                content_type = str(
                    metadata.get(
                        "content_type",
                        "unknown",
                    )
                )

                page_number = metadata.get(
                    "page_number",
                    -1,
                )

                # ------------------------------------------------------
                # Stable point ID
                # ------------------------------------------------------
                point_id = self._point_id(
                    document_id=document_id,
                    tenant_id=tenant_id,
                    source=source,
                    page_number=page_number,
                    content_type=content_type,
                    chunk_index=chunk_index,
                    table_index=metadata.get(
                        "table_index",
                        "",
                    ),
                    image_index=metadata.get(
                        "image_index",
                        "",
                    ),
                )

                # ------------------------------------------------------
                # Mandatory tenant/document metadata
                # ------------------------------------------------------
                metadata.update(
                    {
                        "tenant_id": tenant_id,
                        "document_id": document_id,
                        "filename": Path(
                            filename or source
                        ).name,
                        "chunk_index": chunk_index,
                        "chunk_id": point_id,
                    }
                )

                if workspace_id:
                    metadata["workspace_id"] = workspace_id

                if file_sha256:
                    metadata["file_sha256"] = file_sha256

                prepared.append(
                    Document(
                        page_content=content,
                        metadata=metadata,
                    )
                )

                point_ids.append(point_id)

        if not prepared:
            raise ValueError(
                "No documents available for ingestion"
            )

        logger.info(
            "documents_prepared",
            input_document_count=len(documents),
            prepared_document_count=len(prepared),
            image_count=image_count,
            searchable_image_count=searchable_image_count,
            vision_model=self.vision_model,
        )

        return prepared, point_ids

    # ==================================================================
    # Existing document cleanup
    # ==================================================================

    def _delete_existing_document(
        self,
        *,
        tenant_id: str,
        document_id: str,
    ) -> None:
        """
        Delete old vectors belonging to exactly this tenant
        and document.

        The tenant condition prevents one tenant's re-ingestion
        from deleting another tenant's vectors.
        """

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.tenant_id",
                            match=models.MatchValue(
                                value=tenant_id
                            ),
                        ),
                        models.FieldCondition(
                            key="metadata.document_id",
                            match=models.MatchValue(
                                value=document_id
                            ),
                        ),
                    ]
                )
            ),
            wait=True,
        )

    # ==================================================================
    # Document ingestion
    # ==================================================================

    def ingest_documents(
        self,
        documents: Sequence[Document],
        *,
        tenant_id: str,
        document_id: str,
        workspace_id: str | None = None,
        file_sha256: str | None = None,
        filename: str | None = None,
        replace_existing: bool = True,
        progress_callback: Callable[[str], None] | None = None,
    ) -> dict[str, Any]:
        try:
            # ----------------------------------------------------------
            # Stage: chunking (split + image captioning + metadata)
            # ----------------------------------------------------------
            if progress_callback is not None:
                progress_callback("chunking")

            prepared, point_ids = (
                self.prepare_documents(
                    documents,
                    tenant_id=tenant_id,
                    document_id=document_id,
                    workspace_id=workspace_id,
                    file_sha256=file_sha256,
                    filename=filename,
                )
            )

            document_ids = sorted(
                {
                    str(
                        doc.metadata[
                            "document_id"
                        ]
                    )
                    for doc in prepared
                }
            )

            # ----------------------------------------------------------
            # Remove old vectors for exactly this tenant/document.
            # ----------------------------------------------------------
            if replace_existing:
                self._delete_existing_document(
                    tenant_id=tenant_id,
                    document_id=document_id,
                )

            inserted_ids: list[str] = []

            # ----------------------------------------------------------
            # Stage: indexing (embed + upsert into Qdrant)
            # ----------------------------------------------------------
            if progress_callback is not None:
                progress_callback("indexing")

            # ----------------------------------------------------------
            # Batch insertion into Qdrant.
            # ----------------------------------------------------------
            for start in range(
                0,
                len(prepared),
                self.batch_size,
            ):
                end = start + self.batch_size

                inserted_ids.extend(
                    self.vector_store.add_documents(
                        documents=prepared[start:end],
                        ids=point_ids[start:end],
                    )
                )

            image_documents = [
                doc
                for doc in prepared
                if str(
                    doc.metadata.get(
                        "content_type",
                        "",
                    )
                ).lower()
                == "image"
            ]

            searchable_images = [
                doc
                for doc in image_documents
                if doc.metadata.get(
                    "image_searchable",
                    False,
                )
            ]

            result = {
                "collection_name": (
                    self.collection_name
                ),
                "tenant_id": tenant_id,
                "document_id": document_id,
                "source_document_count": len(
                    document_ids
                ),
                "input_document_count": len(
                    documents
                ),
                "indexed_document_count": len(
                    prepared
                ),
                "inserted_point_count": len(
                    inserted_ids
                ),
                "image_count": len(
                    image_documents
                ),
                "searchable_image_count": len(
                    searchable_images
                ),
                "vision_model": self.vision_model,
            }

            logger.info(
                "document_ingestion_completed",
                **result,
            )

            return result

        except Exception as exc:
            logger.exception(
                "document_ingestion_failed",
                error=str(exc),
            )

            raise DocumentPortalException(
                "Failed to ingest documents into Qdrant",
                exc,
            ) from exc

    # ==================================================================
    # PDF ingestion
    # ==================================================================

    def ingest_pdf(
        self,
        pdf_path: str | Path,
        output_dir: str | Path,
        *,
        tenant_id: str,
        document_id: str,
        workspace_id: str | None = None,
        file_sha256: str | None = None,
        filename: str | None = None,
        tesseract_path: str | None = None,
        replace_existing: bool = True,
        progress_callback: Callable[[str], None] | None = None,
    ) -> dict[str, Any]:
        """
        Parser -> image captioning -> document preparation
        -> embeddings -> Qdrant.

        tenant_id and document_id come from PostgreSQL and are
        attached to every vector. ``filename`` is the original upload
        name; it is recorded in the payload so citations and
        provenance do not leak the localized artifact name.
        """

        if not tenant_id:
            raise ValueError(
                "tenant_id is required for PDF ingestion"
            )

        if not document_id:
            raise ValueError(
                "document_id is required for PDF ingestion"
            )

        try:
            # ----------------------------------------------------------
            # Parse PDF
            # ----------------------------------------------------------
            parser = ComplexPDFParser(
                pdf_path=str(pdf_path),
                output_dir=str(output_dir),
                tesseract_path=tesseract_path,
            )

            parsed = parser.parse(
                save_output=True
            )

            # ----------------------------------------------------------
            # Prepare + caption + embed + store
            # ----------------------------------------------------------
            result = self.ingest_documents(
                documents=parsed["documents"],
                tenant_id=tenant_id,
                document_id=document_id,
                workspace_id=workspace_id,
                file_sha256=file_sha256,
                filename=filename,
                replace_existing=replace_existing,
                progress_callback=progress_callback,
            )

            result.update(
                {
                    "pdf_path": str(pdf_path),
                    "parsed_pages": len(
                        parsed["pages"]
                    ),
                    "parsed_tables": len(
                        parsed["tables"]
                    ),
                    "parsed_images": len(
                        parsed["images"]
                    ),
                }
            )

            return result

        except DocumentPortalException:
            raise

        except Exception as exc:
            logger.exception(
                "pdf_ingestion_failed",
                pdf_path=str(pdf_path),
                tenant_id=tenant_id,
                document_id=document_id,
                error=str(exc),
            )

            raise DocumentPortalException(
                "Failed to parse and ingest PDF",
                exc,
            ) from exc

    # ==================================================================
    # Vector store
    # ==================================================================

    def get_vector_store(
        self,
    ) -> QdrantVectorStore:
        return self.vector_store


# ======================================================================
# Manual ingestion test
# ======================================================================

if __name__ == "__main__":
    pdf_path = (
        PROJECT_ROOT
        / "data"
        / "Client_Contracts_Policies_and_Incident_Records.pdf"
    )

    output_dir = (
        PROJECT_ROOT
        / "data"
        / "parsed_pdf_output"
    )

    ingestion = MultimodalDocumentIngestion()

    # Manual testing requires real PostgreSQL tenant/document IDs.
    result = ingestion.ingest_pdf(
        pdf_path=pdf_path,
        output_dir=output_dir,
        tenant_id="TEST_TENANT_ID",
        document_id="TEST_DOCUMENT_ID",
        tesseract_path=(
            os.getenv("TESSERACT_PATH")
            or None
        ),
        replace_existing=True,
    )

    print(
        "Ingestion completed:",
        result,
    )