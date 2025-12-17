from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.models.job import JobDescription

router = APIRouter()

@router.post("/jobs")
def create_job(
    title: str,
    description: str,
    required_skills: str = None,
    min_experience: float = None,
    db: Session = Depends(get_db)
):
    job = JobDescription(
        title=title,
        description=description,
        required_skills=required_skills,
        min_experience=min_experience
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "title": job.title
    }