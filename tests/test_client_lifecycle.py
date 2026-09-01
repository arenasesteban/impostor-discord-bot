from unittest.mock import AsyncMock, Mock, patch

import discord
import pytest

from impostor_bot.discord.client import create_bot


@pytest.mark.asyncio
async def test_startup_hooks_run_in_order():
    calls = []

    async def database():
        calls.append("database")

    async def recovery():
        calls.append("recovery")

    bot = create_bot(
        startup_hooks=(
            database,
            recovery,
        )
    )

    add_command = Mock(
        side_effect=lambda *_: calls.append(
            "commands"
        )
    )

    sync = AsyncMock(
        side_effect=lambda: calls.append(
            "sync"
        )
    )

    with (
        patch.object(
            bot.tree,
            "add_command",
            add_command,
        ),
        patch.object(
            bot.tree,
            "sync",
            sync,
        ),
    ):
        await bot.setup_hook()

    assert calls == [
        "database",
        "recovery",
        "commands",
        "sync",
    ]

    add_command.assert_called_once()
    sync.assert_awaited_once()


@pytest.mark.asyncio
async def test_failed_startup_hook_aborts_startup():
    calls = []

    async def database():
        calls.append("database")

    async def recovery():
        calls.append("recovery")

        raise RuntimeError(
            "recovery failed"
        )

    async def never_run():
        calls.append("later")

    bot = create_bot(
        startup_hooks=(
            database,
            recovery,
            never_run,
        )
    )

    add_command = Mock()
    sync = AsyncMock()

    with (
        patch.object(
            bot.tree,
            "add_command",
            add_command,
        ),
        patch.object(
            bot.tree,
            "sync",
            sync,
        ),
    ):
        with pytest.raises(
            RuntimeError,
            match="recovery failed",
        ):
            await bot.setup_hook()

    assert calls == [
        "database",
        "recovery",
    ]

    add_command.assert_not_called()
    sync.assert_not_awaited()

    assert (
        bot._startup_completed
        is False
    )


@pytest.mark.asyncio
async def test_completed_startup_is_not_repeated():
    calls = []

    async def startup():
        calls.append("startup")

    bot = create_bot(
        startup_hooks=(
            startup,
        )
    )

    add_command = Mock()
    sync = AsyncMock()

    with (
        patch.object(
            bot.tree,
            "add_command",
            add_command,
        ),
        patch.object(
            bot.tree,
            "sync",
            sync,
        ),
    ):
        await bot.setup_hook()
        await bot.setup_hook()

    assert calls == [
        "startup",
    ]

    add_command.assert_called_once()
    sync.assert_awaited_once()

    assert (
        bot._startup_completed
        is True
    )


@pytest.mark.asyncio
async def test_shutdown_hooks_run_once_in_reverse_order():
    calls = []

    async def database():
        calls.append("database")

    async def other_resource():
        calls.append("other")

    bot = create_bot(
        shutdown_hooks=(
            database,
            other_resource,
        )
    )

    parent_close = AsyncMock()

    with patch.object(
        discord.Client,
        "close",
        parent_close,
    ):
        await bot.close()
        await bot.close()

    assert calls == [
        "other",
        "database",
    ]

    assert (
        bot._shutdown_completed
        is True
    )