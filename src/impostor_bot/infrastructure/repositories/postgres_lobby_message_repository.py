from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.database.error_translation import (
    translate_database_error,
)
from impostor_bot.infrastructure.database.models import DiscordSessionRecord
from impostor_bot.infrastructure.database.session import AsyncSessionFactory


class PostgresLobbyMessageRepository:
    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory

    async def get(self, key: GameSessionKey) -> int | None:
        try:
            async with self._session_factory() as session:
                record = await session.get(DiscordSessionRecord, (key.guild_id, key.channel_id))

                if record is None:
                    return None

                return record.lobby_message_id

        except (SQLAlchemyError, OSError) as error:
            raise translate_database_error(error) from error

    async def save(self, key: GameSessionKey, message_id: int) -> None:
        try:
            async with self._session_factory() as session:
                async with session.begin():
                    record = await session.get(DiscordSessionRecord, (key.guild_id, key.channel_id))

                    if record is None:
                        session.add(
                            DiscordSessionRecord(
                                guild_id=key.guild_id,
                                channel_id=key.channel_id,
                                lobby_message_id=message_id
                            )
                        )
                        return

                    record.lobby_message_id = message_id

        except (SQLAlchemyError, OSError) as error:
            raise translate_database_error(error) from error

    async def delete(self, key: GameSessionKey) -> None:
        try:
            async with self._session_factory() as session:
                async with session.begin():
                    await session.execute(
                        delete(
                            DiscordSessionRecord
                        ).where(
                            DiscordSessionRecord.guild_id == key.guild_id,
                            DiscordSessionRecord.channel_id == key.channel_id
                        )
                    )

        except (SQLAlchemyError, OSError) as error:
            raise translate_database_error(error) from error