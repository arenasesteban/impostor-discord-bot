import pytest

from src.impostor_bot.game.session import Session
from src.impostor_bot.game.exceptions import (
    PlayerAlreadyJoinedError,
    PlayerNotFoundError,
    GameAlreadyStartedError,
    NotEnoughPlayersError,
    HostCannotLeaveError,
)

from src.impostor_bot.constants import (
    STATUS_OPEN,
    STATUS_STARTED,
    STATUS_CANCELLED,
    MIN_PLAYERS,
)


def create_ready_game() -> Session:
    game = Session(host_id=1)
    game.add_player(2)
    game.add_player(3)
    return game


def test_game_session_registers_host_as_player():
    game = Session(host_id=1)

    assert game.host_id == 1
    assert game.players == [1]
    assert game.status == STATUS_OPEN
    assert game.secret_word is None
    assert game.impostor_id is None


def test_add_player_to_open_game():
    game = Session(host_id=1)

    game.add_player(2)

    assert game.players == [1, 2]


def test_add_multiple_players_to_open_game():
    game = Session(host_id=1)

    game.add_player(2)
    game.add_player(3)

    assert game.players == [1, 2, 3]


def test_cannot_add_duplicate_player():
    game = Session(host_id=1)
    game.add_player(2)

    with pytest.raises(PlayerAlreadyJoinedError):
        game.add_player(2)


def test_remove_player_from_open_game():
    game = Session(host_id=1)
    game.add_player(2)

    game.remove_player(2)

    assert game.players == [1]


def test_cannot_remove_player_that_is_not_in_game():
    game = Session(host_id=1)

    with pytest.raises(PlayerNotFoundError):
        game.remove_player(2)


def test_host_cannot_leave_game():
    game = Session(host_id=1)

    with pytest.raises(HostCannotLeaveError):
        game.remove_player(1)


def test_can_start_returns_false_with_less_than_minimum_players():
    game = Session(host_id=1)
    game.add_player(2)

    assert len(game.players) < MIN_PLAYERS
    assert game.can_start() is False


def test_can_start_returns_true_with_minimum_players():
    game = create_ready_game()

    assert len(game.players) == MIN_PLAYERS
    assert game.can_start() is True


def test_game_cannot_start_with_less_than_minimum_players():
    game = Session(host_id=1)
    game.add_player(2)

    with pytest.raises(NotEnoughPlayersError):
        game.start_game(secret_word="pizza")


def test_game_can_start_with_minimum_players():
    game = create_ready_game()

    roles = game.start_game(secret_word="pizza")

    assert game.status == STATUS_STARTED
    assert game.secret_word == "pizza"
    assert game.impostor_id in game.players
    assert len(roles) == len(game.players)


def test_only_one_impostor_is_generated():
    game = create_ready_game()

    roles = game.start_game(secret_word="pizza")

    impostors = [
        player_id
        for player_id, role in roles.items()
        if role == "IMPOSTOR"
    ]

    assert len(impostors) == 1


def test_impostor_does_not_receive_secret_word():
    game = create_ready_game()

    roles = game.start_game(secret_word="pizza")

    assert roles[game.impostor_id] == "IMPOSTOR"


def test_normal_players_receive_secret_word():
    game = create_ready_game()

    roles = game.start_game(secret_word="pizza")

    for player_id, role in roles.items():
        if player_id != game.impostor_id:
            assert role == "pizza"


def test_generate_roles_returns_one_role_per_player():
    game = create_ready_game()

    roles = game.start_game(secret_word="pizza")

    assert set(roles.keys()) == set(game.players)


def test_cannot_add_player_after_game_started():
    game = create_ready_game()
    game.start_game(secret_word="pizza")

    with pytest.raises(GameAlreadyStartedError):
        game.add_player(4)


def test_cannot_remove_player_after_game_started():
    game = create_ready_game()
    game.start_game(secret_word="pizza")

    with pytest.raises(GameAlreadyStartedError):
        game.remove_player(2)


def test_cancel_open_game():
    game = Session(host_id=1)

    game.cancel()

    assert game.status == STATUS_CANCELLED


def test_cannot_cancel_started_game():
    game = create_ready_game()
    game.start_game(secret_word="pizza")

    with pytest.raises(GameAlreadyStartedError):
        game.cancel()