from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = {'extend_existing': True}  # This line fixes the error

    id = Column(Integer, primary_key=True,autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    daily_budget = Column(Integer)
    monthly_budget = Column(Integer)

    brand = relationship("Brand", back_populates="budgets")