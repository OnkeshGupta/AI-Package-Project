from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.services.nlp import match_skills

# load model once (IMPORTANT for performance)
_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> np.ndarray:
    """
    Convert input text into a numerical embedding vector.

    Args:
        text (str): Resume text or Job Description text

    Returns:
        np.ndarray: 1D embedding vector
    """
    if not text or not text.strip():
        raise ValueError("Text for embedding cannot be empty")

    # sentence-transformers expects a list
    embedding = _embedding_model.encode([text])

    # convert to 1D numpy array
    return np.array(embedding[0])

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

def analyze_skill_gap(resume_skills: list, jd_text: str, skills_master: list):
    """
    Compare resume skills against job description skills.

    Args:
        resume_skills (list): skills extracted from resume
        jd_text (str): job description text
        skills_master (list): full skill list (skills.json)

    Returns:
        dict: matched_skills, missing_skills
    """

    jd_skills = match_skills(jd_text, skills_master)

    resume_set = set(s.lower() for s in resume_skills)
    jd_set = set(s.lower() for s in jd_skills)

    matched = sorted(resume_set.intersection(jd_set))
    missing = sorted(jd_set.difference(resume_set))

    return {
        "matched_skills": matched,
        "missing_skills": missing
    }