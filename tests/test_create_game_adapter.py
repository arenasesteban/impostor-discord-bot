import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from impostor_bot.discord.commands import handle_create
from impostor_bot.discord.state import active_lobby_messages
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey


def test_create_handler_maps_discord_data_to_use_case():
    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=Game.create(host_id=300)
        )
    )

    interaction = SimpleNamespace(
        guild_id=100,
        channel=SimpleNamespace(id=200),
        user=SimpleNamespace(id=300),
        response=SimpleNamespace(
            send_message=AsyncMock()
        ),
        original_response=AsyncMock(
            return_value=SimpleNamespace(id=999)
        ),
    )

    asyncio.run(
        handle_create(
            interaction=interaction,
            use_case=use_case,
        )
    )

    use_case.execute.assert_awaited_once_with(
        key=GameSessionKey(
            guild_id=100,
            channel_id=200,
        ),
        host_id=300,
    )

    assert active_lobby_messages[200] == 999

    active_lobby_messages.pop(200, None)