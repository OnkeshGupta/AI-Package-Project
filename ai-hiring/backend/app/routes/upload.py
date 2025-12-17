import os
import shutil
import json
import re
from typing import List

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session

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

from app.db.dependencies import get_db
from app.models.resume import Resume
from app.models.job import JobDescription
from app.models.score import ResumeJobScore
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
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = file.filename
    dest_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception:
        raise FileProcessingError("Failed to save uploaded resume")

    try:
        text = extract_text_from_file(dest_path)
    except Exception:
        raise TextExtractionError()

    emails = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )
    phones = re.findall(r"\+?\d[\d\-\s]{7,}\d", text)

    name = extract_name(text, SKILLS_LIST)
    exp_years = extract_experience_years(text)
    skills_found = match_skills(text, SKILLS_LIST)

    resume_record = Resume(
        filename=filename,
        name=name,
        email=emails[0] if emails else None,
        phone=phones[0] if phones else None,
        experience_years=exp_years,
        skills=", ".join(skills_found),
        raw_text=text
    )

    db.add(resume_record)
    db.commit()
    db.refresh(resume_record)

    return {
        "id": resume_record.id,
        "filename": filename,
        "emails": list(dict.fromkeys(emails)),
        "phones": list(dict.fromkeys(phones)),
        "name": name,
        "experience_years": exp_years,
        "skills_detected": skills_found
    }

# -------------------------------------------------
# 2️⃣ Score single resume vs JD (NO DB)
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
# 3️⃣ Rank & score resumes + persist scores (FINAL)
# -------------------------------------------------

@router.post(
    "/rank_and_score",
    response_model=RankAndScoreResponse
)
async def rank_and_score_resumes(
    jd_text: str = Form(...),
    required_experience: float = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    print("FILES RECEIVED:", files)
    print("FILES COUNT:", len(files))

    results = []

    # -------- Job title extraction --------
    job_title = "Untitled Job Description"
    for line in jd_text.splitlines():
        if "Job Title" in line:
            job_title = line.split(":", 1)[-1].strip()
            break

    job_record = JobDescription(
        title=job_title,
        description=jd_text,
        required_experience=required_experience
    )
    db.add(job_record)
    db.commit()
    db.refresh(job_record)

    try:
        jd_vec = get_embedding(jd_text)
    except Exception:
        raise ScoringError("Failed to process job description")

    # -------- Resume loop --------
    for file in files:
        filename = file.filename
        dest_path = os.path.join(UPLOAD_DIR, filename)

        try:
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            resume_text = extract_text_from_file(dest_path)
        except Exception:
            raise TextExtractionError(f"Failed processing {filename}")

        resume_skills = match_skills(resume_text, SKILLS_LIST)

        resume = Resume(
            filename=f"{job_record.id}_{filename}",  # ensures uniqueness per job
            skills=", ".join(resume_skills),
            raw_text=resume_text
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)


        semantic = compute_similarity(
            get_embedding(resume_text),
            jd_vec
        )

        final_score = hybrid_score(
            semantic_score=semantic,
            resume_skills=resume_skills,
            jd_text=jd_text,
            resume_experience=resume.experience_years,
            required_experience=required_experience,
            skills_master=SKILLS_LIST
        )

        gap = analyze_skill_gap(resume_skills, jd_text, SKILLS_LIST)

        feedback = generate_recruiter_feedback(
            final_score=final_score,
            matched_skills=gap["matched_skills"],
            missing_skills=gap["missing_skills"],
            resume_experience=resume.experience_years,
            required_experience=required_experience
        )

        score = ResumeJobScore(
            resume_id=resume.id,
            job_id=job_record.id,
            semantic_score=float(semantic),
            final_score=float(final_score),
            matched_skills=", ".join(gap["matched_skills"]),
            missing_skills=", ".join(gap["missing_skills"]),
            verdict=feedback["verdict"]
        )

        db.add(score)
        db.commit()

        results.append({
            "filename": filename,
            "semantic_score": round(float(semantic), 2),
            "final_score": round(float(final_score), 2),
            "matched_skills": gap["matched_skills"],
            "missing_skills": gap["missing_skills"],
            "feedback": feedback
        })

    # 🔹 Sort candidates
    results.sort(key=lambda x: x["final_score"], reverse=True)

    # 🔹 FINAL RESPONSE (THIS WAS MISSING EARLIER)
    return {
        "job_description": jd_text[:200],
        "total_resumes": len(results),
        "ranked_candidates": results
    }