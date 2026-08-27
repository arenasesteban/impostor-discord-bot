from dataclasses import dataclass, field

from impostor_bot.constants import (
    IMPOSTOR_ROLE,
    MIN_PLAYERS,
)

from impostor_bot.game.exceptions import (
    GameError,
    GameAlreadyStartedError,
    PlayerAlreadyJoinedError,
    HostCannotLeaveError,
    PlayerNotFoundError,
    NotEnoughPlayersError,
)

from impostor_bot.game.state import GameState


@dataclass
class Game:
    host_id: int
    players: list[int] = field(default_factory=list)
    status: GameState = GameState.WAITING
    secret_word: str | None = None
    impostor_id: int | None = None

    def __post_init__(self) -> None:
        self.players.append(self.host_id)

    @classmethod
    def create(cls, host_id: int) -> "Game":
        return cls(host_id=host_id)

    def add_player(self, player_id: int) -> None:
        if self.status != GameState.WAITING:
            raise GameAlreadyStartedError(
                "Cannot join a game that has already started."
            )
        
        if player_id in self.players:
            raise PlayerAlreadyJoinedError(
                "Player has already joined the game."
            )
        
        self.players.append(player_id)

    def remove_player(self, player_id: int) -> None:
        if self.status != GameState.WAITING:
            raise GameAlreadyStartedError(
                "Cannot leave a game that has already started."
            )
        
        if player_id == self.host_id:
            raise HostCannotLeaveError(
                "The host cannot leave the game."
            )
        
        if player_id not in self.players:
            raise PlayerNotFoundError(
                "Player not found in the game session."
            )
        
        self.players.remove(player_id)

    def can_start(self) -> bool:
        return (
            self.status == GameState.WAITING
            and len(self.players) >= MIN_PLAYERS
        )

    def validate_start(self) -> None:
        if self.status != GameState.WAITING:
            raise GameAlreadyStartedError(
                "Game has already started."
            )

        if len(self.players) < MIN_PLAYERS:
            raise NotEnoughPlayersError(
                f"Cannot start the game with less than "
                f"{MIN_PLAYERS} players."
            )

    def start_game(self, secret_word: str, impostor_id: int) -> dict[int, str]:
        self.validate_start()

        if impostor_id not in self.players:
            raise GameError(
                "The selected impostor must belong to the game."
            )

        self.secret_word = secret_word
        self.impostor_id = impostor_id
        self.status = GameState.STARTED

        return self.generate_roles()

    def generate_roles(self) -> dict[int, str]:
        if self.secret_word is None:
            raise GameError(
                "Cannot generate roles without a secret word."
            )
        
        if self.impostor_id is None:
            raise GameError(
                "Cannot generate roles without an impostor."
            )
        
        roles: dict[int, str] = {}

        for player_id in self.players:
            if player_id == self.impostor_id:
                roles[player_id] = IMPOSTOR_ROLE
            else:
                roles[player_id] = self.secret_word
        
        return roles

    def cancel(self) -> None:
        if self.status == GameState.STARTED:
            raise GameAlreadyStartedError(
                "Cannot cancel a game that has already started."
            )

        self.status = GameState.CANCELLED