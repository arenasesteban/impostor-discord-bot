from impostor_bot.game.session import Session


active_games: dict[int, Session] = {}

active_lobby_messages: dict[int, int] = {}