from contextlib import AbstractAsyncContextManager
from typing import Protocol

from impostor_bot.game.session_key import GameSessionKey


class SessionLockManager(Protocol):
    def lock(self, key: GameSessionKey) -> AbstractAsyncContextManager[None]:
        ...