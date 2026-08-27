from impostor_bot.application.exceptions import GameNotFoundError
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.ports.game_repository import GameRepository


class GetGameStatus:
    def __init__(self, repository: GameRepository) -> None:
        self.repository = repository

    async def execute(self, key: GameSessionKey) -> Game:
        game = await self.repository.get(key)

        if game is None:
            raise GameNotFoundError(
                "There is no active game in this channel."
            )

        return game