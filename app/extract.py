"""Extract text from PDF or DOCX files.

In this app we ONLY ever get bytes (from `await file.read()` in FastAPI).
We don't need paths or file objects, so we keep it dead simple.
"""

from io import BytesIO

import pypdfium2 as pdfium
from docx import Document


def extract_text(filename: str, data: bytes) -> str:
    """Turn uploaded file bytes into plain text.

    Supports only .pdf and .docx.
    """
    name = filename.lower()

    if name.endswith(".pdf"):
        pdf = pdfium.PdfDocument(BytesIO(data))
        return "\n".join(page.get_textpage().get_text_bounded() for page in pdf).strip()

    if name.endswith(".docx"):
        doc = Document(BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs).strip()

    raise ValueError(f"Only .pdf and .docx are supported. Got: {filename}")
