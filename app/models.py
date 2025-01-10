# app/models.py
from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class ProductURL(Base):
    __tablename__ = "product_urls"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    title = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    model_name = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    star_rating = Column(Float, nullable=True)
    no_rating = Column(Integer, nullable=True)
    colour = Column(String, nullable=True)
    storage_cap = Column(String, nullable=True)
    img_url = Column(String, nullable=True)
