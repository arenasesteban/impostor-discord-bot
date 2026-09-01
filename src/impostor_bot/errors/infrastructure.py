class InfrastructureError(Exception):
    """Base class for failures caused by external infrastructure."""


class DatabaseError(InfrastructureError):
    """Raised when a database operation fails."""


class DatabaseUnavailableError(DatabaseError):
    """Raised when the database cannot be reached or used."""


class DiscordAPIError(InfrastructureError):
    """Raised when an unexpected Discord API operation fails."""


class WordProviderError(InfrastructureError):
    """Raised when the configured word provider cannot provide a word."""