from pydantic import BaseModel
from datetime import date

class SpendLogCreate(BaseModel):
    brand_id: int
    amount_spent: int
    date: date

class SpendLogOut(BaseModel):
    id: int
    brand_id: int
    amount_spent: int
    date: date

    class Config:
        orm_mode = True