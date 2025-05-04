from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.spend_log import SpendLog
from app.models.budget import Budget
from datetime import date

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