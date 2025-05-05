from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base

class Brand(Base):
    __tablename__ = "brands"
    __table_args__ = {'extend_existing': True}  # This line fixes the error

    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String, unique=True)

    campaigns = relationship("Campaign", back_populates="brand")
    budgets = relationship("Budget", back_populates="brand")
    spend_logs = relationship("SpendLog", back_populates="brand")