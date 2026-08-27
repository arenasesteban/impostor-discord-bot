import asyncio

import pytest

from impostor_bot.application.exceptions import GameNotFoundError
from impostor_bot.application.get_game_status import GetGameStatus
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.repositories.in_memory_game_repository import (
    InMemoryGameRepository,
)


def create_key() -> GameSessionKey:
    return GameSessionKey(
        guild_id=100,
        channel_id=200,
    )


def test_get_game_status_returns_existing_game():
    repository = InMemoryGameRepository()

    key = create_key()
    game = Game.create(host_id=1)

    asyncio.run(
        repository.save(
            key=key,
            game=game,
        )
    )

    use_case = GetGameStatus(repository)

    result = asyncio.run(
        use_case.execute(key)
    )

    assert result is game


def test_get_game_status_rejects_missing_game():
    use_case = GetGameStatus(
        InMemoryGameRepository()
    )

    with pytest.raises(GameNotFoundError):
        asyncio.run(
            use_case.execute(
                create_key()
            )
        )
        