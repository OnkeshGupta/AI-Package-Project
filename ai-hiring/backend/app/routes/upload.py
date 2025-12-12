import os
import shutil
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.parser import extract_text_from_file
from app.services.nlp import extract_name, extract_experience_years, match_skills
import json

router = APIRouter()

# upload directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

_SKILLS_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "app", "data", "skills.json"))
try:
    with open(_SKILLS_PATH, "r", encoding="utf-8") as f:
        SKILLS_LIST = json.load(f)
except Exception:
    SKILLS_LIST = []


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
    name = extract_name(text, SKILLS_LIST) or None
    exp_years = extract_experience_years(text)
    skills_found = match_skills(text, SKILLS_LIST)

    return {
    "filename": filename,
    "emails": list(dict.fromkeys(emails)),
    "phones": list(dict.fromkeys(phones)),
    "name": name,
    "experience_years": exp_years,
    "skills_detected": skills_found,
    "raw_text_snippet": text[:600]
    }