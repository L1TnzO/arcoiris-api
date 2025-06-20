"""Application configuration settings."""

from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Project info
    project_name: str = "Furniture Product Management API"
    version: str = "1.0.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    
    # Database
    database_url: str = "sqlite:///./furniture.db"
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    postgres_host: Optional[str] = None
    postgres_port: Optional[int] = None
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # File upload
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: str = ".xlsx,.xls"
    
    # CORS
    backend_cors_origins: List[AnyHttpUrl] = []
    
    # Admin user (for initial setup)
    admin_username: str = "admin"
    admin_email: str = "admin@example.com"
    admin_password: str = "admin123"
    
    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get allowed file extensions as a list."""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
