# app/schemas.py

from pydantic import BaseModel
from typing import List, Optional

class ProductURLBase(BaseModel):
    domain: str
    url: str

class ProductURLCreate(ProductURLBase):
    is_valid: Optional[bool] = False

class ProductURLOut(ProductURLBase):
    is_valid: bool
    scraped_at: datetime

    class Config:
        orm_mode = True
