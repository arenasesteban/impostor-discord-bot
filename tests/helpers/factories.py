from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey


def make_session_key(*, guild_id: int = 1, channel_id: int = 1) -> GameSessionKey:
    return GameSessionKey(
        guild_id=guild_id,
        channel_id=channel_id,
    )



def make_ready_game(*, host_id: int = 1, player_ids: tuple[int, ...] = (2, 3)) -> Game:
    game = Game.create(host_id=host_id)

    for player_id in player_ids:
        game.add_player(player_id)

    return game


def make_started_game(*, host_id: int = 1, player_ids: tuple[int, ...] = (2, 3), secret_word: str = "pizza", impostor_id: int = 2) -> Game:
    game = make_ready_game(host_id=host_id, player_ids=player_ids)

    game.start_game(
        secret_word=secret_word,
        impostor_id=impostor_id,
    )

    return game
