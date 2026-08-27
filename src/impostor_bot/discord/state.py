from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.repositories.in_memory_game_repository import (
    InMemoryGameRepository,
)
from impostor_bot.infrastructure.concurrency.asyncio_session_lock_manager import (
    AsyncioSessionLockManager,
)


active_lobby_messages: dict[int, int] = {}

active_games: dict[GameSessionKey, Game] = {}

game_repository = InMemoryGameRepository(active_games)

session_lock_manager = AsyncioSessionLockManager()