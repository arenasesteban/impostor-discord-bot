import asyncio

import pytest

from impostor_bot.application.create_game import CreateGame
from impostor_bot.application.exceptions import GameAlreadyExistsError
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.repositories.in_memory_game_repository import (
    InMemoryGameRepository,
)


def test_create_game_persists_new_game():
    games: dict[int, Game] = {}

    repository = InMemoryGameRepository(games)
    create_game = CreateGame(repository)

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    game = asyncio.run(
        create_game.execute(
            key=key,
            host_id=300,
        )
    )

    assert game.host_id == 300
    assert game.players == [300]

    stored_game = asyncio.run(repository.get(key))

    assert stored_game is game


def test_create_game_uses_full_session_key_storage():
    games: dict[GameSessionKey, Game] = {}

    repository = InMemoryGameRepository(games)
    create_game = CreateGame(repository)

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    game = asyncio.run(
        create_game.execute(
            key=key,
            host_id=300,
        )
    )

    assert games[key] is game


def test_create_game_rejects_existing_game():
    games: dict[int, Game] = {}

    repository = InMemoryGameRepository(games)
    create_game = CreateGame(repository)

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    asyncio.run(
        create_game.execute(
            key=key,
            host_id=300,
        )
    )

    with pytest.raises(GameAlreadyExistsError):
        asyncio.run(
            create_game.execute(
                key=key,
                host_id=400,
            )
        )


def test_different_channels_can_create_independent_games():
    games: dict[GameSessionKey, Game] = {}

    repository = InMemoryGameRepository(games)
    create_game = CreateGame(repository)

    first_key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    second_key = GameSessionKey(
        guild_id=100,
        channel_id=201,
    )

    first_game = asyncio.run(
        create_game.execute(
            key=first_key,
            host_id=1,
        )
    )

    second_game = asyncio.run(
        create_game.execute(
            key=second_key,
            host_id=2,
        )
    )

    assert first_game is not second_game
    assert games[first_key] is first_game
    assert games[second_key] is second_game