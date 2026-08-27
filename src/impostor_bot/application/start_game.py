from dataclasses import dataclass

from impostor_bot.application.exceptions import (
    GameNotFoundError,
    NotGameHostError,
)

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.ports.game_repository import GameRepository
from impostor_bot.ports.random_selector import RandomSelector
from impostor_bot.ports.word_provider import WordProvider


@dataclass(frozen=True)
class StartGameResult:
    game: Game
    roles: dict[int, str]


class StartGame:
    def __init__(self, repository: GameRepository, word_provider: WordProvider, random_selector: RandomSelector) -> None:
        self.repository = repository
        self.word_provider = word_provider
        self.random_selector = random_selector

    async def execute(self, key: GameSessionKey, requester_id: int) -> StartGameResult:
        game = await self.repository.get(key)

        if game is None:
            raise GameNotFoundError(
                "There is no open game in this channel."
            )

        if requester_id != game.host_id:
            raise NotGameHostError(
                "Only the host can start the game."
            )

        game.validate_start()

        secret_word = await self.word_provider.get_word()

        impostor_id = self.random_selector.choose(game.players)

        roles = game.start_game(
            secret_word=secret_word,
            impostor_id=impostor_id,
        )

        await self.repository.save(
            key=key,
            game=game,
        )

        return StartGameResult(
            game=game,
            roles=roles,
        )