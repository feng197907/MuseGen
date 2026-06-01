"""Application configuration via pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/animevideo"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Object storage (MinIO / S3)
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "animevideo"
    S3_REGION: str = "us-east-1"

    # OpenAI
    OPENAI_API_KEY: str = "sk-placeholder"
    OPENAI_MODEL: str = "gpt-4o"

    # Replicate
    REPLICATE_API_TOKEN: str = "r8_placeholder"
    SDXL_MODEL_VERSION: str = "stability-ai/sdxl:39ed52f2319f9c52de0b4b5303d5aab78e0d4291e02a49a8c0e75f7bf0a33e14"
    SVD_MODEL_VERSION: str = "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438"

    # ElevenLabs
    ELEVENLABS_API_KEY: str = "el_placeholder"

    # Volcano TTS
    VOLC_TTS_APP_ID: str = ""
    VOLC_TTS_TOKEN: str = ""

    # Quota limits
    MAX_DAILY_IMAGE_CALLS: int = 500
    MAX_DAILY_VIDEO_CALLS: int = 100
    MAX_DAILY_TTS_CHARS: int = 100000

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # App
    DEBUG: bool = True


settings = Settings()
