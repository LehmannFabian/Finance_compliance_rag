import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    ENV: str = "development"
    PROJECT_NAME: str = "Swiss Regulatory Advisor"

    # Gemini Configuration (Updated for the free tier)
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"  # Free tier eligible, fast and powerful

    # Qdrant Vector DB Configuration
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    COLLECTION_NAME: str = "swiss_compliance_documents"

    # Automatic lookup for a .env file in the root directory
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"  # Ignores additional env variables not defined here
    )


# Instantiate settings to be imported across the application
settings = Settings()