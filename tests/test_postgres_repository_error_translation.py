import pytest
from sqlalchemy.exc import SQLAlchemyError

from impostor_bot.errors.infrastructure import (
    DatabaseError,
)
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import (
    GameSessionKey,
)
from impostor_bot.infrastructure.repositories.postgres_game_repository import (
    PostgresGameRepository,
)
from impostor_bot.infrastructure.repositories.postgres_lobby_message_repository import (
    PostgresLobbyMessageRepository,
)


class BrokenSession:
    async def __aenter__(self):
        raise SQLAlchemyError(
            "internal SQLAlchemy failure"
        )

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        return False


def broken_session_factory():
    return BrokenSession()


@pytest.mark.asyncio
async def test_repository_translates_sqlalchemy_error():
    repository = PostgresGameRepository(
        broken_session_factory
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    with pytest.raises(
        DatabaseError
    ):
        await repository.get(key)


@pytest.mark.asyncio
async def test_repository_preserves_original_database_exception():
    repository = PostgresGameRepository(
        broken_session_factory
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    with pytest.raises(
        DatabaseError
    ) as exc_info:
        await repository.get(key)

    assert isinstance(
        exc_info.value.__cause__,
        SQLAlchemyError,
    )


@pytest.mark.asyncio
async def test_save_translates_sqlalchemy_error():
    repository = PostgresGameRepository(
        broken_session_factory
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    game = Game.create(
        host_id=1
    )

    with pytest.raises(DatabaseError):
        await repository.save(
            key=key,
            game=game,
        )


@pytest.mark.asyncio
async def test_delete_translates_sqlalchemy_error():
    repository = PostgresGameRepository(
        broken_session_factory
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    with pytest.raises(DatabaseError):
        await repository.delete(key)


@pytest.mark.asyncio
async def test_list_active_translates_sqlalchemy_error():
    repository = PostgresGameRepository(
        broken_session_factory
    )

    with pytest.raises(DatabaseError):
        await repository.list_active()


@pytest.mark.asyncio
async def test_lobby_repository_translates_database_error():
    repository = (
        PostgresLobbyMessageRepository(
            broken_session_factory
        )
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    with pytest.raises(DatabaseError):
        await repository.get(key)