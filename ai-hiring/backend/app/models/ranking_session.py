# app/models/ranking_session.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class RankingSession(Base):
    __tablename__ = "ranking_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # relationships
    user = relationship("User", back_populates="ranking_sessions")
    scores = relationship(
        "ResumeJobScore",
        back_populates="ranking_session",
        cascade="all, delete-orphan"
    )