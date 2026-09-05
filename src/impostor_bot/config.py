import os

from dotenv import load_dotenv

load_dotenv()


def _get_discord_token() -> str:
    discord_token = os.getenv("DISCORD_TOKEN")

    if not discord_token:
        raise RuntimeError(
            "DISCORD_TOKEN is not set in the environment variables. "
            "Please make sure to set it in your .env file or "
            "in your system environment variables."
        )

    return discord_token


discord_token = _get_discord_token()