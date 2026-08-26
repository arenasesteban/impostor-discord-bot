from impostor_bot.application.exceptions import GameAlreadyExistsError
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.ports.game_repository import GameRepository


class CreateGame:
    def __init__(self, repository: GameRepository) -> None:
        self.repository = repository

    async def execute(self, key: GameSessionKey, host_id: int) -> Game:
        existing_game = await self.repository.get(key)

        if existing_game is not None:
            raise GameAlreadyExistsError(
                "A game already exists for this session."
            )

        game = Game.create(host_id=host_id)

        await self.repository.save(
            key=key,
            game=game,
        )

        return game