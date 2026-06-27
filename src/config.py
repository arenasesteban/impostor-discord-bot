import os
from dotenv import load_dotenv


load_dotenv()


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


if not DISCORD_TOKEN:
    raise ValueError(
        "DISCORD_TOKEN is not set in the environment variables. "
        "Please make sure to set it in your .env file or in your system environment variables."   
    )