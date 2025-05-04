from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.model import BudgetType
from app.database import SessionLocal
import crud

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/spend/")
def spend(brand_id: int, campaign_id: int, amount: float, db: Session = Depends(get_db)):
    crud.add_spend(db, brand_id, campaign_id, amount)
    return {"message": "Spend logged and budget checked"}

@app.post("/reset/daily")
def reset_daily(db: Session = Depends(get_db)):
    crud.reset_budgets(db, BudgetType.DAILY)
    return {"message": "Daily budgets reset"}

@app.post("/reset/monthly")
def reset_monthly(db: Session = Depends(get_db)):
    crud.reset_budgets(db, BudgetType.MONTHLY)
    return {"message": "Monthly budgets reset"}