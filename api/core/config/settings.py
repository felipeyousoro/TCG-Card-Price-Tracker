import logging
import os
from enum import StrEnum

from pydantic_settings import BaseSettings
from starlette.config import Config

from .enums import LogFormat, LogLevel, CacheBackend, SessionBackend

logger = logging.getLogger(__name__)

current_file_dir = os.path.dirname(os.path.realpath(__file__))
api_root = os.path.abspath(os.path.join(current_file_dir, "..", ".."))
repo_root = os.path.abspath(os.path.join(api_root, ".."))

env_paths = [
    os.path.join(api_root, ".env"),
    os.path.join(repo_root, ".env"),
    "/app/.env",
]

env_path = next((path for path in env_paths if os.path.isfile(path)), env_paths[0])
logger.info(f"Using environment file at: {env_path}")

config = Config(env_path)

class EnvironmentOption(StrEnum):
    """Environment options for the application."""

    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    LOCAL = "local"


class EnvironmentSettings(BaseSettings):
    """Environment-related settings."""

    ENVIRONMENT: EnvironmentOption = config(
        "ENVIRONMENT",
        default=EnvironmentOption.DEVELOPMENT,
        cast=EnvironmentOption
    )


class DatabaseSettings(BaseSettings):
    """Database-related settings."""

    POSTGRES_USER: str = config("POSTGRES_USER", default="postgres")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD", default="postgres")
    POSTGRES_SERVER: str = config("POSTGRES_SERVER", default="localhost")
    POSTGRES_PORT: int = config("POSTGRES_PORT", default=5432)
    POSTGRES_DB: str = config("POSTGRES_DB", default="postgres")
    POSTGRES_SYNC_PREFIX: str = config("POSTGRES_SYNC_PREFIX", default="postgresql://")
    POSTGRES_ASYNC_PREFIX: str = config("POSTGRES_ASYNC_PREFIX", default="postgresql+asyncpg://")
    CREATE_TABLES_ON_STARTUP: bool = config("CREATE_TABLES_ON_STARTUP", default=False, cast=bool)

    POSTGRES_POOL_SIZE: int = config("POSTGRES_POOL_SIZE", default=20, cast=int)
    POSTGRES_MAX_OVERFLOW: int = config("POSTGRES_MAX_OVERFLOW", default=0, cast=int)

    @property
    def DATABASE_URL(self) -> str:
        """Get the full database URL.

        Checks for DATABASE_URL environment variable first (production pattern),
        then falls back to constructing from individual components (development pattern).
        """
        direct_url = config("DATABASE_URL", default=None)
        if direct_url:
            if direct_url.startswith("postgresql://") and "+asyncpg" not in direct_url:
                return direct_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return direct_url

        return (
            f"{self.POSTGRES_ASYNC_PREFIX}{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

class CORSSettings(BaseSettings):
    """CORS-related settings."""

    CORS_ENABLED: bool = config("CORS_ENABLED", default=True, cast=bool)
    CORS_ORIGINS: str = config("CORS_ORIGINS", default="*")
    CORS_ALLOW_CREDENTIALS: bool = config("CORS_ALLOW_CREDENTIALS", default=True, cast=bool)

    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        """Get CORS origins as a list."""
        if not self.CORS_ORIGINS:
            return ["*"]
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]

    CORS_ALLOW_METHODS: str = config("CORS_ALLOW_METHODS", default="*")
    CORS_ALLOW_HEADERS: str = config("CORS_ALLOW_HEADERS", default="*")


class CompressionSettings(BaseSettings):
    """Compression-related settings."""

    GZIP_ENABLED: bool = config("GZIP_ENABLED", default=True, cast=bool)
    GZIP_MINIMUM_SIZE: int = config("GZIP_MINIMUM_SIZE", default=1000, cast=int)


class APIDocSettings(BaseSettings):
    """API documentation settings."""

    ENABLE_DOCS_IN_PRODUCTION: bool = config("ENABLE_DOCS_IN_PRODUCTION", default=False, cast=bool)
    OPENAPI_PREFIX: str = config("OPENAPI_PREFIX", default="")
    DOCS_URL: str = config("DOCS_URL", default="/docs")
    REDOC_URL: str = config("REDOC_URL", default="/redoc")
    OPENAPI_URL: str = config("OPENAPI_URL", default="/openapi.json")

    API_TITLE: str = config("API_TITLE", default="")
    API_SUMMARY: str = config("API_SUMMARY", default="")
    API_DESCRIPTION: str = config("API_DESCRIPTION", default="")
    API_VERSION: str = config("API_VERSION", default="")
    API_TERMS_OF_SERVICE: str = config("API_TERMS_OF_SERVICE", default="")

    API_CONTACT_NAME: str = config("API_CONTACT_NAME", default="")
    API_CONTACT_URL: str = config("API_CONTACT_URL", default="")
    API_CONTACT_EMAIL: str = config("API_CONTACT_EMAIL", default="")

    API_LICENSE_NAME: str = config("API_LICENSE_NAME", default="")
    API_LICENSE_URL: str = config("API_LICENSE_URL", default="")
    API_LICENSE_IDENTIFIER: str = config("API_LICENSE_IDENTIFIER", default="")

    API_TAGS_METADATA: str = config("API_TAGS_METADATA", default="[]")


class AuthSettings(BaseSettings):
    """Authentication-related settings."""

    SECRET_KEY: str = config("SECRET_KEY", default="insecure-secret-key-change-this")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7, cast=int)

    SESSION_TIMEOUT_MINUTES: int = config("SESSION_TIMEOUT_MINUTES", default=30, cast=int)
    SESSION_CLEANUP_INTERVAL_MINUTES: int = config("SESSION_CLEANUP_INTERVAL_MINUTES", default=15, cast=int)
    MAX_SESSIONS_PER_USER: int = config("MAX_SESSIONS_PER_USER", default=5, cast=int)
    SESSION_SECURE_COOKIES: bool = config("SESSION_SECURE_COOKIES", default=True, cast=bool)
    SESSION_BACKEND: str = config("SESSION_BACKEND", default=SessionBackend.MEMORY.value)
    SESSION_COOKIE_MAX_AGE: int = config("SESSION_COOKIE_MAX_AGE", default=86400, cast=int)

    CSRF_ENABLED: bool = config("CSRF_ENABLED", default=True, cast=bool)

    LOGIN_MAX_ATTEMPTS: int = config("LOGIN_MAX_ATTEMPTS", default=5, cast=int)
    LOGIN_WINDOW_MINUTES: int = config("LOGIN_WINDOW_MINUTES", default=15, cast=int)

class APISettings(BaseSettings):
    """API-related settings."""

    API_PREFIX: str = "/api"


class AppSettings(BaseSettings):
    """Application-related settings."""

    # Note: For API documentation, prefer using API_* fields in APIDocSettings
    APP_NAME: str = config("APP_NAME", default="FastAPI Boilerplate")
    APP_DESCRIPTION: str = config("APP_DESCRIPTION", default="Modular FastAPI starter")
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
    VERSION: str = config("VERSION", default="0.1.0")
    CONTACT_NAME: str = config("CONTACT_NAME", default="Support")
    CONTACT_EMAIL: str = config("CONTACT_EMAIL", default="support@example.com")
    LICENSE_NAME: str = config("LICENSE_NAME", default="All rights reserved.")


class AdminSettings(BaseSettings):
    """Admin user settings for initial setup."""

    ADMIN_NAME: str = config("ADMIN_NAME", default="Admin")
    ADMIN_EMAIL: str = config("ADMIN_EMAIL", default="")
    ADMIN_USERNAME: str = config("ADMIN_USERNAME", default="admin")
    ADMIN_PASSWORD: str = config("ADMIN_PASSWORD", default="admin")
    DEFAULT_TIER_NAME: str = config("DEFAULT_TIER_NAME", default="free")


class SQLAdminSettings(BaseSettings):
    """SQLAdmin interface settings."""

    ADMIN_ENABLED: bool = config("ADMIN_ENABLED", default=True, cast=bool)


class SecuritySettings(BaseSettings):
    """Security validation settings."""

    PRODUCTION_SECURITY_VALIDATION_ENABLED: bool = config("PRODUCTION_SECURITY_VALIDATION_ENABLED", default=True, cast=bool)
    PRODUCTION_SECURITY_STRICT_MODE: bool = config("PRODUCTION_SECURITY_STRICT_MODE", default=False, cast=bool)
    SECURITY_HEADERS_ENABLED: bool = config("SECURITY_HEADERS_ENABLED", default=True, cast=bool)


class OptcgApiSettings(BaseSettings):
    """Settings for the optcgapi.com catalog importer."""

    OPTCGAPI_BASE_URL: str = config("OPTCGAPI_BASE_URL", default="https://www.optcgapi.com")
    OPTCGAPI_TIMEOUT_SECONDS: float = config("OPTCGAPI_TIMEOUT_SECONDS", default=120, cast=float)


class LoggingSettings(BaseSettings):
    """Centralized logging configuration settings."""

    LOG_LEVEL: str = config("LOG_LEVEL", default=LogLevel.INFO.value)
    LOG_FORMAT: str = config("LOG_FORMAT", default=LogFormat.STRUCTURED.value)

    LOG_CONSOLE_ENABLED: bool = config("LOG_CONSOLE_ENABLED", default=True, cast=bool)
    LOG_FILE_ENABLED: bool = config("LOG_FILE_ENABLED", default=False, cast=bool)
    LOG_FILE_PATH: str = config("LOG_FILE_PATH", default="logs/app.log")
    LOG_FILE_MAX_SIZE: int = config("LOG_FILE_MAX_SIZE", default=10485760, cast=int)
    LOG_FILE_BACKUP_COUNT: int = config("LOG_FILE_BACKUP_COUNT", default=5, cast=int)

    LOG_CORRELATION_ID: bool = config("LOG_CORRELATION_ID", default=True, cast=bool)
    LOG_STRUCTURED_CONTEXT: bool = config("LOG_STRUCTURED_CONTEXT", default=True, cast=bool)
    LOG_PERFORMANCE_METRICS: bool = config("LOG_PERFORMANCE_METRICS", default=False, cast=bool)

    LOG_SQL_QUERIES: bool = config("LOG_SQL_QUERIES", default=False, cast=bool)
    LOG_INCLUDE_STACKTRACE: bool = config("LOG_INCLUDE_STACKTRACE", default=True, cast=bool)

    LOG_DEVELOPMENT_VERBOSE: bool = config("LOG_DEVELOPMENT_VERBOSE", default=True, cast=bool)
    LOG_PRODUCTION_OPTIMIZE: bool = config("LOG_PRODUCTION_OPTIMIZE", default=True, cast=bool)

    @property
    def LOG_LEVEL_INT(self) -> int:
        """Convert string log level to integer."""
        level_map = {
            LogLevel.DEBUG.value: logging.DEBUG,
            LogLevel.INFO.value: logging.INFO,
            LogLevel.WARNING.value: logging.WARNING,
            LogLevel.ERROR.value: logging.ERROR,
            LogLevel.CRITICAL.value: logging.CRITICAL,
        }
        return level_map.get(self.LOG_LEVEL.upper(), logging.INFO)

class Settings(
    EnvironmentSettings,
    DatabaseSettings,
    CORSSettings,
    CompressionSettings,
    APIDocSettings,
    AuthSettings,
    APISettings,
    AppSettings,
    AdminSettings,
    SQLAdminSettings,
    SecuritySettings,
    LoggingSettings,
    OptcgApiSettings,
):
    """Main settings class that combines all setting categories."""

    pass


settings = Settings()


def get_settings() -> Settings:
    """Get application settings.

    Returns:
        The application settings.
    """
    return settings