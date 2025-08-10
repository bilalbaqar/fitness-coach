import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./fitness_coach.db"
    
    # Authentication
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # Agent Tools
    agent_token: str = "your-agent-token-change-in-production"
    
    # Server
    port: int = 8000
    
    # CORS
    frontend_origin: str = "http://localhost:5173"
    
    # ElevenLabs (optional)
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_model: str = "eleven_multilingual_v2"
    
    class Config:
        env_file = ".env"

settings = Settings()
