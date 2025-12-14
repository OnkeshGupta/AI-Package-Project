import os
import shutil
import json
from typing import List

from fastapi import APIRouter, File, UploadFile, Form, HTTPException

from app.services.parser import extract_text_from_file
from app.services.nlp import (
    extract_name,
    extract_experience_years,
    match_skills
)
from app.services.scoring import (
    get_embedding,
    compute_similarity,
    analyze_skill_gap,
    hybrid_score,
    generate_recruiter_feedback
)

from app.models.schemas import RankAndScoreResponse
from app.core.exceptions import (
    FileProcessingError,
    TextExtractionError,
    ScoringError
)

router = APIRouter()

# -------------------------------------------------
# Paths & configuration
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

SKILLS_PATH = os.path.join(BASE_DIR, "data", "skills.json")
try:
    with open(SKILLS_PATH, "r", encoding="utf-8") as f:
        SKILLS_LIST = json.load(f)
except Exception:
    SKILLS_LIST = []

# -------------------------------------------------
# 1️⃣ Upload & parse single resume
# -------------------------------------------------

@router.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    filename = file.filename
    dest_path = os.path.join(UPLOAD_DIR, filename)

    # Save file
    try:
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception:
        raise FileProcessingError("Failed to save uploaded resume")

    # Extract text
    try:
        text = extract_text_from_file(dest_path)
    except Exception:
        raise TextExtractionError()

    # Basic extractions
    import re
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phones = re.findall(r"\+?\d[\d\-\s]{7,}\d", text)

    name = extract_name(text, SKILLS_LIST)
    experience_years = extract_experience_years(text)
    skills_found = match_skills(text, SKILLS_LIST)

    return {
        "filename": filename,
        "emails": list(dict.fromkeys(emails)),
        "phones": list(dict.fromkeys(phones)),
        "name": name,
        "experience_years": experience_years,
        "skills_detected": skills_found,
        "raw_text_snippet": text[:600]
    }

# -------------------------------------------------
# 2️⃣ Score single resume vs JD
# -------------------------------------------------

@router.post("/score_resume")
async def score_resume(
    jd_text: str = Form(...),
    resume_text: str = Form(None),
    file: UploadFile = File(None)
):
    if file:
        dest_path = os.path.join(UPLOAD_DIR, file.filename)
        try:
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            resume_text = extract_text_from_file(dest_path)
        except Exception:
            raise TextExtractionError()

    if not resume_text:
        raise HTTPException(status_code=400, detail="Resume text or file required")

    try:
        semantic_score = compute_similarity(
            get_embedding(resume_text),
            get_embedding(jd_text)
        )
    except Exception:
        raise ScoringError()

    resume_skills = match_skills(resume_text, SKILLS_LIST)
    gap = analyze_skill_gap(resume_skills, jd_text, SKILLS_LIST)

    return {
        "match_score": round(float(semantic_score), 2),
        "matched_skills": gap["matched_skills"],
        "missing_skills": gap["missing_skills"],
        "resume_skills": resume_skills,
        "note": "Semantic similarity based on resume and job description"
    }

# -------------------------------------------------
# 3️⃣ Rank & score multiple resumes (FINAL API)
# -------------------------------------------------

@router.post(
    "/rank_and_score",
    response_model=RankAndScoreResponse
)
async def rank_and_score_resumes(
    jd_text: str = Form(...),
    required_experience: float = Form(None),
    files: List[UploadFile] = File(...)
):
    results = []

    try:
        jd_vec = get_embedding(jd_text)
    except Exception:
        raise ScoringError("Failed to process job description")

    for file in files:
        filename = file.filename
        dest_path = os.path.join(UPLOAD_DIR, filename)

        # Save file
        try:
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
        except Exception:
            raise FileProcessingError(f"Failed to save {filename}")

        # Extract text
        try:
            resume_text = extract_text_from_file(dest_path)
        except Exception:
            raise TextExtractionError(f"Failed to extract text from {filename}")

        resume_skills = match_skills(resume_text, SKILLS_LIST)

        try:
            semantic = compute_similarity(
                get_embedding(resume_text),
                jd_vec
            )
        except Exception:
            raise ScoringError(f"Failed scoring {filename}")

        final_score = hybrid_score(
            semantic_score=semantic,
            resume_skills=resume_skills,
            jd_text=jd_text,
            resume_experience=None,
            required_experience=required_experience,
            skills_master=SKILLS_LIST
        )

        gap = analyze_skill_gap(
            resume_skills,
            jd_text,
            SKILLS_LIST
        )

        feedback = generate_recruiter_feedback(
            final_score=final_score,
            matched_skills=gap["matched_skills"],
            missing_skills=gap["missing_skills"],
            resume_experience=None,
            required_experience=required_experience
        )

        results.append({
            "filename": filename,
            "semantic_score": round(float(semantic), 2),
            "final_score": final_score,
            "matched_skills": gap["matched_skills"],
            "missing_skills": gap["missing_skills"],
            "feedback": feedback
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)

    return {
        "job_description": jd_text[:200],
        "total_resumes": len(results),
        "ranked_candidates": results
    }