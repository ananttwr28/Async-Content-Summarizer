from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Summarization Service"
    
    # Scraper Settings
    # Default mimic: Chrome on Windows
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    SCRAPER_TIMEOUT_SECONDS: float = 15.0

    # OpenAI Settings
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Gemini Settings
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash-lite-preview-09-2025"

    # Database & Redis Settings
    DATABASE_URL: str = "postgresql://user:password@localhost/summarizer_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
