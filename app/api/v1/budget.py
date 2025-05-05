# app/api/api_v1/endpoints/budget.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.schemas.budget import BudgetOut
from app.models import Budget, SpendLog, Brand, Campaign
from app.schemas import budget as schema
from app.db.session import get_db


router = APIRouter()

class BudgetCreate(BaseModel):
    brand_id: int
    daily_budget: float
    monthly_budget: float

@router.post("/budgets/",response_model=BudgetOut)
def create_budget(budget_data: BudgetCreate, db: Session = Depends(get_db)):
    # Ensure brand_id is present
    if not budget_data.brand_id:
        raise HTTPException(status_code=400, detail="brand_id is required")

    # Check if budget already exists for brand
    existing_budget = db.query(Budget).filter(Budget.brand_id == budget_data.brand_id).first()
    if existing_budget:
        raise HTTPException(status_code=400, detail="Budget already exists for this brand")

    # Create budget
    budget = Budget(
        brand_id=budget_data.brand_id,
        daily_budget=budget_data.daily_budget,
        monthly_budget=budget_data.monthly_budget
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget

@router.get("/budgets/{brand_id}")
def get_budget(brand_id: int, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.brand_id == brand_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

@router.post("/budgets/{brand_id}/spend")
def log_spend(brand_id: int, amount: float, db: Session = Depends(get_db)):
    log = SpendLog(brand_id=brand_id, amount_spent=amount, date=datetime.utcnow())
    db.add(log)
    db.commit()
    return {"message": "Spend logged."}

@router.post("/check-budgets")
def check_budgets(db: Session = Depends(get_db)):
    brands = db.query(Brand).all()
    for brand in brands:
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)

        # Daily spend
        daily_spend = db.query(func.sum(SpendLog.amount))\
            .filter(SpendLog.brand_id == brand.id, SpendLog.spend_date >= today).scalar() or 0

        # Monthly spend
        monthly_spend = db.query(func.sum(SpendLog.amount))\
            .filter(SpendLog.brand_id == brand.id, SpendLog.spend_date >= month_start).scalar() or 0

        budget = db.query(Budget).filter(Budget.brand_id == brand.id).first()

        campaigns = db.query(Campaign).filter(Campaign.brand_id == brand.id).all()

        for campaign in campaigns:
            if monthly_spend >= budget.monthly_budget or daily_spend >= budget.daily_budget:
                campaign.status = False
            else:
                campaign.status = True
    db.commit()
    return {"message": "Budgets checked and campaigns updated."}

@router.post("/reset-budgets")
def reset_budgets(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    if today.day == 1:
        db.query(SpendLog).delete()
    else:
        db.query(SpendLog).filter(SpendLog.spend_date < today).delete()
    db.commit()
    return {"message": "Budgets reset."}

@router.post("/dayparting/enforce")
def enforce_dayparting(db: Session = Depends(get_db)):
    now = datetime.utcnow().time()
    campaigns = db.query(Campaign).filter(Campaign.dayparting_start != None).all()
    for c in campaigns:
        if c.dayparting_start <= now <= c.dayparting_end:
            c.status = True
        else:
            c.status = False
    db.commit()
    return {"message": "Dayparting enforced."}