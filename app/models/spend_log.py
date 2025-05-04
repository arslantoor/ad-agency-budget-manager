from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.base import Base

class SpendLog(Base):
    __tablename__ = "spend_logs"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    amount_spent = Column(Integer)
    date = Column(Date)

    brand = relationship("Brand", back_populates="spend_logs")