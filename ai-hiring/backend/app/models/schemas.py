from typing import List, Optional
from pydantic import BaseModel, Field


class RecruiterFeedback(BaseModel):
    verdict: str
    strengths: List[str]
    concerns: List[str]
    summary: str


class RankedCandidate(BaseModel):
    filename: str
    semantic_score: float = Field(..., ge=0, le=100)
    final_score: float = Field(..., ge=0, le=100)
    matched_skills: List[str]
    missing_skills: List[str]
    feedback: RecruiterFeedback


class RankAndScoreResponse(BaseModel):
    session_id: int
    job_description: str
    total_resumes: int
    ranked_candidates: List[RankedCandidate]