from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.campaign import CampaignCreate, CampaignOut
from app.db.session import get_db
from app.models import Campaign, Brand, Budget
from app.task.campaign_task import simulate_campaign_run
from pytz import timezone as tz
import pytz

router = APIRouter()

# ----------------------------------------
# Create a new campaign
# ----------------------------------------
@router.post("/", response_model=CampaignOut)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == campaign.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    budget = db.query(Budget).filter(Budget.brand_id == campaign.brand_id).first()
    if not budget:
        raise HTTPException(status_code=400, detail="Budget not found for this brand")

    # Convert local times to UTC using user's timezone
    user_tz = tz(campaign.timezone or "UTC")

    start_time_utc = campaign.start_time.astimezone(pytz.UTC) if campaign.start_time else None
    end_time_utc = campaign.end_time.astimezone(pytz.UTC) if campaign.end_time else None

    new_campaign = Campaign(
        name=campaign.name,
        brand_id=campaign.brand_id,
        start_time=start_time_utc,
        end_time=end_time_utc,
    )

    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    return new_campaign


# ----------------------------------------
# List all campaigns
# ----------------------------------------
@router.get("/")
def list_campaigns(db: Session = Depends(get_db)):
    # Fetch and return all campaigns
    return db.query(Campaign).all()

# ----------------------------------------
# Toggle a campaign's active status
# ----------------------------------------
@router.patch("/{id}/toggle")
def toggle_campaign(id: int, db: Session = Depends(get_db)):
    # Fetch the campaign by ID
    campaign = db.query(Campaign).get(id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Toggle its status
    campaign.is_active = not campaign.is_active
    db.commit()
    return {"status": campaign.is_active}

# ----------------------------------------
# Simulate campaign spend for the past hour (background task)
# ----------------------------------------
@router.post("/simulate-hour/")
def run_simulation():
    # Enqueue the simulation task (async)
    simulate_campaign_run.delay()
    return {"message": "Spend simulation started in background."}