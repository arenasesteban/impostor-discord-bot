import random
from dataclasses import dataclass, field

from .exceptions import (
    GameError,
    GameAlreadyStartedError, 
    PlayerAlreadyJoinedError,
    HostCannotLeaveError,
    PlayerNotFoundError
)


MIN_PLAYERS = 3
STATUS_OPEN = "open"
STATUS_STARTED = "started"
STATUS_CANCELLED = "cancelled"


@dataclass
class Session:
    host_id: int
    players: list[int] = field(default_factory=list)
    status: str = STATUS_OPEN
    secret_word: str | None = None
    impostor_id: int | None = None

    def __post_init__(self):
        self.players.append(self.host_id)

    def add_player(self, player_id: int) -> None:
        if self.status != STATUS_OPEN:
            raise GameAlreadyStartedError("Cannot join a game that has already started.")
        
        if player_id in self.players:
            raise PlayerAlreadyJoinedError("Player has already joined the game.")
        
        self.players.append(player_id)

    def remove_player(self, player_id: int) -> None:
        if self.status != STATUS_OPEN:
            raise GameAlreadyStartedError("Cannot leave a game that has already started.")
        
        if player_id == self.host_id:
            raise HostCannotLeaveError("The host cannot leave the game.")
        
        if player_id not in self.players:
            raise PlayerNotFoundError("Player not found in the game session.")
        
        self.players.remove(player_id)

    def can_start(self) -> bool:
        return self.status == STATUS_OPEN and len(self.players) >= MIN_PLAYERS
    
    def start_game(self, secret_word: str) -> None:
        if self.status != STATUS_OPEN:
            raise GameAlreadyStartedError("Game has already started.")
    
        if len(self.players) < MIN_PLAYERS:
            raise ValueError(f"Cannot start the game with less than {MIN_PLAYERS} players.")
        
        self.secret_word = secret_word
        self.impostor_id = random.choice(self.players)
        self.status = STATUS_STARTED

        return self.generate_roles()
    
    def generate_roles(self) -> dict[int, str]:
        if self.secret_word is None:
            raise GameError("Cannot generate roles without a secret word.")
        
        if self.impostor_id is None:
            raise GameError("Cannot generate roles without an impostor.")
        
        roles = {}

        for player_id in self.players:
            if player_id == self.impostor_id:
                roles[player_id] = "impostor"
            else:
                roles[player_id] = self.secret_word
        
        return roles
    
    def cancel_game(self) -> None:
        if self.status == STATUS_STARTED:
            raise GameAlreadyStartedError("Cannot cancel a game that has already started.")
        
        self.status = STATUS_CANCELLED