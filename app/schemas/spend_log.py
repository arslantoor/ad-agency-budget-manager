from typing import Optional

from pydantic import BaseModel
from datetime import date, datetime


class SpendLogCreate(BaseModel):
    brand_id: int
    campaign_id: int
    amount_spent: float
    date: date

class SpendLogOut(BaseModel):
    id: int
    brand_id: int
    campaign_id: Optional[int] = None
    amount_spent: float
    date: datetime

    class Config:
        orm_mode = True