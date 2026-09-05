import logging
from collections.abc import MutableMapping
from dataclasses import dataclass
from typing import Protocol

from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.game.state import GameState
from impostor_bot.observability import log_event
from impostor_bot.ports.game_repository import GameRepository
from impostor_bot.ports.lobby_message_repository import LobbyMessageRepository

logger = logging.getLogger(__name__)


class SessionRecoveryGateway(Protocol):
    async def channel_exists(self, key: GameSessionKey) -> bool:
        ...

    async def lobby_message_exists(self, key: GameSessionKey, message_id: int) -> bool:
        ...

    def register_lobby_view(self, message_id: int) -> None:
        ...


@dataclass(frozen=True, slots=True)
class RecoverySummary:
    discovered: int
    restored_waiting: int
    restored_started: int
    stale_removed: int
    detached_lobbies: int


class RecoverGameSessions:
    def __init__(
        self,
        game_repository: GameRepository,
        lobby_repository: LobbyMessageRepository,
        gateway: SessionRecoveryGateway,
        lobby_cache: MutableMapping[GameSessionKey, int]
    ) -> None:
        self._game_repository = game_repository

        self._lobby_repository = lobby_repository

        self._gateway = gateway
        self._lobby_cache = lobby_cache

    async def execute(self) -> RecoverySummary:
        self._lobby_cache.clear()

        sessions = await self._game_repository.list_active()

        restored_waiting = 0
        restored_started = 0
        stale_removed = 0
        detached_lobbies = 0

        for key, game in sessions:
            channel_exists = await self._gateway.channel_exists(key)

            if not channel_exists:
                await self._remove_stale(key)

                stale_removed += 1
                continue

            if game.status == GameState.WAITING:
                restored = await self._recover_waiting(key)

                if restored:
                    restored_waiting += 1

                else:
                    stale_removed += 1

                continue

            if game.status == GameState.STARTED:
                detached = await self._recover_started(key)

                restored_started += 1

                if detached:
                    detached_lobbies += 1

                continue

            await self._remove_stale(key)

            stale_removed += 1

        summary = RecoverySummary(
            discovered=len(sessions),
            restored_waiting=restored_waiting,
            restored_started=restored_started,
            stale_removed=stale_removed,
            detached_lobbies=detached_lobbies
        )

        log_event(
            logger,
            "session_recovery_completed",
            discovered=summary.discovered,
            restored_waiting=summary.restored_waiting,
            restored_started=summary.restored_started,
            stale_removed=summary.stale_removed,
            detached_lobbies=summary.detached_lobbies
        )

        return summary

    async def _recover_waiting(self, key: GameSessionKey) -> bool:
        message_id = await self._lobby_repository.get(key)

        if message_id is None:
            await self._remove_stale(key)

            return False

        message_exists = await self._gateway.lobby_message_exists(key=key, message_id=message_id)
        
        if not message_exists:
            await self._remove_stale(key)

            return False

        self._lobby_cache[key] = message_id

        self._gateway.register_lobby_view(message_id)

        return True

    async def _recover_started(self, key: GameSessionKey) -> bool:
        message_id = await self._lobby_repository.get(key)

        if message_id is None:
            return False

        message_exists = await self._gateway.lobby_message_exists(key=key, message_id=message_id)

        if not message_exists:
            await self._lobby_repository.delete(key)

            return True

        self._lobby_cache[key] = message_id

        return False

    async def _remove_stale(self, key: GameSessionKey) -> None:
        self._lobby_cache.pop(key, None)

        await self._game_repository.delete(key)

        await self._lobby_repository.delete(key)