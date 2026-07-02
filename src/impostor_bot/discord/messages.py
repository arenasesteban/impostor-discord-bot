import discord

from impostor_bot.constants import (
    EMOJI_DICE,
    EMOJI_DOOR,
    EMOJI_ERROR,
    EMOJI_GAME,
    EMOJI_LIST,
    EMOJI_LOCK,
    EMOJI_SUCCESS,
    EMOJI_WARNING,
)
from impostor_bot.game.session import Session


def format_player_list(player_ids: list[int]) -> str:
    if not player_ids:
        return "No players have joined yet."

    return "\n".join(
        f"{index}. <@{player_id}>"
        for index, player_id in enumerate(player_ids, start=1)
    )


def build_game_created_message(game: Session) -> str:
    return (
        f"{EMOJI_GAME} **Impostor game lobby**\n\n"
        f"**Status:** Open\n"
        f"**Host:** <@{game.host_id}>\n"
        f"**Players joined:** {len(game.players)}\n\n"
        "**Players:**\n"
        "Use **Join** to enter the game or **Leave** to exit before it starts.\n\n"
        "**Host commands:**\n"
        "`/impostor start` — Start the game.\n"
        "`/impostor cancel` — Cancel the lobby.\n"
    )


def build_lobby_started_message(game: Session) -> str:
    return (
        f"{EMOJI_DICE} **The Impostor Game Has Started!**\n\n"
        f"**Status:** Started\n"
        f"**Host:** <@{game.host_id}>\n"
        f"**Players:** {len(game.players)}\n\n"
        f"{EMOJI_LOCK} This lobby is now closed.\n"
        "The secret roles were sent by direct message."
    )


def build_lobby_cancelled_message(game: Session) -> str:
    return (
        f"{EMOJI_ERROR} **The Impostor Game Was Cancelled!**\n\n"
        f"**Status:** Cancelled\n"
        f"**Host:** <@{game.host_id}>\n\n"
        f"{EMOJI_LOCK} This lobby is now closed."
    )


def build_player_joined_message(player_id: int, total_players: int) -> str:
    return (
        f"{EMOJI_SUCCESS} <@{player_id}> joined the game.\n\n"
        f"**Current players:** {total_players}"
    )


def build_player_left_message(player_id: int, total_players: int) -> str:
    return (
        f"{EMOJI_DOOR} <@{player_id}> left the game.\n\n"
        f"**Current players:** {total_players}"
    )


def build_game_cancelled_message() -> str:
    return f"{EMOJI_ERROR} The game was cancelled by the host."


def build_game_status_message(game: Session) -> str:
    player_list = format_player_list(game.players)

    return (
        f"{EMOJI_LIST} **Game status**\n\n"
        f"**Status:** {game.status}\n"
        f"**Host:** <@{game.host_id}>\n"
        f"**Players joined:** {len(game.players)}\n\n"
        f"**Player list:**\n"
        f"{player_list}\n\n"
    )


def build_game_started_message() -> str:
    return (
        f"{EMOJI_DICE} **The game has started**\n\n"
        "I have sent each player their secret role by direct message.\n\n"
    )


def build_dm_error_message(failed_players: list[int]) -> str:
    failed_list = "\n".join(f"- <@{player_id}>" for player_id in failed_players)

    return (
        f"{EMOJI_WARNING} **I could not send a direct message to some players**\n\n"
        f"{failed_list}\n\n"
        "They may have direct messages disabled or they may block messages from server members.\n\n"
        "They need to enable direct messages and then start a new game."
    )


def build_help_message() -> str:
    return (
        f"{EMOJI_GAME} **Help — The Impostor**\n\n"
        "`/impostor create` — Creates a new game in the current channel.\n"
        "`/impostor join` — Joins the open game.\n"
        "`/impostor leave` — Leaves the game before it starts.\n"
        "`/impostor status` — Shows the host, game status, and joined players.\n"
        "`/impostor start` — Starts the game and sends the roles by direct message..\n"
        "`/impostor cancel` — Cancels the open game.\n\n"
    )


async def send_error(interaction: discord.Interaction, message: str, ephemeral: bool = True) -> None:
    await interaction.response.send_message(
        f"{EMOJI_WARNING} {message}",
        ephemeral=ephemeral,
    )


async def send_normal_player_dm(user: discord.User | discord.Member, secret_word: str) -> None:
    await user.send(
        f"{EMOJI_GAME} **The Impostor — Secret role**\n\n"
        "Your secret word is:\n\n"
        f"**{secret_word}**\n\n"
        "Say one word related to the secret concept, "
        "but do not make it too obvious.\n"
    )


async def send_impostor_dm(user: discord.User | discord.Member) -> None:
    await user.send(
        f"{EMOJI_GAME} **The Impostor — Secret role**\n\n"
        "You are the impostor.\n\n"
        "**You do not know the secret word.**\n\n"
        "Listen to the other players' clues and try to say something that sounds related.\n"
        "Do not let them discover that you do not know the word.\n"
    )