import pytest
from tests.helpers.factories import (
    make_started_game,
)

from impostor_bot.game.exceptions import InvalidGameStateError
from impostor_bot.game.game import Game
from impostor_bot.game.state import GameState


def test_started_game_can_be_finished():
    game = make_started_game()

    game.finish()

    assert game.status == GameState.FINISHED


def test_waiting_game_cannot_be_finished():
    game = Game.create(host_id=1)

    with pytest.raises(InvalidGameStateError):
        game.finish()

    assert game.status == GameState.WAITING


def test_waiting_game_can_be_cancelled():
    game = Game.create(host_id=1)

    game.cancel()

    assert game.status == GameState.CANCELLED


def test_started_game_can_be_cancelled():
    game = make_started_game()

    game.cancel()

    assert game.status == GameState.CANCELLED


def test_finished_game_cannot_be_cancelled():
    game = make_started_game()
    game.finish()

    with pytest.raises(InvalidGameStateError):
        game.cancel()

    assert game.status == GameState.FINISHED


def test_cancelled_game_cannot_be_cancelled_again():
    game = Game.create(host_id=1)
    game.cancel()

    with pytest.raises(InvalidGameStateError):
        game.cancel()

    assert game.status == GameState.CANCELLED


def test_finished_game_cannot_be_finished_again():
    game = make_started_game()
    game.finish()

    with pytest.raises(InvalidGameStateError):
        game.finish()

    assert game.status == GameState.FINISHED


def test_cancelled_game_cannot_be_finished():
    game = Game.create(host_id=1)
    game.cancel()

    with pytest.raises(InvalidGameStateError):
        game.finish()

    assert game.status == GameState.CANCELLED