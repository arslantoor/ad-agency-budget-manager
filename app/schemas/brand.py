from pydantic import BaseModel

class BrandCreate(BaseModel):
    name: str

class BrandOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True