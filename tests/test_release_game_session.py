import asyncio

from impostor_bot.application.release_game_session import (
    ReleaseGameSession,
)
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


def test_release_game_session_deletes_game():
    games: dict[int, Game] = {}

    repository = InMemoryGameRepository(games)
    release_game = ReleaseGameSession(repository)

    key = create_key()
    game = Game.create(host_id=1)

    asyncio.run(
        repository.save(
            key=key,
            game=game,
        )
    )

    asyncio.run(
        release_game.execute(key)
    )

    stored_game = asyncio.run(
        repository.get(key)
    )

    assert stored_game is None