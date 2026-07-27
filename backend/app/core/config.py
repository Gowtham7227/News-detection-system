import os
from typing import List, Union
from pydantic import AnyHttpUrl, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


def parse_cors_origins(v: Union[str, List[str]]) -> List[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
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

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgrespassword"
    POSTGRES_DB: str = "fakenewsdb"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # ML Config
    MODEL_TYPE: str = "transformer"
    MODEL_PATH: str = "/app/model/artifacts/fake_news_bert_v1"
    MAX_SEQUENCE_LENGTH: int = 512
    CONFIDENCE_THRESHOLD: float = 0.75

    # File Storage Settings
    MAX_UPLOAD_SIZE_MB: int = 5
    UPLOAD_DIR: str = "/app/uploads"
    ALLOWED_EXTENSIONS: List[str] = ["txt", "pdf", "docx"]


settings = Settings()
