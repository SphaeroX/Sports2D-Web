import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings
from app.models import JobStatus

Base = declarative_base()

class JobRecord(Base):
    __tablename__ = "jobs"
    
    job_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)
    status = Column(String, default=JobStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    original_filename = Column(String, nullable=True)
    upload_path = Column(String, nullable=True)
    result_path = Column(String, nullable=True)
    preview_path = Column(String, nullable=True)
    progress_percent = Column(Integer, default=0)
    message = Column(String, nullable=True)
    access_token_hash = Column(String, nullable=True)
    result_size_mb = Column(Float, nullable=True)
    deleted = Column(String, default="false")

engine = create_engine(f"sqlite:///{settings.DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class StorageService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.result_dir = settings.RESULT_DIR
        self.preview_dir = settings.PREVIEW_DIR
    
    def get_job_upload_dir(self, job_id: str) -> Path:
        path = self.upload_dir / job_id
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_job_result_dir(self, job_id: str) -> Path:
        path = self.result_dir / job_id
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_job_preview_path(self, job_id: str) -> Path:
        return self.preview_dir / f"{job_id}_preview.mp4"
    
    def get_job_zip_path(self, job_id: str) -> Path:
        return self.result_dir / f"{job_id}.zip"
    
    def delete_job_files(self, job_id: str):
        """Delete all files associated with a job."""
        for base_dir in [self.upload_dir, self.result_dir, self.preview_dir]:
            target = base_dir / job_id
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target, ignore_errors=True)
                else:
                    target.unlink(missing_ok=True)
        # Also delete zip if at root of result_dir
        zip_path = self.get_job_zip_path(job_id)
        if zip_path.exists():
            zip_path.unlink(missing_ok=True)
    
    def create_result_zip(self, job_id: str):
        """Zip all result files for a job. Returns (zip_path, size_mb) or None."""
        result_dir = self.get_job_result_dir(job_id)
        zip_path = self.get_job_zip_path(job_id)
        
        if not any(result_dir.iterdir()):
            return None
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(result_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(result_dir)
                    zf.write(file_path, arcname)
        
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        return zip_path, size_mb

storage_service = StorageService()

def cleanup_old_jobs():
    """Delete jobs and files older than AUTO_DELETE_HOURS."""
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=settings.AUTO_DELETE_HOURS)
        old_jobs = db.query(JobRecord).filter(
            JobRecord.created_at < cutoff,
            JobRecord.deleted == "false"
        ).all()
        for job in old_jobs:
            storage_service.delete_job_files(job.job_id)
            job.deleted = "true"
            job.status = JobStatus.FAILED.value
            job.message = "Auto-deleted after timeout"
        db.commit()
    finally:
        db.close()
