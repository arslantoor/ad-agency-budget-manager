from fastapi import FastAPI
from app.api.v1 import (
    brand,
    budget,
    campaign
)
from app.db.session import engine
from app.db.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ad Agency Budget Manager",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

api_v1_prefix = "/api/v1"
app.include_router(brand.router, prefix=api_v1_prefix + "/brands", tags=["Brands"])
app.include_router(campaign.router, prefix=api_v1_prefix + "/campaigns", tags=["Campaigns"])
app.include_router(budget.router, prefix=api_v1_prefix + "/budgets", tags=["Budgets"])
# app.include_router(spend_log.router, prefix=api_v1_prefix + "/spend-logs", tags=["Spend Logs"])