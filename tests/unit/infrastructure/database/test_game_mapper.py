from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.game.state import GameState
from impostor_bot.infrastructure.database.game_mapper import (
    build_player_records,
)


def test_build_player_records_preserves_player_order():
    game = Game.create(host_id=1)
    game.add_player(20)
    game.add_player(30)

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    records = build_player_records(
        key=key,
        game=game,
    )

    assert [
        record.player_id
        for record in records
    ] == [1, 20, 30]

    assert [
        record.position
        for record in records
    ] == [0, 1, 2]


