from sqlalchemy import Column, Integer, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base


class ResumeJobScore(Base):
    __tablename__ = "resume_job_scores"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("ranking_sessions.id"), nullable=True)

    semantic_score = Column(Float)
    final_score = Column(Float)
    matched_skills = Column(Text)
    missing_skills = Column(Text)
    verdict = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    resume = relationship("Resume", backref="scores")
    ranking_session = relationship("RankingSession", back_populates="scores")