from typing import Protocol

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey


class GameRepository(Protocol):
    async def get(self, key: GameSessionKey) -> Game | None:
        ...

    async def save(self, key: GameSessionKey, game: Game) -> None:
        ...

    async def delete(self, key: GameSessionKey) -> None:
        ...