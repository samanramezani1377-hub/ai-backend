from functools import lru_cache
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    model_id: str = "Qwen/Qwen3.5-9B"
    model_revision: str | None = None
    model_runtime: str = "external"
    environment: str = "test"
    api_key: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        model_id=os.getenv("MODEL_ID", "Qwen/Qwen3.5-9B"),
        model_revision=os.getenv("MODEL_REVISION") or None,
        model_runtime=os.getenv("MODEL_RUNTIME", "external"),
        environment=os.getenv("ENVIRONMENT", "test"),
        api_key=os.getenv("AI_API_KEY") or None,
    )
