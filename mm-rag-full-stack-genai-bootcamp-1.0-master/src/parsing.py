# import json
# import sys
# from pathlib import Path
# from typing import Any, Dict, List, Optional

# PROJECT_ROOT = Path(__file__).resolve().parent.parent

# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))

# import pymupdf as fitz
# import pandas as pd
# import pdfplumber
# import pytesseract
# from PIL import Image
# from langchain_core.documents import Document

# from exception.custom_exception import DocumentPortalException
# from logger.custom_logger import CustomLogger


# logger = CustomLogger().get_logger(__name__)



# class ComplexPDFParser:
#     """
#     Parse a complex PDF containing:
#     - selectable text
#     - scanned pages
#     - tables
#     - embedded images

#     Final output can be converted into LangChain Documents for RAG.
#     """

#     def __init__(
#         self,
#         pdf_path: str,
#         output_dir: str,
#         tesseract_path: Optional[str] = None,
#         render_scale: float = 2.0,
#     ):
#         self.pdf_path = Path(pdf_path)
#         self.output_dir = Path(output_dir)
#         self.image_dir = self.output_dir / "extracted_images"
#         self.page_image_dir = self.output_dir / "page_images"
#         self.render_scale = render_scale

#         self.page_records: List[Dict[str, Any]] = []
#         self.image_records: List[Dict[str, Any]] = []
#         self.table_records: List[Dict[str, Any]] = []
#         self.langchain_docs: List[Document] = []

#         try:
#             self._validate_pdf()
#             self._create_output_directories()
#             self._configure_tesseract(tesseract_path)
#             logger.info(
#                 "pdf_parser_initialized",
#                 pdf_path=str(self.pdf_path),
#                 output_dir=str(self.output_dir),
#             )
#         except Exception as exc:
#             logger.exception(
#                 "pdf_parser_initialization_failed",
#                 pdf_path=str(self.pdf_path),
#                 error=str(exc),
#             )
#             raise DocumentPortalException(
#                 "Failed to initialize the PDF parser",
#                 exc,
#             ) from exc

#     # ============================================================
#     # Setup
#     # ============================================================

#     def _validate_pdf(self) -> None:
#         """Validate that the input PDF exists."""
#         if not self.pdf_path.exists():
#             raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

#     def _create_output_directories(self) -> None:
#         """Create directories used by the parser."""
#         self.output_dir.mkdir(parents=True, exist_ok=True)
#         self.image_dir.mkdir(parents=True, exist_ok=True)
#         self.page_image_dir.mkdir(parents=True, exist_ok=True)

#     def _configure_tesseract(self, tesseract_path: Optional[str]) -> None:
#         """
#         Configure Tesseract executable.

#         If a path is provided, it is validated and assigned to pytesseract.
#         If no path is provided, pytesseract will use Tesseract available
#         in the system PATH.
#         """
#         if tesseract_path:
#             path = Path(tesseract_path)

#             if not path.exists():
#                 raise FileNotFoundError(
#                     f"Tesseract executable not found at: {path}"
#                 )

#             pytesseract.pytesseract.tesseract_cmd = str(path)

#     # ============================================================
#     # OCR
#     # ============================================================

#     def run_ocr_on_image(self, image_path: str | Path) -> str:
#         """
#         Run OCR on an image using pytesseract.

#         Returns extracted text.
#         If OCR fails, returns a readable failure marker instead
#         of stopping the entire PDF parsing pipeline.
#         """
#         try:
#             with Image.open(image_path) as image:
#                 text = pytesseract.image_to_string(image)

#             return text.strip()

#         except Exception as exc:
#             logger.warning(
#                 "image_ocr_failed",
#                 image_path=str(image_path),
#                 error=str(exc),
#             )
#             return f"[OCR_SKIPPED_OR_FAILED: {exc}]"

#     # ============================================================
#     # PyMuPDF: Text + Images + Full-page OCR
#     # ============================================================

#     def extract_text_and_images(
#         self,
#     ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
#         """
#         Extract:
#         - selectable page text
#         - page dimensions
#         - full-page rendered images
#         - OCR text from rendered pages
#         - embedded images
#         - OCR text from embedded images
#         """
#         page_records: List[Dict[str, Any]] = []
#         image_records: List[Dict[str, Any]] = []

#         pdf = fitz.open(str(self.pdf_path))

#         try:
#             for page_index in range(len(pdf)):
#                 page = pdf[page_index]
#                 page_number = page_index + 1

#                 images = page.get_images(full=True)
#                 selectable_text = page.get_text("text").strip()

#                 # Render full page for OCR
#                 pixmap = page.get_pixmap(
#                     matrix=fitz.Matrix(self.render_scale, self.render_scale)
#                 )

#                 page_image_path = (
#                     self.page_image_dir / f"page_{page_number:03d}.png"
#                 )
#                 pixmap.save(str(page_image_path))

#                 page_ocr_text = self.run_ocr_on_image(page_image_path)

#                 page_info = {
#                     "page_number": page_number,
#                     "text": selectable_text,
#                     "ocr_text": page_ocr_text,
#                     "image_count": len(images),
#                     "width": page.rect.width,
#                     "height": page.rect.height,
#                     "page_image_path": str(page_image_path),
#                 }

#                 page_records.append(page_info)

#                 # Extract embedded images
#                 for image_index, image_info in enumerate(images, start=1):
#                     xref = image_info[0]
#                     base_image = pdf.extract_image(xref)

#                     image_bytes = base_image["image"]
#                     image_ext = base_image["ext"]

#                     image_path = (
#                         self.image_dir
#                         / (
#                             f"page_{page_number:03d}_"
#                             f"image_{image_index}.{image_ext}"
#                         )
#                     )

#                     with open(image_path, "wb") as file:
#                         file.write(image_bytes)

#                     image_ocr_text = self.run_ocr_on_image(image_path)

#                     image_records.append(
#                         {
#                             "page_number": page_number,
#                             "image_index": image_index,
#                             "image_path": str(image_path),
#                             "image_ext": image_ext,
#                             "image_ocr_text": image_ocr_text,
#                         }
#                     )

#         finally:
#             pdf.close()

#         self.page_records = page_records
#         self.image_records = image_records

#         return page_records, image_records

#     # ============================================================
#     # pdfplumber: Tables
#     # ============================================================

#     def extract_tables(self) -> List[Dict[str, Any]]:
#         """Extract tables from every page using pdfplumber."""
#         table_records: List[Dict[str, Any]] = []

#         with pdfplumber.open(str(self.pdf_path)) as pdf:
#             for page_index, page in enumerate(pdf.pages):
#                 page_number = page_index + 1

#                 try:
#                     tables = page.extract_tables() or []
#                 except Exception as exc:
#                     logger.warning(
#                         "table_extraction_failed",
#                         pdf_path=str(self.pdf_path),
#                         page_number=page_number,
#                         error=str(exc),
#                     )
#                     tables = []

#                 for table_index, table in enumerate(tables, start=1):
#                     if not table:
#                         continue

#                     cleaned_table = []

#                     for row in table:
#                         cleaned_row = [
#                             cell.strip() if isinstance(cell, str) else cell
#                             for cell in row
#                         ]
#                         cleaned_table.append(cleaned_row)

#                     if not cleaned_table:
#                         continue

#                     try:
#                         dataframe = pd.DataFrame(
#                             cleaned_table[1:],
#                             columns=cleaned_table[0],
#                         )
#                     except Exception:
#                         dataframe = pd.DataFrame(cleaned_table)

#                     table_records.append(
#                         {
#                             "page_number": page_number,
#                             "table_index": table_index,
#                             "raw_table": cleaned_table,
#                             "markdown": dataframe.to_markdown(index=False),
#                             "csv": dataframe.to_csv(index=False),
#                         }
#                     )

#         self.table_records = table_records
#         return table_records

#     # ============================================================
#     # LangChain Documents
#     # ============================================================

#     def create_langchain_documents(self) -> List[Document]:
#         """
#         Convert parsed page text, OCR, tables and image OCR
#         into LangChain Document objects.
#         """
#         documents: List[Document] = []

#         # Page text + page OCR
#         for page in self.page_records:
#             page_number = page["page_number"]

#             combined_text = f"""
# PAGE {page_number}

# SELECTABLE TEXT:
# {page["text"]}

# OCR TEXT:
# {page["ocr_text"]}
# """.strip()

#             documents.append(
#                 Document(
#                     page_content=combined_text,
#                     metadata={
#                         "source": str(self.pdf_path),
#                         "page_number": page_number,
#                         "content_type": "page_text_plus_ocr",
#                         "image_count": page["image_count"],
#                         "page_image_path": page["page_image_path"],
#                     },
#                 )
#             )

#         # Tables
#         for table in self.table_records:
#             page_number = table["page_number"]

#             table_text = f"""
# TABLE FOUND ON PAGE {page_number}
# TABLE INDEX: {table["table_index"]}

# TABLE MARKDOWN:
# {table["markdown"]}
# """.strip()

#             documents.append(
#                 Document(
#                     page_content=table_text,
#                     metadata={
#                         "source": str(self.pdf_path),
#                         "page_number": page_number,
#                         "content_type": "table",
#                         "table_index": table["table_index"],
#                     },
#                 )
#             )

#         # Embedded image OCR
#         for image in self.image_records:
#             page_number = image["page_number"]

#             image_text = f"""
# IMAGE FOUND ON PAGE {page_number}
# IMAGE INDEX: {image["image_index"]}
# IMAGE PATH: {image["image_path"]}

# IMAGE OCR TEXT:
# {image["image_ocr_text"]}
# """.strip()

#             documents.append(
#                 Document(
#                     page_content=image_text,
#                     metadata={
#                         "source": str(self.pdf_path),
#                         "page_number": page_number,
#                         "content_type": "image",
#                         "image_index": image["image_index"],
#                         "image_path": image["image_path"],
#                         "image_ext": image["image_ext"],
#                     },
#                 )
#             )

#         self.langchain_docs = documents
#         return documents

#     # ============================================================
#     # Save Outputs
#     # ============================================================

#     @staticmethod
#     def _save_json(path: Path, data: Any) -> None:
#         with open(path, "w", encoding="utf-8") as file:
#             json.dump(
#                 data,
#                 file,
#                 indent=2,
#                 ensure_ascii=False,
#                 default=str,
#             )

#     def save_outputs(self) -> None:
#         """Save parsed records and RAG-ready documents to disk."""
#         self._save_json(
#             self.output_dir / "page_records.json",
#             self.page_records,
#         )

#         self._save_json(
#             self.output_dir / "image_records.json",
#             self.image_records,
#         )

#         self._save_json(
#             self.output_dir / "table_records.json",
#             self.table_records,
#         )

#         # All LangChain Documents as Markdown
#         rag_documents_path = self.output_dir / "rag_ready_documents.md"

#         with open(rag_documents_path, "w", encoding="utf-8") as file:
#             for index, document in enumerate(
#                 self.langchain_docs,
#                 start=1,
#             ):
#                 file.write(f"\n\n# Document {index}\n")
#                 file.write("\nMetadata:\n```json\n")
#                 file.write(
#                     json.dumps(
#                         document.metadata,
#                         indent=2,
#                         ensure_ascii=False,
#                         default=str,
#                     )
#                 )
#                 file.write("\n```\n")
#                 file.write("\nContent:\n")
#                 file.write(document.page_content)
#                 file.write("\n\n---\n")

#         # Tables as Markdown
#         tables_path = self.output_dir / "extracted_tables.md"

#         with open(tables_path, "w", encoding="utf-8") as file:
#             for table in self.table_records:
#                 file.write(
#                     f"\n\n## Page {table['page_number']} "
#                     f"- Table {table['table_index']}\n\n"
#                 )
#                 file.write(table["markdown"])
#                 file.write("\n\n---\n")

#     # ============================================================
#     # Main Pipeline
#     # ============================================================

#     def parse(self, save_output: bool = True) -> Dict[str, Any]:
#         """
#         Run the complete parsing pipeline.

#         Returns:
#             {
#                 "pages": [...],
#                 "images": [...],
#                 "tables": [...],
#                 "documents": [LangChain Document, ...],
#                 "output_dir": "..."
#             }
#         """
#         logger.info(
#             "pdf_parsing_started",
#             pdf_path=str(self.pdf_path),
#         )

#         try:
#             self.extract_text_and_images()
#             logger.info(
#                 "pdf_content_extracted",
#                 pages=len(self.page_records),
#                 images=len(self.image_records),
#             )

#             self.extract_tables()
#             logger.info(
#                 "pdf_tables_extracted",
#                 tables=len(self.table_records),
#             )

#             self.create_langchain_documents()
#             logger.info(
#                 "langchain_documents_created",
#                 documents=len(self.langchain_docs),
#             )

#             if save_output:
#                 self.save_outputs()
#                 logger.info(
#                     "parser_outputs_saved",
#                     output_dir=str(self.output_dir),
#                 )

#             result = {
#                 "pages": self.page_records,
#                 "images": self.image_records,
#                 "tables": self.table_records,
#                 "documents": self.langchain_docs,
#                 "output_dir": str(self.output_dir),
#             }

#             logger.info(
#                 "pdf_parsing_completed",
#                 pdf_path=str(self.pdf_path),
#             )
#             return result

#         except DocumentPortalException:
#             raise
#         except Exception as exc:
#             logger.exception(
#                 "pdf_parsing_failed",
#                 pdf_path=str(self.pdf_path),
#                 error=str(exc),
#             )
#             raise DocumentPortalException(
#                 f"Failed to parse PDF: {self.pdf_path}",
#                 exc,
#             ) from exc

# # ============================================================
# # Example Usage
# # ============================================================

# if __name__ == "__main__":

#     DATA_DIR = PROJECT_ROOT / "data"

#     PDF_PATH = DATA_DIR / "Client_Contracts_Policies_and_Incident_Records.pdf"
#     OUTPUT_DIR = DATA_DIR / "parsed_pdf_output"

#     TESSERACT_PATH = (
#         r"C:\Program Files\Tesseract-OCR\tesseract.exe"
#     )

#     parser = ComplexPDFParser(
#         pdf_path=PDF_PATH,
#         output_dir=OUTPUT_DIR,
#         tesseract_path=TESSERACT_PATH,
#     )

#     result = parser.parse()

#     documents = result["documents"]

#     print("\n================ SUMMARY ================\n")
#     print("Pages:", len(result["pages"]))
#     print("Images:", len(result["images"]))
#     print("Tables:", len(result["tables"]))
#     print("LangChain Documents:", len(documents))

#     if documents:
#         print("\nFirst document preview:\n")
#         print(documents[0].page_content[:1500])





import json
import os
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pymupdf as fitz
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image
from langchain_core.documents import Document

from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger


logger = CustomLogger().get_logger(__name__)


# ================================================================
# OCR engines
#
# Tesseract (pytesseract) remains the primary OCR engine. EasyOCR is
# used as a fallback when Tesseract is unavailable or returns little/no
# text (typical for scanned pages and embedded images). The EasyOCR
# reader is CPU-only and cached for the lifetime of the worker process,
# so it is built once rather than per page/image.
# ================================================================

OCR_FALLBACK_MIN_CHARS = 8
PAGE_TEXT_MIN_CHARS = 40

_EASYOCR_LOCK = threading.Lock()
_EASYOCR_READER: Any = None
_EASYOCR_INIT_FAILED = False


def _env_flag(name: str, default: bool = True) -> bool:
    """Read a boolean environment flag."""
    raw = os.getenv(name)

    if raw is None:
        return default

    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _easyocr_enabled() -> bool:
    return _env_flag("EASYOCR_ENABLED", True)


def _easyocr_languages() -> List[str]:
    languages = [
        language.strip()
        for language in os.getenv("EASYOCR_LANGUAGES", "en").split(",")
        if language.strip()
    ]
    return languages or ["en"]


def get_easyocr_reader() -> Any:
    """
    Return a process-wide, lazily initialised EasyOCR reader.

    The reader runs on CPU and is cached so it is created once per
    worker process instead of once per page/image. Returns ``None`` when
    EasyOCR is disabled or cannot be initialised, so ingestion continues
    without it.
    """
    global _EASYOCR_READER, _EASYOCR_INIT_FAILED

    if not _easyocr_enabled():
        return None

    if _EASYOCR_READER is not None:
        return _EASYOCR_READER

    if _EASYOCR_INIT_FAILED:
        return None

    with _EASYOCR_LOCK:
        if _EASYOCR_READER is not None:
            return _EASYOCR_READER

        try:
            import easyocr

            _EASYOCR_READER = easyocr.Reader(
                _easyocr_languages(),
                gpu=False,
                verbose=False,
            )
            logger.info(
                "easyocr_reader_initialized",
                languages=_easyocr_languages(),
                gpu=False,
            )
        except Exception as exc:
            _EASYOCR_INIT_FAILED = True
            logger.warning(
                "easyocr_reader_initialization_failed",
                error=str(exc),
            )
            return None

    return _EASYOCR_READER


def easyocr_extract_text(image_path: str | Path) -> str:
    """
    Extract text from an image using EasyOCR.

    Returns the extracted text, or an empty string when EasyOCR is
    unavailable or fails. Never raises, so the PDF pipeline is not
    interrupted by OCR problems.
    """
    reader = get_easyocr_reader()

    if reader is None:
        return ""

    try:
        segments = reader.readtext(
            str(image_path),
            detail=0,
            paragraph=True,
        )
    except Exception as exc:
        logger.warning(
            "easyocr_extraction_failed",
            image_path=str(image_path),
            error=str(exc),
        )
        return ""

    return "\n".join(
        str(segment) for segment in segments if str(segment).strip()
    ).strip()



class ComplexPDFParser:
    """
    Parse a complex PDF containing:
    - selectable text
    - scanned pages
    - tables
    - embedded images

    Final output can be converted into LangChain Documents for RAG.
    """

    def __init__(
        self,
        pdf_path: str,
        output_dir: str,
        tesseract_path: Optional[str] = None,
        render_scale: float = 2.0,
        ocr_min_chars: int = OCR_FALLBACK_MIN_CHARS,
        page_text_min_chars: int = PAGE_TEXT_MIN_CHARS,
    ):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.image_dir = self.output_dir / "extracted_images"
        self.page_image_dir = self.output_dir / "page_images"
        self.render_scale = render_scale
        self.ocr_min_chars = ocr_min_chars
        self.page_text_min_chars = page_text_min_chars

        self.page_records: List[Dict[str, Any]] = []
        self.image_records: List[Dict[str, Any]] = []
        self.table_records: List[Dict[str, Any]] = []
        self.langchain_docs: List[Document] = []

        try:
            self._validate_pdf()
            self._create_output_directories()
            self._configure_tesseract(tesseract_path)
            logger.info(
                "pdf_parser_initialized",
                pdf_path=str(self.pdf_path),
                output_dir=str(self.output_dir),
            )
        except Exception as exc:
            logger.exception(
                "pdf_parser_initialization_failed",
                pdf_path=str(self.pdf_path),
                error=str(exc),
            )
            raise DocumentPortalException(
                "Failed to initialize the PDF parser",
                exc,
            ) from exc

    # ============================================================
    # Setup
    # ============================================================

    def _validate_pdf(self) -> None:
        """Validate that the input PDF exists."""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

    def _create_output_directories(self) -> None:
        """Create directories used by the parser."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.page_image_dir.mkdir(parents=True, exist_ok=True)

    def _configure_tesseract(self, tesseract_path: Optional[str]) -> None:
        """
        Configure the Tesseract executable.

        If a path is provided, it is validated and assigned to pytesseract.
        If no path is provided, pytesseract will use Tesseract available
        in the system PATH.

        A missing/invalid path is logged and tolerated rather than fatal,
        so ingestion can continue and fall back to EasyOCR.
        """
        if tesseract_path:
            path = Path(tesseract_path)

            if not path.exists():
                logger.warning(
                    "tesseract_executable_not_found",
                    tesseract_path=str(path),
                )
                return

            pytesseract.pytesseract.tesseract_cmd = str(path)

    # ============================================================
    # OCR
    # ============================================================

    def _run_tesseract_ocr(self, image_path: str | Path) -> str:
        """
        Run Tesseract OCR on an image.

        Returns the extracted text, or an empty string when Tesseract is
        unavailable or fails, so the caller can fall back to EasyOCR.
        """
        try:
            with Image.open(image_path) as image:
                return pytesseract.image_to_string(image).strip()

        except Exception as exc:
            logger.warning(
                "image_ocr_failed",
                engine="tesseract",
                image_path=str(image_path),
                error=str(exc),
            )
            return ""

    def run_ocr_on_image(self, image_path: str | Path) -> str:
        """
        Extract text from an image: Tesseract first, EasyOCR fallback.

        Tesseract (the existing engine) is always tried first. When it is
        unavailable or yields fewer than ``self.ocr_min_chars`` characters
        - which is the normal case for scanned pages and embedded images -
        the cached, CPU-only EasyOCR reader is used as a fallback. OCR
        failures are logged and tolerated so the pipeline never breaks.
        """
        tesseract_text = self._run_tesseract_ocr(image_path)

        if len(tesseract_text) >= self.ocr_min_chars:
            return tesseract_text

        fallback_text = easyocr_extract_text(image_path)

        if len(fallback_text) > len(tesseract_text):
            logger.info(
                "ocr_easyocr_fallback_used",
                image_path=str(image_path),
                tesseract_chars=len(tesseract_text),
                easyocr_chars=len(fallback_text),
            )
            return fallback_text

        return tesseract_text

    # ============================================================
    # PyMuPDF: Text + Images + Full-page OCR
    # ============================================================

    def extract_text_and_images(
        self,
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Extract:
        - selectable page text
        - page dimensions
        - full-page rendered images
        - OCR text from rendered pages
        - embedded images
        - OCR text from embedded images
        """
        page_records: List[Dict[str, Any]] = []
        image_records: List[Dict[str, Any]] = []

        pdf = fitz.open(str(self.pdf_path))

        try:
            for page_index in range(len(pdf)):
                page = pdf[page_index]
                page_number = page_index + 1

                images = page.get_images(full=True)
                selectable_text = page.get_text("text").strip()

                # Render full page for OCR
                pixmap = page.get_pixmap(
                    matrix=fitz.Matrix(self.render_scale, self.render_scale)
                )

                page_image_path = (
                    self.page_image_dir / f"page_{page_number:03d}.png"
                )
                pixmap.save(str(page_image_path))

                # Only OCR the rendered page when the PDF provides little or
                # no selectable text (i.e. a scanned page). Text-rich pages
                # already carry their content, so OCR would be wasted work.
                if len(selectable_text) < self.page_text_min_chars:
                    page_ocr_text = self.run_ocr_on_image(page_image_path)
                else:
                    page_ocr_text = ""

                page_info = {
                    "page_number": page_number,
                    "text": selectable_text,
                    "ocr_text": page_ocr_text,
                    "image_count": len(images),
                    "width": page.rect.width,
                    "height": page.rect.height,
                    "page_image_path": str(page_image_path),
                }

                page_records.append(page_info)

                # Extract embedded images
                for image_index, image_info in enumerate(images, start=1):
                    xref = image_info[0]
                    base_image = pdf.extract_image(xref)

                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    image_path = (
                        self.image_dir
                        / (
                            f"page_{page_number:03d}_"
                            f"image_{image_index}.{image_ext}"
                        )
                    )

                    with open(image_path, "wb") as file:
                        file.write(image_bytes)

                    image_ocr_text = self.run_ocr_on_image(image_path)

                    image_records.append(
                        {
                            "page_number": page_number,
                            "image_index": image_index,
                            "image_path": str(image_path),
                            "image_ext": image_ext,
                            "image_ocr_text": image_ocr_text,
                        }
                    )

        finally:
            pdf.close()

        self.page_records = page_records
        self.image_records = image_records

        return page_records, image_records

    # ============================================================
    # pdfplumber: Tables
    # ============================================================

    def extract_tables(self) -> List[Dict[str, Any]]:
        """
        Extract structured tables from every PDF page using pdfplumber.

        Each table keeps:
            - raw table data
            - normalized headers
            - structured rows
            - row/column counts
            - Markdown representation
            - CSV representation
            - searchable text representation

        Empty extraction artifacts are skipped, while valid tables retain
        their original row/column structure.
        """
        table_records: List[Dict[str, Any]] = []

        with pdfplumber.open(str(self.pdf_path)) as pdf:
            for page_index, page in enumerate(pdf.pages):
                page_number = page_index + 1

                try:
                    tables = page.extract_tables() or []
                except Exception as exc:
                    logger.warning(
                        "table_extraction_failed",
                        pdf_path=str(self.pdf_path),
                        page_number=page_number,
                        error=str(exc),
                    )
                    tables = []

                for table_index, table in enumerate(tables, start=1):
                    if not table:
                        continue

                    # ------------------------------------------------------
                    # Clean extracted cells
                    # ------------------------------------------------------
                    cleaned_table: List[List[str]] = []

                    for row in table:
                        if row is None:
                            continue

                        cleaned_row: List[str] = []

                        for cell in row:
                            if cell is None:
                                cleaned_row.append("")
                            elif isinstance(cell, str):
                                # Collapse whitespace/newlines introduced by
                                # PDF text positioning.
                                cleaned_row.append(
                                    " ".join(cell.split()).strip()
                                )
                            else:
                                cleaned_row.append(str(cell).strip())

                        cleaned_table.append(cleaned_row)

                    if not cleaned_table:
                        continue

                    # ------------------------------------------------------
                    # Normalize row lengths
                    # ------------------------------------------------------
                    column_count = max(
                        len(row) for row in cleaned_table
                    )

                    normalized_table: List[List[str]] = []

                    for row in cleaned_table:
                        padded_row = row + (
                            [""] * (column_count - len(row))
                        )
                        normalized_table.append(padded_row)

                    # ------------------------------------------------------
                    # Skip completely empty extraction artifacts
                    # ------------------------------------------------------
                    if not any(
                        str(cell).strip()
                        for row in normalized_table
                        for cell in row
                    ):
                        logger.info(
                            "empty_table_skipped",
                            page_number=page_number,
                            table_index=table_index,
                        )
                        continue

                    # ------------------------------------------------------
                    # Header row
                    # ------------------------------------------------------
                    raw_headers = normalized_table[0]

                    headers: List[str] = []

                    for index, header in enumerate(
                        raw_headers,
                        start=1,
                    ):
                        header_text = str(header).strip()

                        # pdfplumber can split a header at an internal
                        # character boundary when PDF text boxes overlap.
                        # Normalize the known "Transaction Ref. No Tr" /
                        # "ansaction Date" artifact without changing the
                        # number of table columns.
                        if header_text.endswith(" Tr"):
                            header_text = header_text[:-3].rstrip()

                        if header_text.lower() == "ansaction date":
                            header_text = "Transaction Date"

                        if not header_text:
                            header_text = f"column_{index}"

                        headers.append(header_text)

                    # ------------------------------------------------------
                    # Structured rows
                    # ------------------------------------------------------
                    structured_rows: List[Dict[str, str]] = []

                    for row in normalized_table[1:]:
                        row_data: Dict[str, str] = {}

                        for column_index, header in enumerate(headers):
                            row_data[header] = row[column_index]

                        structured_rows.append(row_data)

                    # ------------------------------------------------------
                    # DataFrame
                    # ------------------------------------------------------
                    try:
                        dataframe = pd.DataFrame(
                            structured_rows,
                            columns=headers,
                        )
                    except Exception:
                        dataframe = pd.DataFrame(
                            normalized_table[1:],
                            columns=headers,
                        )

                    # ------------------------------------------------------
                    # Markdown representation
                    # ------------------------------------------------------
                    try:
                        markdown = dataframe.to_markdown(
                            index=False
                        )
                    except Exception:
                        markdown = "\n".join(
                            " | ".join(row)
                            for row in normalized_table
                        )

                    # ------------------------------------------------------
                    # CSV representation
                    # ------------------------------------------------------
                    csv_text = dataframe.to_csv(
                        index=False
                    )

                    # ------------------------------------------------------
                    # Search-friendly representation
                    # ------------------------------------------------------
                    searchable_lines = [
                        f"TABLE FOUND ON PAGE {page_number}",
                        f"TABLE INDEX: {table_index}",
                        f"NUMBER OF COLUMNS: {column_count}",
                        f"NUMBER OF DATA ROWS: {len(structured_rows)}",
                        "",
                        "TABLE COLUMNS:",
                        ", ".join(headers),
                        "",
                    ]

                    for row_number, row_data in enumerate(
                        structured_rows,
                        start=1,
                    ):
                        searchable_lines.append(
                            f"ROW {row_number}:"
                        )

                        row_values = []

                        for header in headers:
                            value = row_data.get(
                                header,
                                "",
                            )

                            row_values.append(
                                f"{header} = {value}"
                            )

                        searchable_lines.append(
                            " | ".join(row_values)
                        )
                        searchable_lines.append("")

                    searchable_text = "\n".join(
                        searchable_lines
                    ).strip()

                    # ------------------------------------------------------
                    # Save complete table record
                    # ------------------------------------------------------
                    table_records.append(
                        {
                            "page_number": page_number,
                            "table_index": table_index,
                            "raw_table": normalized_table,
                            "headers": headers,
                            "rows": structured_rows,
                            "row_count": len(structured_rows),
                            "column_count": column_count,
                            "markdown": markdown,
                            "csv": csv_text,
                            "searchable_text": searchable_text,
                        }
                    )

                    logger.info(
                        "table_extracted",
                        page_number=page_number,
                        table_index=table_index,
                        rows=len(structured_rows),
                        columns=column_count,
                    )

        self.table_records = table_records

        return table_records

    # ============================================================
    # LangChain Documents
    # ============================================================

    def create_langchain_documents(self) -> List[Document]:
        """
        Convert parsed page text, OCR, tables and image OCR
        into LangChain Document objects.
        """
        documents: List[Document] = []

        # Page text + page OCR
        for page in self.page_records:
            page_number = page["page_number"]

            combined_text = f"""
PAGE {page_number}

SELECTABLE TEXT:
{page["text"]}

OCR TEXT:
{page["ocr_text"]}
""".strip()

            documents.append(
                Document(
                    page_content=combined_text,
                    metadata={
                        "source": str(self.pdf_path),
                        "page_number": page_number,
                        "content_type": "page_text_plus_ocr",
                        "image_count": page["image_count"],
                        "page_image_path": page["page_image_path"],
                    },
                )
            )

        # Tables
        for table in self.table_records:
            page_number = table["page_number"]
            table_index = table["table_index"]

            table_text = f"""
TABLE FOUND ON PAGE {page_number}
TABLE INDEX: {table_index}

TABLE DIMENSIONS:
Rows: {table["row_count"]}
Columns: {table["column_count"]}

TABLE COLUMNS:
{", ".join(table["headers"])}

SEARCHABLE TABLE CONTENT:
{table["searchable_text"]}

TABLE MARKDOWN:
{table["markdown"]}
""".strip()

            documents.append(
                Document(
                    page_content=table_text,
                    metadata={
                        "source": str(self.pdf_path),
                        "page_number": page_number,
                        "content_type": "table",
                        "table_index": table_index,
                        "table_row_count": table["row_count"],
                        "table_column_count": table["column_count"],
                        "table_headers": table["headers"],
                    },
                )
            )

        # Embedded image OCR
        for image in self.image_records:
            page_number = image["page_number"]

            image_text = f"""
IMAGE FOUND ON PAGE {page_number}
IMAGE INDEX: {image["image_index"]}
IMAGE PATH: {image["image_path"]}

IMAGE OCR TEXT:
{image["image_ocr_text"]}
""".strip()

            documents.append(
                Document(
                    page_content=image_text,
                    metadata={
                        "source": str(self.pdf_path),
                        "page_number": page_number,
                        "content_type": "image",
                        "image_index": image["image_index"],
                        "image_path": image["image_path"],
                        "image_ext": image["image_ext"],
                    },
                )
            )

        self.langchain_docs = documents
        return documents

    # ============================================================
    # Save Outputs
    # ============================================================

    @staticmethod
    def _save_json(path: Path, data: Any) -> None:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

    def save_outputs(self) -> None:
        """Save parsed records and RAG-ready documents to disk."""
        self._save_json(
            self.output_dir / "page_records.json",
            self.page_records,
        )

        self._save_json(
            self.output_dir / "image_records.json",
            self.image_records,
        )

        self._save_json(
            self.output_dir / "table_records.json",
            self.table_records,
        )

        # All LangChain Documents as Markdown
        rag_documents_path = self.output_dir / "rag_ready_documents.md"

        with open(rag_documents_path, "w", encoding="utf-8") as file:
            for index, document in enumerate(
                self.langchain_docs,
                start=1,
            ):
                file.write(f"\n\n# Document {index}\n")
                file.write("\nMetadata:\n```json\n")
                file.write(
                    json.dumps(
                        document.metadata,
                        indent=2,
                        ensure_ascii=False,
                        default=str,
                    )
                )
                file.write("\n```\n")
                file.write("\nContent:\n")
                file.write(document.page_content)
                file.write("\n\n---\n")

        # Tables as Markdown
        tables_path = self.output_dir / "extracted_tables.md"

        with open(tables_path, "w", encoding="utf-8") as file:
            for table in self.table_records:
                file.write(
                    f"\n\n## Page {table['page_number']} "
                    f"- Table {table['table_index']}\n\n"
                )
                file.write(table["markdown"])
                file.write("\n\n---\n")

    # ============================================================
    # Main Pipeline
    # ============================================================

    def parse(self, save_output: bool = True) -> Dict[str, Any]:
        """
        Run the complete parsing pipeline.

        Returns:
            {
                "pages": [...],
                "images": [...],
                "tables": [...],
                "documents": [LangChain Document, ...],
                "output_dir": "..."
            }
        """
        logger.info(
            "pdf_parsing_started",
            pdf_path=str(self.pdf_path),
        )

        try:
            self.extract_text_and_images()
            logger.info(
                "pdf_content_extracted",
                pages=len(self.page_records),
                images=len(self.image_records),
            )

            self.extract_tables()
            logger.info(
                "pdf_tables_extracted",
                tables=len(self.table_records),
            )

            self.create_langchain_documents()
            logger.info(
                "langchain_documents_created",
                documents=len(self.langchain_docs),
            )

            if save_output:
                self.save_outputs()
                logger.info(
                    "parser_outputs_saved",
                    output_dir=str(self.output_dir),
                )

            result = {
                "pages": self.page_records,
                "images": self.image_records,
                "tables": self.table_records,
                "documents": self.langchain_docs,
                "output_dir": str(self.output_dir),
            }

            logger.info(
                "pdf_parsing_completed",
                pdf_path=str(self.pdf_path),
            )
            return result

        except DocumentPortalException:
            raise
        except Exception as exc:
            logger.exception(
                "pdf_parsing_failed",
                pdf_path=str(self.pdf_path),
                error=str(exc),
            )
            raise DocumentPortalException(
                f"Failed to parse PDF: {self.pdf_path}",
                exc,
            ) from exc

# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":

    DATA_DIR = PROJECT_ROOT / "data"

    PDF_PATH = DATA_DIR / "Client_Contracts_Policies_and_Incident_Records.pdf"
    OUTPUT_DIR = DATA_DIR / "parsed_pdf_output"

    TESSERACT_PATH = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    parser = ComplexPDFParser(
        pdf_path=PDF_PATH,
        output_dir=OUTPUT_DIR,
        tesseract_path=TESSERACT_PATH,
    )

    result = parser.parse()

    documents = result["documents"]

    print("\n================ SUMMARY ================\n")
    print("Pages:", len(result["pages"]))
    print("Images:", len(result["images"]))
    print("Tables:", len(result["tables"]))
    print("LangChain Documents:", len(documents))

    if documents:
        print("\nFirst document preview:\n")
        print(documents[0].page_content[:1500])
