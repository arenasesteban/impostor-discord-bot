
class GameError(Exception):
    """Base class for all game-domain errors."""


class GameRuleError(GameError):
    """Base class for expected violations of game rules."""


class GameInvariantError(GameError):
    """Raised when the internal state of a game is inconsistent."""


class InvalidGameStateError(GameRuleError):
    """Raised when an operation is invalid for the current game state."""


class GameAlreadyStartedError(InvalidGameStateError):
    """Raised when a waiting-only operation is attempted after start."""


class PlayerAlreadyJoinedError(GameRuleError):
    """Raised when a player tries to join a game they already belong to."""


class HostCannotLeaveError(GameRuleError):
    """Raised when the host tries to leave the game."""


class PlayerNotFoundError(GameRuleError):
    """Raised when a player is not part of the game."""


class NotEnoughPlayersError(GameRuleError):
    """Raised when there are not enough players to start the game."""
