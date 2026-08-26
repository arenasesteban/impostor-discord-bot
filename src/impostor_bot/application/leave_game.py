from impostor_bot.application.exceptions import GameNotFoundError
from impostor_bot.game.game import Game
from impostor_bot.game.player import Player
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.ports.game_repository import GameRepository


class LeaveGame:
    def __init__(self, repository: GameRepository) -> None:
        self.repository = repository

    async def execute(self, key: GameSessionKey, player: Player) -> Game:
        game = await self.repository.get(key)

        if game is None:
            raise GameNotFoundError(
                "There is no open game in this channel."
            )

        game.remove_player(player.id)

        await self.repository.save(
            key=key,
            game=game,
        )

        return game