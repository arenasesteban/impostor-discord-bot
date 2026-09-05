from impostor_bot.errors.infrastructure import (
    DatabaseError,
    DatabaseUnavailableError,
    DiscordAPIError,
    InfrastructureError,
    WordProviderError,
)


def test_database_error_is_infrastructure_error():
    assert issubclass(
        DatabaseError,
        InfrastructureError,
    )


def test_database_unavailable_is_database_error():
    assert issubclass(
        DatabaseUnavailableError,
        DatabaseError,
    )


def test_discord_api_error_is_infrastructure_error():
    assert issubclass(
        DiscordAPIError,
        InfrastructureError,
    )


def test_word_provider_error_is_infrastructure_error():
    assert issubclass(
        WordProviderError,
        InfrastructureError,
    )