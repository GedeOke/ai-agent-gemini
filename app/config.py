from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Agent Backend"
    api_key: str = Field(default="", description="Shared header secret for internal calls")
    gemini_api_key: str = Field(default="", description="API key for Gemini access")
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    log_level: str = "INFO"
    debug: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
