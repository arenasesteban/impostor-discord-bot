import pytest

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.repositories.postgres_game_repository import (
    PostgresGameRepository,
)
from impostor_bot.infrastructure.repositories.postgres_lobby_message_repository import (
    PostgresLobbyMessageRepository,
)


pytestmark = pytest.mark.integration


async def create_persisted_game(
    game_repository: PostgresGameRepository,
    key: GameSessionKey,
    host_id: int = 1,
) -> Game:
    game = Game.create(host_id=host_id)

    await game_repository.save(
        key=key,
        game=game,
    )

    return game


@pytest.mark.asyncio
async def test_lobby_repository_saves_and_gets_message_id(
    postgres_session_factory,
):
    game_repository = PostgresGameRepository(
        postgres_session_factory
    )

    lobby_repository = PostgresLobbyMessageRepository(
        postgres_session_factory
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    await create_persisted_game(
        game_repository,
        key,
    )

    await lobby_repository.save(
        key=key,
        message_id=123456,
    )

    stored_message_id = await lobby_repository.get(
        key
    )

    assert stored_message_id == 123456


@pytest.mark.asyncio
async def test_lobby_repository_updates_existing_message_id(
    postgres_session_factory,
):
    game_repository = PostgresGameRepository(
        postgres_session_factory
    )

    lobby_repository = PostgresLobbyMessageRepository(
        postgres_session_factory
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    await create_persisted_game(
        game_repository,
        key,
    )

    await lobby_repository.save(
        key=key,
        message_id=111,
    )

    await lobby_repository.save(
        key=key,
        message_id=222,
    )

    stored_message_id = await lobby_repository.get(
        key
    )

    assert stored_message_id == 222


@pytest.mark.asyncio
async def test_lobby_repository_returns_none_when_missing(
    postgres_session_factory,
):
    repository = PostgresLobbyMessageRepository(
        postgres_session_factory
    )

    key = GameSessionKey(
        guild_id=999,
        channel_id=999,
    )

    result = await repository.get(key)

    assert result is None


@pytest.mark.asyncio
async def test_lobby_repository_deletes_message_metadata(
    postgres_session_factory,
):
    game_repository = PostgresGameRepository(
        postgres_session_factory
    )

    lobby_repository = PostgresLobbyMessageRepository(
        postgres_session_factory
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    await create_persisted_game(
        game_repository,
        key,
    )

    await lobby_repository.save(
        key=key,
        message_id=123456,
    )

    await lobby_repository.delete(key)

    assert await lobby_repository.get(key) is None

    # El Game padre sigue existiendo.
    assert await game_repository.get(key) is not None


@pytest.mark.asyncio
async def test_deleting_game_cascades_lobby_metadata(
    postgres_session_factory,
):
    game_repository = PostgresGameRepository(
        postgres_session_factory
    )

    lobby_repository = PostgresLobbyMessageRepository(
        postgres_session_factory
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    await create_persisted_game(
        game_repository,
        key,
    )

    await lobby_repository.save(
        key=key,
        message_id=123456,
    )

    assert (
        await lobby_repository.get(key)
        == 123456
    )

    await game_repository.delete(key)

    assert await game_repository.get(key) is None
    assert await lobby_repository.get(key) is None


@pytest.mark.asyncio
async def test_lobby_repository_isolates_session_metadata(
    postgres_session_factory,
):
    game_repository = PostgresGameRepository(
        postgres_session_factory
    )

    lobby_repository = PostgresLobbyMessageRepository(
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

    await create_persisted_game(
        game_repository,
        key_a,
        host_id=1,
    )

    await create_persisted_game(
        game_repository,
        key_b,
        host_id=2,
    )

    await lobby_repository.save(
        key=key_a,
        message_id=111,
    )

    await lobby_repository.save(
        key=key_b,
        message_id=222,
    )

    assert await lobby_repository.get(key_a) == 111
    assert await lobby_repository.get(key_b) == 222


