from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Time, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database  import Base

class BudgetType(str, enum.Enum):
    DAILY = "daily"
    MONTHLY = "monthly"

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    budgets = relationship("Budget", back_populates="brand", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="brand")

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    type = Column(Enum(BudgetType), nullable=False)
    limit = Column(Float, nullable=False)
    reset_at = Column(DateTime, default=datetime.utcnow)
    brand = relationship("Brand", back_populates="budgets")

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    start_at = Column(Time)
    end_at = Column(Time)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    brand = relationship("Brand", back_populates="campaigns")

class SpendLog(Base):
    __tablename__ = "spend_logs"
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer)
    campaign_id = Column(Integer)
    amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)