"""Application configuration settings."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    gemini_api_key: str = ""
    apify_api_key: str = ""
    tavily_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    
    # LLM Configuration
    llm_provider: str = "google"
    llm_model: str = "gemini-2.5-flash"
    llm_temperature: float = 0.6
    
    # Database
    database_path: str = "data/user_profiles/profiles.db"
    
    # Application
    app_title: str = "LinkedIn Profile Optimizer"
    debug: bool = False
    
    # Paths
    project_root: Path = Path(__file__).parent.parent.parent
    data_dir: Path = project_root / "data"
    profiles_dir: Path = data_dir / "user_profiles"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from environment


# Global settings instance
settings = Settings()