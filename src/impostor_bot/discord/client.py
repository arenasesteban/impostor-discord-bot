from collections.abc import (
    Awaitable,
    Callable,
)

import discord
from discord import app_commands

from impostor_bot.discord.commands import (
    impostor_group,
)


LifecycleHook = Callable[[], Awaitable[None]]


class ImpostorBot(discord.Client):
    def __init__(
        self,
        startup_hooks: tuple[LifecycleHook, ...] = (),
        shutdown_hooks: tuple[LifecycleHook, ...] = (),
    ) -> None:
        intents = discord.Intents.default()

        super().__init__(
            intents=intents
        )

        self.tree = app_commands.CommandTree(self)

        self._startup_hooks = startup_hooks
        self._shutdown_hooks = shutdown_hooks

    async def setup_hook(self) -> None:
        for hook in self._startup_hooks:
            await hook()

        self.tree.add_command(impostor_group)

        await self.tree.sync()

    async def close(self) -> None:
        try:
            await super().close()

        finally:
            for hook in reversed(self._shutdown_hooks):
                await hook()

    async def on_ready(self) -> None:
        print(
            f"Bot is ready. "
            f"Logged in as {self.user} "
            f"(ID: {self.user.id})"
        )


def create_bot(
    startup_hooks: tuple[LifecycleHook, ...] = (),
    shutdown_hooks: tuple[LifecycleHook, ...] = (),
) -> ImpostorBot:
    return ImpostorBot(
        startup_hooks=startup_hooks,
        shutdown_hooks=shutdown_hooks,
    )