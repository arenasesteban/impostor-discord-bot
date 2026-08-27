import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from impostor_bot.game.session_key import GameSessionKey


class AsyncioSessionLockManager:
    def __init__(self) -> None:
        self._locks: dict[GameSessionKey, asyncio.Lock] = {}

    def _get_lock(self, key: GameSessionKey) -> asyncio.Lock:
        return self._locks.setdefault(key, asyncio.Lock())

    @asynccontextmanager
    async def lock(self, key: GameSessionKey) -> AsyncIterator[None]:
        session_lock = self._get_lock(key)

        async with session_lock:
            yield