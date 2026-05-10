from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from app.services.storage import get_db, JobRecord, storage_service
from app.models import JobStatus

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{job_id}")
async def download_result(
    job_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    job = db.query(JobRecord).filter(JobRecord.job_id == job_id).first()
    if not job:
        raise HTTPException(404, detail="Job not found")
    if job.status != JobStatus.COMPLETED.value:
        raise HTTPException(400, detail="Job not completed yet")
    
    zip_path = storage_service.get_job_zip_path(job_id)
    if not zip_path.exists():
        raise HTTPException(404, detail="Result file not found")
    
    # After download, schedule immediate deletion
    from app.worker.tasks import delete_job_files_task
    delete_job_files_task.delay(job_id)
    
    return FileResponse(
        path=zip_path,
        filename=f"Sports2D_{job_id}.zip",
        media_type="application/zip",
    )
