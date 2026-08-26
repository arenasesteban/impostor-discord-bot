from dataclasses import dataclass


@dataclass(frozen=True)
class GameSessionKey:
    guild_id: int
    channel_id: int