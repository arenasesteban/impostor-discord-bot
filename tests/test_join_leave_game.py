import asyncio

import pytest

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
from impostor_bot.game.session_key import GameSessionKey

from impostor_bot.infrastructure.concurrency.asyncio_session_lock_manager import (
    AsyncioSessionLockManager,
)

def create_lock_manager() -> AsyncioSessionLockManager:
    return AsyncioSessionLockManager()


class FakeGameRepository:
    def __init__(self, game: Game | None = None) -> None:
        self.game = game
        self.saved_game: Game | None = None
        self.saved_key: GameSessionKey | None = None

    async def get(
        self,
        key: GameSessionKey,
    ) -> Game | None:
        return self.game

    async def save(
        self,
        key: GameSessionKey,
        game: Game,
    ) -> None:
        self.game = game
        self.saved_game = game
        self.saved_key = key


def create_key() -> GameSessionKey:
    return GameSessionKey(
        guild_id=100,
        channel_id=200,
    )


def create_started_game() -> Game:
    game = Game.create(host_id=1)
    game.add_player(2)
    game.add_player(3)
    game.start_game(
        secret_word="pizza",
        impostor_id=2,
    )

    return game


def test_join_game_adds_player_and_saves_game():
    game = Game.create(host_id=1)
    repository = FakeGameRepository(game)
    join_game = JoinGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    key = create_key()

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


def test_join_game_rejects_missing_game():
    repository = FakeGameRepository()
    join_game = JoinGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    with pytest.raises(GameNotFoundError):
        asyncio.run(
            join_game.execute(
                key=create_key(),
                player=Player(id=2),
            )
        )


def test_join_game_rejects_duplicate_player():
    game = Game.create(host_id=1)
    game.add_player(2)

    repository = FakeGameRepository(game)
    join_game = JoinGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    with pytest.raises(PlayerAlreadyJoinedError):
        asyncio.run(
            join_game.execute(
                key=create_key(),
                player=Player(id=2),
            )
        )


def test_join_game_rejects_started_game():
    repository = FakeGameRepository(
        create_started_game()
    )

    join_game = JoinGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    with pytest.raises(GameAlreadyStartedError):
        asyncio.run(
            join_game.execute(
                key=create_key(),
                player=Player(id=4),
            )
        )


def test_leave_game_removes_player_and_saves_game():
    game = Game.create(host_id=1)
    game.add_player(2)

    repository = FakeGameRepository(game)
    leave_game = LeaveGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    key = create_key()

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


def test_leave_game_rejects_missing_game():
    repository = FakeGameRepository()
    leave_game = LeaveGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    with pytest.raises(GameNotFoundError):
        asyncio.run(
            leave_game.execute(
                key=create_key(),
                player=Player(id=2),
            )
        )


def test_leave_game_rejects_non_member():
    game = Game.create(host_id=1)

    repository = FakeGameRepository(game)
    leave_game = LeaveGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    with pytest.raises(PlayerNotFoundError):
        asyncio.run(
            leave_game.execute(
                key=create_key(),
                player=Player(id=2),
            )
        )


def test_leave_game_rejects_host():
    game = Game.create(host_id=1)

    repository = FakeGameRepository(game)
    leave_game = LeaveGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    with pytest.raises(HostCannotLeaveError):
        asyncio.run(
            leave_game.execute(
                key=create_key(),
                player=Player(id=1),
            )
        )


def test_leave_game_rejects_started_game():
    repository = FakeGameRepository(
        create_started_game()
    )

    leave_game = LeaveGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    with pytest.raises(GameAlreadyStartedError):
        asyncio.run(
            leave_game.execute(
                key=create_key(),
                player=Player(id=2),
            )
        )