"""Typed application settings.

Configuration is read from environment variables (and an optional ``.env``
file). Environmental values *must* be provided at deploy time; the backend
fails fast on startup when a required secret is missing rather than silently
falling back to an insecure default.

Security rules:
    * Secrets use :class:`pydantic.SecretStr` so they cannot be accidentally
      logged or serialised. Call ``.get_secret_value()`` where a raw value is
      genuinely required.
    * ``validate_for_startup()`` is invoked from the lifespan hook so startup
      fails loudly with a clear, non-sensitive message.
"""

from __future__ import annotations

import secrets
from functools import lru_cache
from typing import Annotated, Any, Optional

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from app.core.constants import (
    API_PREFIX,
    API_TITLE,
    API_VERSION,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)
from app.exceptions.base import ConfigurationError

# Environment names that permit generated/ephemeral development secrets.
_NON_PRODUCTION_ENVS = frozenset({"development", "dev", "local", "testing", "test"})


def _split_csv(value: Any) -> Any:
    """Allow comma-separated env values for list fields."""
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return value


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -- Application -------------------------------------------------------
    app_name: str = "eyedx-backend"
    app_env: str = Field(default="development")
    debug: bool = False
    api_version: str = API_VERSION
    api_prefix: str = API_PREFIX
    api_title: str = API_TITLE
    host: str = "0.0.0.0"
    port: int = 8000

    # -- Logging -----------------------------------------------------------
    log_level: str = "INFO"
    log_json: bool = False

    # -- Database ----------------------------------------------------------
    database_url: Optional[SecretStr] = None
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_echo: bool = False

    # -- Authentication ----------------------------------------------------
    jwt_secret_key: Optional[SecretStr] = None
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60
    refresh_token_expiry_days: int = 14

    # -- CORS --------------------------------------------------------------
    cors_allow_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=list
    )
    cors_allow_credentials: bool = False
    cors_allow_methods: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["*"]
    )
    cors_allow_headers: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["*"]
    )

    # -- Request limits / rate limiting -----------------------------------
    max_upload_mb: int = 20
    request_timeout_seconds: int = 60
    rate_limit_per_minute: int = 120

    # -- Model service -----------------------------------------------------
    model_service_url: Optional[str] = None
    model_service_timeout_seconds: int = 30
    inference_mock_mode: bool = True
    # Mock inference never reports success; this selects which honest
    # non-success state the mock returns. Must be one of: abstained,
    # uncertain, low_quality.
    inference_mock_result: str = "abstained"

    # -- Feature flags (defaulted OFF; enabled explicitly per environment) --
    feature_explainability: bool = False
    feature_uncertainty: bool = False
    feature_abstention: bool = False
    consent_required: bool = True

    # -- Object storage ----------------------------------------------------
    storage_backend: str = "local"
    storage_local_path: str = "./var/storage"
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None
    s3_endpoint_url: Optional[str] = None
    s3_access_key_id: Optional[SecretStr] = None
    s3_secret_access_key: Optional[SecretStr] = None

    # -- Pagination --------------------------------------------------------
    default_page_size: int = DEFAULT_PAGE_SIZE
    max_page_size: int = MAX_PAGE_SIZE

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------
    @field_validator(
        "cors_allow_origins",
        "cors_allow_methods",
        "cors_allow_headers",
        mode="before",
    )
    @classmethod
    def _parse_csv_lists(cls, value: Any) -> Any:
        return _split_csv(value)

    # ------------------------------------------------------------------
    # Derived helpers
    # ------------------------------------------------------------------
    @property
    def is_production(self) -> bool:
        return self.app_env.strip().lower() in {"production", "prod"}

    @property
    def sqlalchemy_database_uri(self) -> Optional[str]:
        """Return the raw database DSN for SQLAlchemy, or ``None``."""
        if self.database_url is None:
            return None
        return self.database_url.get_secret_value()

    def allow_mock_inference(self) -> bool:
        """Mock inference is only permitted outside production."""
        return self.inference_mock_mode and not self.is_production

    # ------------------------------------------------------------------
    # Startup validation
    # ------------------------------------------------------------------
    def validate_for_startup(self) -> None:
        """Fail fast when required configuration is missing.

        Raises:
            ConfigurationError: with a safe, non-sensitive message describing
                which key is missing and how to provide it.
        """
        if not self.database_url or not self.database_url.get_secret_value():
            raise ConfigurationError(
                "DATABASE_URL is required. Provide it via the environment or a "
                ".env file (see .env.example)."
            )

        secret = self.jwt_secret_key
        if secret is None or not secret.get_secret_value():
            if self.is_production:
                raise ConfigurationError(
                    "JWT_SECRET_KEY is required in production. Provide a strong "
                    "random secret via the environment (see .env.example)."
                )
            # Development/test: generate an ephemeral, in-memory secret. This is
            # not a real credential and is never persisted.
            self.jwt_secret_key = SecretStr(secrets.token_urlsafe(48))

        if self.model_service_url is None and not self.allow_mock_inference():
            raise ConfigurationError(
                "MODEL_SERVICE_URL is required unless mock inference is enabled "
                "in a non-production environment."
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""
    return Settings()
