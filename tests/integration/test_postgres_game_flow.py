import pytest

from impostor_bot.application.cancel_game import (
    CancelGame,
)
from impostor_bot.application.create_game import (
    CreateGame,
)
from impostor_bot.application.finish_game import (
    FinishGame,
)
from impostor_bot.application.get_game_status import (
    GetGameStatus,
)
from impostor_bot.application.join_game import (
    JoinGame,
)
from impostor_bot.application.start_game import (
    StartGame,
)
from impostor_bot.game.player import Player
from impostor_bot.game.session_key import (
    GameSessionKey,
)
from impostor_bot.game.state import GameState
from impostor_bot.infrastructure.concurrency.asyncio_session_lock_manager import (
    AsyncioSessionLockManager,
)
from impostor_bot.infrastructure.repositories.postgres_game_repository import (
    PostgresGameRepository,
)

pytestmark = pytest.mark.integration


class FakeWordProvider:
    async def get_word(
        self,
        category: str | None = None,
    ) -> str:
        return "pizza"


class DeterministicRandomSelector:
    def choose(
        self,
        values,
    ) -> int:
        return values[1]


@pytest.mark.asyncio
async def test_complete_game_flow_with_postgres(
    postgres_session_factory,
):
    repository = PostgresGameRepository(
        postgres_session_factory
    )

    lock_manager = AsyncioSessionLockManager()

    create_game = CreateGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    join_game = JoinGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    start_game = StartGame(
        repository=repository,
        word_provider=FakeWordProvider(),
        random_selector=(
            DeterministicRandomSelector()
        ),
        lock_manager=lock_manager,
    )

    get_game_status = GetGameStatus(
        repository=repository,
    )

    finish_game = FinishGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    # Create
    await create_game.execute(
        key=key,
        host_id=1,
    )

    persisted_waiting_game = (
        await repository.get(key)
    )

    assert persisted_waiting_game is not None

    assert persisted_waiting_game.players == [
        1,
    ]

    assert (
        persisted_waiting_game.status
        == GameState.WAITING
    )

    assert (
        persisted_waiting_game.secret_word
        is None
    )

    assert (
        persisted_waiting_game.impostor_id
        is None
    )

    # Join
    await join_game.execute(
        key=key,
        player=Player(id=2),
    )

    await join_game.execute(
        key=key,
        player=Player(id=3),
    )

    persisted_joined_game = (
        await repository.get(key)
    )

    assert persisted_joined_game is not None

    assert persisted_joined_game.players == [
        1,
        2,
        3,
    ]

    assert (
        persisted_joined_game.status
        == GameState.WAITING
    )

    # Start
    start_result = await start_game.execute(
        key=key,
        requester_id=1,
    )

    assert (
        start_result.game.status
        == GameState.STARTED
    )

    assert (
        start_result.game.secret_word
        == "pizza"
    )

    persisted_started_game = (
        await repository.get(key)
    )

    assert persisted_started_game is not None

    assert (
        persisted_started_game.status
        == GameState.STARTED
    )

    assert (
        persisted_started_game.secret_word
        == "pizza"
    )

    assert persisted_started_game.players == [
        1,
        2,
        3,
    ]

    assert (
        persisted_started_game.impostor_id
        is not None
    )

    assert (
        persisted_started_game.impostor_id
        in persisted_started_game.players
    )

    # Status
    status_game = await (
        get_game_status.execute(
            key=key,
        )
    )

    assert (
        status_game.status
        == GameState.STARTED
    )

    assert status_game.players == [
        1,
        2,
        3,
    ]

    assert (
        status_game.secret_word
        == "pizza"
    )

    assert (
        status_game.impostor_id
        == persisted_started_game.impostor_id
    )

    # Finish
    await finish_game.execute(
        key=key,
        requester_id=1,
    )

    assert (
        await repository.get(key)
        is None
    )


@pytest.mark.asyncio
async def test_cancel_game_removes_postgres_session(
    postgres_session_factory,
):
    repository = PostgresGameRepository(
        postgres_session_factory
    )

    lock_manager = AsyncioSessionLockManager()

    create_game = CreateGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    cancel_game = CancelGame(
        repository=repository,
        lock_manager=lock_manager,
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    await create_game.execute(
        key=key,
        host_id=1,
    )

    persisted_game = await repository.get(
        key
    )

    assert persisted_game is not None

    assert (
        persisted_game.status
        == GameState.WAITING
    )

    await cancel_game.execute(
        key=key,
        requester_id=1,
    )

    assert (
        await repository.get(key)
        is None
    )