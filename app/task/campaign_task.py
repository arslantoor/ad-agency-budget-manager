from fastapi import BackgroundTasks
from datetime import datetime, time

from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Campaign, Budget, SpendLog
from app.db.session import get_db

def simulate_campaign_run(db: Session):
    current_time = datetime.utcnow().time()
    campaigns = db.query(Campaign).filter(Campaign.is_active == True).all()

    for campaign in campaigns:
        # Dayparting check
        if campaign.dayparting_start and campaign.dayparting_end:
            if not (campaign.dayparting_start <= current_time <= campaign.dayparting_end):
                continue

        budget = db.query(Budget).filter(Budget.brand_id == campaign.brand_id).first()
        if not budget:
            continue

        # Get today's and this month's spend
        today = datetime.utcnow().date()
        start_month = today.replace(day=1)

        today_spend = db.query(SpendLog).filter(
            SpendLog.brand_id == campaign.brand_id,
            SpendLog.spend_date == today
        ).with_entities(func.sum(SpendLog.amount)).scalar() or 0

        month_spend = db.query(SpendLog).filter(
            SpendLog.brand_id == campaign.brand_id,
            SpendLog.spend_date >= start_month
        ).with_entities(func.sum(SpendLog.amount)).scalar() or 0

        hourly_spend = campaign.estimated_hourly_spend

        if today_spend + hourly_spend > budget.daily_budget or month_spend + hourly_spend > budget.monthly_budget:
            campaign.is_active = False
        else:
            # Log spend
            log = SpendLog(brand_id=campaign.brand_id, amount=hourly_spend, spend_date=today)
            db.add(log)

    db.commit()