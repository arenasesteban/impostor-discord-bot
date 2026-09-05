from unittest.mock import Mock

import pytest

from impostor_bot.discord.recovery_gateway import (
    DiscordPySessionRecoveryGateway,
)
from impostor_bot.discord.views import LobbyView


@pytest.mark.asyncio
async def test_register_lobby_view_is_idempotent():
    client = Mock()

    gateway = DiscordPySessionRecoveryGateway(
        client
    )

    gateway.register_lobby_view(
        999
    )

    gateway.register_lobby_view(
        999
    )

    client.add_view.assert_called_once()

    call = client.add_view.call_args

    view = call.args[0]

    assert isinstance(
        view,
        LobbyView,
    )

    assert view.is_persistent()

    assert (
        call.kwargs["message_id"]
        == 999
    )