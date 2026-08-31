import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from impostor_bot.infrastructure.database.base import Base
from impostor_bot.infrastructure.database.session import (
    create_database_engine,
    create_session_factory,
)

import impostor_bot.infrastructure.database.models  # noqa: F401


load_dotenv()


@pytest_asyncio.fixture
async def postgres_session_factory():
    database_url = os.getenv(
        "TEST_DATABASE_URL"
    )

    if not database_url:
        pytest.skip(
            "TEST_DATABASE_URL is not configured."
        )

    engine = create_database_engine(
        database_url
    )

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.drop_all
        )

        await connection.run_sync(
            Base.metadata.create_all
        )

    session_factory = create_session_factory(
        engine
    )

    yield session_factory

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.drop_all
        )

    await engine.dispose()