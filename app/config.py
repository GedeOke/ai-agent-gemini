from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Agent Backend"
    api_key: str = Field(default="", description="Shared header secret for internal calls")
    gemini_api_key: str = Field(default="", description="API key for Gemini access")
    cors_origins: list[str] | str = Field(default="*")
    log_level: str = "INFO"
    debug: bool = False
    database_url: str = Field(
        default="sqlite+aiosqlite:///./local.db",
        description="Async DB URL. Use Postgres e.g. postgresql+asyncpg://user:pass@host/db",
    )
    auto_create_tables: bool = True
    followup_poll_interval_seconds: int = Field(default=15, description="Scheduler polling interval for follow-ups")
    embedding_provider: str = Field(default="gemini", description="gemini|local")
    embedding_model_name: str = Field(
        default="models/embedding-001",
        description="Gemini model name or local sentence-transformers model id",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: str | list[str] | None) -> list[str]:
        if value is None:
            return ["*"]
        if isinstance(value, str):
            val = value.strip()
            if not val:
                return ["*"]
            # Support simple list strings like '["*"]' or comma-separated
            if val.startswith("[") and val.endswith("]"):
                val = val.strip("[]")
            return [origin.strip().strip('"').strip("'") for origin in val.split(",") if origin.strip()]
        return value


settings = Settings()
