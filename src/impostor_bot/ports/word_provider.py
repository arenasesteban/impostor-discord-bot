from typing import Protocol


class WordProvider(Protocol):
    def get_word(self, category: str | None = None) -> str:
        ...