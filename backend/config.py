"""
Configuration module for FlyerFlutter application.
Loads environment variables and defines application settings.
"""

import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Google API Configuration
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./flyers.db")
    
    # Flipp API Configuration
    FLIPP_BASE_URL: str = os.getenv("FLIPP_BASE_URL", "https://backflipp.wishabi.com/flipp")
    
    # Application Configuration
    APP_NAME: str = "FlyerFlutter"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS Configuration
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # API Rate Limiting
    GOOGLE_API_RATE_LIMIT: int = int(os.getenv("GOOGLE_API_RATE_LIMIT", "10"))  # requests per second
    FLIPP_API_RATE_LIMIT: int = int(os.getenv("FLIPP_API_RATE_LIMIT", "5"))  # requests per second
    
    # Scheduler Configuration
    FLYER_UPDATE_HOUR: int = int(os.getenv("FLYER_UPDATE_HOUR", "6"))  # 6 AM
    FLYER_UPDATE_DAY: str = os.getenv("FLYER_UPDATE_DAY", "thursday")
    
    # Validation
    def __post_init__(self):
        """Validate critical configuration settings."""
        if not self.GOOGLE_API_KEY and not self.DEBUG:
            raise ValueError("GOOGLE_API_KEY is required for production")


# Global settings instance
settings = Settings()