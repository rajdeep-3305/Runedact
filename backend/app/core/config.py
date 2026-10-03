from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Runedact"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./runedact.db"

    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "auto"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    OPENAI_MODEL: str = "gpt-4o-mini"

    SANDBOX_TIMEOUT_SECONDS: int = 2
    SANDBOX_MEMORY_LIMIT_MB: int = 64
    SANDBOX_MAX_PROCESSES: int = 1
    SANDBOX_MODE: str = "process"  # process | docker
    SANDBOX_DOCKER_IMAGE: str = "python:3.12-alpine"
    SANDBOX_DISABLE_NETWORK: bool = True

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    API_AUTH_ENABLED: bool = False
    API_KEY: Optional[str] = None
    RATE_LIMIT_PER_MINUTE: int = 120

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
