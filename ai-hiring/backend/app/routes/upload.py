import os
import shutil
import json
import re
from typing import List

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.dependencies import get_db
from app.auth.dependencies import get_current_user

from app.models.resume import Resume
from app.models.job import JobDescription
from app.models.score import ResumeJobScore
from app.models.ranking_session import RankingSession
from app.models.unknown_skill import UnknownSkill
from app.models.schemas import RankAndScoreResponse

from app.services.parser import extract_text_from_file
from app.services.nlp import (
    _looks_like_skill_list,
    _clean_name_candidate,
    extract_name,
    _parse_month_year,
    extract_experience_years
)
from app.services.scoring import (
    compute_similarity,
    analyze_skill_gap,
    rank_resumes,
    hybrid_score,
    generate_recruiter_feedback
)
from app.core.exceptions import (
    FileProcessingError,
    TextExtractionError,
    ScoringError
)
from app.services.skills import (
    get_embedding,
    match_skills,
    semantic_skill_match
)
from app.services.skill_utils import flatten_skills
from app.services.embeddings import EmbeddingService

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

FLAT_SKILLS = flatten_skills(SKILLS_LIST)

# -------------------------------------------------
# Utility: Save unknown skills safely
# -------------------------------------------------

def save_unknown_skills(db: Session, skills: list[str]):
    unique_skills = {
        s.lower().strip()
        for s in skills
        if s and len(s.strip()) > 2
    }

    for skill in unique_skills:
        existing = db.query(UnknownSkill).filter_by(name=skill).first()
        if existing:
            existing.frequency += 1
        else:
            db.add(UnknownSkill(name=skill, frequency=1))

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

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

    keyword_skills = match_skills(text, FLAT_SKILLS)
    semantic_skills = semantic_skill_match(text, FLAT_SKILLS)
    resume_skills = list(set(keyword_skills + semantic_skills))

    save_unknown_skills(db, resume_skills)

    resume_record = Resume(
        filename=filename,
        name=name,
        email=emails[0] if emails else None,
        phone=phones[0] if phones else None,
        experience_years=exp_years,
        skills=", ".join(resume_skills),
        raw_text=text
    )

    db.add(resume_record)
    db.commit()
    db.refresh(resume_record)

    return {
        "id": resume_record.id,
        "filename": filename,
        "name": name,
        "experience_years": exp_years,
        "skills_detected": resume_skills
    }

# -------------------------------------------------
# 2️⃣ Rank & score resumes (FINAL PIPELINE)
# -------------------------------------------------

@router.post(
    "/rank_and_score",
    response_model=RankAndScoreResponse
)
async def rank_and_score_resumes(
    jd_text: str = Form(...),
    required_experience: float = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not files:
        raise HTTPException(status_code=400, detail="No resumes uploaded")

    # --- Create Job ---
    job_title = "Untitled Job Description"
    for line in jd_text.splitlines():
        if "job title" in line.lower():
            job_title = line.split(":", 1)[-1].strip()
            break

    job = JobDescription(
        title=job_title,
        description=jd_text,
        required_experience=required_experience
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # --- Create Session ---
    session = RankingSession(
        user_id=current_user.id,
        job_description=jd_text
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # --- JD embedding (ONCE) ---
    if not jd_text or not jd_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty"
        )

    try:
        jd_vec = EmbeddingService.encode([jd_text])[0]
    except Exception as e:
        print("JD embedding failed:", e)
        raise ScoringError("Failed to process job description")
    
    jd_keyword_skills = match_skills(jd_text, FLAT_SKILLS)
    jd_semantic_skills = semantic_skill_match(jd_text, FLAT_SKILLS)
    jd_skills = list(set(jd_keyword_skills + jd_semantic_skills))

    results = []

    # 🔹 STEP 4A: collectors
    resume_texts = []
    resume_files = []
    resume_meta = []

    # -------------------------------
    # PASS 1: parse + store resumes
    # -------------------------------
    for file in files:
        dest_path = os.path.join(UPLOAD_DIR, file.filename)

        try:
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            resume_text = extract_text_from_file(dest_path)
        except Exception:
            raise TextExtractionError(f"Failed processing {file.filename}")

        experience_years = extract_experience_years(resume_text)

        resume_skills = match_skills(resume_text, FLAT_SKILLS)

        save_unknown_skills(db, resume_skills)

        resume = Resume(
            filename=f"{job.id}_{file.filename}",
            experience_years=experience_years,
            skills=", ".join(resume_skills),
            raw_text=resume_text
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        resume_texts.append(resume_text)
        resume_files.append(file)
        resume_meta.append({
            "resume": resume,
            "resume_skills": resume_skills,
            "experience_years": experience_years
        })

    # -------------------------------
    # PASS 2: batch embeddings
    # -------------------------------
    resume_embeddings = EmbeddingService.encode(resume_texts)

    # -------------------------------
    # PASS 3: scoring + persistence
    # -------------------------------
    for idx, meta in enumerate(resume_meta):
        resume = meta["resume"]
        resume_skills = meta["resume_skills"]
        experience_years = meta["experience_years"]

        semantic_score = compute_similarity(
            resume_embeddings[idx],
            jd_vec
        )

        final_score = hybrid_score(
            semantic_score=semantic_score,
            resume_skills=resume_skills,
            jd_text=jd_text,
            resume_experience=experience_years,
            required_experience=required_experience,
            skills_master=SKILLS_LIST
        )

        gap = {
            "matched_skills": sorted(set(resume_skills) & set(jd_skills)),
            "missing_skills": sorted(set(jd_skills) - set(resume_skills)),
        }

        feedback = generate_recruiter_feedback(
            final_score=final_score,
            matched_skills=gap["matched_skills"],
            missing_skills=gap["missing_skills"],
            resume_experience=experience_years,
            required_experience=required_experience
        )

        score = ResumeJobScore(
            resume_id=resume.id,
            job_id=job.id,
            session_id=session.id,
            semantic_score=semantic_score,
            final_score=final_score,
            matched_skills=", ".join(gap["matched_skills"]),
            missing_skills=", ".join(gap["missing_skills"]),
            verdict=feedback["verdict"],
            feedback=feedback
        )
        
        db.add(score)
        db.commit()

        results.append({
            "filename": resume.filename,
            "semantic_score": round(semantic_score, 2),
            "final_score": round(final_score, 2),
            "matched_skills": gap["matched_skills"],
            "missing_skills": gap["missing_skills"],
            "feedback": feedback
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)

    return {
        "session_id": session.id,
        "job_description": jd_text[:200],
        "total_resumes": len(results),
        "ranked_candidates": results
    }