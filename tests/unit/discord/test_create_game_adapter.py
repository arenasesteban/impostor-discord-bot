import asyncio
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from impostor_bot.discord.commands import handle_create
from impostor_bot.discord.state import (
    active_lobby_messages,
)
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import (
    GameSessionKey,
)


@pytest.fixture(autouse=True)
def clear_active_lobby_messages():
    active_lobby_messages.clear()

    yield

    active_lobby_messages.clear()


def test_create_handler_maps_discord_data_to_use_case():
    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=Game.create(host_id=300)
        )
    )

    lobby_repository = SimpleNamespace(
        save=AsyncMock(),
    )

    message = SimpleNamespace(
        id=999,
    )

    response_done = False


    async def defer(*args, **kwargs):
        nonlocal response_done
        response_done = True


    interaction = SimpleNamespace(
        guild_id=100,
        channel=SimpleNamespace(
            id=200,
        ),
        user=SimpleNamespace(
            id=300,
        ),
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
        edit_original_response=AsyncMock(
            return_value=message,
        ),
    )

    asyncio.run(
        handle_create(
            interaction=interaction,
            use_case=use_case,
            lobby_repository=lobby_repository,
        )
    )

    interaction.response.defer.assert_awaited_once_with(
        thinking=True,
    )

    interaction.edit_original_response.assert_awaited_once()

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    use_case.execute.assert_awaited_once_with(
        key=key,
        host_id=300,
    )

    lobby_repository.save.assert_awaited_once_with(
        key=key,
        message_id=999,
    )


def test_create_handler_persists_lobby_message_metadata():
    game = Game.create(
        host_id=1
    )

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game
        )
    )

    lobby_repository = SimpleNamespace(
        save=AsyncMock()
    )

    message = SimpleNamespace(
        id=999,
    )

    response_done = False


    async def defer(*args, **kwargs):
        nonlocal response_done
        response_done = True


    interaction = SimpleNamespace(
        guild_id=100,
        channel=SimpleNamespace(
            id=200,
        ),
        user=SimpleNamespace(
            id=1,
        ),
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
        edit_original_response=AsyncMock(
            return_value=message,
        ),
    )

    asyncio.run(
        handle_create(
            interaction=interaction,
            use_case=use_case,
            lobby_repository=lobby_repository,
        )
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    use_case.execute.assert_awaited_once_with(
        key=key,
        host_id=1,
    )

    lobby_repository.save.assert_awaited_once_with(
        key=key,
        message_id=999,
    )

    assert active_lobby_messages[key] == 999

def test_create_handler_logs_game_created(
    caplog,
):
    game = Game.create(
        host_id=300
    )

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        )
    )

    lobby_repository = SimpleNamespace(
        save=AsyncMock(),
    )

    message = SimpleNamespace(
        id=999,
    )

    response_done = False

    async def defer(
        *args,
        **kwargs,
    ):
        nonlocal response_done
        response_done = True

    interaction = SimpleNamespace(
        id=500,
        guild_id=100,
        channel_id=200,
        channel=SimpleNamespace(
            id=200,
        ),
        user=SimpleNamespace(
            id=300,
        ),
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
        edit_original_response=AsyncMock(
            return_value=message,
        ),
    )

    caplog.set_level(logging.INFO)

    asyncio.run(
        handle_create(
            interaction=interaction,
            use_case=use_case,
            lobby_repository=lobby_repository,
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
        == "game_created"
    )

    assert record.context[
        "guild_id"
    ] == 100

    assert record.context[
        "channel_id"
    ] == 200