from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from app.db.base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    experience_years = Column(Integer, nullable=True)
    skills = Column(Text, nullable=True)  # comma-separated

    raw_text = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))