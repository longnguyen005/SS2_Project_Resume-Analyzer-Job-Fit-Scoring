from __future__ import annotations

import re
from pathlib import Path

from app.core.config import settings


class ResumeParseError(ValueError):
    pass


def extract_text_from_resume(file_path: str, file_type: str) -> str:
    normalized_type = file_type.lower()

    if normalized_type == "pdf":
        return _extract_text_from_pdf(file_path)
    if normalized_type == "docx":
        return _extract_text_from_docx(file_path)

    raise ResumeParseError(f"Unsupported resume file type: {file_type}")


def _extract_text_from_pdf(file_path: str) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ResumeParseError(
            "PDF text extraction dependency is missing. Install `pypdf` to parse PDF resumes."
        ) from exc

    try:
        reader = PdfReader(file_path)
    except Exception as exc:
        raise ResumeParseError("Could not open the PDF file for text extraction.") from exc

    pages = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(page_text)

    text = _normalize_text("\n\n".join(pages))
    if text:
        return text

    if not settings.ocr_fallback_enabled:
        raise ResumeParseError("No readable text was found in the PDF. OCR fallback is disabled.")

    return _extract_text_from_pdf_with_ocr(file_path)


def _extract_text_from_pdf_with_ocr(file_path: str) -> str:
    try:
        import fitz
    except ImportError as exc:
        raise ResumeParseError(
            "OCR fallback dependencies are missing. Install `pymupdf`, `pytesseract`, and `pillow`."
        ) from exc

    try:
        import pytesseract
    except ImportError as exc:
        raise ResumeParseError(
            "OCR fallback dependencies are missing. Install `pymupdf`, `pytesseract`, and `pillow`."
        ) from exc

    try:
        from PIL import Image
    except ImportError as exc:
        raise ResumeParseError(
            "OCR fallback dependencies are missing. Install `pymupdf`, `pytesseract`, and `pillow`."
        ) from exc

    ocr_pages: list[str] = []
    render_scale = max(settings.ocr_render_scale, 1.0)
    matrix = fitz.Matrix(render_scale, render_scale)

    try:
        with fitz.open(file_path) as document:
            for page in document:
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                image_mode = "L" if pixmap.n == 1 else "RGB"
                image = Image.frombytes(image_mode, [pixmap.width, pixmap.height], pixmap.samples)
                page_text = _extract_text_from_image_with_ocr(image, pytesseract)
                if page_text.strip():
                    ocr_pages.append(page_text)
    except ResumeParseError:
        raise
    except Exception as exc:
        raise ResumeParseError("OCR fallback failed while reading the PDF pages.") from exc

    text = _normalize_text("\n\n".join(ocr_pages))
    if not text:
        raise ResumeParseError("No readable text was found in the PDF, even after OCR fallback.")

    return text


def _extract_text_from_image_with_ocr(image, pytesseract_module) -> str:
    try:
        return pytesseract_module.image_to_string(image, lang=settings.ocr_languages)
    except pytesseract_module.TesseractNotFoundError as exc:
        raise ResumeParseError("OCR engine is not available. Install `tesseract-ocr` in the runtime environment.") from exc
    except pytesseract_module.TesseractError as exc:
        fallback_language = settings.ocr_language_fallback.strip()
        if fallback_language and fallback_language != settings.ocr_languages:
            try:
                return pytesseract_module.image_to_string(image, lang=fallback_language)
            except Exception:
                pass
        raise ResumeParseError(f"OCR failed while processing the PDF page: {exc}") from exc


def _extract_text_from_docx(file_path: str) -> str:
    document_path = Path(file_path)
    if document_path.suffix.lower() != ".docx":
        raise ResumeParseError("DOCX extraction expects a .docx file.")

    try:
        from docx import Document
    except ImportError as exc:
        raise ResumeParseError(
            "DOCX text extraction dependency is missing. Install `python-docx` to parse DOCX resumes."
        ) from exc

    try:
        document = Document(document_path)
    except FileNotFoundError as exc:
        raise ResumeParseError("DOCX file was not found for text extraction.") from exc
    except Exception as exc:
        raise ResumeParseError("The uploaded DOCX file is corrupted or invalid.") from exc

    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]

    text = _normalize_text("\n".join(paragraphs))
    if not text:
        raise ResumeParseError("No readable text was found in the DOCX file.")

    return text


def _normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    normalized = re.sub(r"[ \t]{2,}", " ", normalized)
    return normalized.strip()
