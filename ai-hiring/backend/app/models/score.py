from sqlalchemy import Column, Integer, Float, Text, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class ResumeJobScore(Base):
    __tablename__ = "resume_job_scores"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)

    semantic_score = Column(Float)
    final_score = Column(Float)
    matched_skills = Column(Text)
    missing_skills = Column(Text)
    verdict = Column(String(50))

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    resume = relationship("Resume")
    job = relationship("JobDescription")