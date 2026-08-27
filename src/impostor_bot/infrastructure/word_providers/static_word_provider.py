from impostor_bot.words.loader import get_random_word


class StaticWordProvider:
    async def get_word(self, category: str | None = None) -> str:
        if category is None:
            return get_random_word()

        return get_random_word(category)