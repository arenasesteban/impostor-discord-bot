import random
from collections.abc import Sequence


class PythonRandomSelector:
    def choose(self, values: Sequence[int]) -> int:
        return random.choice(values)