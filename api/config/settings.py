from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Environment and Debugging
    ENV: str = os.environ.get("ENV", "development")
    DEBUG: bool = ENV == "development"
    TESTING: bool = ENV == "testing"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-key-please-change")
    
    # Logging Configuration
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "app.log"
    
    # Stripe Configuration
    STRIPE_SECRET_KEY: str = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    SRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY")
    
    # Test Cardholder Configuration
    TEST_CARDHOLDER_ID: str = os.environ.get("TEST_CARDHOLDER_ID", "")
    TEST_CARDHOLDER_NAME: str = os.environ.get("TEST_CARDHOLDER_NAME", "Jack Casey")
    TEST_CARDHOLDER_EMAIL: str = os.environ.get("TEST_CARDHOLDER_EMAIL", "jackcasey614@gmail.com")
    TEST_CARDHOLDER_PHONE: str = os.environ.get("TEST_CARDHOLDER_PHONE", "+353858839191")
    TEST_CARDHOLDER_ADDRESS: str = os.environ.get("TEST_CARDHOLDER_ADDRESS", "123 Main St")
    TEST_CARDHOLDER_CITY: str = os.environ.get("TEST_CARDHOLDER_CITY", "Dunboyne")
    TEST_CARDHOLDER_STATE: str = os.environ.get("TEST_CARDHOLDER_STATE", "Meath")
    TEST_CARDHOLDER_POSTAL: str = os.environ.get("TEST_CARDHOLDER_POSTAL", "A86D586")
    TEST_CARDHOLDER_COUNTRY: str = os.environ.get("TEST_CARDHOLDER_COUNTRY", "IE")
    
    class Config:
        env_file = "/home/surtr/Team-3/api/.env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
