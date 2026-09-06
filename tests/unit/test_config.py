from dataclasses import FrozenInstanceError

import pytest

from impostor_bot.config import (
    ConfigurationError,
    Environment,
    LogLevel,
    load_app_settings,
    load_database_settings,
)


def test_load_database_settings() -> None:
    database_url = (
        "postgresql+asyncpg://"
        "user:pass@localhost:5432/db"
    )

    settings = load_database_settings(
        {
            "DATABASE_URL": database_url,
        }
    )

    assert settings.database_url == database_url


def test_database_settings_do_not_require_discord_token() -> None:
    settings = load_database_settings(
        {
            "DATABASE_URL":
                "postgresql+asyncpg://"
                "user:pass@postgres/db",
        }
    )

    assert settings.database_url


@pytest.mark.parametrize(
    "database_url",
    [
        None,
        "",
        "   ",
    ],
)
def test_database_url_is_required(
    database_url: str | None,
) -> None:
    environ: dict[str, str] = {}

    if database_url is not None:
        environ["DATABASE_URL"] = (
            database_url
        )

    with pytest.raises(
        ConfigurationError,
        match="DATABASE_URL",
    ):
        load_database_settings(environ)


@pytest.mark.parametrize(
    "database_url",
    [
        "postgres://user:pass@host/db",
        "postgresql://user:pass@host/db",
        "mysql://user:pass@host/db",
    ],
)
def test_database_url_requires_asyncpg(
    database_url: str,
) -> None:
    with pytest.raises(
        ConfigurationError,
        match="postgresql\\+asyncpg",
    ):
        load_database_settings(
            {
                "DATABASE_URL":
                    database_url,
            }
        )


@pytest.mark.parametrize(
    "token",
    [
        None,
        "",
        "   ",
    ],
)
def test_discord_token_is_required(
    token: str | None,
) -> None:
    environ = {
        "DATABASE_URL":
            "postgresql+asyncpg://"
            "user:pass@localhost/db",
    }

    if token is not None:
        environ["DISCORD_TOKEN"] = token

    with pytest.raises(
        ConfigurationError,
        match="DISCORD_TOKEN",
    ):
        load_app_settings(environ)


def test_discord_token_is_preserved() -> None:
    token = " token-value "

    settings = load_app_settings(
        {
            "DISCORD_TOKEN": token,
            "DATABASE_URL":
                "postgresql+asyncpg://"
                "user:pass@localhost/db",
        }
    )

    assert settings.discord_token == token


def test_application_settings_use_defaults() -> None:
    settings = load_app_settings(
        {
            "DISCORD_TOKEN": "token",
            "DATABASE_URL":
                "postgresql+asyncpg://"
                "user:pass@localhost/db",
        }
    )

    assert settings.log_level is LogLevel.INFO

    assert (
        settings.environment
        is Environment.DEVELOPMENT
    )


def test_log_level_is_case_insensitive() -> None:
    settings = load_app_settings(
        {
            "DISCORD_TOKEN": "token",
            "DATABASE_URL":
                "postgresql+asyncpg://"
                "user:pass@localhost/db",
            "LOG_LEVEL": "debug",
        }
    )

    assert settings.log_level is LogLevel.DEBUG


def test_environment_is_case_insensitive() -> None:
    settings = load_app_settings(
        {
            "DISCORD_TOKEN": "token",
            "DATABASE_URL":
                "postgresql+asyncpg://"
                "user:pass@localhost/db",
            "ENVIRONMENT": "PRODUCTION",
        }
    )

    assert (
        settings.environment
        is Environment.PRODUCTION
    )


def test_invalid_log_level_is_rejected() -> None:
    with pytest.raises(
        ConfigurationError,
        match="LOG_LEVEL",
    ):
        load_app_settings(
            {
                "DISCORD_TOKEN": "token",
                "DATABASE_URL":
                    "postgresql+asyncpg://"
                    "user:pass@localhost/db",
                "LOG_LEVEL": "verbose",
            }
        )


def test_invalid_environment_is_rejected() -> None:
    with pytest.raises(
        ConfigurationError,
        match="ENVIRONMENT",
    ):
        load_app_settings(
            {
                "DISCORD_TOKEN": "token",
                "DATABASE_URL":
                    "postgresql+asyncpg://"
                    "user:pass@localhost/db",
                "ENVIRONMENT": "staging",
            }
        )


def test_database_error_does_not_expose_url() -> None:
    secret_url = (
        "mysql://secret-user:"
        "secret-password@secret-host/db"
    )

    with pytest.raises(
        ConfigurationError
    ) as exc_info:
        load_database_settings(
            {
                "DATABASE_URL":
                    secret_url,
            }
        )

    assert secret_url not in str(
        exc_info.value
    )


def test_app_settings_are_immutable() -> None:
    settings = load_app_settings(
        {
            "DISCORD_TOKEN": "token",
            "DATABASE_URL":
                "postgresql+asyncpg://"
                "user:pass@localhost/db",
        }
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        settings.discord_token = "new"


def test_app_configuration_error_does_not_expose_secrets() -> None:
    secret_token = "discord-super-secret-token"
    secret_database_url = (
        "mysql://secret-user:"
        "secret-password@secret-host/db"
    )

    with pytest.raises(
        ConfigurationError
    ) as exc_info:
        load_app_settings(
            {
                "DISCORD_TOKEN": secret_token,
                "DATABASE_URL": secret_database_url,
            }
        )

    message = str(exc_info.value)

    assert secret_token not in message
    assert secret_database_url not in message