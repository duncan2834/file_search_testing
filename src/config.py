from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(..., description="Gemini API key")

    class Config:
        env_file = ".env"  
        env_file_encoding = "utf-8"

settings = Settings() # type: ignore