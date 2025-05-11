from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CampaignCreate(BaseModel):
    name: str
    brand_id: int
    start_time: Optional[datetime] = Field(None, description="Timezone-aware start datetime")
    end_time: Optional[datetime] = Field(None, description="Timezone-aware end datetime")

class CampaignOut(BaseModel):
    id: int
    name: str
    brand_id: int
    is_active: bool
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    class Config:
        orm_mode = True