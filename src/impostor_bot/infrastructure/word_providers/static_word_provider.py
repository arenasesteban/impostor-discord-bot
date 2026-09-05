from json import JSONDecodeError

from impostor_bot.errors.infrastructure import WordProviderError
from impostor_bot.words.exceptions import WordError
from impostor_bot.words.loader import get_random_word


class StaticWordProvider:
    async def get_word(self, category: str | None = None) -> str:
        try:
            if category is None:
                return get_random_word()

            return get_random_word(category)

        except (WordError, OSError, JSONDecodeError) as error:
            raise WordProviderError(
                "Unable to provide a game word."
            ) from error
