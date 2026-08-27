import asyncio

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.repositories.in_memory_game_repository import (
    InMemoryGameRepository,
)


def test_in_memory_repository_deletes_game():
    games: dict[GameSessionKey, Game] = {}

    repository = InMemoryGameRepository(games)

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    game = Game.create(host_id=1)

    asyncio.run(
        repository.save(
            key=key,
            game=game,
        )
    )

    asyncio.run(
        repository.delete(key)
    )

    stored_game = asyncio.run(
        repository.get(key)
    )

    assert stored_game is None
    assert key not in games


def test_repository_isolates_games_by_guild_and_channel():
    repository = InMemoryGameRepository()

    guild_a_key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    guild_b_key = GameSessionKey(
        guild_id=101,
        channel_id=200,
    )

    game_a = Game.create(host_id=1)
    game_b = Game.create(host_id=2)

    asyncio.run(
        repository.save(
            key=guild_a_key,
            game=game_a,
        )
    )

    asyncio.run(
        repository.save(
            key=guild_b_key,
            game=game_b,
        )
    )

    stored_a = asyncio.run(
        repository.get(guild_a_key)
    )

    stored_b = asyncio.run(
        repository.get(guild_b_key)
    )

    assert stored_a is game_a
    assert stored_b is game_b


def test_repository_isolates_games_by_channel():
    repository = InMemoryGameRepository()

    channel_a_key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    channel_b_key = GameSessionKey(
        guild_id=100,
        channel_id=201,
    )

    game_a = Game.create(host_id=1)
    game_b = Game.create(host_id=2)

    asyncio.run(
        repository.save(
            key=channel_a_key,
            game=game_a,
        )
    )

    asyncio.run(
        repository.save(
            key=channel_b_key,
            game=game_b,
        )
    )

    assert asyncio.run(
        repository.get(channel_a_key)
    ) is game_a

    assert asyncio.run(
        repository.get(channel_b_key)
    ) is game_b


def test_repository_delete_does_not_affect_other_session():
    repository = InMemoryGameRepository()

    key_a = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    key_b = GameSessionKey(
        guild_id=101,
        channel_id=200,
    )

    game_a = Game.create(host_id=1)
    game_b = Game.create(host_id=2)

    asyncio.run(
        repository.save(
            key=key_a,
            game=game_a,
        )
    )

    asyncio.run(
        repository.save(
            key=key_b,
            game=game_b,
        )
    )

    asyncio.run(
        repository.delete(key_a)
    )

    assert asyncio.run(
        repository.get(key_a)
    ) is None

    assert asyncio.run(
        repository.get(key_b)
    ) is game_b