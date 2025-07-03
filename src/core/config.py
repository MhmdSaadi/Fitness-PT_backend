from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database - Using SQLite for development without Docker
    DATABASE_URL: str = "sqlite+aiosqlite:///./footfit.db"
    
    # Redis - Using in-memory for development
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    JWT_SECRET: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # Email
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # App
    APP_NAME: str = "HBT FootFit"
    DOMAIN: str = "localhost:3000"
    
    class Config:
        env_file = ".env"

settings = Settings()