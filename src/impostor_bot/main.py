from impostor_bot.config import DISCORD_TOKEN
from impostor_bot.bot.client import create_bot


def main() -> None:
    bot = create_bot()
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()