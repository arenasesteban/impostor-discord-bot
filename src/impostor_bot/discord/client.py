import discord

from collections.abc import (
    Awaitable,
    Callable,
)

from impostor_bot.discord.commands import impostor_group
from impostor_bot.discord.command_tree import ImpostorCommandTree


LifecycleHook = Callable[[], Awaitable[None]]


class ImpostorBot(discord.Client):
    def __init__(
        self,
        startup_hooks: tuple[LifecycleHook, ...] = (),
        shutdown_hooks: tuple[LifecycleHook, ...] = ()
    ) -> None:
        intents = discord.Intents.default()

        super().__init__(intents=intents)

        self.tree = ImpostorCommandTree(self)

        self._startup_hooks = list(startup_hooks)
        self._shutdown_hooks = list(shutdown_hooks)
        self._startup_completed = False
        self._shutdown_completed = False

    async def setup_hook(self) -> None:
        if self._startup_completed:
            return

        for hook in self._startup_hooks:
            await hook()

        self.tree.add_command(impostor_group)

        await self.tree.sync()

        self._startup_completed = True

    async def close(self) -> None:
        try:
            await super().close()

        finally:
            if self._shutdown_completed:
                return

            self._shutdown_completed = True

            for hook in reversed(self._shutdown_hooks):
                await hook()

    async def on_ready(self) -> None:
        print(
            f"Bot is ready. "
            f"Logged in as {self.user} "
            f"(ID: {self.user.id})"
        )
    
    def add_startup_hook(self, hook: LifecycleHook) -> None:
        self._startup_hooks.append(hook)


def create_bot(startup_hooks: tuple[LifecycleHook, ...] = (), shutdown_hooks: tuple[LifecycleHook, ...] = ()) -> ImpostorBot:
    return ImpostorBot(
        startup_hooks=startup_hooks,
        shutdown_hooks=shutdown_hooks
    )
