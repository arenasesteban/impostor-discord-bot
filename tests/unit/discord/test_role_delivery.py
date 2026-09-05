from types import SimpleNamespace
from unittest.mock import (
    AsyncMock,
    MagicMock,
    call,
    patch,
)

import discord
import pytest

from impostor_bot.constants import (
    IMPOSTOR_ROLE,
)
from impostor_bot.discord.role_delivery import (
    deliver_roles,
)
from impostor_bot.errors.infrastructure import (
    DiscordAPIError,
)


def make_discord_error(
    error_type: type[discord.HTTPException],
    status: int,
) -> discord.HTTPException:
    response = MagicMock()
    response.status = status
    response.reason = "Test"

    return error_type(
        response,
        "Test failure",
    )


@pytest.mark.asyncio
async def test_deliver_roles_sends_correct_dm_for_each_role():
    impostor = SimpleNamespace(
        id=1,
    )

    normal_player = SimpleNamespace(
        id=2,
    )

    client = SimpleNamespace(
        fetch_user=AsyncMock(
            side_effect=[
                impostor,
                normal_player,
            ]
        )
    )

    with (
        patch(
            "impostor_bot.discord.role_delivery."
            "send_impostor_dm",
            new=AsyncMock(),
        ) as send_impostor_dm,
        patch(
            "impostor_bot.discord.role_delivery."
            "send_normal_player_dm",
            new=AsyncMock(),
        ) as send_normal_player_dm,
    ):
        failed_players = await deliver_roles(
            client=client,
            roles={
                1: IMPOSTOR_ROLE,
                2: "pizza",
            },
        )

    assert failed_players == []

    assert (
        client.fetch_user.await_args_list
        == [
            call(1),
            call(2),
        ]
    )

    send_impostor_dm.assert_awaited_once_with(
        impostor
    )

    send_normal_player_dm.assert_awaited_once_with(
        normal_player,
        "pizza",
    )


@pytest.mark.parametrize(
    ("error_type", "status"),
    [
        (
            discord.Forbidden,
            403,
        ),
        (
            discord.NotFound,
            404,
        ),
    ],
)
@pytest.mark.asyncio
async def test_deliver_roles_reports_unreachable_player(
    error_type,
    status,
):
    user = SimpleNamespace(
        id=123,
    )

    discord_error = make_discord_error(
        error_type,
        status,
    )

    client = SimpleNamespace(
        fetch_user=AsyncMock(
            return_value=user
        )
    )

    with patch(
        "impostor_bot.discord.role_delivery."
        "send_normal_player_dm",
        new=AsyncMock(
            side_effect=discord_error
        ),
    ):
        failed_players = await deliver_roles(
            client=client,
            roles={
                123: "pizza",
            },
        )

    assert failed_players == [
        123,
    ]


@pytest.mark.asyncio
async def test_deliver_roles_continues_after_unreachable_player():
    first_user = SimpleNamespace(
        id=1,
    )

    second_user = SimpleNamespace(
        id=2,
    )

    forbidden_error = make_discord_error(
        discord.Forbidden,
        403,
    )

    client = SimpleNamespace(
        fetch_user=AsyncMock(
            side_effect=[
                first_user,
                second_user,
            ]
        )
    )

    with patch(
        "impostor_bot.discord.role_delivery."
        "send_normal_player_dm",
        new=AsyncMock(
            side_effect=[
                forbidden_error,
                None,
            ]
        ),
    ) as send_normal_player_dm:
        failed_players = await deliver_roles(
            client=client,
            roles={
                1: "pizza",
                2: "pizza",
            },
        )

    assert failed_players == [
        1,
    ]

    assert (
        client.fetch_user.await_args_list
        == [
            call(1),
            call(2),
        ]
    )

    assert (
        send_normal_player_dm.await_count
        == 2
    )

    send_normal_player_dm.assert_any_await(
        second_user,
        "pizza",
    )


@pytest.mark.asyncio
async def test_deliver_roles_translates_discord_http_error():
    user = SimpleNamespace(
        id=1,
    )

    http_error = make_discord_error(
        discord.HTTPException,
        500,
    )

    client = SimpleNamespace(
        fetch_user=AsyncMock(
            return_value=user
        )
    )

    with patch(
        "impostor_bot.discord.role_delivery."
        "send_normal_player_dm",
        new=AsyncMock(
            side_effect=http_error
        ),
    ):
        with pytest.raises(
            DiscordAPIError
        ) as exc_info:
            await deliver_roles(
                client=client,
                roles={
                    1: "pizza",
                },
            )

    assert (
        exc_info.value.__cause__
        is http_error
    )