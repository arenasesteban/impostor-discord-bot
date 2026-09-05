import logging
from unittest.mock import (
    AsyncMock,
    patch,
)

import pytest

from impostor_bot.discord.client import (
    create_bot,
)


def get_event_records(
    caplog: pytest.LogCaptureFixture,
    event: str,
) -> list[logging.LogRecord]:
    return [
        record
        for record in caplog.records
        if getattr(
            record,
            "event",
            None,
        )
        == event
    ]


@pytest.mark.asyncio
async def test_startup_failure_is_logged_and_propagated(
    caplog: pytest.LogCaptureFixture,
):
    async def failing_hook() -> None:
        raise RuntimeError(
            "startup exploded"
        )

    bot = create_bot(
        startup_hooks=(
            failing_hook,
        )
    )

    caplog.set_level(
        logging.CRITICAL,
        logger="impostor_bot.discord.client",
    )

    with (
        patch.object(
            bot.tree,
            "add_command",
        ) as add_command,
        patch.object(
            bot.tree,
            "sync",
            new=AsyncMock(),
        ) as sync,
    ):
        with pytest.raises(
            RuntimeError,
            match="startup exploded",
        ):
            await bot.setup_hook()

        add_command.assert_not_called()
        sync.assert_not_awaited()

    records = get_event_records(
        caplog,
        "startup_failed",
    )

    assert len(records) == 1

    record = records[0]

    assert (
        record.levelno
        == logging.CRITICAL
    )

    assert record.exc_info is not None

    assert bot._startup_completed is False


@pytest.mark.asyncio
async def test_successful_startup_is_logged_once(
    caplog: pytest.LogCaptureFixture,
):
    calls: list[str] = []

    async def startup_hook() -> None:
        calls.append(
            "startup"
        )

    bot = create_bot(
        startup_hooks=(
            startup_hook,
        )
    )

    caplog.set_level(
        logging.INFO,
        logger="impostor_bot.discord.client",
    )

    with (
        patch.object(
            bot.tree,
            "add_command",
        ) as add_command,
        patch.object(
            bot.tree,
            "sync",
            new=AsyncMock(),
        ) as sync,
    ):
        await bot.setup_hook()
        await bot.setup_hook()

        add_command.assert_called_once()
        sync.assert_awaited_once()

    assert calls == [
        "startup"
    ]

    records = get_event_records(
        caplog,
        "bot_started",
    )

    assert len(records) == 1

    assert (
        records[0].levelno
        == logging.INFO
    )


@pytest.mark.asyncio
async def test_successful_shutdown_logs_bot_stopped_once(
    caplog: pytest.LogCaptureFixture,
):
    calls: list[str] = []

    async def first_hook() -> None:
        calls.append(
            "first"
        )

    async def second_hook() -> None:
        calls.append(
            "second"
        )

    bot = create_bot(
        shutdown_hooks=(
            first_hook,
            second_hook,
        )
    )

    caplog.set_level(
        logging.INFO,
        logger="impostor_bot.discord.client",
    )

    discord_close = AsyncMock()

    with patch(
        "discord.Client.close",
        new=discord_close,
    ):
        await bot.close()
        await bot.close()

    assert calls == [
        "second",
        "first",
    ]

    records = get_event_records(
        caplog,
        "bot_stopped",
    )

    assert len(records) == 1

    assert (
        records[0].levelno
        == logging.INFO
    )


@pytest.mark.asyncio
async def test_shutdown_continues_after_hook_failure_and_propagates_error(
    caplog: pytest.LogCaptureFixture,
):
    calls: list[str] = []

    async def hook_a() -> None:
        calls.append("A")

    async def hook_b() -> None:
        calls.append("B")

        raise RuntimeError(
            "hook B failed"
        )

    async def hook_c() -> None:
        calls.append("C")

    bot = create_bot(
        shutdown_hooks=(
            hook_c,
            hook_b,
            hook_a,
        )
    )

    caplog.set_level(
        logging.INFO,
        logger="impostor_bot.discord.client",
    )

    discord_close = AsyncMock()

    with patch(
        "discord.Client.close",
        new=discord_close,
    ):
        with pytest.raises(
            RuntimeError,
            match="hook B failed",
        ):
            await bot.close()

    assert calls == [
        "A",
        "B",
        "C",
    ]

    failed_records = get_event_records(
        caplog,
        "shutdown_hook_failed",
    )

    assert len(
        failed_records
    ) == 1

    assert (
        failed_records[0].levelno
        == logging.ERROR
    )

    assert (
        failed_records[0].exc_info
        is not None
    )

    stopped_records = get_event_records(
        caplog,
        "bot_stopped",
    )

    assert stopped_records == []