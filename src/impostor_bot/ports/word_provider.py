from typing import Protocol


class WordProvider(Protocol):
    async def get_word(self, category: str | None = None) -> str:
        ...