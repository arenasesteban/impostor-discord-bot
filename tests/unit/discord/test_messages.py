import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from impostor_bot.discord.messages import send_error


def test_send_error_uses_initial_response_when_not_done():
    interaction = SimpleNamespace(
        response=SimpleNamespace(
            is_done=lambda: False,
            send_message=AsyncMock(),
        ),
        followup=SimpleNamespace(
            send=AsyncMock(),
        ),
    )

    asyncio.run(
        send_error(
            interaction,
            "Something failed.",
        )
    )

    interaction.response.send_message.assert_awaited_once()
    interaction.followup.send.assert_not_awaited()


def test_send_error_uses_followup_after_defer():
    interaction = SimpleNamespace(
        response=SimpleNamespace(
            is_done=lambda: True,
            send_message=AsyncMock(),
        ),
        followup=SimpleNamespace(
            send=AsyncMock(),
        ),
    )

    asyncio.run(
        send_error(
            interaction,
            "Something failed.",
        )
    )

    interaction.followup.send.assert_awaited_once()
    interaction.response.send_message.assert_not_awaited()