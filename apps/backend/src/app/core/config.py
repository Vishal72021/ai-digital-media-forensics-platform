"""Application configuration for the Sentinel AI backend."""

from functools import lru_cache

from pydantic import PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str

    password_hash_time_cost: PositiveInt = 3
    password_hash_memory_cost: PositiveInt = 65536
    password_hash_parallelism: PositiveInt = 4
    password_hash_hash_len: PositiveInt = 32
    password_hash_salt_len: PositiveInt = 16


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings.

    Returns:
        The singleton application settings instance.
    """
    return Settings()
