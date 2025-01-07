# app/config.py

from pydantic import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    DATABASE_URL: str  # Add this line

    class Config:
        env_file = ".env"

settings = Settings()
