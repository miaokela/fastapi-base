import os
from typing import Any, Dict, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用程序配置"""
    
    # 应用基本信息
    APP_NAME: str = "FastAPI Base"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite://./db.sqlite3"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-please-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 管理员配置
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"
    
    # CORS配置
    ALLOWED_HOSTS: list = ["*"]
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
    ]
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()