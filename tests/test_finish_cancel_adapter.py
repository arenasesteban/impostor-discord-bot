import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import logging

from impostor_bot.application.exceptions import (
    GameNotFoundError,
    NotGameHostError,
)
from impostor_bot.discord.commands import (
    handle_cancel,
    handle_finish,
)
from impostor_bot.game.exceptions import InvalidGameStateError
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.game.state import GameState
from impostor_bot.discord.messages import (
    build_game_cancelled_message,
)


def create_waiting_game() -> Game:
    return Game.create(host_id=1)


def create_started_game() -> Game:
    game = Game.create(host_id=1)
    game.add_player(2)
    game.add_player(3)

    game.start_game(
        secret_word="pizza",
        impostor_id=2,
    )

    return game


def create_finished_game() -> Game:
    game = create_started_game()
    game.finish()

    return game


def create_cancelled_waiting_game() -> Game:
    game = create_waiting_game()
    game.cancel()

    return game


def create_cancelled_started_game() -> Game:
    game = create_started_game()
    game.cancel()

    return game


def create_interaction(
    user_id: int = 1,
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

def test_finish_handler_maps_interaction_and_closes_lobby():
    game = create_finished_game()

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        )
    )

    interaction = create_interaction()

    with (
        patch(
            "impostor_bot.discord.commands.close_lobby_message",
            new=AsyncMock(),
        ) as close_lobby_mock,
        patch(
            "impostor_bot.discord.commands.LobbyView",
        ),
    ):
        asyncio.run(
            handle_finish(
                interaction=interaction,
                use_case=use_case,
            )
        )

    use_case.execute.assert_awaited_once_with(
        key=GameSessionKey(
            guild_id=100,
            channel_id=200,
        ),
        requester_id=1,
    )

    assert game.status == GameState.FINISHED

    close_lobby_mock.assert_awaited_once()

    interaction.response.defer.assert_awaited_once_with(
        thinking=True,
    )
    interaction.followup.send.assert_awaited_once()
    interaction.response.send_message.assert_not_awaited()


def test_finish_handler_rejects_non_host():
    use_case = SimpleNamespace(
        execute=AsyncMock(
            side_effect=NotGameHostError(
                "Only the host can finish the game."
            )
        )
    )

    interaction = create_interaction(
        user_id=2,
    )

    with patch(
        "impostor_bot.discord.commands.close_lobby_message",
        new=AsyncMock(),
    ) as close_lobby_mock:
        asyncio.run(
            handle_finish(
                interaction=interaction,
                use_case=use_case,
            )
        )

    use_case.execute.assert_awaited_once_with(
        key=GameSessionKey(
            guild_id=100,
            channel_id=200,
        ),
        requester_id=2,
    )

    close_lobby_mock.assert_not_awaited()

    interaction.response.defer.assert_awaited_once_with(
        thinking=True,
    )

    interaction.followup.send.assert_awaited_once()

    interaction.response.send_message.assert_not_awaited()


def test_finish_handler_rejects_invalid_state():
    use_case = SimpleNamespace(
        execute=AsyncMock(
            side_effect=InvalidGameStateError(
                "Only a started game can be finished."
            )
        )
    )

    interaction = create_interaction()

    with patch(
        "impostor_bot.discord.commands.close_lobby_message",
        new=AsyncMock(),
    ) as close_lobby_mock:
        asyncio.run(
            handle_finish(
                interaction=interaction,
                use_case=use_case,
            )
        )

    close_lobby_mock.assert_not_awaited()

    interaction.response.defer.assert_awaited_once_with(
        thinking=True,
    )

    interaction.followup.send.assert_awaited_once()

    interaction.response.send_message.assert_not_awaited()


def test_finish_handler_reports_missing_game():
    use_case = SimpleNamespace(
        execute=AsyncMock(
            side_effect=GameNotFoundError(
                "There is no active game in this channel."
            )
        )
    )

    interaction = create_interaction()

    with patch(
        "impostor_bot.discord.commands.close_lobby_message",
        new=AsyncMock(),
    ) as close_lobby_mock:
        asyncio.run(
            handle_finish(
                interaction=interaction,
                use_case=use_case,
            )
        )

    close_lobby_mock.assert_not_awaited()

    interaction.response.defer.assert_awaited_once_with(
        thinking=True,
    )

    interaction.followup.send.assert_awaited_once()

    interaction.response.send_message.assert_not_awaited()


def test_cancel_handler_cancels_waiting_game():
    game = create_cancelled_waiting_game()

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        )
    )

    interaction = create_interaction()

    with (
        patch(
            "impostor_bot.discord.commands.close_lobby_message",
            new=AsyncMock(),
        ) as close_lobby_mock,
        patch(
            "impostor_bot.discord.commands.LobbyView",
        ),
    ):
        asyncio.run(
            handle_cancel(
                interaction=interaction,
                use_case=use_case,
            )
        )

    use_case.execute.assert_awaited_once_with(
        key=GameSessionKey(
            guild_id=100,
            channel_id=200,
        ),
        requester_id=1,
    )

    assert game.status == GameState.CANCELLED

    close_lobby_mock.assert_awaited_once()

    interaction.response.defer.assert_awaited_once_with(
        thinking=True,
    )

    interaction.followup.send.assert_awaited_once_with(
        build_game_cancelled_message(),
        ephemeral=False,
    )

    interaction.response.send_message.assert_not_awaited()


def test_cancel_handler_cancels_started_game():
    game = create_cancelled_started_game()

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        )
    )

    interaction = create_interaction()

    with (
        patch(
            "impostor_bot.discord.commands.close_lobby_message",
            new=AsyncMock(),
        ) as close_lobby_mock,
        patch(
            "impostor_bot.discord.commands.LobbyView",
        ),
    ):
        asyncio.run(
            handle_cancel(
                interaction=interaction,
                use_case=use_case,
            )
        )

    use_case.execute.assert_awaited_once_with(
        key=GameSessionKey(
            guild_id=100,
            channel_id=200,
        ),
        requester_id=1,
    )

    assert game.status == GameState.CANCELLED

    close_lobby_mock.assert_awaited_once()

    interaction.response.defer.assert_awaited_once_with(
        thinking=True,
    )

    interaction.followup.send.assert_awaited_once_with(
        build_game_cancelled_message(),
        ephemeral=False,
    )

    interaction.response.send_message.assert_not_awaited()


def test_cancel_handler_rejects_non_host():
    use_case = SimpleNamespace(
        execute=AsyncMock(
            side_effect=NotGameHostError(
                "Only the host can cancel the game."
            )
        )
    )

    interaction = create_interaction(
        user_id=2,
    )

    with patch(
        "impostor_bot.discord.commands.close_lobby_message",
        new=AsyncMock(),
    ) as close_lobby_mock:
        asyncio.run(
            handle_cancel(
                interaction=interaction,
                use_case=use_case,
            )
        )

    use_case.execute.assert_awaited_once_with(
        key=GameSessionKey(
            guild_id=100,
            channel_id=200,
        ),
        requester_id=2,
    )

    close_lobby_mock.assert_not_awaited()

    interaction.response.defer.assert_awaited_once_with(
        thinking=True,
    )

    interaction.followup.send.assert_awaited_once()

    interaction.response.send_message.assert_not_awaited()


def test_cancel_handler_reports_missing_game():
    use_case = SimpleNamespace(
        execute=AsyncMock(
            side_effect=GameNotFoundError(
                "There is no active game in this channel."
            )
        )
    )

    interaction = create_interaction()

    with patch(
        "impostor_bot.discord.commands.close_lobby_message",
        new=AsyncMock(),
    ) as close_lobby_mock:
        asyncio.run(
            handle_cancel(
                interaction=interaction,
                use_case=use_case,
            )
        )

    close_lobby_mock.assert_not_awaited()

    interaction.response.defer.assert_awaited_once_with(
        thinking=True,
    )

    interaction.followup.send.assert_awaited_once()

    interaction.response.send_message.assert_not_awaited()


def test_finish_handler_logs_game_finished(
    caplog,
):
    game = create_finished_game()

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        )
    )

    interaction = create_interaction()

    caplog.set_level(logging.INFO)

    with patch(
        "impostor_bot.discord.commands.close_lobby_message",
        new=AsyncMock(),
    ):
        asyncio.run(
            handle_finish(
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
        == "game_finished"
    )

    assert record.context[
        "guild_id"
    ] == 100

    assert record.context[
        "channel_id"
    ] == 200


def test_cancel_handler_logs_game_cancelled(
    caplog,
):
    game = (
        create_cancelled_waiting_game()
    )

    use_case = SimpleNamespace(
        execute=AsyncMock(
            return_value=game,
        )
    )

    interaction = create_interaction()

    caplog.set_level(logging.INFO)

    with (
        patch(
            "impostor_bot.discord.commands.close_lobby_message",
            new=AsyncMock(),
        ),
        patch(
            "impostor_bot.discord.commands.LobbyView",
        ),
    ):
        asyncio.run(
            handle_cancel(
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
        == "game_cancelled"
    )

    assert record.context[
        "guild_id"
    ] == 100

    assert record.context[
        "channel_id"
    ] == 200

    assert record.context[
        "reason"
    ] == "host_requested"