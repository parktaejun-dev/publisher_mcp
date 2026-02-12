from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from backend.db.session import get_db
from backend.db.models import IngestJob, Document

router = APIRouter()

@router.get("/")
def list_jobs(
    status: Optional[str] = Query(None),
    engine: Optional[str] = Query(None),
    limit: int = 100,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(IngestJob)
    if status:
        query = query.filter(IngestJob.status == status)
    if engine:
        query = query.filter(IngestJob.engine == engine)

    jobs = query.order_by(IngestJob.updated_at.desc()).offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(IngestJob).filter(IngestJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/{job_id}/retry")
def retry_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(IngestJob).filter(IngestJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Reset job to queued
    job.status = "queued"
    job.attempt += 1
    job.last_error = None
    # We might want to clear any existing draft for this job/doc if we want a fresh start,
    # but the prompt says "retry (attempt+1, status=queued)".

    db.commit()
    db.refresh(job)
    return job
