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


def create_interaction(
    user_id: int = 2,
):
    response_done = False

    async def defer(*args, **kwargs):
        nonlocal response_done
        response_done = True

    return SimpleNamespace(
        guild_id=100,
        channel=SimpleNamespace(
            id=200,
        ),
        user=SimpleNamespace(
            id=user_id,
        ),
        client=SimpleNamespace(),
        response=SimpleNamespace(
            defer=AsyncMock(
                side_effect=defer,
            ),
            is_done=lambda: response_done,
            send_message=AsyncMock(),
        ),
        followup=SimpleNamespace(
            send=AsyncMock(),
        ),
    )


def test_join_handler_maps_discord_data_to_use_case():
    game = Game.create(host_id=1)
    game.add_player(2)

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        )
    )

    interaction = create_interaction()

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

    interaction = create_interaction()

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

    interaction = create_interaction()
    
    asyncio.run(
        handle_join(
            interaction=interaction,
            use_case=use_case,
        )
    )

    interaction.response.defer.assert_awaited_once_with(
        thinking=True,
        ephemeral=True,
    )

    interaction.followup.send.assert_awaited_once()