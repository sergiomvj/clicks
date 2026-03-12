from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    app_domain: str = Field(default="localhost", alias="APP_DOMAIN")
    database_url_asyncpg: str = Field(alias="DATABASE_URL_ASYNCPG")
    redis_url: str = Field(alias="REDIS_URL")
    allowed_origins: str = Field(default="http://localhost:3000", alias="ALLOWED_ORIGINS")
    session_secret: str = Field(alias="SESSION_SECRET")
    jwt_secret: str = Field(alias="JWT_SECRET")
    openclaw_agent_jwt_secret: str = Field(alias="OPENCLAW_AGENT_JWT_SECRET")
    openclaw_gateway_url: str = Field(alias="OPENCLAW_GATEWAY_URL")
    fbr_leads_webhook_secret: str = Field(alias="FBR_LEADS_WEBHOOK_SECRET")
    fbr_dev_webhook_secret: str = Field(alias="FBR_DEV_WEBHOOK_SECRET")
    fbr_suporte_webhook_secret: str = Field(alias="FBR_SUPORTE_WEBHOOK_SECRET")
    fbr_leads_api_url: str = Field(default="", alias="FBR_LEADS_API_URL")
    fbr_dev_api_url: str = Field(default="", alias="FBR_DEV_API_URL")
    fbr_suporte_api_url: str = Field(default="", alias="FBR_SUPORTE_API_URL")
    ollama_base_url: str = Field(default="", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="", alias="OLLAMA_MODEL")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="", alias="ANTHROPIC_MODEL")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="", alias="OPENAI_MODEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
