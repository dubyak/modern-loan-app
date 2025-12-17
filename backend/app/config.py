"""
Application configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Modern Loan App API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_ANON_KEY: str

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_ASSISTANT_ID: str = ""  # Will be created on first run if empty
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # OTP
    OTP_LENGTH: int = 6
    OTP_EXPIRY_MINUTES: int = 5

    # Loans
    DEFAULT_INTEREST_RATE: float = 15.0  # 15% per month
    MIN_LOAN_AMOUNT: float = 1000.0
    MAX_LOAN_AMOUNT: float = 50000.0
    DEFAULT_LOAN_TENURE_DAYS: int = 30

    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/jpg",
        "application/pdf"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
