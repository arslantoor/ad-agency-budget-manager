from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "ad_agency",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.task_routes = {
    "app.tasks.*": {"queue": "default"},
}

celery_app.conf.beat_schedule = {
    'run-campaign-spend-every-hour': {
        'task': 'app.tasks.campaign_tasks.simulate_campaign_spend',
        'schedule': crontab(minute=0, hour='*'),
    },
}