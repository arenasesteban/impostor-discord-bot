from enum import StrEnum

from impostor_bot.constants import (
    STATUS_OPEN,
    STATUS_STARTED,
    STATUS_CANCELLED
)


class GameState(StrEnum):
    WAITING = STATUS_OPEN
    STARTED = STATUS_STARTED
    CANCELLED = STATUS_CANCELLED