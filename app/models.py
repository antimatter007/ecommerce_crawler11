# app/models.py

from sqlalchemy import Column, Integer, String, Boolean, Text
from app.database import Base

class ProductURL(Base):
    __tablename__ = "product_urls"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), index=True, nullable=False)
    url = Column(Text, unique=True, nullable=False)
    is_valid = Column(Boolean, default=True)
    title = Column(Text, nullable=True)
    brand = Column(String(255), nullable=True)
    model_name = Column(String(255), nullable=True)
    price = Column(String(50), nullable=True)
    star_rating = Column(String(50), nullable=True)
    no_rating = Column(String(50), nullable=True)
    colour = Column(String(50), nullable=True)
    storage_cap = Column(String(50), nullable=True)
    img_url = Column(Text, nullable=True)
