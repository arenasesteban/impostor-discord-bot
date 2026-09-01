from json import JSONDecodeError
from unittest.mock import Mock

import pytest

import impostor_bot.infrastructure.word_providers.static_word_provider as provider_module
from impostor_bot.errors import (
    WordProviderError,
)
from impostor_bot.infrastructure.word_providers.static_word_provider import (
    StaticWordProvider,
)
from impostor_bot.words.exceptions import (
    WordsFileNotFoundError,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "source_error",
    [
        WordsFileNotFoundError(
            "/secret/path/words.json"
        ),
        OSError(
            "filesystem unavailable"
        ),
        JSONDecodeError(
            "invalid JSON",
            "{",
            0,
        ),
    ],
)
async def test_provider_translates_external_errors(
    monkeypatch,
    source_error,
):
    monkeypatch.setattr(
        provider_module,
        "get_random_word",
        Mock(
            side_effect=source_error
        ),
    )

    provider = StaticWordProvider()

    with pytest.raises(
        WordProviderError
    ) as exc_info:
        await provider.get_word()

    assert (
        exc_info.value.__cause__
        is source_error
    )


@pytest.mark.asyncio
async def test_provider_returns_word(
    monkeypatch,
):
    monkeypatch.setattr(
        provider_module,
        "get_random_word",
        Mock(return_value="pizza"),
    )

    assert (
        await StaticWordProvider().get_word()
        == "pizza"
    )