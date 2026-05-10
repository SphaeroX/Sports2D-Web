from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import logging

from app.models import VideoUploadResponse, JobStatus
from app.config import settings
from app.services.storage import get_db, JobRecord, storage_service
from app.services.security import generate_job_id
from app.services.video_processor import get_video_duration, create_preview

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    user_id: str = Form(default=None),
    db: Session = Depends(get_db)
):
    # Validate file type
    allowed = {"video/mp4", "video/avi", "video/x-msvideo", "video/quicktime", "video/webm", "video/mov"}
    content_type = file.content_type or ""
    filename = file.filename or "video.mp4"
    ext = Path(filename).suffix.lower()
    
    if content_type not in allowed and ext not in {".mp4", ".avi", ".mov", ".webm", ".mkv"}:
        raise HTTPException(400, detail="Invalid file type. Please upload a video file.")
    
    job_id = generate_job_id()
    upload_dir = storage_service.get_job_upload_dir(job_id)
    video_path = upload_dir / f"original{ext}"
    
    # Save uploaded file
    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save upload: {e}")
        raise HTTPException(500, detail="Failed to save uploaded file")
    finally:
        file.file.close()
    
    # Check file size
    size_mb = video_path.stat().st_size / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        shutil.rmtree(upload_dir, ignore_errors=True)
        raise HTTPException(413, detail=f"File too large. Max {settings.MAX_UPLOAD_SIZE_MB}MB allowed.")
    
    # Get duration
    duration = get_video_duration(video_path)
    if duration > settings.MAX_VIDEO_DURATION_SEC:
        shutil.rmtree(upload_dir, ignore_errors=True)
        raise HTTPException(413, detail=f"Video too long. Max {settings.MAX_VIDEO_DURATION_SEC}s allowed.")
    
    # Create preview
    preview_path = storage_service.get_job_preview_path(job_id)
    try:
        create_preview(video_path, preview_path)
    except Exception as e:
        logger.error(f"Preview creation failed: {e}")
        preview_path = None
    
    # Record in DB
    job = JobRecord(
        job_id=job_id,
        user_id=user_id,
        status=JobStatus.PENDING.value,
        original_filename=filename,
        upload_path=str(video_path),
        preview_path=str(preview_path) if preview_path else None,
    )
    db.add(job)
    db.commit()
    
    return VideoUploadResponse(
        job_id=job_id,
        preview_url=f"/previews/{job_id}_preview.mp4" if preview_path else "",
        original_duration=duration,
        message="Upload successful. Proceed to video editing.",
    )
