"""
Consolidated monolith-level settings (M4 — Database Consolidation).

This is the single settings object the monolith will use once modules are
wired together (M5/M6). It is NOT yet imported by any module's code —
each app/<module>/core/config.py still defines its own Settings, unused by
this file, left in place until M5/M6 replace per-module config wiring with
this one. Having both exist simultaneously is intentional (anti-destruction
rule): nothing is deleted until the replacement is proven equivalent.
"""
from __future__ import annotations

from typing import List

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    SERVICE_NAME: str = "agrovision-monolith"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Single consolidated database (M4: was 7 databases, one per service).
    # Schema-per-module routing (identity/farm/poultry/inventory/finance/notifications)
    # is applied via search_path at the connection level when modules are wired (M5/M6),
    # not via this URL — see db_consolidation_design.md.
    DATABASE_URL: str = "postgresql+asyncpg://agrovision:agrovision@localhost/agrovision"

    REDIS_URL: str = "redis://:password@localhost:6379/0"

    # JWT: carried over from the gateway, the only component that ever issued/verified
    # tokens for real (audit current_state_architecture_report.md §7). Per-module
    # JWT_SECRET_KEY settings in app/<module>/core/config.py are dead config and will
    # be removed in M7 once this settings object is the one actually in use.
    JWT_SECRET_KEY: str = "changeme"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:80"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",")]
        return v

    @model_validator(mode="after")
    def require_secret_in_production(self) -> "Settings":
        if self.ENVIRONMENT != "development" and self.JWT_SECRET_KEY == "changeme":
            raise ValueError(
                "JWT_SECRET_KEY must be set to a secure value in non-development environments. "
                "Set the JWT_SECRET_KEY environment variable."
            )
        return self


settings = Settings()
