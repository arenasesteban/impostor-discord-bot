from dataclasses import FrozenInstanceError

import pytest

from impostor_bot.game.player import Player


def test_player_stores_discord_user_id():
    player = Player(id=100)

    assert player.id == 100


def test_player_is_immutable():
    player = Player(id=100)

    with pytest.raises(FrozenInstanceError):
        player.id = 200