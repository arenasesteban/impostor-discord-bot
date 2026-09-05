from impostor_bot.application.exceptions import GameNotFoundError, NotGameHostError
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.ports.game_repository import GameRepository
from impostor_bot.ports.session_lock_manager import SessionLockManager


class FinishGame:
    def __init__(self, repository: GameRepository, lock_manager: SessionLockManager) -> None:
        self.repository = repository
        self.lock_manager = lock_manager

    async def execute(self, key: GameSessionKey, requester_id: int) -> Game:
        async with self.lock_manager.lock(key):
            game = await self.repository.get(key)

            if game is None:
                raise GameNotFoundError(
                    "There is no active game in this channel."
                )

            if requester_id != game.host_id:
                raise NotGameHostError(
                    "Only the host can finish the game."
                )

            game.finish()

            await self.repository.delete(key)

            return game