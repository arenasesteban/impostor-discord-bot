from collections.abc import MutableMapping

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey


class InMemoryGameRepository:
    def __init__(self, games: MutableMapping[GameSessionKey, Game] | None = None) -> None:
        self._games = games if games is not None else {}

    async def get(self, key: GameSessionKey) -> Game | None:
        return self._games.get(key)

    async def save(self, key: GameSessionKey, game: Game) -> None:
        self._games[key] = game

    async def delete(self, key: GameSessionKey) -> None:
        self._games.pop(key, None)

    async def list_active(self) -> list[tuple[GameSessionKey, Game]]:
        return list(self._games.items())