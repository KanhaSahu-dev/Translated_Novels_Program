import os
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "sqlite:///./novels.db"
    
    # API Configuration
    api_title: str = "Novel Translation Refiner"
    api_version: str = "1.0.0"
    api_description: str = "API for extracting and refining machine-translated novel text"
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:4200", "http://127.0.0.1:4200"]
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Scraping Configuration
    scraping_delay: float = 1.0  # Delay between requests in seconds
    max_retries: int = 3
    request_timeout: int = 30
    
    # NLP Configuration
    max_text_length: int = 50000  # Maximum text length for processing
    batch_size: int = 10  # Chapters to process in batch
    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings() 