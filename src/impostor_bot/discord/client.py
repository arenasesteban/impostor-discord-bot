import logging
from collections.abc import Awaitable, Callable

import discord

from impostor_bot.discord.command_tree import ImpostorCommandTree
from impostor_bot.discord.commands import impostor_group
from impostor_bot.observability import log_error, log_event

logger = logging.getLogger(__name__)


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

    def add_startup_hook(self, hook: LifecycleHook) -> None:
        self._startup_hooks.append(hook)

    async def setup_hook(self) -> None:
        if self._startup_completed:
            return

        try: 
            for hook in self._startup_hooks:
                await hook()

            self.tree.add_command(impostor_group)

            await self.tree.sync()

        except Exception as error:
            log_error(
                logger,
                "startup_failed",
                error,
                level=logging.CRITICAL,
            )

            raise

        self._startup_completed = True

        log_event(
            logger,
            "bot_started",
        )

    async def close(self) -> None:
        if self._shutdown_completed:
            return

        errors: list[Exception] = []

        try:
            await super().close()

        except Exception as error:
            errors.append(error)

            log_error(
                logger,
                "shutdown_failed",
                error,
                stage="discord_client_close",
            )

        try:
            await self._run_shutdown_hooks()

        except Exception as error:
            errors.append(error)

        self._shutdown_completed = True

        if errors:
            raise errors[0]

        log_event(
            logger,
            "bot_stopped",
        )

    async def on_ready(self) -> None:
        log_event(
            logger,
            "bot_ready",
            bot_id=self.user.id if self.user else None
        )

    async def _run_shutdown_hooks(self) -> None:
        errors: list[Exception] = []

        for hook in reversed(self._shutdown_hooks):
            try:
                await hook()

            except Exception as error:
                errors.append(error)

                log_error(
                    logger,
                    "shutdown_hook_failed",
                    error,
                    hook=getattr(
                        hook,
                        "__name__",
                        type(hook).__name__,
                    )
                )

        if errors:
            raise errors[0]


def create_bot(startup_hooks: tuple[LifecycleHook, ...] = (), shutdown_hooks: tuple[LifecycleHook, ...] = ()) -> ImpostorBot:
    return ImpostorBot(
        startup_hooks=startup_hooks,
        shutdown_hooks=shutdown_hooks
    )
