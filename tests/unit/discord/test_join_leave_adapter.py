import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from impostor_bot.discord.commands import (
    handle_join,
    handle_leave,
)
import logging

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.application.exceptions import GameNotFoundError


def create_interaction(
    user_id: int = 2,
    guild_id: int = 100,
    channel_id: int = 200,
    interaction_id: int = 1000,
):
    return SimpleNamespace(
        id=interaction_id,
        guild_id=guild_id,
        channel_id=channel_id,
        channel=SimpleNamespace(
            id=channel_id,
        ),
        user=SimpleNamespace(
            id=user_id,
        ),
        client=SimpleNamespace(),
        response=SimpleNamespace(
            defer=AsyncMock(),
            is_done=lambda: True,
            send_message=AsyncMock(),
        ),
        followup=SimpleNamespace(
            send=AsyncMock(),
        ),
    )

def create_logging_interaction(
    user_id: int = 2,
):
    response_done = False

    async def defer(
        *args,
        **kwargs,
    ):
        nonlocal response_done
        response_done = True

    return SimpleNamespace(
        id=500,
        guild_id=100,
        channel_id=200,
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

def test_join_handler_logs_player_joined(
    caplog,
):
    game = Game.create(
        host_id=1
    )

    game.add_player(2)

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        )
    )

    interaction = (
        create_logging_interaction(
            user_id=2
        )
    )

    caplog.set_level(logging.INFO)

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

    record = next(
        record
        for record in caplog.records
        if getattr(
            record,
            "event",
            None,
        )
        == "player_joined"
    )

    assert record.context[
        "guild_id"
    ] == 100

    assert record.context[
        "channel_id"
    ] == 200

    assert record.context[
        "player_count"
    ] == len(game.players)


def test_leave_handler_logs_player_left(
    caplog,
):
    game = Game.create(
        host_id=1
    )

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        )
    )

    interaction = (
        create_logging_interaction(
            user_id=2
        )
    )

    caplog.set_level(logging.INFO)

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

    record = next(
        record
        for record in caplog.records
        if getattr(
            record,
            "event",
            None,
        )
        == "player_left"
    )

    assert record.context[
        "guild_id"
    ] == 100

    assert record.context[
        "channel_id"
    ] == 200

    assert record.context[
        "player_count"
    ] == len(game.players)