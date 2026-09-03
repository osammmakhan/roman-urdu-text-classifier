from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./urdu_classifier.db"
    
    # Groq
    groq_api_key: Optional[str] = None
    groq_model: str = "llama3-8b-8192"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Classification
    classification_labels: list[str] = ["positive", "negative", "neutral"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()