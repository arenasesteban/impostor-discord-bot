from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from impostor_bot.infrastructure.database.session import (
    create_database_engine,
    create_session_factory,
)
from impostor_bot.infrastructure.repositories.postgres_game_repository import (
    PostgresGameRepository,
)
from impostor_bot.infrastructure.repositories.postgres_lobby_message_repository import (
    PostgresLobbyMessageRepository,
)


@dataclass(slots=True)
class PostgresRuntime:
    engine: AsyncEngine
    game_repository: PostgresGameRepository
    lobby_message_repository: PostgresLobbyMessageRepository

    async def check_connection(self) -> None:
        async with self.engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    async def close(self) -> None:
        await self.engine.dispose()


def create_postgres_runtime(database_url: str) -> PostgresRuntime:
    engine = create_database_engine(database_url)

    session_factory = create_session_factory(engine)

    return PostgresRuntime(
        engine=engine,
        game_repository=PostgresGameRepository(session_factory),
        lobby_message_repository=PostgresLobbyMessageRepository(session_factory)
    )