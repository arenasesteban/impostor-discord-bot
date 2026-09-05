import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from impostor_bot.discord.commands import handle_status
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey


def create_interaction(
    guild_id: int,
    channel_id: int,
):
    response_done = False

    async def defer(*args, **kwargs):
        nonlocal response_done
        response_done = True

    return SimpleNamespace(
        guild_id=guild_id,
        channel=SimpleNamespace(
            id=channel_id,
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
    )


def test_status_handler_uses_full_game_session_key():
    game = Game.create(host_id=1)

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        ),
    )

    interaction = create_interaction(
        guild_id=100,
        channel_id=200,
    )

    asyncio.run(
        handle_status(
            interaction=interaction,
            use_case=use_case,
        )
    )

    use_case.execute.assert_awaited_once_with(
        key=GameSessionKey(
            guild_id=100,
            channel_id=200,
        ),
    )

    interaction.response.defer.assert_awaited_once_with(
        ephemeral=True,
        thinking=True,
    )

    interaction.followup.send.assert_awaited_once()

    interaction.response.send_message.assert_not_awaited()


def test_status_handler_preserves_guild_id():
    game = Game.create(host_id=1)

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        ),
    )

    interaction = create_interaction(
        guild_id=999,
        channel_id=200,
    )

    asyncio.run(
        handle_status(
            interaction=interaction,
            use_case=use_case,
        )
    )

    use_case.execute.assert_awaited_once_with(
        key=GameSessionKey(
            guild_id=999,
            channel_id=200,
        ),
    )

    interaction.response.defer.assert_awaited_once_with(
        ephemeral=True,
        thinking=True,
    )

    interaction.followup.send.assert_awaited_once()