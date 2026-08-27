import asyncio

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.repositories.in_memory_game_repository import (
    InMemoryGameRepository,
)

def test_in_memory_repository_deletes_game():
    games: dict[int, Game] = {}

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
    assert 200 not in games