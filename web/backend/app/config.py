from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    APP_NAME: str = "Sports2D-Web"
    DEBUG: bool = False
    
    # Paths (inside container)
    BASE_DIR: Path = Path("/app/data")
    UPLOAD_DIR: Path = Path("/app/data/uploads")
    RESULT_DIR: Path = Path("/app/data/results")
    PREVIEW_DIR: Path = Path("/app/data/previews")
    DB_PATH: Path = Path("/app/data/jobs.db")
    
    # File limits
    MAX_UPLOAD_SIZE_MB: int = 500
    MAX_VIDEO_DURATION_SEC: int = 300  # 5 minutes
    CHUNK_SIZE_BYTES: int = 8192
    
    # Redis / Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
    
    # Cleanup
    AUTO_DELETE_HOURS: int = 24
    
    # Sports2D
    SPORTS2D_DEMO_CONFIG: Path = Path("/app/Sports2D-Web/Sports2D/Demo/Config_demo.toml")
    SPORTS2D_DEMO_VIDEO: Path = Path("/app/Sports2D-Web/Sports2D/Demo/demo.mp4")
    
    class Config:
        env_file = ".env"

settings = Settings()
