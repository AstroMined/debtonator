from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    # App settings
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    # Database settings
    DATABASE_URL: str

    # Security settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # CORS settings
    CORS_ORIGINS: str  # Comma-separated list of origins

    # Optional API keys for future integrations
    BANKING_API_KEY: Optional[str] = None

    @property
    def cors_origin_list(self) -> list[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
