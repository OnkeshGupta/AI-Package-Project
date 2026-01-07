from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.auth.dependencies import get_current_user
from app.models.ranking_session import RankingSession

router = APIRouter()

@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    sessions = (
        db.query(RankingSession)
        .filter(RankingSession.user_id == current_user.id)
        .order_by(RankingSession.created_at.desc())
        .all()
    )

    return [
        {
            "session_id": s.id,
            "created_at": s.created_at,
            "job_description": s.job_description[:200] + "...",
            "total_candidates": len(s.scores),
            "top_score": max([sc.final_score for sc in s.scores]) if s.scores else 0
        }
        for s in sessions
    ]

@router.get("/history/{session_id}")
def get_history_detail(
    session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    session = (
        db.query(RankingSession)
        .filter(
            RankingSession.id == session_id,
            RankingSession.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.id,
        "created_at": session.created_at,
        "job_description": session.job_description,
        "ranked_candidates": [
            {
                "filename": score.resume.filename,
                "semantic_score": score.semantic_score,
                "final_score": score.final_score,
                "matched_skills": score.matched_skills.split(", "),
                "missing_skills": score.missing_skills.split(", "),
                "feedback": score.feedback
            }
            for score in session.scores
        ]
    }

@router.delete("/history/{session_id}")
def delete_history_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    session = (
        db.query(RankingSession)
        .filter(
            RankingSession.id == session_id,
            RankingSession.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    db.commit()

    return {"message": "History deleted successfully"}