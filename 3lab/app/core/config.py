from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database settings
    database_url: str = "sqlite:///./bruteforce.db"
    
    # Celery settings
    celery_broker_url: str = "redislite://bruteforce.rdb"
    celery_result_backend: str = "redislite://bruteforce.rdb"
    
    # Security
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    # Bruteforce settings
    max_password_length: int = 8
    default_charset: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    class Config:
        env_file = ".env"


settings = Settings() 