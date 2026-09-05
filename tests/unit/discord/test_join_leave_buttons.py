import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from impostor_bot.discord.views import (
    handle_join_button,
    handle_leave_button,
)

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey


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
        message=SimpleNamespace(
            edit=AsyncMock(),
        ),
    )


def test_join_button_maps_interaction_to_use_case():
    game = Game.create(host_id=1)
    game.add_player(2)

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        )
    )

    interaction = create_interaction()

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

    interaction.response.defer.assert_awaited_once()

    interaction.message.edit.assert_awaited_once()

    interaction.followup.send.assert_awaited_once()

    interaction.response.send_message.assert_not_awaited()


def test_leave_button_maps_interaction_to_use_case():
    game = Game.create(host_id=1)
    game.add_player(2)

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        )
    )

    interaction = create_interaction()

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

    interaction.response.defer.assert_awaited_once()

    interaction.message.edit.assert_awaited_once()

    interaction.followup.send.assert_awaited_once()

    interaction.response.send_message.assert_not_awaited()
