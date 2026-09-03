class InfrastructureError(Exception):
    """Base class for technical dependency failures."""


class DatabaseError(InfrastructureError):
    """Raised when a database operation fails."""


class DatabaseUnavailableError(DatabaseError):
    """Raised when the database cannot be reached or used."""


class DiscordAPIError(InfrastructureError):
    """Raised when a Discord API operation fails unexpectedly."""


class WordProviderError(InfrastructureError):
    """Raised when the configured word provider cannot provide a word."""