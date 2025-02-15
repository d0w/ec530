# filepath: /house-management-api/house-management-api/src/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # default values, get overriden by .env
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    app_name: str = "House Management API"
    admin_email: str = "admin@example.com"
    secret_key: str = "your_secret_key"
    # database_url: str = "sqlite:///./test.db"

    class Config:
        env_file = ".env"

settings = Settings()