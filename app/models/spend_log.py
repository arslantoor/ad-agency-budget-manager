from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

now = datetime.now(timezone.utc)

class SpendLog(Base):
    __tablename__ = "spend_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False) # new added
    amount_spent = Column(Integer)
    date = Column(DateTime(timezone=True), default=func.now())

    brand = relationship("Brand", back_populates="spend_logs")
    campaign = relationship("Campaign", back_populates="spend_logs")