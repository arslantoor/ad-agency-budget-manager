# Required imports
import pytz
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.schemas.budget import BudgetOut, BudgetCreate
from app.models import Budget, SpendLog, Brand, Campaign
from typing import List
from app.schemas.spend_log import SpendLogOut
from app.db.session import get_db
from app.core.config import Settings

router = APIRouter()

# ------------------------------------------
# Create a new budget for a brand
# ------------------------------------------
@router.post("/budgets/", response_model=BudgetOut)
def create_budget(budget_data: BudgetCreate, db: Session = Depends(get_db)):
    # Ensure brand_id is provided
    if not budget_data.brand_id:
        raise HTTPException(status_code=400, detail="brand_id is required")

    # Verify the brand exists
    brand = db.query(Brand).filter(Brand.id == budget_data.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    # Check for an existing budget for the brand
    existing_budget = db.query(Budget).filter(Budget.brand_id == budget_data.brand_id).first()
    if existing_budget:
        raise HTTPException(status_code=400, detail="Budget already exists for this brand")

    # Create and store the new budget
    budget = Budget(
        brand_id=budget_data.brand_id,
        daily_budget=budget_data.daily_budget,
        monthly_budget=budget_data.monthly_budget
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


# ------------------------------------------
# Update an existing budget for a brand
# ------------------------------------------
@router.patch("/budgets/", response_model=BudgetOut)
def update_budget(budget_data: BudgetCreate, db: Session = Depends(get_db)):
    # Validate brand_id
    if not budget_data.brand_id:
        raise HTTPException(status_code=400, detail="brand_id is required")

    # Check brand existence
    brand = db.query(Brand).filter(Brand.id == budget_data.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    # Find existing budget
    budget = db.query(Budget).filter(Budget.brand_id == budget_data.brand_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found for this brand")

    # Update daily/monthly budget if provided
    if budget_data.daily_budget is not None:
        budget.daily_budget = budget_data.daily_budget
    if budget_data.monthly_budget is not None:
        budget.monthly_budget = budget_data.monthly_budget

    db.commit()
    db.refresh(budget)
    return budget


# ------------------------------------------
# Retrieve budget for a given brand
# ------------------------------------------
@router.get("/budgets/{brand_id}")
def get_budget(brand_id: int, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.brand_id == brand_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


# ------------------------------------------
# Log spend for a brand (add a spend log)
# ------------------------------------------
@router.post("/budgets/{brand_id}/spend")
def log_spend(brand_id: int, amount: float, db: Session = Depends(get_db)):
    log = SpendLog(brand_id=brand_id, amount_spent=amount, date=datetime.utcnow())
    db.add(log)
    db.commit()
    return {"message": "Spend logged."}


# ------------------------------------------
# Fetch spend logs (filterable by brand or campaign)
# ------------------------------------------
@router.get("/spend-logs", response_model=List[SpendLogOut])
def get_spend_logs(
    brand_id: int = Query(None),
    campaign_id: int = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(SpendLog)
    if brand_id:
        query = query.filter(SpendLog.brand_id == brand_id)
    if campaign_id:
        query = query.filter(SpendLog.campaign_id == campaign_id)
    logs = query.order_by(SpendLog.date.desc()).all()
    return logs


# ------------------------------------------
# Check budgets for all brands and update campaign statuses
# ------------------------------------------
@router.post("/check-budgets")
def check_budgets(db: Session = Depends(get_db)):
    results = []
    tz = pytz.timezone(Settings.Time_ZONE)
    today = datetime.now(tz).date()
    month_start = today.replace(day=1)

    brands = db.query(Brand).all()

    for brand in brands:
        # Calculate today's and this month's spend
        daily_spend = db.query(func.sum(SpendLog.amount_spent))\
            .filter(SpendLog.brand_id == brand.id, SpendLog.date >= today).scalar() or 0
        monthly_spend = db.query(func.sum(SpendLog.amount_spent))\
            .filter(SpendLog.brand_id == brand.id, SpendLog.date >= month_start).scalar() or 0

        # Get brand budget and campaigns
        budget = db.query(Budget).filter(Budget.brand_id == brand.id).first()
        campaigns = db.query(Campaign).filter(Campaign.brand_id == brand.id).all()

        campaign_updates = []

        # Pause/activate campaigns based on budget usage
        for campaign in campaigns:
            if monthly_spend >= budget.monthly_budget or daily_spend >= budget.daily_budget:
                campaign.status = False
            else:
                campaign.status = True

            campaign_updates.append({
                "campaign_id": campaign.id,
                "campaign_name": campaign.name,
                "status": "active" if campaign.status else "paused"
            })

        db.commit()

        results.append({
            "brand_id": brand.id,
            "brand_name": brand.name,
            "daily_spend": float(daily_spend),
            "daily_budget": float(budget.daily_budget),
            "monthly_spend": float(monthly_spend),
            "monthly_budget": float(budget.monthly_budget),
            "campaigns": campaign_updates
        })

    return {"message": "Budgets checked and campaigns updated.", "data": results}


# ------------------------------------------
# Check budget status for a specific brand
# ------------------------------------------
@router.get("/check-budgets/{brand_id}")
def check_budget_by_brand_id(brand_id: int, db: Session = Depends(get_db)):
    tz = pytz.timezone(Settings.Time_ZONE)
    today = datetime.now(tz).date()
    month_start = today.replace(day=1)

    # Validate brand and budget
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    budget = db.query(Budget).filter(Budget.brand_id == brand.id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found for this brand")

    # Calculate spend totals
    daily_spend = db.query(func.sum(SpendLog.amount_spent))\
        .filter(SpendLog.brand_id == brand.id, SpendLog.date >= today).scalar() or 0
    monthly_spend = db.query(func.sum(SpendLog.amount_spent))\
        .filter(SpendLog.brand_id == brand.id, SpendLog.date >= month_start).scalar() or 0

    # Determine campaign status
    campaigns = db.query(Campaign).filter(Campaign.brand_id == brand.id).all()
    campaign_statuses = []
    for campaign in campaigns:
        status = "paused" if monthly_spend >= budget.monthly_budget or daily_spend >= budget.daily_budget else "active"
        campaign_statuses.append({
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "status": status
        })

    return {
        "brand_id": brand.id,
        "brand_name": brand.name,
        "daily_spend": float(daily_spend),
        "daily_budget": float(budget.daily_budget),
        "monthly_spend": float(monthly_spend),
        "monthly_budget": float(budget.monthly_budget),
        "campaigns": campaign_statuses
    }


# ------------------------------------------
# Reset spend logs for all brands
# ------------------------------------------
@router.post("/reset-budgets")
def reset_budgets(db: Session = Depends(get_db)):
    tz = pytz.timezone(Settings.Time_ZONE)
    today = datetime.now(tz).date()

    # Delete all logs on 1st of the month, else delete older than today
    if today.day == 1:
        db.query(SpendLog).delete()
    else:
        db.query(SpendLog).filter(SpendLog.date < today).delete()

    db.commit()
    return {"message": "Budgets reset."}


# ------------------------------------------
# Reset spend logs for a specific brand
# ------------------------------------------
@router.post("/reset-budgets/{brand_id}")
def reset_budget_by_brand(brand_id: int, db: Session = Depends(get_db)):
    tz = pytz.timezone(Settings.Time_ZONE)
    today = datetime.now(tz).date()

    # Validate brand
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    # Reset budget depending on the date
    if today.day == 1:
        deleted = db.query(SpendLog).filter(SpendLog.brand_id == brand_id).delete(synchronize_session=False)
    else:
        deleted = db.query(SpendLog).filter(
            SpendLog.brand_id == brand_id,
            func.date(SpendLog.date) < today
        ).delete(synchronize_session=False)

    db.commit()
    return {
        "message": f"Budget reset for brand ID {brand_id}.",
        "records_deleted": deleted
    }


# ------------------------------------------
# Enforce dayparting by activating or pausing campaigns
# ------------------------------------------
@router.post("/dayparting/enforce")
def enforce_dayparting(db: Session = Depends(get_db)):
    timezone_str = Settings.Time_ZONE
    tz = pytz.timezone(timezone_str)
    now = datetime.now(tz)
    campaigns = db.query(Campaign).filter(Campaign.start_time != None, Campaign.end_time != None).all()

    for c in campaigns:
        start_time = c.start_time.astimezone(tz).time()
        end_time = c.end_time.astimezone(tz).time()
        current_time = now.time()

        # Handle regular and overnight time windows
        if start_time < end_time:
            c.is_active = start_time <= current_time <= end_time
        else:
            c.is_active = current_time >= start_time or current_time <= end_time

    db.commit()
    return {"message": "Dayparting enforced successfully."}