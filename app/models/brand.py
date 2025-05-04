from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    campaigns = relationship("Campaign", back_populates="brand")
    budgets = relationship("Budget", back_populates="brand")
    spend_logs = relationship("SpendLog", back_populates="brand")