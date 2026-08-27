from impostor_bot.application.exceptions import (
    GameNotFoundError,
    NotGameHostError,
)

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.ports.game_repository import GameRepository


class CancelGame:
    def __init__(self, repository: GameRepository) -> None:
        self.repository = repository

    async def execute(self, key: GameSessionKey, requester_id: int) -> Game:
        game = await self.repository.get(key)

        if game is None:
            raise GameNotFoundError(
                "There is no active game in this channel."
            )

        if requester_id != game.host_id:
            raise NotGameHostError(
                "Only the host can cancel the game."
            )

        game.cancel()

        await self.repository.delete(key)

        return game