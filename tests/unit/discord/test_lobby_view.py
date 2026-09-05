
import discord
import pytest

from unittest.mock import (
    AsyncMock,
    MagicMock,
    patch,
)

from impostor_bot.discord.views import (
    LobbyView,
)



@pytest.mark.asyncio
async def test_lobby_view_is_persistent():
    view = LobbyView()

    try:
        assert view.timeout is None
        assert view.is_persistent()
    finally:
        view.stop()



@pytest.mark.asyncio
async def test_lobby_view_uses_stable_custom_ids():
    view = LobbyView()

    try:
        custom_ids = {
            item.custom_id
            for item in view.children
            if isinstance(
                item,
                discord.ui.Button,
            )
        }

        assert custom_ids == {
            "impostor:lobby:join:v1",
            "impostor:lobby:leave:v1",
        }

    finally:
        view.stop()


@pytest.mark.asyncio
async def test_lobby_view_delegates_unexpected_error():
    view = LobbyView()

    interaction = MagicMock(
        spec=discord.Interaction
    )

    error = RuntimeError(
        "boom"
    )

    item = MagicMock(
        spec=discord.ui.Item
    )

    with patch(
        "impostor_bot.discord.views."
        "handle_unexpected_error",
        new=AsyncMock(),
    ) as handler:
        await view.on_error(
            interaction,
            error,
            item,
        )

    handler.assert_awaited_once_with(
        interaction,
        error,
    )