from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB
    mongodb_url: str = "mongodb+srv://mauryaabhi2003_db_user:kjOVZqJ7ktwibRtr@cluster0.ebvpdby.mongodb.net/?appName=Cluster0"
    database_name: str = "forest_fire_system"
    
    # JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 300
    
    # Serial Port
    serial_port: str = "/dev/ttyUSB0"
    baud_rate: int = 115200
    
    # Groq AI (fast LLM inference)
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-70b-versatile"  # Fast and intelligent model
    
    # AI Analysis Settings
    ai_analysis_interval: int = 30  # Run AI every N seconds (30-60 recommended)
    
    # System Thresholds
    fire_risk_threshold: float = 70.0
    high_smoke_threshold: float = 100.0
    high_temp_threshold: float = 35.0
    low_humidity_threshold: float = 30.0
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
