import os
import pytest

from sqlalchemy import func, select

from impostor_bot.discord.recovery import (
    RecoverGameSessions,
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
from impostor_bot.infrastructure.database.models import (
    DiscordSessionRecord,
    GamePlayerRecord,
    GameRecord,
)
from impostor_bot.infrastructure.database.runtime import (
    create_postgres_runtime,
)


pytestmark = pytest.mark.integration


class FakeRecoveryGateway:
    def __init__(
        self,
        existing_channels=None,
        existing_lobbies=None,
    ):
        self.existing_channels = set(
            existing_channels or []
        )

        self.existing_lobbies = set(
            existing_lobbies or []
        )

        self.registered_messages: list[int] = []

    async def channel_exists(
        self,
        key: GameSessionKey,
    ) -> bool:
        return key in self.existing_channels

    async def lobby_message_exists(
        self,
        key: GameSessionKey,
        message_id: int,
    ) -> bool:
        return (
            key,
            message_id,
        ) in self.existing_lobbies

    def register_lobby_view(
        self,
        message_id: int,
    ) -> None:
        self.registered_messages.append(
            message_id
        )


@pytest.mark.asyncio
async def test_recovery_restores_persisted_waiting_game(
    postgres_session_factory,
):
    game_repository = (
        PostgresGameRepository(
            postgres_session_factory
        )
    )

    lobby_repository = (
        PostgresLobbyMessageRepository(
            postgres_session_factory
        )
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    game = Game.create(
        host_id=1
    )

    game.add_player(2)

    await game_repository.save(
        key=key,
        game=game,
    )

    await lobby_repository.save(
        key=key,
        message_id=999,
    )

    gateway = FakeRecoveryGateway(
        existing_channels={
            key,
        },
        existing_lobbies={
            (key, 999),
        },
    )

    cache: dict[
        GameSessionKey,
        int,
    ] = {}

    recovery = RecoverGameSessions(
        game_repository=game_repository,
        lobby_repository=lobby_repository,
        gateway=gateway,
        lobby_cache=cache,
    )

    summary = await recovery.execute()

    assert summary.discovered == 1
    assert summary.restored_waiting == 1
    assert summary.stale_removed == 0

    assert cache == {
        key: 999,
    }

    assert (
        gateway.registered_messages
        == [999]
    )

    persisted_game = (
        await game_repository.get(key)
    )

    assert persisted_game is not None

    assert persisted_game.host_id == 1

    assert persisted_game.players == [
        1,
        2,
    ]

    assert (
        await lobby_repository.get(key)
        == 999
    )


@pytest.mark.asyncio
async def test_recovery_removes_persisted_waiting_game_when_lobby_is_missing(
    postgres_session_factory,
):
    game_repository = (
        PostgresGameRepository(
            postgres_session_factory
        )
    )

    lobby_repository = (
        PostgresLobbyMessageRepository(
            postgres_session_factory
        )
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    game = Game.create(
        host_id=1
    )

    game.add_player(2)

    await game_repository.save(
        key=key,
        game=game,
    )

    await lobby_repository.save(
        key=key,
        message_id=999,
    )

    gateway = FakeRecoveryGateway(
        existing_channels={
            key,
        },
        existing_lobbies=set(),
    )

    cache: dict[
        GameSessionKey,
        int,
    ] = {}

    recovery = RecoverGameSessions(
        game_repository=game_repository,
        lobby_repository=lobby_repository,
        gateway=gateway,
        lobby_cache=cache,
    )

    summary = await recovery.execute()

    assert summary.discovered == 1
    assert summary.restored_waiting == 0
    assert summary.restored_started == 0
    assert summary.stale_removed == 1

    assert (
        await game_repository.get(key)
        is None
    )

    assert (
        await lobby_repository.get(key)
        is None
    )

    assert cache == {}

    assert (
        gateway.registered_messages
        == []
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repeated_recovery_does_not_duplicate_postgres_state(
    postgres_session_factory,
):
    game_repository = PostgresGameRepository(
        postgres_session_factory
    )

    lobby_repository = (
        PostgresLobbyMessageRepository(
            postgres_session_factory
        )
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    await game_repository.save(
        key=key,
        game=Game.create(host_id=1),
    )

    await lobby_repository.save(
        key=key,
        message_id=999,
    )

    gateway = FakeRecoveryGateway(
        existing_channels={key},
        existing_lobbies={
            (key, 999),
        },
    )

    cache = {}

    recovery = RecoverGameSessions(
        game_repository=game_repository,
        lobby_repository=lobby_repository,
        gateway=gateway,
        lobby_cache=cache,
    )

    first = await recovery.execute()
    second = await recovery.execute()

    assert first.restored_waiting == 1
    assert second.restored_waiting == 1

    sessions = (
        await game_repository.list_active()
    )

    assert len(sessions) == 1

    assert (
        await lobby_repository.get(key)
        == 999
    )

    assert cache == {
        key: 999,
    }

    async with (
        postgres_session_factory()
        as session
    ):
        games_count = (
            await session.scalar(
                select(
                    func.count()
                ).select_from(
                    GameRecord
                )
            )
        )

        players_count = (
            await session.scalar(
                select(
                    func.count()
                ).select_from(
                    GamePlayerRecord
                )
            )
        )

        discord_sessions_count = (
            await session.scalar(
                select(
                    func.count()
                ).select_from(
                    DiscordSessionRecord
                )
            )
        )

    assert games_count == 1
    assert players_count == 1
    assert discord_sessions_count == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_stale_postgres_session_remains_clean_after_second_recovery(
    postgres_session_factory,
):
    game_repository = PostgresGameRepository(
        postgres_session_factory
    )

    lobby_repository = (
        PostgresLobbyMessageRepository(
            postgres_session_factory
        )
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    await game_repository.save(
        key=key,
        game=Game.create(host_id=1),
    )

    await lobby_repository.save(
        key=key,
        message_id=999,
    )

    gateway = FakeRecoveryGateway(
        existing_channels={key},
        existing_lobbies=set(),
    )

    cache = {}

    recovery = RecoverGameSessions(
        game_repository=game_repository,
        lobby_repository=lobby_repository,
        gateway=gateway,
        lobby_cache=cache,
    )

    first = await recovery.execute()
    second = await recovery.execute()

    assert first.discovered == 1
    assert first.stale_removed == 1

    assert second.discovered == 0
    assert second.stale_removed == 0

    assert (
        await game_repository.list_active()
        == []
    )

    assert (
        await lobby_repository.get(key)
        is None
    )

    assert cache == {}

    async with (
        postgres_session_factory()
        as session
    ):
        games_count = await session.scalar(
            select(
                func.count()
            ).select_from(
                GameRecord
            )
        )

        players_count = await session.scalar(
            select(
                func.count()
            ).select_from(
                GamePlayerRecord
            )
        )

        metadata_count = await session.scalar(
            select(
                func.count()
            ).select_from(
                DiscordSessionRecord
            )
        )

    assert games_count == 0
    assert players_count == 0
    assert metadata_count == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_runtime_shutdown_does_not_delete_persisted_session(
    postgres_session_factory,
):
    # The fixture guarantees that the test schema
    # already exists in TEST_DATABASE_URL.
    database_url = os.getenv(
        "TEST_DATABASE_URL"
    )

    assert database_url is not None

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    runtime = create_postgres_runtime(
        database_url
    )

    await runtime.game_repository.save(
        key=key,
        game=Game.create(host_id=1),
    )

    await runtime.lobby_message_repository.save(
        key=key,
        message_id=999,
    )

    await runtime.close()

    runtime_after_restart = (
        create_postgres_runtime(
            database_url
        )
    )

    try:
        stored_game = (
            await runtime_after_restart
            .game_repository
            .get(key)
        )

        stored_message_id = (
            await runtime_after_restart
            .lobby_message_repository
            .get(key)
        )

        assert stored_game is not None
        assert stored_game.host_id == 1

        assert (
            stored_message_id
            == 999
        )

    finally:
        await (
            runtime_after_restart.close()
        )