from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "ad_agency",
    broker="redis://localhost:6379/0",
    backend=f"db+{settings.DATABASE_URL}",
    include=["app.task.campaign_task"]
)

celery_app.conf.update(
    task_routes={
        "app.tasks.*": {"queue": "default"},
    },
    beat_schedule={
        'run-campaign-spend-every-hour': {
            'task': 'app.task.campaign_task.simulate_campaign_run',
            'schedule': crontab(minute='*'),
            'options': {'queue': 'default'}  # Make sure queue matches
        },
        'reset-campaigns-daily-midnight': {
            'task': 'app.task.campaign_task.reset_campaigns',
            'schedule': crontab(minute=0, hour=0),  # every day at midnight
            'options': {'queue': 'default'}
        }
    },
    timezone = 'UTC',
    enable_utc = True
)