from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey


class FakeGameRepository:
    def __init__(self, game: Game | None = None) -> None:
        self.game = game
        self.saved_game: Game | None = None
        self.saved_key: GameSessionKey | None = None
        self.deleted_key: GameSessionKey | None = None

    async def get(self, key: GameSessionKey) -> Game | None:
        return self.game

    async def save(self, key: GameSessionKey, game: Game) -> None:
        self.game = game
        self.saved_game = game
        self.saved_key = key

    async def delete(self, key: GameSessionKey) -> None:
        self.deleted_key = key
        self.game = None


