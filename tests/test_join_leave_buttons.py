import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from impostor_bot.discord.views import (
    handle_join_button,
    handle_leave_button,
)

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey


def test_join_button_maps_interaction_to_use_case():
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
        response=SimpleNamespace(
            edit_message=AsyncMock(),
            send_message=AsyncMock(),
        ),
        followup=SimpleNamespace(
            send=AsyncMock(),
        ),
    )

    view = SimpleNamespace()

    asyncio.run(
        handle_join_button(
            interaction=interaction,
            view=view,
            use_case=use_case,
        )
    )

    call = use_case.execute.await_args

    assert call.kwargs["key"] == GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    assert call.kwargs["player"].id == 2

    interaction.response.edit_message.assert_awaited_once()
    interaction.followup.send.assert_awaited_once()


def test_leave_button_maps_interaction_to_use_case():
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
        response=SimpleNamespace(
            edit_message=AsyncMock(),
            send_message=AsyncMock(),
        ),
        followup=SimpleNamespace(
            send=AsyncMock(),
        ),
    )

    view = SimpleNamespace()

    asyncio.run(
        handle_leave_button(
            interaction=interaction,
            view=view,
            use_case=use_case,
        )
    )

    call = use_case.execute.await_args

    assert call.kwargs["key"] == GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    assert call.kwargs["player"].id == 2

    interaction.response.edit_message.assert_awaited_once()
    interaction.followup.send.assert_awaited_once()
