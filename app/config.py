from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Gemini API
    gemini_api_key: str
    
    # Database
    mongodb_url: str
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # File Storage
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"
    max_file_size_mb: int = 50
    
    # System
    system_version: str = "1.0.0"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
