import asyncio
import logging
import os

from dotenv import load_dotenv

from impostor_bot.config import load_app_settings
from impostor_bot.discord.client import create_bot
from impostor_bot.discord.recovery import RecoverGameSessions
from impostor_bot.discord.recovery_gateway import DiscordPySessionRecoveryGateway
from impostor_bot.discord.state import (
    active_lobby_messages,
    configure_game_repository,
    configure_lobby_message_repository,
)
from impostor_bot.infrastructure.database.runtime import create_postgres_runtime
from impostor_bot.observability import configure_logging


async def run() -> None:
    load_dotenv()

    settings = load_app_settings(os.environ)

    configure_logging(
        level=logging.INFO,
        sensitive_values=(
            settings.discord_token, 
            settings.database.database_url
        )
    )

    postgres_runtime = create_postgres_runtime(settings.database.database_url)

    try:
        configure_game_repository(postgres_runtime.game_repository)

        configure_lobby_message_repository(postgres_runtime.lobby_message_repository)

        bot = create_bot(startup_hooks=(postgres_runtime.check_connection,))

        recovery = RecoverGameSessions(
            game_repository= postgres_runtime.game_repository,
            lobby_repository=postgres_runtime.lobby_message_repository,
            gateway=DiscordPySessionRecoveryGateway(bot),
            lobby_cache=active_lobby_messages
        )

        async def recover_sessions() -> None:
            await recovery.execute()

        bot.add_startup_hook(recover_sessions)

        async with bot:
            await bot.start(settings.discord_token)

    finally:
        await postgres_runtime.close()


def main() -> None:
    try:
        asyncio.run(
            run()
        )
        
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()