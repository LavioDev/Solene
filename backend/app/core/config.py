from pathlib import Path
from typing import List, Union
from pydantic import AnyHttpUrl, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Solène"
    API_V1_STR: str = "/api/v1"

    # Server Host & Port
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8200
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:80", "*"]

    # Database Configuration
    USE_SQLITE: bool = False
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_DATABASE: str = "solene"
    DB_USERNAME: str = "postgres"
    DB_PASSWORD: str = "riojen2005"

    # Security & Tokens (Cookie / In-Memory Sanctum pattern)
    SECRET_KEY: str = "solene-super-secret-production-ready-jwt-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis Cache & Pub/Sub
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # MQTT Settings
    MQTT_BROKER_HOST: str = "127.0.0.1"
    MQTT_BROKER_PORT: int = 1883
    MQTT_TELEMETRY_TOPIC: str = "v1/devices/me/telemetry"

    # Upstream Main Server
    MAIN_SERVER_ENABLED: bool = False
    MAIN_SERVER_URL: str = "http://localhost:8000"
    MAIN_SERVER_API_KEY: str = ""
    MAIN_SERVER_JWT_TOKEN: str = ""

    # AI Module Toggle
    ENABLE_AI_MODULE: bool = False

    @computed_field
    def async_database_url(self) -> str:
        if self.USE_SQLITE:
            sqlite_path = BASE_DIR / "solene.db"
            return f"sqlite+aiosqlite:///{sqlite_path}"
        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    @computed_field
    def sync_database_url(self) -> str:
        if self.USE_SQLITE:
            sqlite_path = BASE_DIR / "solene.db"
            return f"sqlite:///{sqlite_path}"
        return f"postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    @computed_field
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
