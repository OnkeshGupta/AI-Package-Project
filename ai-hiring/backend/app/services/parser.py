import pdfplumber
from docx import Document

def extract_text_from_file(path: str) -> str:
    path_lower = path.lower()

    # PDF
    if path_lower.endswith(".pdf"):
        text_pages = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_pages.append(t)
        return "\n".join(text_pages)

    # DOCX
    elif path_lower.endswith(".docx"):
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    # fallback for txt files
    else:
        with open(path, "r", errors="ignore") as f:
            return f.read()