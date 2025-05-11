from sqlalchemy import Column, String, Integer, Boolean,DateTime, ForeignKey, Time
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float
from app.db.base import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    is_active = Column(Boolean, default=True)
    start_time = Column(DateTime(timezone=True))  # Timezone-aware datetime for start time
    end_time = Column(DateTime(timezone=True))    # Timezone-aware datetime for end time
    estimated_hourly_spend = Column(Float, default=100)  # in your models.py
    brand = relationship("Brand", back_populates="campaigns")
    spend_logs = relationship("SpendLog", back_populates="campaign")