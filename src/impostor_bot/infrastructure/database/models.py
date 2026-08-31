from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from impostor_bot.game.state import GameState
from impostor_bot.infrastructure.database.base import Base


_VALID_STATES_SQL = ", ".join(
    f"'{state.value}'"
    for state in GameState
)


class GameRecord(Base):
    __tablename__ = "games"

    guild_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    channel_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    host_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    state: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    secret_word: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    impostor_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    players: Mapped[list["GamePlayerRecord"]] = relationship(
        "GamePlayerRecord",
        back_populates="game",
        cascade="all, delete-orphan",
        order_by="GamePlayerRecord.position",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint(
            f"state IN ({_VALID_STATES_SQL})",
            name="ck_games_state",
        ),
    )


class GamePlayerRecord(Base):
    __tablename__ = "game_players"

    guild_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    channel_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    player_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    game: Mapped[GameRecord] = relationship(
        "GameRecord",
        back_populates="players",
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["guild_id", "channel_id"],
            ["games.guild_id", "games.channel_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "guild_id",
            "channel_id",
            "position",
            name="uq_game_players_position",
        ),
    )