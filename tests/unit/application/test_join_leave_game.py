import asyncio

import pytest
from tests.helpers.factories import (
    make_session_key,
    make_started_game,
)
from tests.helpers.fakes import FakeGameRepository

from impostor_bot.application.exceptions import GameNotFoundError
from impostor_bot.application.join_game import JoinGame
from impostor_bot.application.leave_game import LeaveGame
from impostor_bot.game.exceptions import (
    GameAlreadyStartedError,
    HostCannotLeaveError,
    PlayerAlreadyJoinedError,
    PlayerNotFoundError,
)
from impostor_bot.game.game import Game
from impostor_bot.game.player import Player

key = make_session_key()


def test_join_game_adds_player_and_saves_game(lock_manager):
    game = Game.create(host_id=1)
    repository = FakeGameRepository(game)
    join_game = JoinGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    result = asyncio.run(
        join_game.execute(
            key=key,
            player=Player(id=2),
        )
    )

    assert result is game
    assert game.players == [1, 2]
    assert repository.saved_game is game
    assert repository.saved_key == key


def test_join_game_rejects_missing_game(lock_manager):
    repository = FakeGameRepository()
    join_game = JoinGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    with pytest.raises(GameNotFoundError):
        asyncio.run(
            join_game.execute(
                key=key,
                player=Player(id=2),
            )
        )


def test_join_game_rejects_duplicate_player(lock_manager):
    game = Game.create(host_id=1)
    game.add_player(2)

    repository = FakeGameRepository(game)
    join_game = JoinGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    with pytest.raises(PlayerAlreadyJoinedError):
        asyncio.run(
            join_game.execute(
                key=key,
                player=Player(id=2),
            )
        )


def test_join_game_rejects_started_game(lock_manager):
    game = make_started_game()

    repository = FakeGameRepository(game)

    join_game = JoinGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    with pytest.raises(GameAlreadyStartedError):
        asyncio.run(
            join_game.execute(
                key=key,
                player=Player(id=4),
            )
        )


def test_leave_game_removes_player_and_saves_game(lock_manager):
    game = Game.create(host_id=1)
    game.add_player(2)

    repository = FakeGameRepository(game)
    leave_game = LeaveGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    result = asyncio.run(
        leave_game.execute(
            key=key,
            player=Player(id=2),
        )
    )

    assert result is game
    assert game.players == [1]
    assert repository.saved_game is game
    assert repository.saved_key == key


def test_leave_game_rejects_missing_game(lock_manager):
    repository = FakeGameRepository()
    leave_game = LeaveGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    with pytest.raises(GameNotFoundError):
        asyncio.run(
            leave_game.execute(
                key=key,
                player=Player(id=2),
            )
        )


def test_leave_game_rejects_non_member(lock_manager):
    game = Game.create(host_id=1)

    repository = FakeGameRepository(game)
    leave_game = LeaveGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    with pytest.raises(PlayerNotFoundError):
        asyncio.run(
            leave_game.execute(
                key=key,
                player=Player(id=2),
            )
        )


def test_leave_game_rejects_host(lock_manager):
    game = Game.create(host_id=1)

    repository = FakeGameRepository(game)
    leave_game = LeaveGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    with pytest.raises(HostCannotLeaveError):
        asyncio.run(
            leave_game.execute(
                key=key,
                player=Player(id=1),
            )
        )


def test_leave_game_rejects_started_game(lock_manager):
    game = make_started_game()
    
    repository = FakeGameRepository(game)

    leave_game = LeaveGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    with pytest.raises(GameAlreadyStartedError):
        asyncio.run(
            leave_game.execute(
                key=key,
                player=Player(id=2),
            )
        )
