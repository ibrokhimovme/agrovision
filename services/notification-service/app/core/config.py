from __future__ import annotations

from typing import List

from pydantic import AnyHttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    SERVICE_NAME: str = "notification-service"
    PORT: int = 8006
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://agrovision:agrovision@localhost/notification_db"

    # Redis
    REDIS_URL: str = "redis://:password@localhost:6379/0"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://agrovision:agrovision@localhost:5672/agrovision"

    # JWT (public key / secret for token verification)
    JWT_SECRET_KEY: str = "changeme"
    JWT_ALGORITHM: str = "HS256"

    # CORS
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
