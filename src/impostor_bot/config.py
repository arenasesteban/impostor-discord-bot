from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum


class ConfigurationError(RuntimeError):
    """Raised when application configuration is invalid."""


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True, slots=True)
class DatabaseSettings:
    database_url: str


@dataclass(frozen=True, slots=True)
class AppSettings:
    discord_token: str
    database: DatabaseSettings
    log_level: LogLevel
    environment: Environment


def load_database_settings(
    environ: Mapping[str, str],
) -> DatabaseSettings:
    database_url = _required(
        environ,
        "DATABASE_URL",
    )

    if not database_url.startswith(
        "postgresql+asyncpg://"
    ):
        raise ConfigurationError(
            "DATABASE_URL must use postgresql+asyncpg."
        )

    return DatabaseSettings(
        database_url=database_url,
    )


def load_app_settings(
    environ: Mapping[str, str],
) -> AppSettings:
    discord_token = _required(
        environ,
        "DISCORD_TOKEN",
    )

    database = load_database_settings(
        environ,
    )

    log_level = _load_log_level(
        environ.get("LOG_LEVEL"),
    )

    environment = _load_environment(
        environ.get("ENVIRONMENT"),
    )

    return AppSettings(
        discord_token=discord_token,
        database=database,
        log_level=log_level,
        environment=environment,
    )


def _required(
    environ: Mapping[str, str],
    name: str,
) -> str:
    value = environ.get(name)

    if value is None or not value.strip():
        raise ConfigurationError(
            f"{name} must be configured."
        )

    return value


def _load_log_level(
    value: str | None,
) -> LogLevel:
    normalized = (
        value
        if value is not None
        else LogLevel.INFO.value
    ).strip().upper()

    try:
        return LogLevel(normalized)
    except ValueError as error:
        raise ConfigurationError(
            "LOG_LEVEL must be one of: "
            "DEBUG, INFO, WARNING, ERROR, CRITICAL."
        ) from error


def _load_environment(
    value: str | None,
) -> Environment:
    normalized = (
        value
        if value is not None
        else Environment.DEVELOPMENT.value
    ).strip().lower()

    try:
        return Environment(normalized)
    except ValueError as error:
        raise ConfigurationError(
            "ENVIRONMENT must be one of: "
            "development, test, production."
        ) from error