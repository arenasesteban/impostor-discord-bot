import asyncio

import pytest

from impostor_bot.application.exceptions import (
    GameNotFoundError,
    NotGameHostError,
)

from impostor_bot.application.start_game import StartGame

from impostor_bot.constants import IMPOSTOR_ROLE

from impostor_bot.game.exceptions import (
    GameAlreadyStartedError,
    NotEnoughPlayersError,
    GameError,
)

from impostor_bot.game.game import Game
from impostor_bot.game.state import GameState

from tests.helpers.fakes import FakeGameRepository

from tests.helpers.factories import (
    make_session_key,
    make_ready_game,
    make_started_game,
)


class FakeWordProvider:
    def __init__(self, word: str = "pizza"):
        self.word = word
        self.called = False

    async def get_word(
        self,
        category: str | None = None,
    ) -> str:
        self.called = True
        return self.word


class DeterministicRandomSelector:
    def __init__(self, selected_id: int):
        self.selected_id = selected_id
        self.called = False

    def choose(
        self,
        values,
    ) -> int:
        self.called = True
        return self.selected_id


key = make_session_key()


def test_start_game_assigns_deterministic_impostor(lock_manager):
    game = make_ready_game()

    repository = FakeGameRepository(game)
    word_provider = FakeWordProvider("pizza")
    selector = DeterministicRandomSelector(2)

    start_game = StartGame(
        repository=repository,
        word_provider=word_provider,
        random_selector=selector,
        lock_manager=lock_manager,
    )

    result = asyncio.run(
        start_game.execute(
            key=key,
            requester_id=1,
        )
    )

    assert result.game is game

    assert game.status == GameState.STARTED
    assert game.secret_word == "pizza"
    assert game.impostor_id == 2

    assert result.roles[2] == IMPOSTOR_ROLE
    assert result.roles[1] == "pizza"
    assert result.roles[3] == "pizza"

    assert repository.saved_game is game


def test_start_game_assigns_exactly_one_impostor(lock_manager):
    game = make_ready_game()

    start_game = StartGame(
        repository=FakeGameRepository(game),
        word_provider=FakeWordProvider("pizza"),
        random_selector=DeterministicRandomSelector(3),
        lock_manager=lock_manager,
    )

    result = asyncio.run(
        start_game.execute(
            key=key,
            requester_id=1,
        )
    )

    impostors = [
        role
        for role in result.roles.values()
        if role == IMPOSTOR_ROLE
    ]

    assert len(impostors) == 1


def test_start_game_rejects_missing_game(lock_manager):
    start_game = StartGame(
        repository=FakeGameRepository(),
        word_provider=FakeWordProvider(),
        random_selector=DeterministicRandomSelector(2),
        lock_manager=lock_manager,
    )

    with pytest.raises(GameNotFoundError):
        asyncio.run(
            start_game.execute(
                key=key,
                requester_id=1,
            )
        )


def test_start_game_rejects_non_host(lock_manager):
    game = make_ready_game()
    word_provider = FakeWordProvider()
    selector = DeterministicRandomSelector(2)

    start_game = StartGame(
        repository=FakeGameRepository(game),
        word_provider=word_provider,
        random_selector=selector,
        lock_manager=lock_manager,
    )

    with pytest.raises(NotGameHostError):
        asyncio.run(
            start_game.execute(
                key=key,
                requester_id=2,
            )
        )

    assert word_provider.called is False
    assert selector.called is False
    assert game.status == GameState.WAITING


def test_start_game_rejects_insufficient_players_before_providers(lock_manager):
    game = Game.create(host_id=1)

    word_provider = FakeWordProvider()
    selector = DeterministicRandomSelector(1)

    start_game = StartGame(
        repository=FakeGameRepository(game),
        word_provider=word_provider,
        random_selector=selector,
        lock_manager=lock_manager,
    )

    with pytest.raises(NotEnoughPlayersError):
        asyncio.run(
            start_game.execute(
                key=key,
                requester_id=1,
            )
        )

    assert word_provider.called is False
    assert selector.called is False
    assert game.status == GameState.WAITING


def test_start_game_rejects_started_game(lock_manager):
    game = make_started_game()

    start_game = StartGame(
        repository=FakeGameRepository(game),
        word_provider=FakeWordProvider(),
        random_selector=DeterministicRandomSelector(3),
        lock_manager=lock_manager
    )

    with pytest.raises(GameAlreadyStartedError):
        asyncio.run(
            start_game.execute(
                key=key,
                requester_id=1,
            )
        )


def test_game_start_uses_explicit_impostor():
    game = Game.create(host_id=1)
    game.add_player(2)
    game.add_player(3)

    roles = game.start_game(
        secret_word="pizza",
        impostor_id=2,
    )

    assert game.impostor_id == 2
    assert roles[2] == IMPOSTOR_ROLE


def test_game_rejects_impostor_outside_players():
    game = make_ready_game()
    
    with pytest.raises(GameError):
        game.start_game(
            secret_word="pizza",
            impostor_id=999,
        )