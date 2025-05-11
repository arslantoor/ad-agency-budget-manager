from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.brand import BrandCreate, BrandOut
from app.models import brand as models
from app.db.session import get_db

router = APIRouter()

# POST / - Create a new brand
# Accepts brand data from the request body, creates a new Brand record in the database,
# commits the changes, and returns the created brand as a response.
@router.post("/", response_model=BrandOut)
def create_brand(brand: BrandCreate, db: Session = Depends(get_db)):
    db_brand = models.Brand(**brand.dict())  # Convert Pydantic model to ORM model
    db.add(db_brand)                         # Add brand to the session
    db.commit()                              # Commit the transaction
    db.refresh(db_brand)                     # Refresh instance to reflect DB state
    return db_brand

# GET / - Retrieve a list of all brands
# Queries the database for all existing Brand records and returns them in the response.
@router.get("/", response_model=list[BrandOut])
def list_brands(db: Session = Depends(get_db)):
    return db.query(models.Brand).all()  # Fetch all brand entries from the database
