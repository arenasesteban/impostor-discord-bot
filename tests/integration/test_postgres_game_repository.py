import pytest

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.game.state import GameState
from impostor_bot.infrastructure.repositories.postgres_game_repository import (
    PostgresGameRepository,
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from impostor_bot.infrastructure.database.models import (
    GamePlayerRecord,
)


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_save_and_get_waiting_game(
    postgres_session_factory,
):
    repository = PostgresGameRepository(
        postgres_session_factory
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    game = Game.create(
        host_id=1
    )

    game.add_player(2)
    game.add_player(3)

    await repository.save(
        key=key,
        game=game,
    )

    stored_game = await repository.get(
        key
    )

    assert stored_game is not None

    assert stored_game.host_id == 1
    assert stored_game.players == [
        1,
        2,
        3,
    ]

    assert (
        stored_game.status
        == GameState.WAITING
    )

    assert stored_game.secret_word is None
    assert stored_game.impostor_id is None


@pytest.mark.asyncio
async def test_started_game_round_trip(
    postgres_session_factory,
):
    repository = PostgresGameRepository(
        postgres_session_factory
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    game = Game.create(host_id=1)
    game.add_player(2)
    game.add_player(3)

    game.start_game(
        secret_word="pizza",
        impostor_id=2,
    )

    await repository.save(
        key=key,
        game=game,
    )

    stored_game = await repository.get(
        key
    )

    assert stored_game is not None

    assert (
        stored_game.status
        == GameState.STARTED
    )

    assert (
        stored_game.secret_word
        == "pizza"
    )

    assert stored_game.impostor_id == 2

    assert stored_game.players == [
        1,
        2,
        3,
    ]


@pytest.mark.asyncio
async def test_save_replaces_persisted_player_state(
    postgres_session_factory,
):
    repository = PostgresGameRepository(
        postgres_session_factory
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    game = Game.create(host_id=1)
    game.add_player(2)
    game.add_player(3)

    await repository.save(
        key=key,
        game=game,
    )

    game.remove_player(2)

    await repository.save(
        key=key,
        game=game,
    )

    stored_game = await repository.get(
        key
    )

    assert stored_game is not None
    assert stored_game.players == [
        1,
        3,
    ]

@pytest.mark.asyncio
async def test_postgres_repository_isolates_sessions(
    postgres_session_factory,
):
    repository = PostgresGameRepository(
        postgres_session_factory
    )

    key_a = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    key_b = GameSessionKey(
        guild_id=101,
        channel_id=200,
    )

    game_a = Game.create(host_id=1)
    game_b = Game.create(host_id=2)

    await repository.save(
        key=key_a,
        game=game_a,
    )

    await repository.save(
        key=key_b,
        game=game_b,
    )

    stored_a = await repository.get(
        key_a
    )

    stored_b = await repository.get(
        key_b
    )

    assert stored_a is not None
    assert stored_b is not None

    assert stored_a.host_id == 1
    assert stored_b.host_id == 2


@pytest.mark.asyncio
async def test_delete_removes_game(
    postgres_session_factory,
):
    repository = PostgresGameRepository(
        postgres_session_factory
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    game = Game.create(host_id=1)
    game.add_player(2)

    await repository.save(
        key=key,
        game=game,
    )

    await repository.delete(key)

    assert await repository.get(
        key
    ) is None

    async with postgres_session_factory() as session:
        result = await session.execute(
            select(
                func.count()
            ).select_from(
                GamePlayerRecord
            )
        )

    assert result.scalar_one() == 0


@pytest.mark.asyncio
async def test_database_rejects_duplicate_player(
    postgres_session_factory,
):
    repository = PostgresGameRepository(
        postgres_session_factory
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    game = Game.create(host_id=1)
    game.add_player(2)

    await repository.save(
        key=key,
        game=game,
    )

    with pytest.raises(IntegrityError):
        async with postgres_session_factory() as session:
            async with session.begin():
                session.add(
                    GamePlayerRecord(
                        guild_id=100,
                        channel_id=200,
                        player_id=2,
                        position=99,
                    )
                )


@pytest.mark.asyncio
async def test_get_returns_none_for_missing_game(
    postgres_session_factory,
):
    repository = PostgresGameRepository(
        postgres_session_factory
    )

    game = await repository.get(
        GameSessionKey(
            guild_id=999,
            channel_id=999,
        )
    )

    assert game is None