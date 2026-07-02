import discord

from impostor_bot.constants import (
    EMOJI_GAME,
    EMOJI_SUCCESS,
    EMOJI_WARNING,
    EMOJI_ERROR,
    EMOJI_DOOR,
    EMOJI_DICE,
    EMOJI_LIST
)
from impostor_bot.game.session import Session


def format_player_list(player_ids: list[int]) -> str:
    if not player_ids:
        return "No players have joined yet."
    
    return "\n".join(
        f"{index + 1}. <@{player_id}>" 
        for index, player_id in enumerate(player_ids, start=1)
    )


def build_game_created_message(host_id: int) -> str:
    return (
       f"🎭 **The Impostor Game Has Been Created!**\n\n"
        f"Host: <@{host_id}>\n\n"
        "Players can join the game using the `/impostor join` command.\n"
        "The host can start the game using the `/impostor start` command."
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