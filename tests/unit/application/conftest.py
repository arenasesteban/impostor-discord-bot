import pytest

from impostor_bot.infrastructure.concurrency.asyncio_session_lock_manager import (
    AsyncioSessionLockManager,
)


@pytest.fixture
def lock_manager():
    return AsyncioSessionLockManager()