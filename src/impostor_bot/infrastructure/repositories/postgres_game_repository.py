from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.database.game_mapper import (
    apply_game_to_record,
    build_player_records,
    game_record_to_domain,
)
from impostor_bot.infrastructure.database.models import (
    GamePlayerRecord,
    GameRecord,
)
from impostor_bot.infrastructure.database.session import (
    AsyncSessionFactory,
)


class PostgresGameRepository:
    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory

    async def get(self, key: GameSessionKey) -> Game | None:
        async with self._session_factory() as session:
            statement = (
                select(GameRecord)
                .options(
                    selectinload(
                        GameRecord.players
                    )
                )
                .where(
                    GameRecord.guild_id == key.guild_id,
                    GameRecord.channel_id == key.channel_id
                )
            )

            result = await session.execute(statement)

            record = result.scalar_one_or_none()

            if record is None:
                return None

            return game_record_to_domain(record)

    async def save(self, key: GameSessionKey, game: Game) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                record = await session.get(GameRecord, (key.guild_id, key.channel_id),)

                if record is None:
                    record = GameRecord(
                        guild_id=key.guild_id,
                        channel_id=key.channel_id,
                        host_id=game.host_id,
                        state=game.status.value,
                        secret_word=game.secret_word,
                        impostor_id=game.impostor_id,
                    )

                    session.add(record)

                    await session.flush()

                else:
                    apply_game_to_record(record, game)

                await session.execute(
                    delete(
                        GamePlayerRecord
                    ).where(
                        GamePlayerRecord.guild_id == key.guild_id,
                        GamePlayerRecord.channel_id == key.channel_id,
                    )
                )

                await session.flush()

                session.add_all(
                    build_player_records(
                        key=key,
                        game=game,
                    )
                )

    async def delete(self, key: GameSessionKey) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                await session.execute(
                    delete(
                        GameRecord  
                    ).where(
                        GameRecord.guild_id == key.guild_id,
                        GameRecord.channel_id == key.channel_id,
                    )
                )


    async def list_active(self) -> list[tuple[GameSessionKey, Game]]:
        async with self._session_factory() as session:
            statement = (
                select(GameRecord)
                .options(
                    selectinload(
                        GameRecord.players
                    )
                )
                .order_by(
                    GameRecord.guild_id,
                    GameRecord.channel_id,
                )
            )

            result = await session.execute(statement)

            records = result.scalars().all()

            return [
                (
                    GameSessionKey(
                        guild_id=record.guild_id,
                        channel_id=record.channel_id,
                    ),
                    game_record_to_domain(
                        record
                    ),
                )
                for record in records
            ]