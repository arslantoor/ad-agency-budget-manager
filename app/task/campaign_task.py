from datetime import datetime, timezone
import pytz
from sqlalchemy import func, cast, Date
from app.celery_worker import celery_app
from app.db.session import SessionLocal
from app.models import Campaign, Budget, SpendLog
import os

# Load timezone from environment variable
TIMEZONE = os.getenv("APP_TIMEZONE", "UTC")  # Default to UTC if not set

import logging
logger = logging.getLogger(__name__)

@celery_app.task(name="app.task.campaign_task.simulate_campaign_run")
def simulate_campaign_run():
    try:
        db = SessionLocal()

        # Get the timezone-aware datetime
        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)  # Current time in the configured timezone
        current_time = now.time()  # Only the time part for comparison
        today = now.date()  # Current date
        start_month = today.replace(day=1)  # Start of the current month

        campaigns = db.query(Campaign).filter(Campaign.is_active == True).all()
        for campaign in campaigns:
            if campaign.start_time and campaign.end_time:
                start_time = campaign.start_time
                end_time = campaign.end_time

                # Convert campaign start_time and end_time to the configured timezone
                campaign_start_time = start_time
                campaign_end_time = end_time

                if campaign_start_time < campaign_end_time:
                    # Same-day campaign window
                    if not (campaign_start_time.time() <= current_time <= campaign_end_time.time()):
                        continue
                else:
                    # Overnight campaign window (e.g., 22:00 to 02:00)
                    if not (current_time >= campaign_start_time.time() or current_time <= campaign_end_time.time()):
                        continue

            budget = db.query(Budget).filter(Budget.brand_id == campaign.brand_id).first()
            if not budget:
                continue

            # Calculate daily spend
            today_spend = db.query(func.sum(SpendLog.amount_spent)).filter(
                SpendLog.brand_id == campaign.brand_id,
                cast(SpendLog.date, Date) == today
            ).scalar() or 0

            # Calculate monthly spend
            month_spend = db.query(func.sum(SpendLog.amount_spent)).filter(
                SpendLog.brand_id == campaign.brand_id,
                cast(SpendLog.date, Date) >= start_month
            ).scalar() or 0

            hourly_spend = campaign.estimated_hourly_spend

            # Budget check
            if today_spend + hourly_spend > budget.daily_budget or \
                    month_spend + hourly_spend > budget.monthly_budget:
                campaign.is_active = False
            else:
                # Create a new SpendLog with the current time in the correct timezone
                log = SpendLog(
                    brand_id=campaign.brand_id,
                    campaign_id=campaign.id,
                    amount_spent=hourly_spend,
                    date=now  # Storing the current UTC time (timezone-aware)
                )
                db.add(log)

        db.commit()
        db.close()
    except Exception as error:
        logger.error("Exception ",error)
