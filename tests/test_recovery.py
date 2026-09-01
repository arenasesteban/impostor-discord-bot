import pytest

from impostor_bot.discord.recovery import RecoverGameSessions
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.repositories.in_memory_game_repository import (
    InMemoryGameRepository,
)


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


class FakeLobbyMessageRepository:
    def __init__(self) -> None:
        self.messages: dict[
            GameSessionKey,
            int,
        ] = {}

    async def get(
        self,
        key: GameSessionKey,
    ) -> int | None:
        return self.messages.get(key)

    async def save(
        self,
        key: GameSessionKey,
        message_id: int,
    ) -> None:
        self.messages[key] = message_id

    async def delete(
        self,
        key: GameSessionKey,
    ) -> None:
        self.messages.pop(
            key,
            None,
        )


def create_key(
    guild_id: int = 100,
    channel_id: int = 200,
) -> GameSessionKey:
    return GameSessionKey(
        guild_id=guild_id,
        channel_id=channel_id,
    )


def create_started_game() -> Game:
    game = Game.create(
        host_id=1
    )

    game.add_player(2)
    game.add_player(3)

    game.start_game(
        secret_word="pizza",
        impostor_id=2,
    )

    return game


@pytest.mark.asyncio
async def test_recovery_restores_waiting_session():
    key = create_key()

    game_repository = (
        InMemoryGameRepository()
    )

    game = Game.create(
        host_id=1
    )

    await game_repository.save(
        key=key,
        game=game,
    )

    lobby_repository = (
        FakeLobbyMessageRepository()
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

    assert cache == {
        key: 999,
    }

    assert (
        gateway.registered_messages
        == [999]
    )

    assert summary.discovered == 1
    assert summary.restored_waiting == 1
    assert summary.restored_started == 0
    assert summary.stale_removed == 0
    assert summary.detached_lobbies == 0

    assert (
        await game_repository.get(key)
        is not None
    )

    assert (
        await lobby_repository.get(key)
        == 999
    )


@pytest.mark.asyncio
async def test_recovery_removes_waiting_session_without_lobby_metadata():
    key = create_key()

    game_repository = (
        InMemoryGameRepository()
    )

    await game_repository.save(
        key=key,
        game=Game.create(
            host_id=1
        ),
    )

    lobby_repository = (
        FakeLobbyMessageRepository()
    )

    gateway = FakeRecoveryGateway(
        existing_channels={
            key,
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

    assert summary.discovered == 1
    assert summary.restored_waiting == 0
    assert summary.restored_started == 0
    assert summary.stale_removed == 1
    assert summary.detached_lobbies == 0


@pytest.mark.asyncio
async def test_recovery_removes_waiting_session_when_lobby_message_is_missing():
    key = create_key()

    game_repository = (
        InMemoryGameRepository()
    )

    await game_repository.save(
        key=key,
        game=Game.create(
            host_id=1
        ),
    )

    lobby_repository = (
        FakeLobbyMessageRepository()
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

    assert summary.discovered == 1
    assert summary.stale_removed == 1


@pytest.mark.parametrize(
    "started",
    [
        False,
        True,
    ],
)
@pytest.mark.asyncio
async def test_recovery_removes_session_when_channel_no_longer_exists(
    started: bool,
):
    key = create_key()

    if started:
        game = create_started_game()
    else:
        game = Game.create(
            host_id=1
        )

    game_repository = (
        InMemoryGameRepository()
    )

    await game_repository.save(
        key=key,
        game=game,
    )

    lobby_repository = (
        FakeLobbyMessageRepository()
    )

    await lobby_repository.save(
        key=key,
        message_id=999,
    )

    gateway = FakeRecoveryGateway(
        existing_channels=set(),
        existing_lobbies=set(),
    )

    cache = {
        key: 999,
    }

    recovery = RecoverGameSessions(
        game_repository=game_repository,
        lobby_repository=lobby_repository,
        gateway=gateway,
        lobby_cache=cache,
    )

    summary = await recovery.execute()

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

    assert summary.discovered == 1
    assert summary.stale_removed == 1


@pytest.mark.asyncio
async def test_recovery_restores_started_session():
    key = create_key()

    game_repository = (
        InMemoryGameRepository()
    )

    await game_repository.save(
        key=key,
        game=create_started_game(),
    )

    lobby_repository = (
        FakeLobbyMessageRepository()
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

    assert cache == {
        key: 999,
    }

    assert (
        gateway.registered_messages
        == []
    )

    assert summary.discovered == 1
    assert summary.restored_waiting == 0
    assert summary.restored_started == 1
    assert summary.stale_removed == 0
    assert summary.detached_lobbies == 0

    stored_game = (
        await game_repository.get(key)
    )

    assert stored_game is not None


@pytest.mark.asyncio
async def test_started_session_survives_missing_lobby_message():
    key = create_key()

    game_repository = (
        InMemoryGameRepository()
    )

    await game_repository.save(
        key=key,
        game=create_started_game(),
    )

    lobby_repository = (
        FakeLobbyMessageRepository()
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

    assert (
        await game_repository.get(key)
        is not None
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

    assert summary.discovered == 1
    assert summary.restored_waiting == 0
    assert summary.restored_started == 1
    assert summary.stale_removed == 0
    assert summary.detached_lobbies == 1


@pytest.mark.asyncio
async def test_recovery_removes_unexpected_terminal_game():
    key = create_key()

    game = Game.create(
        host_id=1
    )

    game.cancel()

    game_repository = (
        InMemoryGameRepository()
    )

    await game_repository.save(
        key=key,
        game=game,
    )

    lobby_repository = (
        FakeLobbyMessageRepository()
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

    assert summary.discovered == 1
    assert summary.stale_removed == 1


@pytest.mark.asyncio
async def test_recovery_handles_multiple_sessions_independently():
    waiting_key = create_key(
        guild_id=100,
        channel_id=200,
    )

    stale_key = create_key(
        guild_id=100,
        channel_id=201,
    )

    started_key = create_key(
        guild_id=101,
        channel_id=200,
    )

    game_repository = (
        InMemoryGameRepository()
    )

    await game_repository.save(
        key=waiting_key,
        game=Game.create(
            host_id=1
        ),
    )

    await game_repository.save(
        key=stale_key,
        game=Game.create(
            host_id=2
        ),
    )

    await game_repository.save(
        key=started_key,
        game=create_started_game(),
    )

    lobby_repository = (
        FakeLobbyMessageRepository()
    )

    await lobby_repository.save(
        key=waiting_key,
        message_id=1001,
    )

    await lobby_repository.save(
        key=stale_key,
        message_id=1002,
    )

    await lobby_repository.save(
        key=started_key,
        message_id=1003,
    )

    gateway = FakeRecoveryGateway(
        existing_channels={
            waiting_key,
            stale_key,
            started_key,
        },
        existing_lobbies={
            (waiting_key, 1001),
            (started_key, 1003),
        },
    )

    old_key = create_key(
        guild_id=999,
        channel_id=999,
    )

    cache = {
        old_key: 12345,
    }

    recovery = RecoverGameSessions(
        game_repository=game_repository,
        lobby_repository=lobby_repository,
        gateway=gateway,
        lobby_cache=cache,
    )

    summary = await recovery.execute()

    assert summary.discovered == 3
    assert summary.restored_waiting == 1
    assert summary.restored_started == 1
    assert summary.stale_removed == 1
    assert summary.detached_lobbies == 0

    assert (
        await game_repository.get(
            waiting_key
        )
        is not None
    )

    assert (
        await game_repository.get(
            started_key
        )
        is not None
    )

    assert (
        await game_repository.get(
            stale_key
        )
        is None
    )

    assert cache == {
        waiting_key: 1001,
        started_key: 1003,
    }

    assert (
        gateway.registered_messages
        == [1001]
    )

    assert (
        await lobby_repository.get(
            stale_key
        )
        is None
    )