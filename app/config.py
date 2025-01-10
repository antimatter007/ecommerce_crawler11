# app/config.py

class Settings:
    # Database Configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "dCQIJcrivbBKaqIBmEExwVrCcYhurtWl"
    POSTGRES_DB: str = "railway"
    POSTGRES_HOST: str = "junction.proxy.rlwy.net"
    POSTGRES_PORT: int = 38132
    
    # Redis Configuration
    REDIS_HOST: str = "viaduct.proxy.rlwy.net"
    REDIS_PORT: int = 11471
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://default:tbLFXmaqfWGHvbXrJELyyTWKbWsrGODH@viaduct.proxy.rlwy.net:11471/0"
    CELERY_RESULT_BACKEND: str = "redis://default:tbLFXmaqfWGHvbXrJELyyTWKbWsrGODH@viaduct.proxy.rlwy.net:11471/0"
    
    # API Keys
    SCRAPERAPI_KEY: str = "a808071ccff9da6df8e44950f64246c8"
    
    # Database URL
    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

settings = Settings()
