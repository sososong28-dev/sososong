from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "wdt-fastapi"
    app_env: str = "dev"
    app_debug: bool = True
    database_url: str = "sqlite:///./wdt_fastapi.db"

    wdt_base_url: str = "https://example-wdt-gateway"
    wdt_app_key: str = "replace_me"
    wdt_app_secret: str = "replace_me"
    wdt_format: str = "json"
    wdt_version: str = "1.0"
    wdt_timeout_seconds: int = 10

    model_config = SettingsConfigDict(
        env_file=("wdt_fastapi/.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
