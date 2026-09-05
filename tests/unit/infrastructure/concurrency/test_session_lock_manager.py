import asyncio

import pytest

from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.concurrency.asyncio_session_lock_manager import (
    AsyncioSessionLockManager,
)


def test_same_session_operations_are_serialized():
    async def scenario():
        manager = AsyncioSessionLockManager()

        first_key = GameSessionKey(
            guild_id=100,
            channel_id=200,
        )

        second_key = GameSessionKey(
            guild_id=100,
            channel_id=200,
        )

        first_entered = asyncio.Event()
        release_first = asyncio.Event()

        second_attempting = asyncio.Event()
        second_entered = asyncio.Event()

        async def first_operation():
            async with manager.lock(first_key):
                first_entered.set()
                await release_first.wait()

        async def second_operation():
            await first_entered.wait()

            second_attempting.set()

            async with manager.lock(second_key):
                second_entered.set()

        first_task = asyncio.create_task(
            first_operation()
        )

        second_task = asyncio.create_task(
            second_operation()
        )

        await first_entered.wait()
        await second_attempting.wait()

        await asyncio.sleep(0)

        assert second_entered.is_set() is False

        release_first.set()

        await asyncio.gather(
            first_task,
            second_task,
        )

        assert second_entered.is_set() is True

    asyncio.run(scenario())


@pytest.mark.parametrize(
    (
        "second_guild_id",
        "second_channel_id",
    ),
    [
        (101, 200),
        (100, 201),
    ],
    ids=[
        "different-guild-same-channel",
        "same-guild-different-channel",
    ],
)
def test_different_sessions_can_run_concurrently(
    second_guild_id,
    second_channel_id,
):
    async def scenario():
        manager = AsyncioSessionLockManager()

        first_key = GameSessionKey(
            guild_id=100,
            channel_id=200,
        )

        second_key = GameSessionKey(
            guild_id=second_guild_id,
            channel_id=second_channel_id,
        )

        first_entered = asyncio.Event()
        release_first = asyncio.Event()

        second_entered = asyncio.Event()

        async def first_operation():
            async with manager.lock(first_key):
                first_entered.set()
                await release_first.wait()

        async def second_operation():
            await first_entered.wait()

            async with manager.lock(second_key):
                second_entered.set()

        first_task = asyncio.create_task(
            first_operation()
        )

        second_task = asyncio.create_task(
            second_operation()
        )

        await first_entered.wait()

        await asyncio.wait_for(
            second_entered.wait(),
            timeout=1,
        )

        assert second_entered.is_set() is True

        release_first.set()

        await asyncio.gather(
            first_task,
            second_task,
        )

    asyncio.run(scenario())



@pytest.mark.asyncio
async def test_lock_is_released_after_exception():
    manager = AsyncioSessionLockManager()

    key = GameSessionKey(
        guild_id=1,
        channel_id=1,
    )

    with pytest.raises(RuntimeError):
        async with manager.lock(key):
            raise RuntimeError("boom")

    async def acquire_again():
        async with manager.lock(key):
            return True

    acquired = await asyncio.wait_for(
        acquire_again(),
        timeout=1,
    )

    assert acquired is True