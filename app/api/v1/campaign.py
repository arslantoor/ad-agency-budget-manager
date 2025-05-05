from fastapi import APIRouter, HTTPException, Depends,BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.campaign import CampaignCreate, CampaignOut
from app.db.session import get_db
from app.models import Campaign, Brand
from app.task.campaign_task import simulate_campaign_run

router = APIRouter()

@router.post("/", response_model=CampaignOut)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == campaign.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    new_campaign = Campaign(**campaign.dict())
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    return new_campaign

@router.get("/")
def list_campaigns(db: Session = Depends(get_db)):
    return db.query(Campaign).all()

@router.patch("/{id}/toggle")
def toggle_campaign(id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).get(id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.status = not campaign.status
    db.commit()
    return {"status": campaign.status}

@router.post("/simulate-hour/")
def run_simulation(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(simulate_campaign_run, db)
    return {"message": "Spend simulation started in background."}