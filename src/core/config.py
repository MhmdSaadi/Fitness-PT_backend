# TEMPLATE: Customize this file for your own project. Replace all {{...}} placeholders.
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database - Using SQLite for development without Docker
    DATABASE_URL: str = "sqlite+aiosqlite:///./{{project_name}}.db"  # TODO: Replace with your database URL
    
    # Redis - Using in-memory for development
    REDIS_URL: str = "redis://localhost:6379/0"  # TODO: Replace with your Redis URL
    
    # JWT
    JWT_SECRET: str = "your-super-secret-jwt-key-change-this-in-production"  # TODO: Set a secure secret
    JWT_ALGORITHM: str = "HS256"
    
    # Email
    SMTP_USERNAME: Optional[str] = None  # TODO: Set your SMTP username
    SMTP_PASSWORD: Optional[str] = None  # TODO: Set your SMTP password
    
    # App
    APP_NAME: str = "{{app_name}}"  # TODO: Replace with your app name
    DOMAIN: str = "{{domain}}"  # TODO: Replace with your domain
    
    class Config:
        env_file = ".env"

settings = Settings()