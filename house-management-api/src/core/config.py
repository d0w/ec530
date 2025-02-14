# filepath: /house-management-api/house-management-api/src/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "House Management API"
    admin_email: str = "admin@example.com"
    # database_url: str = "sqlite:///./test.db"

    class Config:
        env_file = ".env"

settings = Settings()