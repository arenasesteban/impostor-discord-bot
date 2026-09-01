from typing import Protocol

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import (
    GameSessionKey,
)


class LobbyMessageRepository(Protocol):
    async def get(self, key: GameSessionKey) -> int | None:
        ...

    async def save(self, key: GameSessionKey, message_id: int) -> None:
        ...

    async def delete(self, key: GameSessionKey) -> None:
        ...

    async def list_active(self) -> list[tuple[GameSessionKey, Game]]:
        ...