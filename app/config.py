from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FINTECH AI Backend"
    database_url: str = "sqlite:///./aura.db"
    frontend_origins: str = "http://localhost:3000"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "gemma4"
    ai_provider: str = "local"
    cloud_ai_api_key: str | None = None
    cloud_ai_model: str = "gemma-4-26b-a4b-it"
    google_genai_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    ai_timeout_seconds: float = 180.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


settings = Settings()
