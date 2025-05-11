from datetime import datetime, timezone
import pytz
from sqlalchemy import func, cast, Date
from app.celery_worker import celery_app
from app.db.session import SessionLocal
from app.models import Campaign, Budget, SpendLog
import os

# Load timezone from environment variable
TIMEZONE = os.getenv("APP_TIMEZONE", "UTC")  # Default to UTC if not set

@celery_app.task(name="app.task.campaign_task.reset_campaigns")
def reset_campaigns():
    db = SessionLocal()
    try:
        today = datetime.now(pytz.timezone(TIMEZONE)).date()
        start_month = today.replace(day=1)

        brands = db.query(Budget).all()
        for budget in brands:
            today_spend = db.query(func.sum(SpendLog.amount_spent)).filter(
                SpendLog.brand_id == budget.brand_id,
                cast(SpendLog.date, Date) == today
            ).scalar() or 0

            month_spend = db.query(func.sum(SpendLog.amount_spent)).filter(
                SpendLog.brand_id == budget.brand_id,
                cast(SpendLog.date, Date) >= start_month
            ).scalar() or 0

            if today_spend < budget.daily_budget and month_spend < budget.monthly_budget:
                db.query(Campaign).filter(
                    Campaign.brand_id == budget.brand_id
                ).update({Campaign.is_active: True})

        db.commit()
    finally:
        db.close()
