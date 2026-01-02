from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class UnknownSkill(Base):
    __tablename__ = "unknown_skills"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    frequency = Column(Integer, default=1)
    approved = Column(Boolean, default=False)