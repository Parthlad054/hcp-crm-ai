from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_MODEL_FALLBACK: str = "openai/gpt-oss-120b"

    @field_validator("GROQ_MODEL")
    @classmethod
    def validate_groq_model(cls, v: str) -> str:
        cleaned = v.strip() if v else ""
        if not cleaned:
            raise ValueError(
                "GROQ_MODEL cannot be empty. Please specify a verified Groq model (e.g. openai/gpt-oss-120b) in your .env file."
            )
        return cleaned

    @field_validator("GROQ_API_KEY")
    @classmethod
    def validate_groq_api_key(cls, v: str) -> str:
        cleaned = v.strip() if v else ""
        if not cleaned:
            raise ValueError(
                "GROQ_API_KEY cannot be empty. Please provide a valid Groq API key in your .env file."
            )
        return cleaned

    # JWT
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_MINUTES: int = 15

    # SMTP (for forgot-password emails)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "HCP CRM AI"

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed frontend origins.
    # In .env: ALLOWED_ORIGINS=http://localhost:5173,https://app.yourcompany.com
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # ── Frontend URL (used in password-reset email links) ─────────────────────
    FRONTEND_URL: str = "http://localhost:5173"

    # ── DB Connection Pool ────────────────────────────────────────────────────
    # Tune these via .env for staging / production.
    DB_POOL_SIZE: int = 10        # persistent connections in pool
    DB_MAX_OVERFLOW: int = 20     # extra connections beyond pool_size under load
    DB_POOL_TIMEOUT: int = 30     # seconds to wait for a free connection
    DB_POOL_RECYCLE: int = 1800   # recycle connections after 30 min (avoids stale)

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse ALLOWED_ORIGINS into a list for CORSMiddleware."""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
