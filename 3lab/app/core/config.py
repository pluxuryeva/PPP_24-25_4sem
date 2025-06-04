from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database settings
    database_url: str = "sqlite:///./bruteforce.db"
    
    # Используем встроенную асинхронную обработку вместо Celery
    use_async_tasks: bool = True
    
    # Security
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    # Bruteforce settings
    max_password_length: int = 8
    default_charset: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    class Config:
        env_file = ".env"


settings = Settings() 