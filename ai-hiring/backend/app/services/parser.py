"""
backend/app/services/parser.py

Day-2 updated parser:
- Extract text from PDFs (pdfplumber) and DOCX (python-docx)
- If PDF text is missing or too short, fallback to OCR:
    - pdf2image to convert pages to images (requires Poppler)
    - OpenCV preprocessing (grayscale, resize, denoise, adaptive threshold)
    - pytesseract.image_to_data for word-level confidence filtering
    - postprocessing to fix common OCR artifacts
- Safe handling of TESSERACT_CMD via env var
- Returns a string (possibly empty) containing extracted text
"""

import os
import re
from typing import Optional, List

# External libs used at runtime (make sure installed in your venv):
# pdfplumber, python-docx, pdf2image, pytesseract, pillow, opencv-python (cv2), numpy
# Install: pip install pdfplumber python-docx pdf2image pytesseract pillow opencv-python numpy

def _read_pdf_with_pdfplumber(path: str) -> str:
    try:
        import pdfplumber
    except Exception:
        return ""
    text_pages = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_pages.append(t)
    except Exception:
        return ""
    return "\n".join(text_pages).strip()


def _read_docx(path: str) -> str:
    try:
        from docx import Document
    except Exception:
        return ""
    try:
        doc = Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
        return "\n".join(paragraphs).strip()
    except Exception:
        return ""


def _read_text_file(path: str) -> str:
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


# ---------------- OCR helpers ----------------

def _postprocess_ocr_text(text: str) -> str:
    """Apply simple fixes to common OCR artifacts."""
    if not text:
        return text
    # replace non-breaking spaces
    text = text.replace('\xa0', ' ')
    # fix common punctuation around domains, e.g. 'gmail,cota' -> 'gmail.com'
    text = re.sub(r'([A-Za-z0-9._%+-]+)[\s,;:]+(com|in|org|net|co\.in|edu)\b', r'\1.\2', text, flags=re.I)
    # collapse repeated whitespace
    text = re.sub(r'[^\S\r\n]+', ' ', text)
    # join broken year ranges like '2020 - 2021' to '2020-2021'
    text = re.sub(r'(\d{4})\s*[-\u2013\u2014to]{1,4}\s*(\d{4})', r'\1-\2', text)
    # remove stray weird characters often produced by OCR
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()


def _preprocess_image_for_ocr(pil_img, scale: float = 2.0):
    """
    Preprocess PIL Image for OCR using OpenCV:
    - convert to gray
    - upscale
    - denoise
    - adaptive threshold
    Returns a PIL.Image ready for pytesseract.
    """
    try:
        import cv2
        import numpy as np
        from PIL import Image
    except Exception as e:
        raise RuntimeError("OpenCV / numpy / Pillow required for preprocessing") from e

    # convert to RGB PIL -> numpy (BGR for OpenCV)
    img = np.array(pil_img.convert("RGB"))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # convert to gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # resize for small text
    if scale != 1.0:
        new_w = int(gray.shape[1] * scale)
        new_h = int(gray.shape[0] * scale)
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    # denoise
    gray = cv2.medianBlur(gray, 3)

    # adaptive threshold
    th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 31, 12)

    # convert back to PIL
    return Image.fromarray(th)


def _ocr_pdf_with_pytesseract(path: str, dpi: int = 300, scale: float = 2.0, conf_threshold: int = 50, psm: int = 3) -> str:
    """
    Convert PDF pages to images, preprocess, run pytesseract image_to_data,
    keep tokens above conf_threshold, and return cleaned text.
    Requires:
      - pdf2image (and Poppler installed)
      - pytesseract (and Tesseract binary installed)
      - Pillow, OpenCV, numpy
    """
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except Exception as e:
        raise RuntimeError("pdf2image and pytesseract required for OCR") from e

    # Use explicit Tesseract binary from env if provided
    t_cmd = os.getenv("TESSERACT_CMD")
    if t_cmd:
        pytesseract.pytesseract.tesseract_cmd = t_cmd

    try:
        images = convert_from_path(path, dpi=dpi)
    except Exception as e:
        raise RuntimeError(f"pdf2image failed to convert PDF to images: {e}") from e

    page_texts: List[str] = []

    for pil_img in images:
        # preprocess (may raise if cv2 not installed)
        try:
            proc_img = _preprocess_image_for_ocr(pil_img, scale=scale)
        except Exception:
            # if preprocessing fails, fall back to raw image
            proc_img = pil_img

        # get word-level data
        try:
            data = pytesseract.image_to_data(proc_img, output_type=pytesseract.Output.DICT, lang='eng', config=f'--oem 1 --psm {psm}')
        except Exception as e:
            # fallback to simple string OCR
            raw = pytesseract.image_to_string(proc_img, lang='eng', config=f'--oem 1 --psm {psm}')
            page_texts.append(raw)
            continue

        confs = data.get('conf') or []
        texts = data.get('text') or []

        words = []
        for i, w in enumerate(texts):
            # safe confidence parsing (handles ints, floats, strings)
            conf_val = None
            if i < len(confs):
                conf_val = confs[i]
            try:
                conf = int(float(conf_val))
            except Exception:
                conf = -1

            if w and w.strip() and conf >= conf_threshold:
                words.append(w.strip())

        if words:
            page_texts.append(" ".join(words))
        else:
            # fallback to full ocr for this page (less strict)
            raw = pytesseract.image_to_string(proc_img, lang='eng', config=f'--oem 1 --psm {psm}')
            page_texts.append(raw)

    full_text = "\n\n".join(page_texts)
    full_text = _postprocess_ocr_text(full_text)
    return full_text


# ---------------- Master extractor ----------------

def extract_text_from_file(path: str, ocr_enabled: bool = True) -> str:
    """
    Master entry point:
    1) If PDF: try pdfplumber first; if empty and ocr_enabled -> OCR via pdf2image+pytesseract
    2) If DOCX: try python-docx
    3) Else try plain text read
    Returns extracted text (possibly empty string).
    """
    path = os.path.abspath(path)
    path_lower = path.lower()
    text = ""

    if path_lower.endswith(".pdf"):
        text = _read_pdf_with_pdfplumber(path)
        # if pdfplumber found little/no text, use OCR fallback
        if (not text or len(text.strip()) < 50) and ocr_enabled:
            try:
                # tweak dpi/scale/conf_threshold as needed
                text = _ocr_pdf_with_pytesseract(path, dpi=300, scale=2.0, conf_threshold=50, psm=3)
            except Exception as e:
                # return whatever text we had (possibly empty) or bubble up minimal message
                raise RuntimeError(f"OCR extraction failed: {e}") from e

    elif path_lower.endswith(".docx"):
        text = _read_docx(path)
    else:
        text = _read_text_file(path)

    return text or ""