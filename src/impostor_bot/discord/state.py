from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.concurrency.asyncio_session_lock_manager import (
    AsyncioSessionLockManager,
)
from impostor_bot.ports.game_repository import GameRepository
from impostor_bot.ports.lobby_message_repository import LobbyMessageRepository


class RuntimeGameRepository:
    def __init__(self) -> None:
        self._repository: GameRepository | None = None

    def configure(self, repository: GameRepository) -> None:
        self._repository = repository

    def _get_repository(self) -> GameRepository:
        if self._repository is None:
            raise RuntimeError(
                "Game repository has not been configured."
            )

        return self._repository

    async def get(self, key: GameSessionKey) -> Game | None:
        return await self._get_repository().get(key)

    async def save(self, key: GameSessionKey, game: Game) -> None:
        await self._get_repository().save(
            key=key,
            game=game,
        )

    async def delete(self, key: GameSessionKey) -> None:
        await self._get_repository().delete(key)

    async def list_active(self) -> list[tuple[GameSessionKey, Game]]:
        return await self._get_repository().list_active()


class RuntimeLobbyMessageRepository:
    def __init__(self) -> None:
        self._repository: LobbyMessageRepository | None = None

    def configure(self, repository: LobbyMessageRepository) -> None:
        self._repository = repository

    def _get_repository(self) -> LobbyMessageRepository:
        if self._repository is None:
            raise RuntimeError(
                "Lobby message repository "
                "has not been configured."
            )

        return self._repository

    async def get(self, key: GameSessionKey) -> int | None:
        return await self._get_repository().get(key)

    async def save(self, key: GameSessionKey, message_id: int) -> None:
        await self._get_repository().save(
            key=key,
            message_id=message_id,
        )

    async def delete(self, key: GameSessionKey) -> None:
        await self._get_repository().delete(key)


active_lobby_messages: dict[GameSessionKey, int] = {}

game_repository = RuntimeGameRepository()

session_lock_manager = AsyncioSessionLockManager()

lobby_message_repository = RuntimeLobbyMessageRepository()


def configure_game_repository(repository: GameRepository) -> None:
    game_repository.configure(repository)

def configure_lobby_message_repository(repository: LobbyMessageRepository) -> None:
    lobby_message_repository.configure(repository)