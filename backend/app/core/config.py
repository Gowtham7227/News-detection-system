import os
from typing import List, Union, Optional
from pydantic import AnyHttpUrl, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


def parse_cors_origins(v: Union[str, List[str]]) -> List[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, (list, str)):
        import json
        try:
            return json.loads(v) if isinstance(v, str) else v
        except Exception:
            return []
    return v


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

    PROJECT_NAME: str = "Fake News Detection System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "supersecretkeyreplaceinproduction1234567890!@#"

    # CORS Config
    BACKEND_CORS_ORIGINS: Annotated[
        List[str], BeforeValidator(parse_cors_origins)
    ] = []

    # --- Database ---
    # Render injects DATABASE_URL directly for Postgres addons.
    # Falls back to SQLite if not set (good for free-tier / demo deployments).
    DATABASE_URL: Optional[str] = None

    # Legacy Postgres fields (used only when DATABASE_URL is not set)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgrespassword"
    POSTGRES_DB: str = "fakenewsdb"
    POSTGRES_PORT: int = 5432

    @property
    def EFFECTIVE_DATABASE_URL(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Default to SQLite for zero-config deployments
        return "sqlite:///./fakenews.db"

    # Redis Settings (optional — only needed if Celery is used)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # ML Config
    MODEL_TYPE: str = "tfidf"
    MODEL_PATH: str = "/app/model/artifacts"
    MAX_SEQUENCE_LENGTH: int = 512
    CONFIDENCE_THRESHOLD: float = 0.75

    # File Storage Settings
    MAX_UPLOAD_SIZE_MB: int = 5
    UPLOAD_DIR: str = "/data/uploads"
    ALLOWED_EXTENSIONS: List[str] = ["txt", "pdf", "docx"]


settings = Settings()
