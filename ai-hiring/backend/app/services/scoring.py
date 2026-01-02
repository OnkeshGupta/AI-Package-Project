from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.services.skills import match_skills, semantic_skill_match
from app.services.embeddings import EmbeddingService
from app.services.skill_utils import flatten_skills

def get_embedding(text: str) -> np.ndarray:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    return EmbeddingService.encode([text])[0]


def compute_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute cosine similarity between two embedding vectors.

    Args:
        vec1 (np.ndarray): Resume embedding
        vec2 (np.ndarray): Job description embedding

    Returns:
        float: similarity score between 0 and 100
    """
    # reshape for sklearn (expects 2D arrays)
    v1 = vec1.reshape(1, -1)
    v2 = vec2.reshape(1, -1)

    similarity = cosine_similarity(v1, v2)[0][0]

    # convert to percentage score
    return float(round(similarity * 100, 2))

def analyze_skill_gap(
    resume_skills: list,
    jd_text: str,
    skills_master: dict
):
    """
    Optimized skill gap analysis:
    1. Extract skills from JD only
    2. Compare resume against JD-relevant skills
    """

    all_skills = flatten_skills(skills_master)

    jd_keyword = match_skills(jd_text, all_skills)
    jd_semantic = semantic_skill_match(jd_text, all_skills)

    jd_skills = {
        s.lower().strip()
        for s in (jd_keyword + jd_semantic)
    }

    resume_set = {
        s.lower().strip()
        for s in resume_skills
    }

    matched = sorted(jd_skills & resume_set)
    missing = sorted(jd_skills - resume_set)

    return {
        "matched_skills": matched,
        "missing_skills": missing
    }

def rank_resumes(resume_entries: list, jd_text: str, skills_master: dict):
    """
    Rank multiple resumes against a single job description.

    Args:
        resume_entries (list): list of dicts with keys: filename, text, skills
        jd_text (str): job description
        skills_master (list): skills list

    Returns:
        list: ranked resumes with score and gap analysis
    """
    ranked = []

    jd_vec = get_embedding(jd_text)

    for entry in resume_entries:
        resume_vec = get_embedding(entry["text"])
        score = compute_similarity(resume_vec, jd_vec)

        gap = analyze_skill_gap(
            entry["skills"],
            jd_text,
            skills_master
        )

        ranked.append({
            "filename": entry["filename"],
            "match_score": round(float(score), 2),
            "matched_skills": gap["matched_skills"],
            "missing_skills": gap["missing_skills"]
        })

    # sort by score (highest first)
    ranked.sort(key=lambda x: x["match_score"], reverse=True)

    return ranked

def hybrid_score(
    semantic_score: float,
    resume_skills: list,
    jd_text: str,
    resume_experience: float,
    required_experience: float,
    skills_master: dict
) -> float:
    """
    Compute hybrid score using semantic similarity, skill match, and experience.

    Returns:
        float: final score (0–100)
    """
    # --- Skill match percentage ---
    all_skills = flatten_skills(skills_master)

    jd_skills = match_skills(jd_text, all_skills)

    if jd_skills:
        skill_match_pct = (len(set(resume_skills) & set(jd_skills)) / len(jd_skills)) * 100
    else:
        skill_match_pct = 50  

    # --- Experience score ---
    if resume_experience is None or required_experience is None:
        exp_score = 50
    elif resume_experience >= required_experience:
        exp_score = 100
    elif resume_experience >= required_experience * 0.7:
        exp_score = 70
    else:
        exp_score = 30

    # --- Weighted final score ---
    final_score = (
        0.5 * semantic_score +
        0.3 * skill_match_pct +
        0.2 * exp_score
    )

    return round(float(final_score), 2)

def generate_recruiter_feedback(
    final_score: float,
    matched_skills: list,
    missing_skills: list,
    resume_experience: float,
    required_experience: float
) -> dict:
    """
    Generate human-readable recruiter feedback based on scoring signals.
    """

    # --- Overall verdict ---
    if final_score >= 75:
        verdict = "Strong Match"
    elif final_score >= 60:
        verdict = "Good Match"
    elif final_score >= 45:
        verdict = "Average Match"
    else:
        verdict = "Weak Match"


    # --- Strengths ---
    strengths = []
    if matched_skills:
        strengths.append(f"Strong skill match in {', '.join(matched_skills[:5])}")
    if resume_experience and required_experience:
        if resume_experience >= required_experience:
            strengths.append("Meets or exceeds required experience")
        elif resume_experience >= required_experience * 0.7:
            strengths.append("Close to required experience")

    # --- Concerns ---
    concerns = []
    if missing_skills:
        concerns.append(f"Missing key skills: {', '.join(missing_skills[:5])}")
    if resume_experience and required_experience:
        if resume_experience < required_experience * 0.7:
            concerns.append("Experience significantly below requirement")

    # --- Summary ---
    summary_parts = []
    if strengths:
        summary_parts.append(strengths[0])
    if concerns:
        summary_parts.append(concerns[0])

    summary = ". ".join(summary_parts) if summary_parts else "Profile requires further review."

    return {
        "verdict": verdict,
        "strengths": strengths,
        "concerns": concerns,
        "summary": summary
    }