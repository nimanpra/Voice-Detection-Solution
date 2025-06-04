import os
from pydantic import BaseSettings, HttpUrl
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Voice Recognition API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # Hugging Face settings
    HUGGINGFACE_TOKEN: str = os.getenv("HUGGINGFACE_TOKEN", "")
    
    # Model settings
    DIARIZATION_MODEL: str = "pyannote/speaker-diarization@2.1"
    
    # Audio settings
    MAX_AUDIO_DURATION: int = 3600  # 1 hour in seconds
    SUPPORTED_AUDIO_TYPES = ["audio/wav", "audio/mpeg", "audio/ogg", "audio/x-wav", "audio/mp3"]
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    BACKEND_CORS_ORIGINS = ["*"]  # In production, replace with your frontend URL
    
    class Config:
        case_sensitive = True

# Create settings instance
settings = Settings()
