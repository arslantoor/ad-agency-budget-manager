from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.brand import BrandCreate, BrandOut
from app.models import brand as models
from app.db.session import get_db

router = APIRouter()



@router.post("/", response_model=BrandOut)
def create_brand(brand: BrandCreate, db: Session = Depends(get_db)):
    db_brand = models.Brand(**brand.dict())
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

@router.get("/", response_model=list[BrandOut])
def list_brands(db: Session = Depends(get_db)):
    return db.query(models.Brand).all()