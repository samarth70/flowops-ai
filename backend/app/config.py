import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "FlowOps AI - Autonomous CRM Deal Desk"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,https://*.vercel.app"

    # LLMs (Free Tier Providers)
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    DEFAULT_LLM_PROVIDER: str = "groq"
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Observability (Langfuse Cloud)
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # Database
    DATABASE_URL: str = "sqlite:///./flowops_crm.db"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def cors_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def has_groq(self) -> bool:
        return bool(self.GROQ_API_KEY and self.GROQ_API_KEY.startswith("gsk_") and "your_free" not in self.GROQ_API_KEY)

    @property
    def has_gemini(self) -> bool:
        return bool(self.GEMINI_API_KEY and len(self.GEMINI_API_KEY) > 10 and "your_free" not in self.GEMINI_API_KEY)

    @property
    def has_langfuse(self) -> bool:
        return bool(self.LANGFUSE_PUBLIC_KEY and "your_public" not in self.LANGFUSE_PUBLIC_KEY and self.LANGFUSE_SECRET_KEY)

settings = Settings()
