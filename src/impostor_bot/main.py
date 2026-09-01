from impostor_bot.config import DISCORD_TOKEN
from impostor_bot.discord.client import (
    create_bot,
)
from impostor_bot.discord.state import (
    configure_game_repository,
    configure_lobby_message_repository,
)
from impostor_bot.infrastructure.database.runtime import (
    create_postgres_runtime,
)
from impostor_bot.infrastructure.database.settings import (
    get_database_url,
)


def main() -> None:
    postgres_runtime = create_postgres_runtime(get_database_url())

    configure_game_repository(postgres_runtime.game_repository)
    configure_lobby_message_repository(postgres_runtime.lobby_message_repository)

    bot = create_bot(
        startup_hooks=(postgres_runtime.check_connection,),
        shutdown_hooks=(postgres_runtime.close,)
    )

    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()