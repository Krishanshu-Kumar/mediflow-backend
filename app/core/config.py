from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ANTHROPIC_API_KEY: str
    AI_MODEL_GENERAL: str = "llama3.2:3b"
    AI_MODEL_CODER: str = "qwen2.5-coder:3b"
    AI_BASE_URL: str = "http://localhost:11434/v1"
    DEBUG: bool = False 

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

settings = Settings()
