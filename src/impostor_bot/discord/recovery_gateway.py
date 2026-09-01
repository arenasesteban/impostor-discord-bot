import discord

from impostor_bot.discord.views import LobbyView
from impostor_bot.game.session_key import GameSessionKey


class DiscordPySessionRecoveryGateway:
    def __init__(self, client: discord.Client) -> None:
        self._client = client
        self._registered_lobbies: set[int] = set()

    async def channel_exists(self, key: GameSessionKey) -> bool:
        channel = await self._resolve_channel(key)

        return channel is not None

    async def lobby_message_exists(self, key: GameSessionKey, message_id: int) -> bool:
        channel = await self._resolve_channel(key)

        if channel is None:
            return False

        try:
            await channel.fetch_message(message_id)

        except (discord.NotFound, discord.Forbidden):
            return False

        return True

    def register_lobby_view(self, message_id: int) -> None:
        if message_id in self._registered_lobbies:
            return

        self._client.add_view(
            LobbyView(),
            message_id=message_id,
        )

        self._registered_lobbies.add(message_id)

    async def _resolve_channel(self, key: GameSessionKey) -> discord.abc.Messageable | None:
        channel = self._client.get_channel(key.channel_id)

        if channel is None:
            try:
                channel = await self._client.fetch_channel(key.channel_id)

            except (discord.NotFound, discord.Forbidden):
                return None

        guild = getattr(channel, "guild", None)

        if guild is None or guild.id != key.guild_id:
            return None

        if not isinstance(channel, discord.abc.Messageable):
            return None

        return channel