from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.model import Brand, Budget, Campaign, SpendLog, BudgetType

def get_spend(db: Session, brand_id: int, budget_type: BudgetType):
    now = datetime.utcnow()
    if budget_type == BudgetType.DAILY:
        start = datetime(now.year, now.month, now.day)
    else:
        start = datetime(now.year, now.month, 1)

    return db.query(func.sum(SpendLog.amount))\
             .filter(SpendLog.brand_id == brand_id)\
             .filter(SpendLog.timestamp >= start)\
             .scalar() or 0

def add_spend(db: Session, brand_id: int, campaign_id: int, amount: float):
    db.add(SpendLog(brand_id=brand_id, campaign_id=campaign_id, amount=amount))

    # Check both budgets
    for budget_type in [BudgetType.DAILY, BudgetType.MONTHLY]:
        total_spend = get_spend(db, brand_id, budget_type)
        budget = db.query(Budget).filter(Budget.brand_id == brand_id, Budget.type == budget_type).first()
        if budget and total_spend >= budget.limit:
            # Deactivate all campaigns
            campaigns = db.query(Campaign).filter(Campaign.brand_id == brand_id).all()
            for c in campaigns:
                c.is_active = False

    db.commit()

def reset_budgets(db: Session, budget_type: BudgetType):
    now = datetime.utcnow()
    budgets = db.query(Budget).filter(Budget.type == budget_type).all()

    for budget in budgets:
        budget.reset_at = now
        brand = db.query(Brand).filter(Brand.id == budget.brand_id).first()
        if not brand:
            continue

        for c in brand.campaigns:
            if c.dayparting_start <= now.time() <= c.dayparting_end:
                c.is_active = True
    db.commit()