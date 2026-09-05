import asyncio
from copy import deepcopy

from impostor_bot.application.cancel_game import CancelGame
from impostor_bot.application.create_game import CreateGame
from impostor_bot.application.exceptions import (
    GameAlreadyExistsError,
    GameNotFoundError,
)
from impostor_bot.application.finish_game import FinishGame
from impostor_bot.application.join_game import JoinGame

from impostor_bot.game.exceptions import (
    PlayerAlreadyJoinedError,
)
from impostor_bot.game.game import Game
from impostor_bot.game.player import Player
from impostor_bot.game.session_key import GameSessionKey

from tests.helpers.factories import (
    make_session_key,
    make_started_game,
)


class YieldingGameRepository:
    def __init__(self) -> None:
        self.games: dict[
            GameSessionKey,
            Game,
        ] = {}

    async def get(
        self,
        key: GameSessionKey,
    ) -> Game | None:
        await asyncio.sleep(0)

        return self.games.get(key)

    async def save(
        self,
        key: GameSessionKey,
        game: Game,
    ) -> None:
        await asyncio.sleep(0)

        self.games[key] = game

    async def delete(
        self,
        key: GameSessionKey,
    ) -> None:
        await asyncio.sleep(0)

        self.games.pop(
            key,
            None,
        )


class CopyingYieldingRepository:
    def __init__(self) -> None:
        self.games: dict[
            GameSessionKey,
            Game,
        ] = {}

    async def get(
        self,
        key: GameSessionKey,
    ) -> Game | None:
        await asyncio.sleep(0)

        game = self.games.get(key)

        if game is None:
            return None

        return deepcopy(game)

    async def save(
        self,
        key: GameSessionKey,
        game: Game,
    ) -> None:
        await asyncio.sleep(0)

        self.games[key] = deepcopy(game)

    async def delete(
        self,
        key: GameSessionKey,
    ) -> None:
        await asyncio.sleep(0)

        self.games.pop(
            key,
            None,
        )


key = make_session_key()

def test_concurrent_create_allows_only_one_game(lock_manager):
    async def scenario():
        repository = YieldingGameRepository()

        use_case = CreateGame(
            repository=repository,
            lock_manager=lock_manager,
        )

        results = await asyncio.gather(
            use_case.execute(
                key=key,
                host_id=1,
            ),
            use_case.execute(
                key=key,
                host_id=2,
            ),
            return_exceptions=True,
        )

        successful_games = [
            result
            for result in results
            if isinstance(
                result,
                Game,
            )
        ]

        duplicate_errors = [
            result
            for result in results
            if isinstance(
                result,
                GameAlreadyExistsError,
            )
        ]

        assert len(successful_games) == 1
        assert len(duplicate_errors) == 1

        stored_game = await repository.get(key)

        assert stored_game is not None

        assert stored_game.host_id in {
            1,
            2,
        }

    asyncio.run(scenario())


def test_concurrent_joins_preserve_both_players(lock_manager):
    async def scenario():
        repository = CopyingYieldingRepository()

        await repository.save(
            key=key,
            game=Game.create(
                host_id=1,
            ),
        )

        use_case = JoinGame(
            repository=repository,
            lock_manager=lock_manager,
        )

        await asyncio.gather(
            use_case.execute(
                key=key,
                player=Player(
                    id=2,
                ),
            ),
            use_case.execute(
                key=key,
                player=Player(
                    id=3,
                ),
            ),
        )

        game = await repository.get(key)

        assert game is not None

        assert set(game.players) == {
            1,
            2,
            3,
        }

        assert len(game.players) == 3

    asyncio.run(scenario())


def test_concurrent_duplicate_join_is_rejected(lock_manager):
    async def scenario():
        repository = CopyingYieldingRepository()

        await repository.save(
            key=key,
            game=Game.create(
                host_id=1,
            ),
        )

        use_case = JoinGame(
            repository=repository,
            lock_manager=lock_manager,
        )

        results = await asyncio.gather(
            use_case.execute(
                key=key,
                player=Player(
                    id=2,
                ),
            ),
            use_case.execute(
                key=key,
                player=Player(
                    id=2,
                ),
            ),
            return_exceptions=True,
        )

        successful_joins = [
            result
            for result in results
            if isinstance(
                result,
                Game,
            )
        ]

        duplicate_errors = [
            result
            for result in results
            if isinstance(
                result,
                PlayerAlreadyJoinedError,
            )
        ]

        assert len(successful_joins) == 1
        assert len(duplicate_errors) == 1

        game = await repository.get(key)

        assert game is not None

        assert game.players.count(2) == 1

        assert set(game.players) == {
            1,
            2,
        }

    asyncio.run(scenario())



def test_concurrent_finish_and_cancel_have_single_winner(lock_manager):
    async def scenario():
        game = make_started_game()

        repository = CopyingYieldingRepository()

        await repository.save(
            key=key,
            game=game,
        )

        finish_game = FinishGame(
            repository=repository,
            lock_manager=lock_manager,
        )

        cancel_game = CancelGame(
            repository=repository,
            lock_manager=lock_manager,
        )

        results = await asyncio.gather(
            finish_game.execute(
                key=key,
                requester_id=1,
            ),
            cancel_game.execute(
                key=key,
                requester_id=1,
            ),
            return_exceptions=True,
        )

        successful_operations = [
            result
            for result in results
            if isinstance(
                result,
                Game,
            )
        ]

        missing_errors = [
            result
            for result in results
            if isinstance(
                result,
                GameNotFoundError,
            )
        ]

        assert len(successful_operations) == 1
        assert len(missing_errors) == 1

        remaining_game = await repository.get(key)

        assert remaining_game is None

    asyncio.run(scenario())