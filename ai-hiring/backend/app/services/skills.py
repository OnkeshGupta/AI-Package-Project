import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Optional
from datetime import datetime
from app.services.embeddings import EmbeddingService

def get_embedding(text: str) -> np.ndarray | None:
    if not text or not text.strip():
        return None
    return EmbeddingService.encode([text])[0]

def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9+.# ]", " ", text.lower())


def match_skills(text: str, skills_list: list[str]) -> list[str]:
    """
    Robust skill matching:
    - Supports multi-word skills
    - Case-insensitive
    - Space-normalized
    """

    if not text or not skills_list:
        return []

    text_norm = f" {normalize_text(text)} "

    found = []
    for skill in skills_list:
        skill_norm = f" {normalize_text(skill)} "
        if skill_norm in text_norm:
            found.append(skill)

    return found

def semantic_skill_match(
    text: str,
    skills_list: list[str],
    threshold: float = 0.72
) -> list[str]:
    """
    Optimized semantic skill matching:
    - Encode sentences once
    - Encode skills once
    - Compare vectors efficiently
    """

    sentences = [
        s.strip()
        for s in re.split(r"[.\n]", text)
        if len(s.strip()) > 20
    ]

    if not sentences or not skills_list:
        return []

    sentence_vecs = EmbeddingService.encode(sentences)
    skill_vecs = EmbeddingService.encode(skills_list)

    matched = set()

    for skill, skill_vec in zip(skills_list, skill_vecs):
        sims = cosine_similarity(
            [skill_vec],
            sentence_vecs
        )[0]

        if sims.max() >= threshold:
            matched.add(skill)

    return list(matched)

STOPWORDS = {
    # generic resume words
    "experience", "experiences", "experienced",
    "worked", "working", "work",
    "using", "used", "use",
    "with", "and", "or",
    "role", "roles",
    "responsibilities", "responsibility",
    "skills", "skill",
    "projects", "project",
    "years", "year", "yrs", "yr",
    "months", "month",
    "duration",

    # job titles / generic
    "developer", "engineer", "designer", "architect",
    "analyst", "consultant", "intern",
    "lead", "manager",

    # resume structure
    "education", "certification", "certifications",
    "summary", "profile",
    "objective",
    "employment",
    "company", "organization",
    "team", "client",

    # verbs
    "developed", "designed", "implemented",
    "built", "created", "maintained",
    "improved", "optimized", "tested",
    "deployed", "managed",

    # filler tech words
    "system", "systems",
    "application", "applications",
    "software", "platform",
    "tools", "tool",
    "framework", "frameworks",
    "library", "libraries",

    # misc noise
    "basic", "advanced", "intermediate",
    "strong", "good", "excellent",
    "hands", "hands-on",
}

def detect_unknown_skills(text: str, known_skills: list[str]) -> list[str]:
    tokens = set(re.findall(r"[A-Za-z][A-Za-z0-9\+\.\-]{2,}", text))
    known = {s.lower() for s in known_skills}

    return [
        t.lower()
        for t in tokens
        if t.lower() not in known and t.lower() not in STOPWORDS
    ]