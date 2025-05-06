from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.spend_log import SpendLog
from app.models.budget import Budget
from datetime import date
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Campaign, SpendLog, Budget, Brand

def check_daily_budget(db: Session, brand_id: int) -> bool:
    today = date.today()
    spent_today = db.query(func.sum(SpendLog.amount_spent)).filter(
        SpendLog.brand_id == brand_id,
        SpendLog.date == today
    ).scalar() or 0

    budget = db.query(Budget).filter(Budget.brand_id == brand_id).first()
    return spent_today < budget.daily_budget if budget else True

def check_monthly_budget(db: Session, brand_id: int) -> bool:
    today = date.today()
    first_day = today.replace(day=1)
    spent_this_month = db.query(func.sum(SpendLog.amount_spent)).filter(
        SpendLog.brand_id == brand_id,
        SpendLog.date >= first_day
    ).scalar() or 0

    budget = db.query(Budget).filter(Budget.brand_id == brand_id).first()
    return spent_this_month < budget.monthly_budget if budget else True

def get_daily_spend(db: Session, brand_id: int) -> float:
    today = datetime.utcnow().date()
    return db.query(SpendLog).filter(
        SpendLog.brand_id == brand_id,
        SpendLog.spend_date >= today
    ).with_entities(func.sum(SpendLog.amount)).scalar() or 0

def get_monthly_spend(db: Session, brand_id: int) -> float:
    now = datetime.utcnow()
    start_of_month = now.replace(day=1)
    return db.query(SpendLog).filter(
        SpendLog.brand_id == brand_id,
        SpendLog.spend_date >= start_of_month
    ).with_entities(func.sum(SpendLog.amount)).scalar() or 0


def simulate_campaign_run(db: Session):
    from datetime import time as dtime
    from sqlalchemy import func

    current_time = datetime.utcnow().time()
    campaigns = db.query(Campaign).filter(Campaign.status == True).all()

    for campaign in campaigns:
        if campaign.start_hour and campaign.end_hour:
            if not (campaign.start_hour <= current_time <= campaign.end_hour):
                continue

        brand = db.query(Brand).filter_by(id=campaign.brand_id).first()
        budget = db.query(Budget).filter_by(brand_id=brand.id).first()

        daily_spend = get_daily_spend(db, brand.id)
        monthly_spend = get_monthly_spend(db, brand.id)

        est_cost = campaign.estimated_hourly_spend

        if (daily_spend + est_cost > budget.daily_budget or
            monthly_spend + est_cost > budget.monthly_budget):
            campaign.status = False
            db.commit()
            continue

        # Log spend
        log = SpendLog(
            brand_id=brand.id,
            campaign_id=campaign.id,
            amount=est_cost,
            spend_date=datetime.utcnow()
        )
        db.add(log)
        db.commit()
