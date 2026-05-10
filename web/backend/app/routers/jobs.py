from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import logging

from app.models import JobStatusResponse, ProcessRequest, JobStatus, Segment
from app.services.storage import get_db, JobRecord, storage_service
from app.worker.tasks import process_video_task

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/process")
async def start_processing(
    request: ProcessRequest,
    db: Session = Depends(get_db)
):
    job = db.query(JobRecord).filter(JobRecord.job_id == request.job_id).first()
    if not job:
        raise HTTPException(404, detail="Job not found")
    if job.status not in {JobStatus.PENDING.value, JobStatus.PREPROCESSING.value}:
        raise HTTPException(400, detail="Job already processed or processing")
    
    # Validate segments
    for seg in request.segments:
        if seg.end <= seg.start:
            raise HTTPException(400, detail="Segment end must be greater than start")
    
    # Update job status
    job.status = JobStatus.QUEUED.value
    db.commit()
    
    # Build segments list
    segments = [(seg.start, seg.end) for seg in request.segments]
    
    # Queue task
    process_video_task.delay(
        job_id=request.job_id,
        segments=segments,
        params=request.params.model_dump(),
        expert_mode=request.expert_mode,
    )
    
    return {"job_id": request.job_id, "status": JobStatus.QUEUED.value, "message": "Processing queued"}

@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobRecord).filter(JobRecord.job_id == job_id).first()
    if not job:
        raise HTTPException(404, detail="Job not found")
    
    download_url = None
    if job.status == JobStatus.COMPLETED.value and job.result_path:
        download_url = f"/api/download/{job_id}"
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=JobStatus(job.status),
        created_at=job.created_at,
        updated_at=job.updated_at,
        completed_at=job.completed_at,
        progress_percent=job.progress_percent,
        message=job.message,
        download_url=download_url,
        result_size_mb=job.result_size_mb,
    )
