from enum import StrEnum

from impostor_bot.constants import (
    STATUS_OPEN,
    STATUS_STARTED,
    STATUS_CANCELLED,
    STATUS_FINISHED
)


class GameState(StrEnum):
    WAITING = STATUS_OPEN
    STARTED = STATUS_STARTED
    FINISHED = STATUS_FINISHED
    CANCELLED = STATUS_CANCELLED