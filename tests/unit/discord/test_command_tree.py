from unittest.mock import (
    AsyncMock,
    MagicMock,
    patch,
)

import discord
import pytest
from discord import app_commands

from impostor_bot.discord.command_tree import (
    ImpostorCommandTree,
)


@pytest.mark.asyncio
async def test_command_tree_unwraps_command_invoke_error():
    interaction = MagicMock(
        spec=discord.Interaction
    )

    command = MagicMock()
    command.name = "test"

    original_error = RuntimeError(
        "boom"
    )

    wrapped_error = (
        app_commands.CommandInvokeError(
            command,
            original_error,
        )
    )

    tree = MagicMock(
        spec=ImpostorCommandTree
    )

    with patch(
        "impostor_bot.discord.command_tree."
        "handle_unexpected_error",
        new=AsyncMock(),
    ) as handler:
        await ImpostorCommandTree.on_error(
            tree,
            interaction,
            wrapped_error,
        )

    handler.assert_awaited_once_with(
        interaction,
        original_error,
    )


@pytest.mark.asyncio
async def test_command_tree_preserves_non_invoke_error():
    interaction = MagicMock(
        spec=discord.Interaction
    )

    error = app_commands.AppCommandError(
        "boom"
    )

    tree = MagicMock(
        spec=ImpostorCommandTree
    )

    with patch(
        "impostor_bot.discord.command_tree."
        "handle_unexpected_error",
        new=AsyncMock(),
    ) as handler:
        await ImpostorCommandTree.on_error(
            tree,
            interaction,
            error,
        )

    handler.assert_awaited_once_with(
        interaction,
        error,
    )