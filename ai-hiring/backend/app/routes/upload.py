import os
import shutil
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.parser import extract_text_from_file

router = APIRouter()

# upload directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    filename = file.filename

    # Save uploaded file
    dest_path = os.path.join(UPLOAD_DIR, filename)
    try:
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

    # Extract text
    try:
        text = extract_text_from_file(dest_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {e}")

    # Extract emails + phone numbers
    import re
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phones = re.findall(r"\+?\d[\d\-\s]{7,}\d", text)

    return {
        "filename": filename,
        "emails": list(set(emails)),
        "phones": list(set(phones)),
        "raw_text_snippet": text[:300]
    }