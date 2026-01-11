"""
Application configuration management.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # Application
    APP_NAME = os.getenv("APP_NAME", "Flow - Cross-Border FX Payment Platform")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql://flow_user:flow_password@localhost:5432/flow_db"
    )

    # Session
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))

    # FX Provider
    FX_PROVIDER_API_KEY = os.getenv("FX_PROVIDER_API_KEY", "")
    FX_PROVIDER_API_URL = os.getenv("FX_PROVIDER_API_URL", "")
    FX_MARKUP_PERCENTAGE = float(os.getenv("FX_MARKUP_PERCENTAGE", "0.005"))

    # Payment Provider
    PAYMENT_PROVIDER_API_KEY = os.getenv("PAYMENT_PROVIDER_API_KEY", "")
    PAYMENT_PROVIDER_API_URL = os.getenv("PAYMENT_PROVIDER_API_URL", "")

    # Email
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "noreply@flow-payments.com")


config = Config()
