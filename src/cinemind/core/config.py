from functools import cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    database_url: str = Field(default="", alias="DATABASE_URL")
    llm_provider: str = Field(default="openrouter", alias="LLM_PROVIDER")
    llm_model_name: str = Field(default="openai/gpt-4o", alias="LLM_MODEL_NAME")
    cinemind_api_base_url: str = Field(
        default="http://127.0.0.1:8000", alias="CINEMIND_API_BASE_URL"
    )


@cache
def get_settings() -> Settings:
    return Settings()
