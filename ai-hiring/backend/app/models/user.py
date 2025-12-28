from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    ranking_sessions = relationship(
        "RankingSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )