from pydantic import BaseModel
from typing import Optional
from datetime import time

class CampaignCreate(BaseModel):
    name: str
    brand_id: int
    start_time: Optional[time]
    end_time: Optional[time]

class CampaignOut(BaseModel):
    id: int
    name: str
    brand_id: int
    is_active: bool
    start_time: Optional[time]
    end_time: Optional[time]

    class Config:
        orm_mode = True