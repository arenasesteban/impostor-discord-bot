from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.game.state import GameState
from impostor_bot.infrastructure.database.models import (
    GamePlayerRecord,
    GameRecord,
)


def game_record_to_domain(record: GameRecord) -> Game:
    players = [
        player.player_id
        for player in sorted(
            record.players,
            key=lambda player: player.position,
        )
    ]

    game = Game.create(
        host_id=record.host_id,
    )

    game.players = players

    game.status = GameState(record.state)
    game.secret_word = record.secret_word
    game.impostor_id = record.impostor_id

    return game


def apply_game_to_record(record: GameRecord,game: Game) -> None:
    record.host_id = game.host_id
    record.state = game.status.value
    record.secret_word = game.secret_word
    record.impostor_id = game.impostor_id


def build_player_records(key: GameSessionKey, game: Game) -> list[GamePlayerRecord]:
    return [
        GamePlayerRecord(
            guild_id=key.guild_id,
            channel_id=key.channel_id,
            player_id=player_id,
            position=position,
        )
        for position, player_id in enumerate(
            game.players
        )
    ]