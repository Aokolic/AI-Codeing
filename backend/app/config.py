"""Application configuration via environment variables."""
from __future__ import annotations

import json
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "sqlite+aiosqlite:///./post_truth.db"

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Admin credentials (for MVP single-admin setup)
    admin_username: str = "admin"
    admin_password: str = "changeme123"

    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v

    # NLP
    nlp_model_name: str = "shibing624/text2vec-base-chinese"
    nlp_similarity_threshold: float = 0.82
    nlp_time_window_hours: int = 48

    # Case classification
    case_similarity_threshold: float = 0.45
    case_entity_overlap_threshold: float = 0.3

    # Logging
    log_level: str = "INFO"

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
