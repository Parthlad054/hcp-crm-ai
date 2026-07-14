from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    GROQ_API_KEY: str
    GROQ_MODEL: str = "gemma2-9b-it"
    GROQ_MODEL_FALLBACK: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"


settings = Settings()
