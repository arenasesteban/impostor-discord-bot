import asyncio

import pytest
from tests.helpers.factories import (
    make_session_key,
    make_started_game,
)
from tests.helpers.fakes import FakeGameRepository

from impostor_bot.application.cancel_game import CancelGame
from impostor_bot.application.exceptions import (
    GameNotFoundError,
    NotGameHostError,
)
from impostor_bot.application.finish_game import FinishGame
from impostor_bot.game.exceptions import InvalidGameStateError
from impostor_bot.game.game import Game
from impostor_bot.game.state import GameState

key = make_session_key()


def test_finish_game_finishes_and_releases_session(lock_manager):
    game = make_started_game()

    repository = FakeGameRepository(game)

    use_case = FinishGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    result = asyncio.run(
        use_case.execute(
            key=key,
            requester_id=1,
        )
    )

    assert result.status == GameState.FINISHED
    assert repository.game is None
    assert repository.deleted_key == key


def test_finish_game_rejects_missing_game(lock_manager):
    use_case = FinishGame(
        repository=FakeGameRepository(),
        lock_manager=lock_manager
    )

    with pytest.raises(GameNotFoundError):
        asyncio.run(
            use_case.execute(
                key=key,
                requester_id=1,
            )
        )



def test_finish_game_rejects_non_host(lock_manager):
    game = make_started_game()

    repository = FakeGameRepository(game)

    use_case = FinishGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    with pytest.raises(NotGameHostError):
        asyncio.run(
            use_case.execute(
                key=key,
                requester_id=2,
            )
        )

    assert repository.deleted_key is None


def test_cancel_waiting_game_cancels_and_releases_session(lock_manager):
    game = Game.create(host_id=1)
    repository = FakeGameRepository(game)

    use_case = CancelGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    result = asyncio.run(
        use_case.execute(
            key=key,
            requester_id=1,
        )
    )

    assert result.status == GameState.CANCELLED
    assert repository.game is None


def test_cancel_started_game_cancels_and_releases_session(lock_manager):
    started_game = make_started_game()
    repository = FakeGameRepository(started_game)

    use_case = CancelGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    result = asyncio.run(
        use_case.execute(
            key=key,
            requester_id=1,
        )
    )

    assert result.status == GameState.CANCELLED
    assert repository.game is None


def test_cancel_game_rejects_missing_game(lock_manager):
    use_case = CancelGame(
        repository=FakeGameRepository(),
        lock_manager=lock_manager,
    )

    with pytest.raises(GameNotFoundError):
        asyncio.run(
            use_case.execute(
                key=key,
                requester_id=1,
            )
        )


def test_cancel_game_rejects_non_host(lock_manager):
    repository = FakeGameRepository(
        Game.create(host_id=1)
    )

    use_case = CancelGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    with pytest.raises(NotGameHostError):
        asyncio.run(
            use_case.execute(
                key=key,
                requester_id=2,
            )
        )

    assert repository.deleted_key is None


def test_finish_game_does_not_release_session_when_game_cannot_be_finished(
    lock_manager,
):
    game = Game.create(host_id=1)
    repository = FakeGameRepository(game)

    use_case = FinishGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    with pytest.raises(InvalidGameStateError):
        asyncio.run(
            use_case.execute(
                key=make_session_key(),
                requester_id=1,
            )
        )

    assert repository.game is game


def test_cancel_game_does_not_release_session_when_game_cannot_be_cancelled(
    lock_manager,
):
    game = make_started_game()
    game.finish()

    repository = FakeGameRepository(game)

    use_case = CancelGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    with pytest.raises(InvalidGameStateError):
        asyncio.run(
            use_case.execute(
                key=make_session_key(),
                requester_id=1,
            )
        )

    assert repository.game is game