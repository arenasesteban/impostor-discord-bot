from impostor_bot.constants import STATUS_OPEN
from impostor_bot.game.game import Game
from impostor_bot.game.session import Session
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.game.state import GameState


def test_game_create_registers_host():
    game = Game.create(host_id=1)

    assert game.host_id == 1
    assert game.players == [1]


def test_game_create_uses_waiting_initial_state():
    game = Game.create(host_id=1)

    assert game.status == GameState.WAITING
    assert game.status == STATUS_OPEN


def test_session_remains_compatible_with_game():
    game = Session(host_id=1)

    assert isinstance(game, Game)


def test_game_session_key_identifies_discord_context():
    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    assert key.guild_id == 100
    assert key.channel_id == 200