class ApplicationError(Exception):
    """Base class for expected application-level failures."""


class GameAlreadyExistsError(ApplicationError):
    """Raised when a game already exists for the requested session."""


class GameNotFoundError(ApplicationError):
    """Raised when no game exists for the requested session."""


class NotGameHostError(ApplicationError):
    """Raised when a non-host user attempts a host-only action."""