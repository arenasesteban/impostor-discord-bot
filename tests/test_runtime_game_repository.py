import asyncio

import pytest

from impostor_bot.discord.state import (
    RuntimeGameRepository,
)
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import (
    GameSessionKey,
)
from impostor_bot.infrastructure.repositories.in_memory_game_repository import (
    InMemoryGameRepository,
)


def test_runtime_repository_requires_configuration():
    repository = RuntimeGameRepository()

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    with pytest.raises(RuntimeError):
        asyncio.run(
            repository.get(key)
        )


def test_runtime_repository_delegates_to_configured_repository():
    repository = RuntimeGameRepository()

    backing_repository = (
        InMemoryGameRepository()
    )

    repository.configure(
        backing_repository
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    game = Game.create(
        host_id=1
    )

    asyncio.run(
        repository.save(
            key=key,
            game=game,
        )
    )

    stored_game = asyncio.run(
        repository.get(key)
    )

    assert stored_game is game