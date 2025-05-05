from pydantic import BaseModel


class BudgetCreate(BaseModel):
    brand_id: int
    daily_budget: float
    monthly_budget: float
