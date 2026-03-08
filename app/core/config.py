from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(alias="APP_ENV")
    database_url_asyncpg: str = Field(alias="DATABASE_URL_ASYNCPG")
    redis_url: str = Field(alias="REDIS_URL")
    allowed_origins: str = Field(alias="ALLOWED_ORIGINS")
    ollama_base_url: str = Field(alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(alias="OLLAMA_MODEL")
    ollama_timeout_seconds: int = Field(alias="OLLAMA_TIMEOUT_SECONDS")
    anthropic_api_key: str = Field(alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(alias="ANTHROPIC_MODEL")
    anthropic_timeout_seconds: int = Field(alias="ANTHROPIC_TIMEOUT_SECONDS")
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_model: str = Field(alias="OPENAI_MODEL")
    openai_timeout_seconds: int = Field(alias="OPENAI_TIMEOUT_SECONDS")
    postal_webhook_secret: str = Field(alias="POSTAL_WEBHOOK_SECRET")
    fbr_click_webhook_secret: str = Field(alias="FBR_CLICK_WEBHOOK_SECRET")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
