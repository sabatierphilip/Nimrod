from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "Nimrod AI Trading Assistant"
    cors_origins: str = "http://localhost:3000"
    alpha_vantage_api_key: str = ""
    finnhub_api_key: str = ""
    fmp_api_key: str = ""
    news_api_key: str = ""
    groq_model: str = "llama-3.1-70b-versatile"
    cache_ttl_seconds: int = 300

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
