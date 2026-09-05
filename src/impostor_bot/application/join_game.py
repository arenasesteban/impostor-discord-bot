from impostor_bot.application.exceptions import GameNotFoundError
from impostor_bot.game.game import Game
from impostor_bot.game.player import Player
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.ports.game_repository import GameRepository
from impostor_bot.ports.session_lock_manager import SessionLockManager


class JoinGame:
    def __init__(self, repository: GameRepository, lock_manager: SessionLockManager) -> None:
        self.repository = repository
        self.lock_manager = lock_manager

    async def execute(self, key: GameSessionKey, player: Player) -> Game:
        async with self.lock_manager.lock(key):
            game = await self.repository.get(key)

            if game is None:
                raise GameNotFoundError(
                    "There is no open game in this channel."
                )

            game.add_player(player.id)

            await self.repository.save(
                key=key,
                game=game
            )

            return game