from celery import Celery
from app.config import settings
from celery.schedules import crontab

celery_app = Celery(
    "sports2d_web",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "cleanup-old-jobs": {
            "task": "app.worker.tasks.cleanup_old_jobs_task",
            "schedule": crontab(hour="*/3", minute=0),
        },
    },
)
