# backend/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # загружаем .env

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 30

    # YouTube
    YOUTUBE_API_KEY: str

    # AI (пока не обязательны, но для структуры)
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    POLLINATIONS_API_KEY: str = ""

    # ЮKassa
    YOOKASSA_SHOP_ID: str = ""
    YOOKASSA_SECRET_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"  # игнорируем лишние переменные

settings = Settings()