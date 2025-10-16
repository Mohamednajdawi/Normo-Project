from functools import lru_cache
from typing import Literal, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: Literal["development", "staging", "production"] = "development"
    openai_api_key: Optional[str] = None
    log_level: Literal["debug", "info", "warning", "error", "critical"] = "info"

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
