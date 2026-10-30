from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Intermarket Analysis Terminal"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/intermarket"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/intermarket"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300  # 5 minutes
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Data Sources
    FRED_API_KEY: Optional[str] = None
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    # Calculation Settings
    DEFAULT_CORR_WINDOWS: list[int] = [20, 60, 250]
    ANOMALY_Z_THRESHOLD: float = 2.0
    COINT_P_VALUE_THRESHOLD: float = 0.05
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
