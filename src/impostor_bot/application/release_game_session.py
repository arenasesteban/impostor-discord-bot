from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.ports.game_repository import GameRepository


class ReleaseGameSession:
    def __init__(self, repository: GameRepository) -> None:
        self.repository = repository

    async def execute(self, key: GameSessionKey) -> None:
        await self.repository.delete(key)