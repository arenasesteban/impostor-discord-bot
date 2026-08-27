from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.repositories.in_memory_game_repository import (
    InMemoryGameRepository,
)


active_games: dict[GameSessionKey, Game] = {}

active_lobby_messages: dict[int, int] = {}

game_repository = InMemoryGameRepository(active_games)