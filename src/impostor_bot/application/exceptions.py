class ApplicationError(Exception):
    """Base class for application-level errors."""


class GameAlreadyExistsError(ApplicationError):
    """Raised when a game already exists for the requested session."""