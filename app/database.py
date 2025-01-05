# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

Base = declarative_base()

DATABASE_URL = settings.DATABASE_URL  # Ensure this is correctly set in config.py

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from app.models import ProductURL  # Import models to register with SQLAlchemy
    Base.metadata.create_all(bind=engine)
