import discord
import pytest

from impostor_bot.discord.views import LobbyView



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