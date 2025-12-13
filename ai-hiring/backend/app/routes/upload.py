import os
import shutil
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.parser import extract_text_from_file
from app.services.nlp import extract_name, extract_experience_years, match_skills
import json
from fastapi import Form
from app.services.scoring import (
    get_embedding,
    compute_similarity,
    analyze_skill_gap
)

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

@router.post("/score_resume")
async def score_resume(
    jd_text: str = Form(...),
    resume_text: str = Form(None),
    file: UploadFile = File(None)
):
    """
    Score resume against a job description.
    Accepts resume as text OR file.
    """

    # Step 1: Get resume text
    if file:
        filename = file.filename
        dest_path = os.path.join(UPLOAD_DIR, filename)
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        resume_text = extract_text_from_file(dest_path)

    if not resume_text:
        raise HTTPException(status_code=400, detail="Resume text or file required")

    # Step 2: Compute embeddings
    resume_vec = get_embedding(resume_text)
    jd_vec = get_embedding(jd_text)

    match_score = compute_similarity(resume_vec, jd_vec)

    # Step 3: Extract resume skills
    resume_skills = match_skills(resume_text, SKILLS_LIST)

    # Step 4: Skill gap analysis
    gap = analyze_skill_gap(resume_skills, jd_text, SKILLS_LIST)

    return {
        "match_score": round(float(match_score), 2),
        "matched_skills": gap["matched_skills"],
        "missing_skills": gap["missing_skills"],
        "resume_skills": resume_skills,
        "note": "Semantic similarity based on resume and job description"
    }