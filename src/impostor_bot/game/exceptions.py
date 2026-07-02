class GameError(Exception):
    """Base class for all game-related exceptions."""


class GameAlreadyStartedError(GameError):
    """Raised when an operation is attempted on a game that has already started."""


class PlayerAlreadyJoinedError(GameError):
    """Raised when a player tries to join a game they are already part of."""


class HostCannotLeaveError(GameError):
    """Raised when the host tries to leave the game."""


class PlayerNotFoundError(GameError):
    """Raised when a player is not found in the game session."""


class NotEnoughPlayersError(GameError):
    """Raised when there are not enough players to start the game."""