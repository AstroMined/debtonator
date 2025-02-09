from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./debtonator.db"
    
    # Application
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    APP_NAME: str = "Debtonator"
    APP_VERSION: str = "0.1.0"
    DESCRIPTION: str = "Bill & Cashflow Management System"
    
    # Security
    SECRET_KEY: str = "VeN37vbQTHWVhqIhptGn2MR27dfceaVtoFDS2qJcbPE"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # CORS
    CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:8000"

    @property
    def cors_origins(self) -> List[str]:
        """Get list of CORS origins"""
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",") if origin.strip()]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"  # Allow extra fields from environment variables
    )

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()

# Create settings instance
settings = get_settings()
