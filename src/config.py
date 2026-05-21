from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Swiss Regulatory Advisor"
    environment: str = "local"
    openai_api_key: str | None = None
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "swiss_regulatory_documents"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
