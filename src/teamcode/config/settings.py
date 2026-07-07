from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class TeamCodeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    mistral_api_key: str | None = None
    deepseek_api_key: str | None = None
    openrouter_api_key: str | None = None

    log_level: str = "INFO"
    default_model: str = "gpt-4o"

    @property
    def available_providers(self) -> dict[str, str | None]:
        return {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "gemini": self.gemini_api_key,
            "groq": self.groq_api_key,
            "mistral": self.mistral_api_key,
            "deepseek": self.deepseek_api_key,
            "openrouter": self.openrouter_api_key,
        }
