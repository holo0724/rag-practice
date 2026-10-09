from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# .env lives in the repo root, two levels above this file's folder
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    database_url: str
    ollama_base_url: str = "http://localhost:11434"
    embed_model: str
    embed_dim: int = 768


settings = Settings()