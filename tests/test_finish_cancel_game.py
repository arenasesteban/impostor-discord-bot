import asyncio

import pytest

from impostor_bot.application.cancel_game import CancelGame
from impostor_bot.application.exceptions import (
    GameNotFoundError,
    NotGameHostError,
)
from impostor_bot.application.finish_game import FinishGame

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.game.state import GameState
from impostor_bot.infrastructure.concurrency.asyncio_session_lock_manager import (
    AsyncioSessionLockManager,
)

def create_lock_manager() -> AsyncioSessionLockManager:
    return AsyncioSessionLockManager()


class FakeGameRepository:
    def __init__(
        self,
        game: Game | None = None,
    ) -> None:
        self.game = game
        self.deleted_key: GameSessionKey | None = None

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

    async def delete(
        self,
        key: GameSessionKey,
    ) -> None:
        self.deleted_key = key
        self.game = None


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


def test_finish_game_finishes_and_releases_session():
    game = create_started_game()
    repository = FakeGameRepository(game)

    use_case = FinishGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    result = asyncio.run(
        use_case.execute(
            key=create_key(),
            requester_id=1,
        )
    )

    assert result.status == GameState.FINISHED
    assert repository.game is None
    assert repository.deleted_key == create_key()


def test_finish_game_rejects_missing_game():
    use_case = FinishGame(
        repository=FakeGameRepository(),
        lock_manager=create_lock_manager(),
    )

    with pytest.raises(GameNotFoundError):
        asyncio.run(
            use_case.execute(
                key=create_key(),
                requester_id=1,
            )
        )


def test_finish_game_rejects_non_host():
    repository = FakeGameRepository(
        create_started_game()
    )

    use_case = FinishGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    with pytest.raises(NotGameHostError):
        asyncio.run(
            use_case.execute(
                key=create_key(),
                requester_id=2,
            )
        )

    assert repository.deleted_key is None


def test_cancel_waiting_game_cancels_and_releases_session():
    game = Game.create(host_id=1)
    repository = FakeGameRepository(game)

    use_case = CancelGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    result = asyncio.run(
        use_case.execute(
            key=create_key(),
            requester_id=1,
        )
    )

    assert result.status == GameState.CANCELLED
    assert repository.game is None


def test_cancel_started_game_cancels_and_releases_session():
    repository = FakeGameRepository(
        create_started_game()
    )

    use_case = CancelGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    result = asyncio.run(
        use_case.execute(
            key=create_key(),
            requester_id=1,
        )
    )

    assert result.status == GameState.CANCELLED
    assert repository.game is None


def test_cancel_game_rejects_missing_game():
    use_case = CancelGame(
        repository=FakeGameRepository(),
        lock_manager=create_lock_manager(),
    )

    with pytest.raises(GameNotFoundError):
        asyncio.run(
            use_case.execute(
                key=create_key(),
                requester_id=1,
            )
        )


def test_cancel_game_rejects_non_host():
    repository = FakeGameRepository(
        Game.create(host_id=1)
    )

    use_case = CancelGame(
        repository=repository,
        lock_manager=create_lock_manager(),
    )

    with pytest.raises(NotGameHostError):
        asyncio.run(
            use_case.execute(
                key=create_key(),
                requester_id=2,
            )
        )

    assert repository.deleted_key is None