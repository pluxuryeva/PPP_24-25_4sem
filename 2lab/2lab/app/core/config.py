from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "BruteForce API"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "ваш_секретный_ключ_здесь"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"


settings = Settings() 