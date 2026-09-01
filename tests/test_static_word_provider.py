import pytest

from impostor_bot.errors.infrastructure import (
    WordProviderError,
)
from impostor_bot.infrastructure.word_providers.static_word_provider import (
    StaticWordProvider,
)
from impostor_bot.words.exceptions import (
    WordsFileNotFoundError,
)


@pytest.mark.asyncio
async def test_word_provider_translates_loader_error(
    monkeypatch,
):
    def fail(*args, **kwargs):
        raise WordsFileNotFoundError(
            "secret/path/words.json"
        )

    monkeypatch.setattr(
        "impostor_bot.infrastructure."
        "word_providers.static_word_provider."
        "get_random_word",
        fail,
    )

    provider = StaticWordProvider()

    with pytest.raises(
        WordProviderError
    ) as exc_info:
        await provider.get_word()

    assert isinstance(
        exc_info.value.__cause__,
        WordsFileNotFoundError,
    )


@pytest.mark.asyncio
async def test_word_provider_does_not_expose_loader_details(
    monkeypatch,
):
    def fail(*args, **kwargs):
        raise WordsFileNotFoundError(
            "C:/secret/private/words.json"
        )

    monkeypatch.setattr(
        "impostor_bot.infrastructure."
        "word_providers.static_word_provider."
        "get_random_word",
        fail,
    )

    provider = StaticWordProvider()

    with pytest.raises(
        WordProviderError
    ) as exc_info:
        await provider.get_word()

    message = str(
        exc_info.value
    )

    assert "secret" not in message
    assert "private" not in message
    assert "words.json" not in message