import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import (
    AsyncMock,
    MagicMock,
    Mock,
)

import pytest
from dotenv import load_dotenv as real_load_dotenv

import impostor_bot.main as main_module
from impostor_bot.config import (
    AppSettings,
    ConfigurationError,
    DatabaseSettings,
    Environment,
    LogLevel,
)


def make_settings(
    *,
    token: str = "test-token",
    database_url: str = (
        "postgresql+asyncpg://"
        "user:password@postgres:5432/test_db"
    ),
    log_level: LogLevel = LogLevel.INFO,
    environment: Environment = (
        Environment.DEVELOPMENT
    ),
) -> AppSettings:
    return AppSettings(
        discord_token=token,
        database=DatabaseSettings(
            database_url=database_url,
        ),
        log_level=log_level,
        environment=environment,
    )


@pytest.mark.asyncio
async def test_run_injects_settings_into_runtime(
    monkeypatch,
) -> None:
    settings = make_settings(
        token="discord-secret",
        database_url=(
            "postgresql+asyncpg://"
            "user:password@postgres:5432/test_db"
        ),
        log_level=LogLevel.DEBUG,
    )

    runtime = SimpleNamespace(
        game_repository=object(),
        lobby_message_repository=object(),
        check_connection=AsyncMock(),
        close=AsyncMock(),
    )

    bot = MagicMock()

    bot.__aenter__ = AsyncMock(
        return_value=bot,
    )

    bot.__aexit__ = AsyncMock(
        return_value=None,
    )

    bot.start = AsyncMock()
    bot.add_startup_hook = Mock()

    configure_logging_mock = Mock()

    create_postgres_runtime_mock = Mock(
        return_value=runtime,
    )

    create_bot_mock = Mock(
        return_value=bot,
    )

    recovery = MagicMock()
    recovery.execute = AsyncMock()

    recover_game_sessions_mock = Mock(
        return_value=recovery,
    )

    monkeypatch.setattr(
        main_module,
        "configure_logging",
        configure_logging_mock,
    )

    monkeypatch.setattr(
        main_module,
        "create_postgres_runtime",
        create_postgres_runtime_mock,
    )

    monkeypatch.setattr(
        main_module,
        "configure_game_repository",
        Mock(),
    )

    monkeypatch.setattr(
        main_module,
        "configure_lobby_message_repository",
        Mock(),
    )

    monkeypatch.setattr(
        main_module,
        "create_bot",
        create_bot_mock,
    )

    monkeypatch.setattr(
        main_module,
        "DiscordPySessionRecoveryGateway",
        Mock(
            return_value=object(),
        ),
    )

    monkeypatch.setattr(
        main_module,
        "RecoverGameSessions",
        recover_game_sessions_mock,
    )

    await main_module.run(settings)

    configure_logging_mock.assert_called_once_with(
        level=LogLevel.DEBUG.value,
        sensitive_values=(
            "discord-secret",
            (
                "postgresql+asyncpg://"
                "user:password@postgres:5432/test_db"
            ),
        ),
    )

    create_postgres_runtime_mock.assert_called_once_with(
            "postgresql+asyncpg://"
            "user:password@postgres:5432/test_db"
        
    )

    bot.start.assert_awaited_once_with(
        "discord-secret"
    )

    runtime.close.assert_awaited_once()


def test_main_preserves_existing_environment_over_dotenv(
    monkeypatch,
    tmp_path: Path,
) -> None:
    dotenv_path = (
        tmp_path / ".env"
    )

    dotenv_path.write_text(
        "LOG_LEVEL=INFO\n",
        encoding="utf-8",
    )

    monkeypatch.setenv(
        "DISCORD_TOKEN",
        "test-token",
    )

    monkeypatch.setenv(
        "DATABASE_URL",
        (
            "postgresql+asyncpg://"
            "user:password@localhost/test_db"
        ),
    )

    monkeypatch.setenv(
        "LOG_LEVEL",
        "DEBUG",
    )

    captured_settings: list[
        AppSettings
    ] = []

    def load_test_dotenv(
        *,
        override: bool,
    ) -> bool:
        return real_load_dotenv(
            dotenv_path=dotenv_path,
            override=override,
        )

    async def fake_run(
        settings: AppSettings,
    ) -> None:
        captured_settings.append(
            settings
        )

    monkeypatch.setattr(
        main_module,
        "load_dotenv",
        load_test_dotenv,
    )

    monkeypatch.setattr(
        main_module,
        "run",
        fake_run,
    )

    main_module.main()

    assert len(
        captured_settings
    ) == 1

    assert (
        captured_settings[0].log_level
        is LogLevel.DEBUG
    )


def test_invalid_configuration_fails_before_runtime(
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "DISCORD_TOKEN",
        raising=False,
    )

    monkeypatch.setenv(
        "DATABASE_URL",
        (
            "postgresql+asyncpg://"
            "user:password@localhost/test_db"
        ),
    )

    monkeypatch.setattr(
        main_module,
        "load_dotenv",
        lambda *, override: None,
    )

    run_mock = Mock()

    monkeypatch.setattr(
        main_module,
        "run",
        run_mock,
    )

    with pytest.raises(
        ConfigurationError,
        match="DISCORD_TOKEN",
    ):
        main_module.main()

    run_mock.assert_not_called()


def test_imports_do_not_require_application_environment() -> None:
    repo_root = (
        Path(__file__).resolve().parents[2]
    )

    environ = os.environ.copy()

    for variable in (
        "DISCORD_TOKEN",
        "DATABASE_URL",
        "LOG_LEVEL",
        "ENVIRONMENT",
    ):
        environ.pop(
            variable,
            None,
        )

    src_path = str(
        repo_root / "src"
    )

    existing_pythonpath = (
        environ.get("PYTHONPATH")
    )

    environ["PYTHONPATH"] = (
        src_path
        if not existing_pythonpath
        else os.pathsep.join(
            (
                src_path,
                existing_pythonpath,
            )
        )
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import impostor_bot.config; "
                "import impostor_bot.main"
            ),
        ],
        cwd=repo_root,
        env=environ,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        result.stderr
    )