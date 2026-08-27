from collections.abc import Sequence
from typing import Protocol


class RandomSelector(Protocol):
    def choose(self, values: Sequence[int]) -> int:
        ...