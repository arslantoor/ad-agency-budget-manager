from pydantic import BaseModel

class BudgetCreate(BaseModel):
    brand_id: int
    daily_budget: int
    monthly_budget: int

class BudgetOut(BaseModel):
    id: int
    brand_id: int
    daily_budget: int
    monthly_budget: int

    class Config:
        orm_mode = True