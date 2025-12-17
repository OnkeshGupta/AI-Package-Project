from sqlalchemy import Column, Integer, Text, Float, DateTime
from datetime import datetime, timezone
from app.db.base import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    required_experience = Column(Float, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )