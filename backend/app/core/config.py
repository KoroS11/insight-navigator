"""
NSA-X Backend Configuration
All settings loaded from environment variables
"""
import logging
import sys
from functools import lru_cache
from typing import Optional

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Known weak/default values that should never be used in production
WEAK_PASSWORDS = {"changeme123", "password", "admin", "123456", "secret"}
WEAK_USERNAMES = {"admin", "root", "user", "test"}
PLACEHOLDER_DATABASE_URL = "CHANGE_ME_DATABASE_URL"
PLACEHOLDER_DATABASE_URL_SYNC = "CHANGE_ME_DATABASE_URL_SYNC"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = PLACEHOLDER_DATABASE_URL
    database_url_sync: str = PLACEHOLDER_DATABASE_URL_SYNC
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT Authentication - REQUIRED (no default)
    jwt_secret_key: SecretStr = SecretStr("")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    
    # API Settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "NSA-X"
    debug: bool = False
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    
    # Default Admin User - REQUIRED (no defaults)
    default_admin_username: str = ""
    default_admin_password: SecretStr = SecretStr("")
    
    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8080", "http://localhost:3000"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    def validate_startup(self) -> None:
        """Validate settings at startup. Raises SystemExit on critical issues."""
        errors = []

        # Validate database URLs
        db_async_invalid = not self.database_url or self.database_url == PLACEHOLDER_DATABASE_URL
        db_sync_invalid = not self.database_url_sync or self.database_url_sync == PLACEHOLDER_DATABASE_URL_SYNC
        if not self.debug:
            if db_async_invalid:
                errors.append("DATABASE_URL is required for production")
            if db_sync_invalid:
                errors.append("DATABASE_URL_SYNC is required for production")
        else:
            if db_async_invalid:
                logger.warning("DATABASE_URL is not configured - acceptable in debug mode only")
            if db_sync_invalid:
                logger.warning("DATABASE_URL_SYNC is not configured - acceptable in debug mode only")
        
        # Validate JWT secret
        jwt_secret = self.jwt_secret_key.get_secret_value()
        if not jwt_secret:
            if not self.debug:
                errors.append("JWT_SECRET_KEY is required and cannot be empty")
            else:
                logger.warning("JWT_SECRET_KEY is empty - only acceptable in debug mode")
        elif len(jwt_secret) < 32:
            if not self.debug:
                errors.append("JWT_SECRET_KEY must be at least 32 characters")
            else:
                logger.warning("JWT_SECRET_KEY is shorter than 32 characters")
        
        # Validate admin credentials
        admin_password = self.default_admin_password.get_secret_value()
        if not self.debug:
            if not self.default_admin_username:
                errors.append("DEFAULT_ADMIN_USERNAME is required")
            elif self.default_admin_username.lower() in WEAK_USERNAMES:
                errors.append("DEFAULT_ADMIN_USERNAME is too weak for production")
            
            if not admin_password:
                errors.append("DEFAULT_ADMIN_PASSWORD is required")
            elif admin_password in WEAK_PASSWORDS or len(admin_password) < 12:
                errors.append("DEFAULT_ADMIN_PASSWORD is too weak (must be 12+ chars and not a common password)")
        else:
            if self.default_admin_username.lower() in WEAK_USERNAMES:
                logger.warning("DEFAULT_ADMIN_USERNAME is weak - OK for debug mode only")
            if admin_password in WEAK_PASSWORDS:
                logger.warning("DEFAULT_ADMIN_PASSWORD is weak - OK for debug mode only")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            logger.error("Application cannot start with invalid configuration. Set DEBUG=true for development.")
            sys.exit(1)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def get_validated_settings() -> Settings:
    """Get settings with startup validation. Use in app startup, not during import."""
    settings = get_settings()
    settings.validate_startup()
    return settings


# Global settings instance - validation happens in app startup, not here
settings = get_settings()
