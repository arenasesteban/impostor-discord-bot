import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from impostor_bot.application.exceptions import (
    NotGameHostError,
)
from impostor_bot.application.start_game import (
    StartGameResult,
)
from impostor_bot.constants import IMPOSTOR_ROLE
from impostor_bot.discord.commands import handle_start
from impostor_bot.game.exceptions import NotEnoughPlayersError
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey


def create_ready_game() -> Game:
    game = Game.create(host_id=1)
    game.add_player(2)
    game.add_player(3)

    return game


def create_start_result() -> StartGameResult:
    game = create_ready_game()

    return StartGameResult(
        game=game,
        roles={
            1: "pizza",
            2: IMPOSTOR_ROLE,
            3: "pizza",
        },
    )


def create_interaction():
    return SimpleNamespace(
        guild_id=100,
        channel=SimpleNamespace(
            id=200,
        ),
        user=SimpleNamespace(
            id=1,
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


def test_start_handler_executes_use_case_and_releases_session():
    result = create_start_result()

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=result,
        )
    )

    release_use_case = SimpleNamespace(
        execute=AsyncMock(),
    )

    interaction = create_interaction()

    with (
        patch(
            "impostor_bot.discord.commands.deliver_roles",
            new=AsyncMock(
                return_value=[],
            ),
        ),
        patch(
            "impostor_bot.discord.commands.close_lobby_message",
            new=AsyncMock(),
        ),
        patch(
            "impostor_bot.discord.commands.LobbyView",
        ),
    ):
        asyncio.run(
            handle_start(
                interaction=interaction,
                use_case=use_case,
                release_use_case=release_use_case,
            )
        )

    use_case.execute.assert_awaited_once_with(
        key=GameSessionKey(
            guild_id=100,
            channel_id=200,
        ),
        requester_id=1,
    )

    release_use_case.execute.assert_awaited_once_with(
        GameSessionKey(
            guild_id=100,
            channel_id=200,
        )
    )

    interaction.response.defer.assert_awaited_once()

    interaction.followup.send.assert_awaited_once()


def test_start_handler_releases_game_when_dm_delivery_fails():
    result = create_start_result()

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=result,
        )
    )

    release_use_case = SimpleNamespace(
        execute=AsyncMock(),
    )

    interaction = create_interaction()

    with (
        patch(
            "impostor_bot.discord.commands.deliver_roles",
            new=AsyncMock(
                return_value=[3],
            ),
        ),
        patch(
            "impostor_bot.discord.commands.close_lobby_message",
            new=AsyncMock(),
        ),
        patch(
            "impostor_bot.discord.commands.LobbyView",
        ),
    ):
        asyncio.run(
            handle_start(
                interaction=interaction,
                use_case=use_case,
                release_use_case=release_use_case,
            )
        )

    release_use_case.execute.assert_awaited_once_with(
        GameSessionKey(
            guild_id=100,
            channel_id=200,
        )
    )

    interaction.followup.send.assert_awaited_once()


def test_start_handler_reports_insufficient_players_with_followup():
    use_case = SimpleNamespace(
        execute=AsyncMock(
            side_effect=NotEnoughPlayersError(
                "Not enough players."
            )
        )
    )

    release_use_case = SimpleNamespace(
        execute=AsyncMock(),
    )

    interaction = create_interaction()

    asyncio.run(
        handle_start(
            interaction=interaction,
            use_case=use_case,
            release_use_case=release_use_case,
        )
    )

    interaction.response.defer.assert_awaited_once()

    interaction.followup.send.assert_awaited_once()

    interaction.response.send_message.assert_not_awaited()

    release_use_case.execute.assert_not_awaited()


def test_start_handler_reports_non_host_with_followup():
    use_case = SimpleNamespace(
        execute=AsyncMock(
            side_effect=NotGameHostError(
                "Only the host can start the game."
            )
        )
    )

    release_use_case = SimpleNamespace(
        execute=AsyncMock(),
    )

    interaction = create_interaction()

    interaction.user.id = 2

    asyncio.run(
        handle_start(
            interaction=interaction,
            use_case=use_case,
            release_use_case=release_use_case,
        )
    )

    use_case.execute.assert_awaited_once_with(
        key=GameSessionKey(
            guild_id=100,
            channel_id=200,
        ),
        requester_id=2,
    )

    interaction.followup.send.assert_awaited_once()

    interaction.response.send_message.assert_not_awaited()

    release_use_case.execute.assert_not_awaited()