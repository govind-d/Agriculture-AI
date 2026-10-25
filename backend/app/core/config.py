"""
Application configuration — reads from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Global application settings loaded from environment variables."""

    # App
    APP_NAME: str = "AI Smart Agriculture Guardian"
    DEBUG: bool = False

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "agriguardian"

    # JWT
    JWT_SECRET: str = "change-me-in-production-use-a-strong-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # OpenWeatherMap
    OPENWEATHER_API_KEY: str = ""

    # Google Gemini — each model has its own free-tier daily quota, so switching
    # models here (no code change) is the quickest way around an exhausted quota
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash"
    # Tried in order when the model above runs out of free quota for the day
    GEMINI_FALLBACK_MODELS: str = (
        "gemini-3.5-flash-lite,gemini-3.1-flash-lite,gemini-3.7-flash,"
        "gemini-3.8-flash,gemini-3-flash-preview"
    )


    # Firebase Cloud Messaging
    FCM_SERVER_KEY: str = ""

    # SMTP Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "https://*.vercel.app",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
