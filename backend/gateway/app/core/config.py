from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App settings
    app_name: str = "PPT Generator API Gateway"
    debug: bool = True
    
    # Database settings - MATCH YOUR DOCKER COMPOSE EXACTLY
    database_url: str = "postgresql://ppt_admin:SecurePass123!@localhost:5432/ppt_generator"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    # JWT settings
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # Service URLs
    document_processor_url: str = "http://localhost:8001"
    ai_generator_url: str = "http://localhost:8002"
    presentation_renderer_url: str = "http://localhost:8003"
    
    # File upload settings
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [".pdf", ".docx", ".txt", ".pptx"]
    upload_directory: str = "./uploads"
    
    # Cache settings
    cache_ttl_short: int = 300      # 5 minutes
    cache_ttl_medium: int = 1800    # 30 minutes
    cache_ttl_long: int = 3600      # 1 hour
    
    # Pub/Sub channels
    channel_presentation_events: str = "presentation.events"
    channel_task_updates: str = "task.updates"
    channel_user_notifications: str = "user.notifications"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()