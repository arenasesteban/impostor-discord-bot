import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from impostor_bot.discord.commands import (
    handle_join,
    handle_leave,
)

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.application.exceptions import GameNotFoundError


def test_join_handler_maps_discord_data_to_use_case():
    game = Game.create(host_id=1)
    game.add_player(2)

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        )
    )

    interaction = SimpleNamespace(
        guild_id=100,
        channel=SimpleNamespace(id=200),
        user=SimpleNamespace(id=2),
        client=SimpleNamespace(),
        response=SimpleNamespace(
            send_message=AsyncMock(),
        ),
    )

    with patch(
        "impostor_bot.discord.commands.refresh_lobby_message",
        new=AsyncMock(),
    ):
        asyncio.run(
            handle_join(
                interaction=interaction,
                use_case=use_case,
            )
        )

    use_case.execute.assert_awaited_once()

    call = use_case.execute.await_args

    assert call.kwargs["key"] == GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    assert call.kwargs["player"].id == 2


def test_leave_handler_maps_discord_data_to_use_case():
    game = Game.create(host_id=1)
    game.add_player(2)

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        )
    )

    interaction = SimpleNamespace(
        guild_id=100,
        channel=SimpleNamespace(id=200),
        user=SimpleNamespace(id=2),
        client=SimpleNamespace(),
        response=SimpleNamespace(
            send_message=AsyncMock(),
        ),
    )

    with patch(
        "impostor_bot.discord.commands.refresh_lobby_message",
        new=AsyncMock(),
    ):
        asyncio.run(
            handle_leave(
                interaction=interaction,
                use_case=use_case,
            )
        )

    call = use_case.execute.await_args

    assert call.kwargs["key"] == GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    assert call.kwargs["player"].id == 2


def test_join_handler_reports_missing_game():
    use_case = SimpleNamespace(
        execute=AsyncMock(
            side_effect=GameNotFoundError(
                "There is no open game in this channel."
            )
        )
    )

    interaction = SimpleNamespace(
        guild_id=100,
        channel=SimpleNamespace(id=200),
        user=SimpleNamespace(id=2),
        client=SimpleNamespace(),
        response=SimpleNamespace(
            send_message=AsyncMock(),
        ),
    )

    asyncio.run(
        handle_join(
            interaction=interaction,
            use_case=use_case,
        )
    )

    interaction.response.send_message.assert_awaited_once()