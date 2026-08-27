from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Player:
    id: int