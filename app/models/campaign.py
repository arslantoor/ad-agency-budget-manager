from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.db.base import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    is_active = Column(Boolean, default=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)

    brand = relationship("Brand", back_populates="campaigns")