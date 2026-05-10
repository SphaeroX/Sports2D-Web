from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import os
import sys

# Add parent repo to path so we can import Sports2D
sys.path.insert(0, "/app/Sports2D-Web")

from app.config import settings
from app.routers import upload, jobs, download
from app.services.storage import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create directories
for d in [settings.UPLOAD_DIR, settings.RESULT_DIR, settings.PREVIEW_DIR]:
    d.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    description="Web interface for Sports2D markerless motion analysis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler for large uploads
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(download.router, prefix="/api/download", tags=["download"])

# Mount static dirs for previews and results (protected by uuid filenames)
app.mount("/previews", StaticFiles(directory=settings.PREVIEW_DIR), name="previews")
app.mount("/results", StaticFiles(directory=settings.RESULT_DIR), name="results")

@app.on_event("startup")
async def on_startup():
    init_db()
    logger.info("Sports2D-Web backend started")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
