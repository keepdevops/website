from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    
    stripe_secret_key: str
    stripe_webhook_secret: str
    stripe_publishable_key: str
    
    redis_url: str = "redis://localhost:6379"
    
    docker_registry_url: str
    docker_registry_token: str
    
    email_provider_api_key: str
    
    api_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    environment: str = "development"
    
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    jwt_secret_key: str = "your-jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

