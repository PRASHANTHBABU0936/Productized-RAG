# from __future__ import annotations

# import os
# import sys
# from pathlib import Path
# from typing import Any, Iterable

# from dotenv import load_dotenv
# from langchain_core.documents import Document
# from langchain_core.vectorstores import VectorStoreRetriever
# from langchain_openai import OpenAIEmbeddings
# from langchain_qdrant import QdrantVectorStore, RetrievalMode
# from qdrant_client import QdrantClient, models


# # ---------------------------------------------------------------------
# # Project setup
# # ---------------------------------------------------------------------

# PROJECT_ROOT = Path(__file__).resolve().parent.parent

# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))

# load_dotenv(PROJECT_ROOT / ".env")

# from exception.custom_exception import DocumentPortalException
# from logger.custom_logger import CustomLogger


# logger = CustomLogger().get_logger(__name__)



# class MultimodalQdrantRetriever:
#     """
#     Retrieve MM-RAG documents from an existing Qdrant collection.

#     The ingestion pipeline stores LangChain documents using this payload shape:

#         {
#             "page_content": "...",
#             "metadata": {
#                 "document_id": "...",
#                 "filename": "...",
#                 "content_type": "page_text_plus_ocr | table | image",
#                 "page_number": 1,
#                 ...
#             }
#         }

#     Therefore Qdrant filters use keys such as:
#         metadata.filename
#         metadata.content_type
#         metadata.page_number
#         metadata.document_id
#     """

#     VALID_CONTENT_TYPES = {
#         "page_text_plus_ocr",
#         "text",
#         "table",
#         "image",
#     }

#     def __init__(
#         self,
#         collection_name: str | None = None,
#     ) -> None:
#         try:
#             self.collection_name = (
#                 collection_name
#                 or os.getenv("QDRANT_COLLECTION_NAME")
#                 or "mm-rag-documents"
#             )

#             self.embedding_model = (
#                 os.getenv("OPENAI_EMBEDDING_MODEL")
#                 or "text-embedding-3-large"
#             )

#             self.embedding_dimension = int(
#                 os.getenv("OPENAI_EMBEDDING_DIMENSION")
#                 or 3072
#             )

#             self.qdrant_url = (
#                 os.getenv("QDRANT_URL")
#                 or os.getenv("QDRANT_Cluster_Endpoint")
#             )

#             self.qdrant_api_key = os.getenv("QDRANT_API_KEY")

#             self._validate_config()

#             self.client = QdrantClient(
#                 url=self.qdrant_url,
#                 api_key=self.qdrant_api_key,
#             )

#             self._validate_collection()

#             self.embeddings = OpenAIEmbeddings(
#                 model=self.embedding_model,
#                 dimensions=self.embedding_dimension,
#             )

#             self.vector_store = QdrantVectorStore(
#                 client=self.client,
#                 collection_name=self.collection_name,
#                 embedding=self.embeddings,
#                 retrieval_mode=RetrievalMode.DENSE,
#             )

#             logger.info(
#                 "retriever_initialized",
#                 collection_name=self.collection_name,
#                 embedding_model=self.embedding_model,
#             )

#         except Exception as exc:
#             logger.exception(
#                 "retriever_initialization_failed",
#                 error=str(exc),
#             )
#             raise DocumentPortalException(
#                 "Failed to initialize Qdrant retriever",
#                 exc,
#             ) from exc

#     # -----------------------------------------------------------------
#     # Configuration
#     # -----------------------------------------------------------------

#     def _validate_config(self) -> None:
#         if not os.getenv("OPENAI_API_KEY"):
#             raise ValueError("OPENAI_API_KEY is missing")

#         if not self.qdrant_url:
#             raise ValueError("QDRANT_URL is missing")

#         if self.embedding_dimension <= 0:
#             raise ValueError(
#                 "OPENAI_EMBEDDING_DIMENSION must be positive"
#             )

#     def _validate_collection(self) -> None:
#         """
#         Retrieval should use an already-ingested collection.

#         Unlike ingestion.py, this class intentionally does not create a
#         collection if one is missing.
#         """
#         if not self.client.collection_exists(self.collection_name):
#             raise ValueError(
#                 f"Qdrant collection does not exist: "
#                 f"{self.collection_name}"
#             )

#     # -----------------------------------------------------------------
#     # Filter helpers
#     # -----------------------------------------------------------------

#     @classmethod
#     def _normalize_content_types(
#         cls,
#         content_types: Iterable[str] | None,
#     ) -> list[str]:
#         if content_types is None:
#             return []

#         normalized = [
#             str(content_type).strip()
#             for content_type in content_types
#             if str(content_type).strip()
#         ]

#         invalid = sorted(
#             set(normalized) - cls.VALID_CONTENT_TYPES
#         )

#         if invalid:
#             raise ValueError(
#                 "Unsupported content_types: "
#                 f"{invalid}. Valid values are: "
#                 f"{sorted(cls.VALID_CONTENT_TYPES)}"
#             )

#         return normalized

#     def build_filter(
#         self,
#         *,
#         filename: str | None = None,
#         document_id: str | None = None,
#         content_types: Iterable[str] | None = None,
#         page_number: int | None = None,
#         page_from: int | None = None,
#         page_to: int | None = None,
#     ) -> models.Filter | None:
#         """
#         Build a Qdrant metadata filter.

#         Examples:
#             filename="report.pdf"

#             content_types=["table", "image"]

#             page_number=5

#             page_from=3, page_to=10
#         """
#         must_conditions: list[Any] = []

#         if filename:
#             must_conditions.append(
#                 models.FieldCondition(
#                     key="metadata.filename",
#                     match=models.MatchValue(
#                         value=Path(filename).name
#                     ),
#                 )
#             )

#         if document_id:
#             must_conditions.append(
#                 models.FieldCondition(
#                     key="metadata.document_id",
#                     match=models.MatchValue(
#                         value=document_id
#                     ),
#                 )
#             )

#         normalized_types = self._normalize_content_types(
#             content_types
#         )

#         if normalized_types:
#             must_conditions.append(
#                 models.FieldCondition(
#                     key="metadata.content_type",
#                     match=models.MatchAny(
#                         any=normalized_types
#                     ),
#                 )
#             )

#         if page_number is not None:
#             if page_number <= 0:
#                 raise ValueError(
#                     "page_number must be greater than 0"
#                 )

#             must_conditions.append(
#                 models.FieldCondition(
#                     key="metadata.page_number",
#                     match=models.MatchValue(
#                         value=page_number
#                     ),
#                 )
#             )

#         elif page_from is not None or page_to is not None:
#             if page_from is not None and page_from <= 0:
#                 raise ValueError(
#                     "page_from must be greater than 0"
#                 )

#             if page_to is not None and page_to <= 0:
#                 raise ValueError(
#                     "page_to must be greater than 0"
#                 )

#             if (
#                 page_from is not None
#                 and page_to is not None
#                 and page_from > page_to
#             ):
#                 raise ValueError(
#                     "page_from cannot be greater than page_to"
#                 )

#             must_conditions.append(
#                 models.FieldCondition(
#                     key="metadata.page_number",
#                     range=models.Range(
#                         gte=page_from,
#                         lte=page_to,
#                     ),
#                 )
#             )

#         if not must_conditions:
#             return None

#         return models.Filter(
#             must=must_conditions
#         )

#     # -----------------------------------------------------------------
#     # Dense retrieval
#     # -----------------------------------------------------------------

#     def retrieve(
#         self,
#         query: str,
#         *,
#         k: int = 5,
#         filename: str | None = None,
#         document_id: str | None = None,
#         content_types: Iterable[str] | None = None,
#         page_number: int | None = None,
#         page_from: int | None = None,
#         page_to: int | None = None,
#     ) -> list[Document]:
#         """
#         Return the top-k most relevant documents.

#         Higher-level generation code can use the returned metadata to decide
#         whether a result is normal text, a table, or an image record.
#         """
#         try:
#             query = query.strip()

#             if not query:
#                 raise ValueError("Query cannot be empty")

#             if k <= 0:
#                 raise ValueError("k must be greater than 0")

#             query_filter = self.build_filter(
#                 filename=filename,
#                 document_id=document_id,
#                 content_types=content_types,
#                 page_number=page_number,
#                 page_from=page_from,
#                 page_to=page_to,
#             )

#             documents = self.vector_store.similarity_search(
#                 query=query,
#                 k=k,
#                 filter=query_filter,
#             )

#             logger.info(
#                 "documents_retrieved",
#                 query=query,
#                 k=k,
#                 result_count=len(documents),
#                 content_types=list(content_types)
#                 if content_types is not None
#                 else None,
#             )

#             return documents

#         except Exception as exc:
#             logger.exception(
#                 "document_retrieval_failed",
#                 query=query,
#                 error=str(exc),
#             )
#             raise DocumentPortalException(
#                 "Failed to retrieve documents from Qdrant",
#                 exc,
#             ) from exc

#     def retrieve_with_scores(
#         self,
#         query: str,
#         *,
#         k: int = 5,
#         filename: str | None = None,
#         document_id: str | None = None,
#         content_types: Iterable[str] | None = None,
#         page_number: int | None = None,
#         page_from: int | None = None,
#         page_to: int | None = None,
#     ) -> list[tuple[Document, float]]:
#         """
#         Return documents with Qdrant similarity scores.

#         For our cosine-similarity collection, larger scores indicate a closer
#         vector match.
#         """
#         try:
#             query = query.strip()

#             if not query:
#                 raise ValueError("Query cannot be empty")

#             if k <= 0:
#                 raise ValueError("k must be greater than 0")

#             query_filter = self.build_filter(
#                 filename=filename,
#                 document_id=document_id,
#                 content_types=content_types,
#                 page_number=page_number,
#                 page_from=page_from,
#                 page_to=page_to,
#             )

#             results = (
#                 self.vector_store.similarity_search_with_score(
#                     query=query,
#                     k=k,
#                     filter=query_filter,
#                 )
#             )

#             logger.info(
#                 "documents_retrieved_with_scores",
#                 query=query,
#                 k=k,
#                 result_count=len(results),
#             )

#             return results

#         except Exception as exc:
#             logger.exception(
#                 "scored_document_retrieval_failed",
#                 query=query,
#                 error=str(exc),
#             )
#             raise DocumentPortalException(
#                 "Failed to retrieve scored documents from Qdrant",
#                 exc,
#             ) from exc

#     # -----------------------------------------------------------------
#     # LangChain retriever
#     # -----------------------------------------------------------------

#     def as_langchain_retriever(
#         self,
#         *,
#         search_type: str = "similarity",
#         k: int = 5,
#         fetch_k: int = 20,
#         lambda_mult: float = 0.5,
#         filename: str | None = None,
#         document_id: str | None = None,
#         content_types: Iterable[str] | None = None,
#         page_number: int | None = None,
#         page_from: int | None = None,
#         page_to: int | None = None,
#     ) -> VectorStoreRetriever:
#         """
#         Return a standard LangChain retriever.

#         Supported search types here:
#         - similarity
#         - mmr

#         Example:
#             retriever = obj.as_langchain_retriever(
#                 search_type="similarity",
#                 k=5,
#                 content_types=["table", "image"],
#             )

#             docs = retriever.invoke("What does the chart show?")
#         """
#         if search_type not in {"similarity", "mmr"}:
#             raise ValueError(
#                 "search_type must be 'similarity' or 'mmr'"
#             )

#         if k <= 0:
#             raise ValueError("k must be greater than 0")

#         query_filter = self.build_filter(
#             filename=filename,
#             document_id=document_id,
#             content_types=content_types,
#             page_number=page_number,
#             page_from=page_from,
#             page_to=page_to,
#         )

#         search_kwargs: dict[str, Any] = {
#             "k": k,
#         }

#         if query_filter is not None:
#             search_kwargs["filter"] = query_filter

#         if search_type == "mmr":
#             if fetch_k < k:
#                 raise ValueError(
#                     "fetch_k must be greater than or equal to k"
#                 )

#             if not 0.0 <= lambda_mult <= 1.0:
#                 raise ValueError(
#                     "lambda_mult must be between 0 and 1"
#                 )

#             search_kwargs.update(
#                 {
#                     "fetch_k": fetch_k,
#                     "lambda_mult": lambda_mult,
#                 }
#             )

#         return self.vector_store.as_retriever(
#             search_type=search_type,
#             search_kwargs=search_kwargs,
#         )

#     # -----------------------------------------------------------------
#     # Useful inspection helpers
#     # -----------------------------------------------------------------

#     @staticmethod
#     def format_results(
#         results: list[tuple[Document, float]],
#         *,
#         content_preview_chars: int = 700,
#     ) -> str:
#         """Format scored results for CLI/debugging."""
#         lines: list[str] = []

#         for rank, (document, score) in enumerate(
#             results,
#             start=1,
#         ):
#             metadata = document.metadata
#             content = document.page_content.strip()

#             if len(content) > content_preview_chars:
#                 content = (
#                     content[:content_preview_chars]
#                     + "..."
#                 )

#             lines.extend(
#                 [
#                     f"\n{'=' * 80}",
#                     f"Rank: {rank}",
#                     f"Score: {score:.4f}",
#                     (
#                         "Type: "
#                         f"{metadata.get('content_type', 'unknown')}"
#                     ),
#                     (
#                         "Page: "
#                         f"{metadata.get('page_number', 'unknown')}"
#                     ),
#                     (
#                         "File: "
#                         f"{metadata.get('filename', 'unknown')}"
#                     ),
#                     f"Content:\n{content}",
#                 ]
#             )

#             image_path = metadata.get("image_path")
#             if image_path:
#                 lines.append(
#                     f"Image path: {image_path}"
#                 )

#         return "\n".join(lines)

#     def collection_status(self) -> dict[str, Any]:
#         """Return basic collection information for debugging/UI."""
#         try:
#             info = self.client.get_collection(
#                 self.collection_name
#             )

#             return {
#                 "collection_name": self.collection_name,
#                 "points_count": getattr(
#                     info,
#                     "points_count",
#                     None,
#                 ),
#                 "vectors_count": getattr(
#                     info,
#                     "vectors_count",
#                     None,
#                 ),
#                 "status": str(
#                     getattr(info, "status", "unknown")
#                 ),
#             }

#         except Exception as exc:
#             raise DocumentPortalException(
#                 "Failed to read Qdrant collection status",
#                 exc,
#             ) from exc


# # ---------------------------------------------------------------------
# # Manual retrieval test
# # ---------------------------------------------------------------------

# if __name__ == "__main__":
#     retriever = MultimodalQdrantRetriever()

#     print(
#         "Collection status:",
#         retriever.collection_status(),
#     )

#     query = (
#         "What are the important policies and incident details?"
#     )

#     results = retriever.retrieve_with_scores(
#         query=query,
#         k=5,
#     )

#     print(
#         retriever.format_results(results)
#     )



# from __future__ import annotations

# import os
# import sys
# from pathlib import Path
# from typing import Any, Iterable

# from dotenv import load_dotenv
# from langchain_core.documents import Document
# from langchain_core.vectorstores import VectorStoreRetriever
# from langchain_openai import OpenAIEmbeddings
# from langchain_qdrant import QdrantVectorStore, RetrievalMode
# from qdrant_client import QdrantClient, models


# # ---------------------------------------------------------------------
# # Project setup
# # ---------------------------------------------------------------------

# PROJECT_ROOT = Path(__file__).resolve().parent.parent

# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))

# load_dotenv(PROJECT_ROOT / ".env")

# from exception.custom_exception import DocumentPortalException
# from logger.custom_logger import CustomLogger


# logger = CustomLogger().get_logger(__name__)



# class MultimodalQdrantRetriever:
#     """
#     Retrieve MM-RAG documents from an existing Qdrant collection.

#     The ingestion pipeline stores LangChain documents using this payload shape:

#         {
#             "page_content": "...",
#             "metadata": {
#                 "document_id": "...",
#                 "filename": "...",
#                 "content_type": "page_text_plus_ocr | table | image",
#                 "page_number": 1,
#                 ...
#             }
#         }

#     Therefore Qdrant filters use keys such as:
#         metadata.filename
#         metadata.content_type
#         metadata.page_number
#         metadata.document_id
#     """

#     VALID_CONTENT_TYPES = {
#         "page_text_plus_ocr",
#         "text",
#         "table",
#         "image",
#     }

#     def __init__(
#         self,
#         collection_name: str | None = None,
#     ) -> None:
#         try:
#             self.collection_name = (
#                 collection_name
#                 or os.getenv("QDRANT_COLLECTION_NAME")
#                 or "mm-rag-documents"
#             )

#             self.embedding_model = (
#                 os.getenv("OPENAI_EMBEDDING_MODEL")
#                 or "text-embedding-3-large"
#             )

#             self.embedding_dimension = int(
#                 os.getenv("OPENAI_EMBEDDING_DIMENSION")
#                 or 3072
#             )

#             self.qdrant_url = (
#                 os.getenv("QDRANT_URL")
#                 or os.getenv("QDRANT_Cluster_Endpoint")
#             )

#             self.qdrant_api_key = os.getenv("QDRANT_API_KEY")

#             self._validate_config()

#             self.client = QdrantClient(
#                 url=self.qdrant_url,
#                 api_key=self.qdrant_api_key,
#             )

#             self._validate_collection()

#             self.embeddings = OpenAIEmbeddings(
#                 model=self.embedding_model,
#                 dimensions=self.embedding_dimension,
#             )

#             self.vector_store = QdrantVectorStore(
#                 client=self.client,
#                 collection_name=self.collection_name,
#                 embedding=self.embeddings,
#                 retrieval_mode=RetrievalMode.DENSE,
#             )

#             logger.info(
#                 "retriever_initialized",
#                 collection_name=self.collection_name,
#                 embedding_model=self.embedding_model,
#             )

#         except Exception as exc:
#             logger.exception(
#                 "retriever_initialization_failed",
#                 error=str(exc),
#             )
#             raise DocumentPortalException(
#                 "Failed to initialize Qdrant retriever",
#                 exc,
#             ) from exc

#     # -----------------------------------------------------------------
#     # Configuration
#     # -----------------------------------------------------------------

#     def _validate_config(self) -> None:
#         if not os.getenv("OPENAI_API_KEY"):
#             raise ValueError("OPENAI_API_KEY is missing")

#         if not self.qdrant_url:
#             raise ValueError("QDRANT_URL is missing")

#         if self.embedding_dimension <= 0:
#             raise ValueError(
#                 "OPENAI_EMBEDDING_DIMENSION must be positive"
#             )

#     def _validate_collection(self) -> None:
#         """
#         Retrieval should use an already-ingested collection.

#         Unlike ingestion.py, this class intentionally does not create a
#         collection if one is missing.
#         """
#         if not self.client.collection_exists(self.collection_name):
#             raise ValueError(
#                 f"Qdrant collection does not exist: "
#                 f"{self.collection_name}"
#             )

#     # -----------------------------------------------------------------
#     # Filter helpers
#     # -----------------------------------------------------------------

#     @classmethod
#     def _normalize_content_types(
#         cls,
#         content_types: Iterable[str] | None,
#     ) -> list[str]:
#         if content_types is None:
#             return []

#         normalized = [
#             str(content_type).strip()
#             for content_type in content_types
#             if str(content_type).strip()
#         ]

#         invalid = sorted(
#             set(normalized) - cls.VALID_CONTENT_TYPES
#         )

#         if invalid:
#             raise ValueError(
#                 "Unsupported content_types: "
#                 f"{invalid}. Valid values are: "
#                 f"{sorted(cls.VALID_CONTENT_TYPES)}"
#             )

#         return normalized

#     def build_filter(
#         self,
#         *,
#         filename: str | None = None,
#         document_id: str | None = None,
#         content_types: Iterable[str] | None = None,
#         page_number: int | None = None,
#         page_from: int | None = None,
#         page_to: int | None = None,
#     ) -> models.Filter | None:
#         """
#         Build a Qdrant metadata filter.

#         Examples:
#             filename="report.pdf"

#             content_types=["table", "image"]

#             page_number=5

#             page_from=3, page_to=10
#         """
#         must_conditions: list[Any] = []

#         if filename:
#             must_conditions.append(
#                 models.FieldCondition(
#                     key="metadata.filename",
#                     match=models.MatchValue(
#                         value=Path(filename).name
#                     ),
#                 )
#             )

#         if document_id:
#             must_conditions.append(
#                 models.FieldCondition(
#                     key="metadata.document_id",
#                     match=models.MatchValue(
#                         value=document_id
#                     ),
#                 )
#             )

#         normalized_types = self._normalize_content_types(
#             content_types
#         )

#         if normalized_types:
#             must_conditions.append(
#                 models.FieldCondition(
#                     key="metadata.content_type",
#                     match=models.MatchAny(
#                         any=normalized_types
#                     ),
#                 )
#             )

#         if page_number is not None:
#             if page_number <= 0:
#                 raise ValueError(
#                     "page_number must be greater than 0"
#                 )

#             must_conditions.append(
#                 models.FieldCondition(
#                     key="metadata.page_number",
#                     match=models.MatchValue(
#                         value=page_number
#                     ),
#                 )
#             )

#         elif page_from is not None or page_to is not None:
#             if page_from is not None and page_from <= 0:
#                 raise ValueError(
#                     "page_from must be greater than 0"
#                 )

#             if page_to is not None and page_to <= 0:
#                 raise ValueError(
#                     "page_to must be greater than 0"
#                 )

#             if (
#                 page_from is not None
#                 and page_to is not None
#                 and page_from > page_to
#             ):
#                 raise ValueError(
#                     "page_from cannot be greater than page_to"
#                 )

#             must_conditions.append(
#                 models.FieldCondition(
#                     key="metadata.page_number",
#                     range=models.Range(
#                         gte=page_from,
#                         lte=page_to,
#                     ),
#                 )
#             )

#         if not must_conditions:
#             return None

#         return models.Filter(
#             must=must_conditions
#         )

#     # -----------------------------------------------------------------
#     # Dense retrieval
#     # -----------------------------------------------------------------

#     def retrieve(
#         self,
#         query: str,
#         *,
#         k: int = 5,
#         filename: str | None = None,
#         document_id: str | None = None,
#         content_types: Iterable[str] | None = None,
#         page_number: int | None = None,
#         page_from: int | None = None,
#         page_to: int | None = None,
#     ) -> list[Document]:
#         """
#         Return the top-k most relevant documents.

#         Higher-level generation code can use the returned metadata to decide
#         whether a result is normal text, a table, or an image record.
#         """
#         try:
#             query = query.strip()

#             if not query:
#                 raise ValueError("Query cannot be empty")

#             if k <= 0:
#                 raise ValueError("k must be greater than 0")

#             query_filter = self.build_filter(
#                 filename=filename,
#                 document_id=document_id,
#                 content_types=content_types,
#                 page_number=page_number,
#                 page_from=page_from,
#                 page_to=page_to,
#             )

#             documents = self.vector_store.similarity_search(
#                 query=query,
#                 k=k,
#                 filter=query_filter,
#             )

#             logger.info(
#                 "documents_retrieved",
#                 query=query,
#                 k=k,
#                 result_count=len(documents),
#                 content_types=list(content_types)
#                 if content_types is not None
#                 else None,
#             )

#             return documents

#         except Exception as exc:
#             logger.exception(
#                 "document_retrieval_failed",
#                 query=query,
#                 error=str(exc),
#             )
#             raise DocumentPortalException(
#                 "Failed to retrieve documents from Qdrant",
#                 exc,
#             ) from exc

#     def retrieve_with_scores(
#         self,
#         query: str,
#         *,
#         k: int = 5,
#         filename: str | None = None,
#         document_id: str | None = None,
#         content_types: Iterable[str] | None = None,
#         page_number: int | None = None,
#         page_from: int | None = None,
#         page_to: int | None = None,
#     ) -> list[tuple[Document, float]]:
#         """
#         Return documents with Qdrant similarity scores.

#         For our cosine-similarity collection, larger scores indicate a closer
#         vector match.
#         """
#         try:
#             query = query.strip()

#             if not query:
#                 raise ValueError("Query cannot be empty")

#             if k <= 0:
#                 raise ValueError("k must be greater than 0")

#             query_filter = self.build_filter(
#                 filename=filename,
#                 document_id=document_id,
#                 content_types=content_types,
#                 page_number=page_number,
#                 page_from=page_from,
#                 page_to=page_to,
#             )

#             results = (
#                 self.vector_store.similarity_search_with_score(
#                     query=query,
#                     k=k,
#                     filter=query_filter,
#                 )
#             )

#             logger.info(
#                 "documents_retrieved_with_scores",
#                 query=query,
#                 k=k,
#                 result_count=len(results),
#             )

#             return results

#         except Exception as exc:
#             logger.exception(
#                 "scored_document_retrieval_failed",
#                 query=query,
#                 error=str(exc),
#             )
#             raise DocumentPortalException(
#                 "Failed to retrieve scored documents from Qdrant",
#                 exc,
#             ) from exc

#     # -----------------------------------------------------------------
#     # LangChain retriever
#     # -----------------------------------------------------------------

#     def as_langchain_retriever(
#         self,
#         *,
#         search_type: str = "similarity",
#         k: int = 5,
#         fetch_k: int = 20,
#         lambda_mult: float = 0.5,
#         filename: str | None = None,
#         document_id: str | None = None,
#         content_types: Iterable[str] | None = None,
#         page_number: int | None = None,
#         page_from: int | None = None,
#         page_to: int | None = None,
#     ) -> VectorStoreRetriever:
#         """
#         Return a standard LangChain retriever.

#         Supported search types here:
#         - similarity
#         - mmr

#         Example:
#             retriever = obj.as_langchain_retriever(
#                 search_type="similarity",
#                 k=5,
#                 content_types=["table", "image"],
#             )

#             docs = retriever.invoke("What does the chart show?")
#         """
#         if search_type not in {"similarity", "mmr"}:
#             raise ValueError(
#                 "search_type must be 'similarity' or 'mmr'"
#             )

#         if k <= 0:
#             raise ValueError("k must be greater than 0")

#         query_filter = self.build_filter(
#             filename=filename,
#             document_id=document_id,
#             content_types=content_types,
#             page_number=page_number,
#             page_from=page_from,
#             page_to=page_to,
#         )

#         search_kwargs: dict[str, Any] = {
#             "k": k,
#         }

#         if query_filter is not None:
#             search_kwargs["filter"] = query_filter

#         if search_type == "mmr":
#             if fetch_k < k:
#                 raise ValueError(
#                     "fetch_k must be greater than or equal to k"
#                 )

#             if not 0.0 <= lambda_mult <= 1.0:
#                 raise ValueError(
#                     "lambda_mult must be between 0 and 1"
#                 )

#             search_kwargs.update(
#                 {
#                     "fetch_k": fetch_k,
#                     "lambda_mult": lambda_mult,
#                 }
#             )

#         return self.vector_store.as_retriever(
#             search_type=search_type,
#             search_kwargs=search_kwargs,
#         )

#     # -----------------------------------------------------------------
#     # Useful inspection helpers
#     # -----------------------------------------------------------------

#     @staticmethod
#     def format_results(
#         results: list[tuple[Document, float]],
#         *,
#         content_preview_chars: int = 700,
#     ) -> str:
#         """Format scored results for CLI/debugging."""
#         lines: list[str] = []

#         for rank, (document, score) in enumerate(
#             results,
#             start=1,
#         ):
#             metadata = document.metadata
#             content = document.page_content.strip()

#             if len(content) > content_preview_chars:
#                 content = (
#                     content[:content_preview_chars]
#                     + "..."
#                 )

#             lines.extend(
#                 [
#                     f"\n{'=' * 80}",
#                     f"Rank: {rank}",
#                     f"Score: {score:.4f}",
#                     (
#                         "Type: "
#                         f"{metadata.get('content_type', 'unknown')}"
#                     ),
#                     (
#                         "Page: "
#                         f"{metadata.get('page_number', 'unknown')}"
#                     ),
#                     (
#                         "File: "
#                         f"{metadata.get('filename', 'unknown')}"
#                     ),
#                     f"Content:\n{content}",
#                 ]
#             )

#             image_path = metadata.get("image_path")
#             if image_path:
#                 lines.append(
#                     f"Image path: {image_path}"
#                 )

#         return "\n".join(lines)

#     def collection_status(self) -> dict[str, Any]:
#         """Return basic collection information for debugging/UI."""
#         try:
#             info = self.client.get_collection(
#                 self.collection_name
#             )

#             return {
#                 "collection_name": self.collection_name,
#                 "points_count": getattr(
#                     info,
#                     "points_count",
#                     None,
#                 ),
#                 "vectors_count": getattr(
#                     info,
#                     "vectors_count",
#                     None,
#                 ),
#                 "status": str(
#                     getattr(info, "status", "unknown")
#                 ),
#             }

#         except Exception as exc:
#             raise DocumentPortalException(
#                 "Failed to read Qdrant collection status",
#                 exc,
#             ) from exc


# # ---------------------------------------------------------------------
# # Manual retrieval test
# # ---------------------------------------------------------------------

# if __name__ == "__main__":
#     retriever = MultimodalQdrantRetriever()

#     print(
#         "Collection status:",
#         retriever.collection_status(),
#     )

#     query = (
#         "What are the important policies and incident details?"
#     )

#     results = retriever.retrieve_with_scores(
#         query=query,
#         k=5,
#     )

#     print(
#         retriever.format_results(results)
#     )

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder


# ---------------------------------------------------------------------
# Project setup
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger


logger = CustomLogger().get_logger(__name__)


# ---------------------------------------------------------------------
# Retriever
# ---------------------------------------------------------------------

class MultimodalQdrantRetriever:
    """
    Multimodal MM-RAG retriever.

    Current retrieval architecture:

        Query
          |
          +---- Dense Retrieval ----> Qdrant
          |
          +---- Sparse Retrieval ---> BM25
          |
          +---- Hybrid Retrieval ---> RRF
          |
          +---- Reranking ----------> Cross-Encoder
          |
          +---- Final Top-K

    Tenant isolation is enforced for every retrieval path through:

        metadata.tenant_id == tenant_id
    """

    VALID_CONTENT_TYPES = {
        "page_text_plus_ocr",
        "text",
        "table",
        "image",
    }

    # Cross-encoder used for second-stage relevance reranking.
    RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def __init__(
        self,
        collection_name: str | None = None,
    ) -> None:
        try:
            # ---------------------------------------------------------
            # Qdrant configuration
            # ---------------------------------------------------------

            self.collection_name = (
                collection_name
                or os.getenv("QDRANT_COLLECTION_NAME")
                or "mm-rag-documents"
            )

            # ---------------------------------------------------------
            # Dense embedding configuration
            # ---------------------------------------------------------

            self.embedding_model = (
                os.getenv("HF_EMBEDDING_MODEL")
                or "sentence-transformers/all-MiniLM-L6-v2"
            )

            self.embedding_dimension = int(
                os.getenv("HF_EMBEDDING_DIMENSION") or 384
            )

            # ---------------------------------------------------------
            # Qdrant connection
            # ---------------------------------------------------------

            self.qdrant_url = (
                os.getenv("QDRANT_URL")
                or os.getenv("QDRANT_Cluster_Endpoint")
            )

            self.qdrant_api_key = os.getenv("QDRANT_API_KEY")

            self._validate_config()

            self.client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
            )

            self._validate_collection()

            # ---------------------------------------------------------
            # Dense embedding model
            # ---------------------------------------------------------

            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=self.embeddings,
                retrieval_mode=RetrievalMode.DENSE,
            )

            # ---------------------------------------------------------
            # Cross-Encoder reranker
            # ---------------------------------------------------------

            self.reranker = CrossEncoder(
                self.RERANKER_MODEL
            )

            logger.info(
                "retriever_initialized",
                collection_name=self.collection_name,
                embedding_model=self.embedding_model,
                reranker_model=self.RERANKER_MODEL,
            )

        except Exception as exc:
            logger.exception(
                "retriever_initialization_failed",
                error=str(exc),
            )

            raise DocumentPortalException(
                "Failed to initialize Qdrant retriever",
                exc,
            ) from exc

    # -----------------------------------------------------------------
    # Configuration
    # -----------------------------------------------------------------

    def _validate_config(self) -> None:
        if not self.qdrant_url:
            raise ValueError("QDRANT_URL is missing")

        if self.embedding_dimension <= 0:
            raise ValueError(
                "HF_EMBEDDING_DIMENSION must be positive"
            )

    def _validate_collection(self) -> None:
        """
        Retrieval should use an already-ingested collection.

        This class intentionally does not create a collection if
        one is missing.
        """

        if not self.client.collection_exists(self.collection_name):
            raise ValueError(
                f"Qdrant collection does not exist: "
                f"{self.collection_name}"
            )

    # -----------------------------------------------------------------
    # Filter helpers
    # -----------------------------------------------------------------

    @classmethod
    def _normalize_content_types(
        cls,
        content_types: Iterable[str] | None,
    ) -> list[str]:
        if content_types is None:
            return []

        normalized = [
            str(content_type).strip()
            for content_type in content_types
            if str(content_type).strip()
        ]

        invalid = sorted(
            set(normalized) - cls.VALID_CONTENT_TYPES
        )

        if invalid:
            raise ValueError(
                "Unsupported content_types: "
                f"{invalid}. Valid values are: "
                f"{sorted(cls.VALID_CONTENT_TYPES)}"
            )

        return normalized

    def build_filter(
        self,
        *,
        tenant_id: str,
        filename: str | None = None,
        document_id: str | None = None,
        workspace_id: str | None = None,
        content_types: Iterable[str] | None = None,
        page_number: int | None = None,
        page_from: int | None = None,
        page_to: int | None = None,
    ) -> models.Filter | None:
        """
        Build a Qdrant metadata filter.

        Tenant filtering is mandatory.
        """

        if not tenant_id or not str(tenant_id).strip():
            raise ValueError("tenant_id is required")

        # Tenant isolation is ALWAYS applied.
        must_conditions: list[Any] = [
            models.FieldCondition(
                key="metadata.tenant_id",
                match=models.MatchValue(
                    value=str(tenant_id),
                ),
            )
        ]

        # -------------------------------------------------------------
        # Filename
        # -------------------------------------------------------------

        if filename:
            must_conditions.append(
                models.FieldCondition(
                    key="metadata.filename",
                    match=models.MatchValue(
                        value=Path(filename).name,
                    ),
                )
            )

        # -------------------------------------------------------------
        # Document ID
        # -------------------------------------------------------------

        if document_id:
            must_conditions.append(
                models.FieldCondition(
                    key="metadata.document_id",
                    match=models.MatchValue(
                        value=document_id,
                    ),
                )
            )

        # -------------------------------------------------------------
        # Workspace
        # -------------------------------------------------------------

        if workspace_id:
            must_conditions.append(
                models.FieldCondition(
                    key="metadata.workspace_id",
                    match=models.MatchValue(
                        value=workspace_id,
                    ),
                )
            )

        # -------------------------------------------------------------
        # Content type
        # -------------------------------------------------------------

        normalized_types = self._normalize_content_types(
            content_types
        )

        if normalized_types:
            must_conditions.append(
                models.FieldCondition(
                    key="metadata.content_type",
                    match=models.MatchAny(
                        any=normalized_types,
                    ),
                )
            )

        # -------------------------------------------------------------
        # Exact page
        # -------------------------------------------------------------

        if page_number is not None:
            if page_number <= 0:
                raise ValueError(
                    "page_number must be greater than 0"
                )

            must_conditions.append(
                models.FieldCondition(
                    key="metadata.page_number",
                    match=models.MatchValue(
                        value=page_number,
                    ),
                )
            )

        # -------------------------------------------------------------
        # Page range
        # -------------------------------------------------------------

        elif page_from is not None or page_to is not None:
            if page_from is not None and page_from <= 0:
                raise ValueError(
                    "page_from must be greater than 0"
                )

            if page_to is not None and page_to <= 0:
                raise ValueError(
                    "page_to must be greater than 0"
                )

            if (
                page_from is not None
                and page_to is not None
                and page_from > page_to
            ):
                raise ValueError(
                    "page_from cannot be greater than page_to"
                )

            must_conditions.append(
                models.FieldCondition(
                    key="metadata.page_number",
                    range=models.Range(
                        gte=page_from,
                        lte=page_to,
                    ),
                )
            )

        if not must_conditions:
            return None

        return models.Filter(
            must=must_conditions,
        )

    # -----------------------------------------------------------------
    # Dense retrieval
    # -----------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        *,
        tenant_id: str,
        k: int = 5,
        filename: str | None = None,
        document_id: str | None = None,
        workspace_id: str | None = None,
        content_types: Iterable[str] | None = None,
        page_number: int | None = None,
        page_from: int | None = None,
        page_to: int | None = None,
    ) -> list[Document]:
        """
        Return top-k dense semantic results from Qdrant.
        """

        try:
            query = query.strip()

            if not query:
                raise ValueError("Query cannot be empty")

            if k <= 0:
                raise ValueError("k must be greater than 0")

            query_filter = self.build_filter(
                tenant_id=tenant_id,
                filename=filename,
                document_id=document_id,
                workspace_id=workspace_id,
                content_types=content_types,
                page_number=page_number,
                page_from=page_from,
                page_to=page_to,
            )

            documents = self.vector_store.similarity_search(
                query=query,
                k=k,
                filter=query_filter,
            )

            logger.info(
                "documents_retrieved",
                query=query,
                tenant_id=tenant_id,
                k=k,
                result_count=len(documents),
                content_types=(
                    list(content_types)
                    if content_types is not None
                    else None
                ),
            )

            return documents

        except Exception as exc:
            logger.exception(
                "document_retrieval_failed",
                query=query,
                tenant_id=tenant_id,
                error=str(exc),
            )

            raise DocumentPortalException(
                "Failed to retrieve documents from Qdrant",
                exc,
            ) from exc

    # -----------------------------------------------------------------
    # Dense retrieval with scores
    # -----------------------------------------------------------------

    def retrieve_with_scores(
        self,
        query: str,
        *,
        tenant_id: str,
        k: int = 5,
        filename: str | None = None,
        document_id: str | None = None,
        workspace_id: str | None = None,
        content_types: Iterable[str] | None = None,
        page_number: int | None = None,
        page_from: int | None = None,
        page_to: int | None = None,
    ) -> list[tuple[Document, float]]:
        """
        Return dense documents with Qdrant similarity scores.
        """

        try:
            query = query.strip()

            if not query:
                raise ValueError("Query cannot be empty")

            if k <= 0:
                raise ValueError("k must be greater than 0")

            query_filter = self.build_filter(
                tenant_id=tenant_id,
                filename=filename,
                document_id=document_id,
                workspace_id=workspace_id,
                content_types=content_types,
                page_number=page_number,
                page_from=page_from,
                page_to=page_to,
            )

            results = (
                self.vector_store.similarity_search_with_score(
                    query=query,
                    k=k,
                    filter=query_filter,
                )
            )

            logger.info(
                "documents_retrieved_with_scores",
                query=query,
                tenant_id=tenant_id,
                k=k,
                result_count=len(results),
            )

            return results

        except Exception as exc:
            logger.exception(
                "scored_document_retrieval_failed",
                query=query,
                tenant_id=tenant_id,
                error=str(exc),
            )

            raise DocumentPortalException(
                "Failed to retrieve scored documents from Qdrant",
                exc,
            ) from exc

    # -----------------------------------------------------------------
    # BM25 sparse retrieval
    # -----------------------------------------------------------------

    def retrieve_bm25(
        self,
        query: str,
        *,
        tenant_id: str,
        k: int = 5,
        filename: str | None = None,
        document_id: str | None = None,
        workspace_id: str | None = None,
        content_types: Iterable[str] | None = None,
        page_number: int | None = None,
        page_from: int | None = None,
        page_to: int | None = None,
    ) -> list[tuple[Document, float]]:
        """
        Retrieve documents using BM25 lexical matching.

        Qdrant is first used to restrict the candidate corpus by
        tenant and metadata filters.

        This guarantees tenant isolation before BM25 scoring.
        """

        try:
            query = query.strip()

            if not query:
                raise ValueError("Query cannot be empty")

            if not tenant_id or not str(tenant_id).strip():
                raise ValueError("tenant_id is required")

            if k <= 0:
                raise ValueError("k must be greater than 0")

            query_filter = self.build_filter(
                tenant_id=tenant_id,
                filename=filename,
                document_id=document_id,
                workspace_id=workspace_id,
                content_types=content_types,
                page_number=page_number,
                page_from=page_from,
                page_to=page_to,
            )

            # ---------------------------------------------------------
            # Fetch tenant-scoped candidate documents.
            # ---------------------------------------------------------

            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                limit=10000,
                with_payload=True,
                with_vectors=False,
            )

            documents: list[Document] = []

            for point in points:
                payload = point.payload or {}

                page_content = payload.get(
                    "page_content",
                    "",
                )

                if not page_content:
                    continue

                metadata = payload.get(
                    "metadata",
                    {},
                )

                # Defensive tenant validation.
                if str(metadata.get("tenant_id")) != str(tenant_id):
                    continue

                documents.append(
                    Document(
                        page_content=str(page_content),
                        metadata=metadata,
                    )
                )

            if not documents:
                logger.info(
                    "bm25_no_documents",
                    query=query,
                    tenant_id=tenant_id,
                )

                return []

            # ---------------------------------------------------------
            # BM25 tokenization
            # ---------------------------------------------------------

            corpus = [
                document.page_content.lower().split()
                for document in documents
            ]

            tokenized_query = query.lower().split()

            bm25 = BM25Okapi(corpus)

            scores = bm25.get_scores(
                tokenized_query
            )

            ranked = sorted(
                zip(documents, scores),
                key=lambda item: item[1],
                reverse=True,
            )

            results = [
                (
                    document,
                    float(score),
                )
                for document, score in ranked[:k]
            ]

            logger.info(
                "bm25_documents_retrieved",
                query=query,
                tenant_id=tenant_id,
                candidate_count=len(documents),
                result_count=len(results),
            )

            return results

        except Exception as exc:
            logger.exception(
                "bm25_retrieval_failed",
                query=query,
                tenant_id=tenant_id,
                error=str(exc),
            )

            raise DocumentPortalException(
                "Failed to retrieve documents using BM25",
                exc,
            ) from exc

    # -----------------------------------------------------------------
    # Reciprocal Rank Fusion
    # -----------------------------------------------------------------

    @staticmethod
    def reciprocal_rank_fusion(
        dense_results: list[tuple[Document, float]],
        sparse_results: list[tuple[Document, float]],
        *,
        k: int = 60,
        top_k: int = 20,
    ) -> list[tuple[Document, float]]:
        """
        Combine dense and BM25 rankings using Reciprocal Rank Fusion.

        RRF:

            score(d) = SUM 1 / (k + rank)

        Dense and BM25 raw scores are not directly mixed because
        their score scales are different.
        """

        if k <= 0:
            raise ValueError(
                "RRF k must be greater than 0"
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0"
            )

        fused_scores: dict[str, float] = {}
        documents_by_key: dict[str, Document] = {}

        def document_key(document: Document) -> str:
            metadata = document.metadata

            document_id = metadata.get(
                "document_id"
            )

            page_number = metadata.get(
                "page_number"
            )

            content_type = metadata.get(
                "content_type"
            )

            chunk_id = metadata.get(
                "chunk_id"
            )

            if document_id:
                return (
                    f"{document_id}|"
                    f"{page_number}|"
                    f"{content_type}|"
                    f"{chunk_id}|"
                    f"{document.page_content}"
                )

            return document.page_content

        # -------------------------------------------------------------
        # Dense ranking contribution
        # -------------------------------------------------------------

        for rank, (document, _) in enumerate(
            dense_results,
            start=1,
        ):
            key = document_key(document)

            fused_scores[key] = (
                fused_scores.get(key, 0.0)
                + 1.0 / (k + rank)
            )

            documents_by_key[key] = document

        # -------------------------------------------------------------
        # BM25 ranking contribution
        # -------------------------------------------------------------

        for rank, (document, _) in enumerate(
            sparse_results,
            start=1,
        ):
            key = document_key(document)

            fused_scores[key] = (
                fused_scores.get(key, 0.0)
                + 1.0 / (k + rank)
            )

            documents_by_key[key] = document

        ranked = sorted(
            fused_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        results = [
            (
                documents_by_key[key],
                float(score),
            )
            for key, score in ranked[:top_k]
        ]

        return results

    # -----------------------------------------------------------------
    # Cross-Encoder reranking
    # -----------------------------------------------------------------

    def rerank_documents(
        self,
        query: str,
        documents: list[tuple[Document, float]],
        *,
        top_k: int = 5,
    ) -> list[tuple[Document, float]]:
        """
        Rerank RRF candidates using a Cross-Encoder.

        The Cross-Encoder receives:

            [query, document_text]

        and produces a direct relevance score.

        The input documents have already passed tenant filtering
        during dense/BM25 retrieval.
        """

        try:
            query = query.strip()

            if not query:
                raise ValueError("Query cannot be empty")

            if top_k <= 0:
                raise ValueError(
                    "top_k must be greater than 0"
                )

            if not documents:
                return []

            # ---------------------------------------------------------
            # Build query-document pairs.
            # ---------------------------------------------------------

            pairs = [
                [
                    query,
                    document.page_content,
                ]
                for document, _ in documents
            ]

            # ---------------------------------------------------------
            # Cross-Encoder scoring.
            # ---------------------------------------------------------

            scores = self.reranker.predict(
                pairs,
                show_progress_bar=False,
            )

            reranked = [
                (
                    document,
                    float(score),
                )
                for (document, _), score in zip(
                    documents,
                    scores,
                )
            ]

            # Highest Cross-Encoder score first.
            reranked.sort(
                key=lambda item: item[1],
                reverse=True,
            )

            final_results = reranked[:top_k]

            logger.info(
                "cross_encoder_reranking_completed",
                query=query,
                candidate_count=len(documents),
                result_count=len(final_results),
                reranker_model=self.RERANKER_MODEL,
            )

            return final_results

        except Exception as exc:
            logger.exception(
                "cross_encoder_reranking_failed",
                query=query,
                error=str(exc),
            )

            raise DocumentPortalException(
                "Failed to rerank documents",
                exc,
            ) from exc

    # -----------------------------------------------------------------
    # Multimodal evidence guarantee
    # -----------------------------------------------------------------

    @staticmethod
    def _document_identity(document: Document) -> str:
        """Stable identity for de-duplicating retrieved documents."""
        metadata = document.metadata or {}

        document_id = metadata.get("document_id")
        chunk_id = metadata.get("chunk_id")

        if chunk_id:
            return f"{document_id}|{chunk_id}"

        return (
            f"{document_id}|"
            f"{metadata.get('page_number')}|"
            f"{metadata.get('content_type')}|"
            f"{document.page_content}"
        )

    def _augment_with_content_types(
        self,
        *,
        query: str,
        base_results: list[tuple[Document, float]],
        guaranteed_content_types: Iterable[str],
        per_type_k: int,
        tenant_id: str,
        candidate_k: int,
        rrf_k: int,
        filename: str | None,
        document_id: str | None,
        workspace_id: str | None,
        page_number: int | None,
        page_from: int | None,
        page_to: int | None,
    ) -> list[tuple[Document, float]]:
        """
        Ensure at least one document of each guaranteed content type is
        present in the final result set.

        Tables and images are sparse in most corpora, so a pure
        similarity ranking can drop them entirely even when they hold the
        answer. This tops up the ranked results with the best hybrid hits
        for any missing content type (e.g. ``table``).

        The result set never grows beyond the caller's ``k`` (the size of
        the reranked ``base_results``): the guaranteed evidence displaces
        the weakest reranked documents instead of being appended, so
        retrieval stays within budget rather than silently returning more
        documents than were requested.
        """

        budget = len(base_results)

        present_types = {
            str(document.metadata.get("content_type"))
            for document, _ in base_results
        }

        missing_types = [
            content_type
            for content_type in guaranteed_content_types
            if content_type not in present_types
        ]

        if not missing_types:
            return base_results

        seen = {
            self._document_identity(document)
            for document, _ in base_results
        }

        extra: list[tuple[Document, float]] = []

        for content_type in missing_types:
            try:
                top_up = self.retrieve_hybrid(
                    query=query,
                    tenant_id=tenant_id,
                    k=per_type_k,
                    candidate_k=max(candidate_k, per_type_k),
                    rrf_k=rrf_k,
                    filename=filename,
                    document_id=document_id,
                    workspace_id=workspace_id,
                    content_types=[content_type],
                    page_number=page_number,
                    page_from=page_from,
                    page_to=page_to,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "content_type_topup_failed",
                    content_type=content_type,
                    error=str(exc),
                )
                continue

            for document, score in top_up:
                identity = self._document_identity(document)

                if identity in seen:
                    continue

                seen.add(identity)
                extra.append((document, score))

        if not extra:
            return base_results

        if budget <= 0:
            # Nothing was reranked, so there is nothing to displace and
            # the top-up becomes the result set.
            augmented = extra
        else:
            extra = extra[:budget]
            augmented = list(base_results[: budget - len(extra)]) + extra

        logger.info(
            "multimodal_evidence_augmented",
            query=query,
            tenant_id=tenant_id,
            missing_types=missing_types,
            base_count=len(base_results),
            augmented_count=len(augmented),
        )

        return augmented

    # -----------------------------------------------------------------
    # Hybrid retrieval + RRF + Cross-Encoder
    # -----------------------------------------------------------------

    def retrieve_hybrid(
        self,
        query: str,
        *,
        tenant_id: str,
        k: int = 5,
        candidate_k: int = 20,
        rrf_k: int = 60,
        filename: str | None = None,
        document_id: str | None = None,
        workspace_id: str | None = None,
        content_types: Iterable[str] | None = None,
        page_number: int | None = None,
        page_from: int | None = None,
        page_to: int | None = None,
        guaranteed_content_types: Iterable[str] | None = None,
        per_type_k: int = 1,
    ) -> list[tuple[Document, float]]:
        """
        Complete Phase 5 retrieval pipeline:

            Dense Retrieval
                    +
            BM25 Sparse Retrieval
                    ↓
                  RRF
                    ↓
             Cross-Encoder
                    ↓
                Final Top-K

        Tenant filtering is applied to both retrieval paths before
        RRF and therefore before reranking.
        """

        try:
            query = query.strip()

            if not query:
                raise ValueError(
                    "Query cannot be empty"
                )

            if not tenant_id or not str(tenant_id).strip():
                raise ValueError(
                    "tenant_id is required"
                )

            if k <= 0:
                raise ValueError(
                    "k must be greater than 0"
                )

            if candidate_k <= 0:
                raise ValueError(
                    "candidate_k must be greater than 0"
                )

            if candidate_k < k:
                raise ValueError(
                    "candidate_k must be greater than or equal to k"
                )

            # ---------------------------------------------------------
            # 1. Dense retrieval
            # ---------------------------------------------------------

            dense_results = self.retrieve_with_scores(
                query=query,
                tenant_id=tenant_id,
                k=candidate_k,
                filename=filename,
                document_id=document_id,
                workspace_id=workspace_id,
                content_types=content_types,
                page_number=page_number,
                page_from=page_from,
                page_to=page_to,
            )

            # ---------------------------------------------------------
            # 2. BM25 sparse retrieval
            # ---------------------------------------------------------

            sparse_results = self.retrieve_bm25(
                query=query,
                tenant_id=tenant_id,
                k=candidate_k,
                filename=filename,
                document_id=document_id,
                workspace_id=workspace_id,
                content_types=content_types,
                page_number=page_number,
                page_from=page_from,
                page_to=page_to,
            )

            # ---------------------------------------------------------
            # 3. RRF fusion
            #
            # Keep candidate_k results here because the reranker
            # should receive a larger candidate pool than final k.
            # ---------------------------------------------------------

            fused_results = self.reciprocal_rank_fusion(
                dense_results,
                sparse_results,
                k=rrf_k,
                top_k=candidate_k,
            )

            logger.info(
                "rrf_fusion_completed",
                query=query,
                tenant_id=tenant_id,
                dense_count=len(dense_results),
                sparse_count=len(sparse_results),
                fused_count=len(fused_results),
            )

            # ---------------------------------------------------------
            # 4. Cross-Encoder reranking
            # ---------------------------------------------------------

            reranked_results = self.rerank_documents(
                query=query,
                documents=fused_results,
                top_k=k,
            )

            logger.info(
                "hybrid_reranking_completed",
                query=query,
                tenant_id=tenant_id,
                dense_count=len(dense_results),
                sparse_count=len(sparse_results),
                rrf_count=len(fused_results),
                final_count=len(reranked_results),
                top_k=k,
            )

            # ---------------------------------------------------------
            # 5. Guarantee table / image evidence when requested.
            # ---------------------------------------------------------
            if guaranteed_content_types:
                reranked_results = self._augment_with_content_types(
                    query=query,
                    base_results=reranked_results,
                    guaranteed_content_types=self._normalize_content_types(
                        guaranteed_content_types
                    ),
                    per_type_k=max(per_type_k, 1),
                    tenant_id=tenant_id,
                    candidate_k=candidate_k,
                    rrf_k=rrf_k,
                    filename=filename,
                    document_id=document_id,
                    workspace_id=workspace_id,
                    page_number=page_number,
                    page_from=page_from,
                    page_to=page_to,
                )

            return reranked_results

        except Exception as exc:
            logger.exception(
                "hybrid_retrieval_failed",
                query=query,
                tenant_id=tenant_id,
                error=str(exc),
            )

            raise DocumentPortalException(
                "Failed to perform hybrid retrieval",
                exc,
            ) from exc

    # -----------------------------------------------------------------
    # LangChain retriever
    # -----------------------------------------------------------------

    def as_langchain_retriever(
        self,
        *,
        tenant_id: str,
        search_type: str = "similarity",
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filename: str | None = None,
        document_id: str | None = None,
        content_types: Iterable[str] | None = None,
        page_number: int | None = None,
        page_from: int | None = None,
        page_to: int | None = None,
    ) -> VectorStoreRetriever:
        """
        Return a standard LangChain retriever with tenant filtering.
        """

        if search_type not in {
            "similarity",
            "mmr",
        }:
            raise ValueError(
                "search_type must be 'similarity' or 'mmr'"
            )

        if k <= 0:
            raise ValueError(
                "k must be greater than 0"
            )

        query_filter = self.build_filter(
            tenant_id=tenant_id,
            filename=filename,
            document_id=document_id,
            content_types=content_types,
            page_number=page_number,
            page_from=page_from,
            page_to=page_to,
        )

        search_kwargs: dict[str, Any] = {
            "k": k,
        }

        if query_filter is not None:
            search_kwargs["filter"] = query_filter

        if search_type == "mmr":
            if fetch_k < k:
                raise ValueError(
                    "fetch_k must be greater than or equal to k"
                )

            if not 0.0 <= lambda_mult <= 1.0:
                raise ValueError(
                    "lambda_mult must be between 0 and 1"
                )

            search_kwargs.update(
                {
                    "fetch_k": fetch_k,
                    "lambda_mult": lambda_mult,
                }
            )

        return self.vector_store.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs,
        )

    # -----------------------------------------------------------------
    # Useful inspection helpers
    # -----------------------------------------------------------------

    @staticmethod
    def format_results(
        results: list[tuple[Document, float]],
        *,
        content_preview_chars: int = 700,
    ) -> str:
        """
        Format scored results for CLI/debugging.
        """

        lines: list[str] = []

        for rank, (document, score) in enumerate(
            results,
            start=1,
        ):
            metadata = document.metadata
            content = document.page_content.strip()

            if len(content) > content_preview_chars:
                content = (
                    content[:content_preview_chars]
                    + "..."
                )

            lines.extend(
                [
                    f"\n{'=' * 80}",
                    f"Rank: {rank}",
                    f"Score: {score:.4f}",
                    (
                        "Type: "
                        f"{metadata.get('content_type', 'unknown')}"
                    ),
                    (
                        "Page: "
                        f"{metadata.get('page_number', 'unknown')}"
                    ),
                    (
                        "File: "
                        f"{metadata.get('filename', 'unknown')}"
                    ),
                    (
                        "Tenant: "
                        f"{metadata.get('tenant_id', 'unknown')}"
                    ),
                    (
                        "Document ID: "
                        f"{metadata.get('document_id', 'unknown')}"
                    ),
                    f"Content:\n{content}",
                ]
            )

            image_path = metadata.get(
                "image_path"
            )

            if image_path:
                lines.append(
                    f"Image path: {image_path}"
                )

        return "\n".join(lines)

    def collection_status(self) -> dict[str, Any]:
        """
        Return basic Qdrant collection information.
        """

        try:
            info = self.client.get_collection(
                self.collection_name
            )

            return {
                "collection_name": self.collection_name,
                "points_count": getattr(
                    info,
                    "points_count",
                    None,
                ),
                "vectors_count": getattr(
                    info,
                    "vectors_count",
                    None,
                ),
                "status": str(
                    getattr(
                        info,
                        "status",
                        "unknown",
                    )
                ),
            }

        except Exception as exc:
            raise DocumentPortalException(
                "Failed to read Qdrant collection status",
                exc,
            ) from exc


# ---------------------------------------------------------------------
# Manual retrieval test
# ---------------------------------------------------------------------

if __name__ == "__main__":
    retriever = MultimodalQdrantRetriever()

    print(
        "Collection status:",
        retriever.collection_status(),
    )

    tenant_id = os.getenv(
        "TEST_TENANT_ID",
        "",
    )

    if not tenant_id:
        raise ValueError(
            "TEST_TENANT_ID is not set. "
            "Set it in .env before running this file directly."
        )

    query = (
        "What are the important policies and incident details?"
    )

    # -------------------------------------------------------------
    # Dense retrieval
    # -------------------------------------------------------------

    print("\n" + "=" * 80)
    print("DENSE RETRIEVAL")
    print("=" * 80)

    dense_results = retriever.retrieve_with_scores(
        query=query,
        tenant_id=tenant_id,
        k=5,
    )

    print(
        retriever.format_results(
            dense_results
        )
    )

    # -------------------------------------------------------------
    # BM25 retrieval
    # -------------------------------------------------------------

    print("\n" + "=" * 80)
    print("BM25 SPARSE RETRIEVAL")
    print("=" * 80)

    bm25_results = retriever.retrieve_bm25(
        query=query,
        tenant_id=tenant_id,
        k=5,
    )

    print(
        retriever.format_results(
            bm25_results
        )
    )

    # -------------------------------------------------------------
    # Complete Hybrid + RRF + Reranking
    # -------------------------------------------------------------

    print("\n" + "=" * 80)
    print("HYBRID + RRF + CROSS-ENCODER RERANKING")
    print("=" * 80)

    hybrid_results = retriever.retrieve_hybrid(
        query=query,
        tenant_id=tenant_id,
        k=5,
        candidate_k=20,
        rrf_k=60,
    )

    print(
        retriever.format_results(
            hybrid_results
        )
    )