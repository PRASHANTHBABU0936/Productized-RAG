"""Tests for the EasyOCR fallback in :mod:`src.parsing`.

These tests are self-contained: the EasyOCR model is never downloaded and
Tesseract is never invoked. The EasyOCR module/reader and the Tesseract
call are monkeypatched so the fallback *logic* (precedence, reader reuse,
graceful failure, page-level gating) is verified deterministically.

Real end-to-end OCR extraction on a sample image is verified manually
(see ``docs/IMPLEMENTATION_STATUS.md``) because it requires downloading
the EasyOCR detector/recognizer weights.
"""

from __future__ import annotations

import sys
import types

import pytest

from src import parsing


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def _reset_easyocr_cache(monkeypatch) -> None:
    """Reset the process-wide EasyOCR reader cache for a clean test."""
    monkeypatch.setattr(parsing, "_EASYOCR_READER", None, raising=False)
    monkeypatch.setattr(parsing, "_EASYOCR_INIT_FAILED", False, raising=False)


class _FakeReader:
    """A stand-in EasyOCR reader whose constructor is counted."""

    def __init__(self, counter, result=None, raise_on_init=False):
        counter["init"] += 1
        if raise_on_init:
            raise RuntimeError("reader init failed")
        self._result = result

    def readtext(self, *args, **kwargs):
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


def _install_fake_easyocr(monkeypatch, result=None, raise_on_init=False):
    """Install a fake ``easyocr`` module and return an init counter."""
    counter = {"init": 0}

    def _reader(*args, **kwargs):
        return _FakeReader(counter, result=result, raise_on_init=raise_on_init)

    module = types.ModuleType("easyocr")
    module.Reader = _reader
    monkeypatch.setitem(sys.modules, "easyocr", module)
    return counter


def _make_parser(tmp_path, pdf_bytes, **kwargs):
    from src.parsing import ComplexPDFParser

    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(pdf_bytes)
    return ComplexPDFParser(
        pdf_path=str(pdf_path),
        output_dir=str(tmp_path / "parsed"),
        **kwargs,
    )


# ---------------------------------------------------------------------
# get_easyocr_reader: lazy, cached, CPU-only, failure-tolerant
# ---------------------------------------------------------------------


def test_reader_is_created_once_and_reused(monkeypatch):
    _reset_easyocr_cache(monkeypatch)
    counter = _install_fake_easyocr(monkeypatch, result=[])

    first = parsing.get_easyocr_reader()
    second = parsing.get_easyocr_reader()

    assert first is not None
    assert first is second
    assert counter["init"] == 1


def test_reader_returns_none_when_disabled(monkeypatch):
    _reset_easyocr_cache(monkeypatch)
    counter = _install_fake_easyocr(monkeypatch, result=[])
    monkeypatch.setenv("EASYOCR_ENABLED", "false")

    assert parsing.get_easyocr_reader() is None
    assert counter["init"] == 0


def test_reader_init_failure_is_tolerated_and_cached(monkeypatch):
    _reset_easyocr_cache(monkeypatch)
    counter = _install_fake_easyocr(monkeypatch, raise_on_init=True)

    assert parsing.get_easyocr_reader() is None
    # Second call must not retry the (failing) heavy initialization.
    assert parsing.get_easyocr_reader() is None
    assert counter["init"] == 1
    assert parsing._EASYOCR_INIT_FAILED is True


def test_languages_default_to_english(monkeypatch):
    monkeypatch.delenv("EASYOCR_LANGUAGES", raising=False)
    assert parsing._easyocr_languages() == ["en"]

    monkeypatch.setenv("EASYOCR_LANGUAGES", "en, hi ,")
    assert parsing._easyocr_languages() == ["en", "hi"]


# ---------------------------------------------------------------------
# easyocr_extract_text: returns text, never raises
# ---------------------------------------------------------------------


def test_extract_text_returns_empty_without_reader(monkeypatch):
    monkeypatch.setattr(parsing, "get_easyocr_reader", lambda: None)
    assert parsing.easyocr_extract_text("whatever.png") == ""


def test_extract_text_joins_segments(monkeypatch):
    monkeypatch.setattr(
        parsing,
        "get_easyocr_reader",
        lambda: _FakeReader({"init": 0}, result=["Hello", "World", "  "]),
    )
    assert parsing.easyocr_extract_text("img.png") == "Hello\nWorld"


def test_extract_text_swallows_reader_errors(monkeypatch):
    monkeypatch.setattr(
        parsing,
        "get_easyocr_reader",
        lambda: _FakeReader({"init": 0}, result=RuntimeError("boom")),
    )
    assert parsing.easyocr_extract_text("img.png") == ""


# ---------------------------------------------------------------------
# run_ocr_on_image: Tesseract first, EasyOCR fallback
# ---------------------------------------------------------------------


def test_run_ocr_prefers_tesseract_when_sufficient(tmp_path, pdf_bytes, monkeypatch):
    parser = _make_parser(tmp_path, pdf_bytes)

    long_text = "x" * (parser.ocr_min_chars + 10)
    monkeypatch.setattr(parser, "_run_tesseract_ocr", lambda path: long_text)
    monkeypatch.setattr(
        parsing,
        "easyocr_extract_text",
        lambda path: pytest.fail("EasyOCR must not run when Tesseract succeeds"),
    )

    assert parser.run_ocr_on_image("page.png") == long_text


def test_run_ocr_falls_back_to_easyocr_when_tesseract_short(
    tmp_path, pdf_bytes, monkeypatch
):
    parser = _make_parser(tmp_path, pdf_bytes)

    monkeypatch.setattr(parser, "_run_tesseract_ocr", lambda path: "")
    monkeypatch.setattr(
        parsing, "easyocr_extract_text", lambda path: "Recovered by EasyOCR"
    )

    assert parser.run_ocr_on_image("page.png") == "Recovered by EasyOCR"


def test_run_ocr_returns_empty_when_both_engines_fail(
    tmp_path, pdf_bytes, monkeypatch
):
    parser = _make_parser(tmp_path, pdf_bytes)

    monkeypatch.setattr(parser, "_run_tesseract_ocr", lambda path: "")
    monkeypatch.setattr(parsing, "easyocr_extract_text", lambda path: "")

    assert parser.run_ocr_on_image("page.png") == ""


def test_run_ocr_keeps_tesseract_text_when_fallback_is_worse(
    tmp_path, pdf_bytes, monkeypatch
):
    parser = _make_parser(tmp_path, pdf_bytes)

    monkeypatch.setattr(parser, "_run_tesseract_ocr", lambda path: "abc")
    monkeypatch.setattr(parsing, "easyocr_extract_text", lambda path: "a")

    assert parser.run_ocr_on_image("page.png") == "abc"


# ---------------------------------------------------------------------
# Page-level gating (req #3)
# ---------------------------------------------------------------------


def test_page_ocr_skipped_when_selectable_text_is_sufficient(
    tmp_path, pdf_bytes, monkeypatch
):
    # The fixture PDF contains selectable text (> page_text_min_chars).
    parser = _make_parser(tmp_path, pdf_bytes)

    calls: list[str] = []
    monkeypatch.setattr(
        parser,
        "run_ocr_on_image",
        lambda path: calls.append(str(path)) or "SHOULD_NOT_BE_USED",
    )

    page_records, _ = parser.extract_text_and_images()

    assert calls == []
    assert page_records[0]["ocr_text"] == ""
    assert len(page_records[0]["text"]) >= parser.page_text_min_chars


def test_page_ocr_runs_when_selectable_text_is_insufficient(
    tmp_path, pdf_bytes, monkeypatch
):
    # Force the scanned-page path by requiring a very high selectable-text
    # threshold, so the (short) fixture text is treated as insufficient.
    parser = _make_parser(tmp_path, pdf_bytes, page_text_min_chars=10_000)

    monkeypatch.setattr(
        parser, "run_ocr_on_image", lambda path: "OCR-RECOVERED-TEXT"
    )

    page_records, _ = parser.extract_text_and_images()

    assert page_records[0]["ocr_text"] == "OCR-RECOVERED-TEXT"
