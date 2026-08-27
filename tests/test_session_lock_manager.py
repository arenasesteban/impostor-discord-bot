import asyncio

from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.concurrency.asyncio_session_lock_manager import (
    AsyncioSessionLockManager,
)


def test_same_session_operations_are_serialized():
    async def scenario():
        manager = AsyncioSessionLockManager()

        key = GameSessionKey(
            guild_id=100,
            channel_id=200,
        )

        first_entered = asyncio.Event()
        release_first = asyncio.Event()

        second_attempting = asyncio.Event()
        second_entered = asyncio.Event()

        async def first_operation():
            async with manager.lock(key):
                first_entered.set()

                await release_first.wait()

        async def second_operation():
            await first_entered.wait()

            second_attempting.set()

            async with manager.lock(key):
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


def test_different_sessions_can_run_concurrently():
    async def scenario():
        manager = AsyncioSessionLockManager()

        first_key = GameSessionKey(
            guild_id=100,
            channel_id=200,
        )

        second_key = GameSessionKey(
            guild_id=101,
            channel_id=200,
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