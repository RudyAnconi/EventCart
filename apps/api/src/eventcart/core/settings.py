from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_log_level: str = "info"
    api_secret_key: str = "change-me"
    api_access_token_expire_minutes: int = 15
    api_refresh_token_expire_days: int = 14
    api_allowed_origins: str = "http://localhost:3000"

    database_url: str
    database_url_sync: str

    worker_poll_interval_seconds: float = 1.5
    worker_max_attempts: int = 8

    seed_demo_email: str = "demo@eventcart.dev"
    seed_demo_password: str = "Demo1234!"

    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.api_allowed_origins.split(",") if origin.strip()]


settings = Settings()
