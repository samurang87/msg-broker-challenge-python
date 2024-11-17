from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    APP_NAME: str = "broker"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    WORKERS: int = 1
    LOG_LEVEL: str = "info"

    # Application specific settings
    STORAGE_PATH: str | None = None
    MAX_MESSAGE_SIZE: int = 1024 * 1024  # 1MB

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
