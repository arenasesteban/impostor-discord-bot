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
from impostor_bot.game.game import Game


def format_player_list(player_ids: list[int]) -> str:
    if not player_ids:
        return "*No players have joined yet.*"

    return "\n".join(
        f"{index}. <@{player_id}>"
        for index, player_id in enumerate(player_ids, start=1)
    )


def build_game_created_message(game: Game) -> str:
    return (
        f"{EMOJI_GAME} **The Impostor — Game Lobby**\n\n"
        "🟢 **Status:** Open\n"
        f"👑 **Host:** <@{game.host_id}>\n"
        f"👥 **Players:** {len(game.players)}\n\n"
        "Use **Join** to enter the game or **Leave** to exit before it starts.\n\n"
        "**Host commands:**\n"
        "`/impostor start` — Start the game.\n"
        "`/impostor cancel` — Cancel the lobby."
    )


def build_lobby_started_message(game: Game) -> str:
    return (
        f"{EMOJI_DICE} **The Impostor — Game Started**\n\n"
        "🟢 **Status:** Started\n"
        f"👑 **Host:** <@{game.host_id}>\n"
        f"👥 **Players:** {len(game.players)}\n\n"
        f"{EMOJI_LOCK} Player registration is now closed.\n"
        "📩 Secret roles have been sent through Discord DMs.\n\n"
        "**Host commands:**\n"
        "`/impostor finish` — Finish the game.\n"
        "`/impostor cancel` — Cancel the game."
    )


def build_lobby_cancelled_message(game: Game) -> str:
    return (
        f"{EMOJI_ERROR} **The Impostor — Game Cancelled**\n\n"
        "🔴 **Status:** Cancelled\n"
        f"👑 **Host:** <@{game.host_id}>\n\n"
        f"{EMOJI_LOCK} This game is now closed."
    )


def build_player_joined_message(
    player_id: int,
    total_players: int,
) -> str:
    return (
        f"{EMOJI_SUCCESS} <@{player_id}> **joined the game.**\n"
        f"👥 **Players:** {total_players}"
    )


def build_player_left_message(
    player_id: int,
    total_players: int,
) -> str:
    return (
        f"{EMOJI_DOOR} <@{player_id}> **left the game.**\n"
        f"👥 **Players:** {total_players}"
    )


def build_game_cancelled_message() -> str:
    return (
        f"{EMOJI_ERROR} **Game cancelled.**\n"
        "The active game was cancelled by the host."
    )


def build_game_status_message(game: Game) -> str:
    player_list = format_player_list(game.players)

    return (
        f"{EMOJI_LIST} **The Impostor — Game Status**\n\n"
        f"**Status:** {game.status}\n"
        f"👑 **Host:** <@{game.host_id}>\n"
        f"👥 **Players:** {len(game.players)}\n\n"
        f"**Player list:**\n{player_list}"
    )


def build_game_started_message() -> str:
    return (
        f"{EMOJI_DICE} **Game started.**\n"
        "📩 Each player has received their secret role through Discord DMs."
    )


def build_dm_error_message(failed_players: list[int]) -> str:
    failed_list = "\n".join(
        f"• <@{player_id}>"
        for player_id in failed_players
    )

    return (
        f"{EMOJI_WARNING} **Some roles could not be delivered**\n\n"
        f"{failed_list}\n\n"
        "These players may have Discord DMs disabled or may be blocking "
        "messages from server members.\n"
        "Enable DMs before creating a new game."
    )


def build_lobby_finished_message(game: Game) -> str:
    return (
        f"{EMOJI_SUCCESS} **The Impostor — Game Finished**\n\n"
        "🟢 **Status:** Finished\n"
        f"👑 **Host:** <@{game.host_id}>\n"
        f"👥 **Players:** {len(game.players)}\n\n"
        f"{EMOJI_LOCK} This game is now closed."
    )


def build_game_finished_message() -> str:
    return (
        f"{EMOJI_SUCCESS} **Game finished.**\n"
        "The game was completed by the host."
    )


def build_help_message() -> str:
    return (
        f"{EMOJI_GAME} **The Impostor — Commands**\n\n"
        "`/impostor create`  — Create a new game in this channel.\n"
        "`/impostor join`    — Join the open game.\n"
        "`/impostor leave`   — Leave before the game starts.\n"
        "`/impostor status`  — View the current game session.\n"
        "`/impostor start`   — Start the game and deliver the secret roles.\n"
        "`/impostor finish`  — Finish a started game.\n"
        "`/impostor cancel`  — Cancel the active game."
    )


def build_service_error_message() -> str:
    return (
        f"{EMOJI_WARNING} **Something went wrong**\n"
        "The bot could not complete this action because of an internal "
        "service problem. Please try again later."
    )


async def send_error(interaction: discord.Interaction, message: str, ephemeral: bool = True) -> None:
    content = f"{EMOJI_WARNING} {message}"

    if interaction.response.is_done():
        await interaction.followup.send(
            content,
            ephemeral=ephemeral,
        )
        return

    await interaction.response.send_message(
        content,
        ephemeral=ephemeral,
    )


async def send_normal_player_dm(
    user: discord.User | discord.Member,
    secret_word: str,
) -> None:
    await user.send(
        f"{EMOJI_GAME} **The Impostor — Secret Role**\n\n"
        "🟢 **You are a normal player.**\n"
        f"Your secret word is **{secret_word}**.\n\n"
        "💬 Give a clue related to the word without making it too obvious.\n"
        "Pay attention to the other players and try to identify the impostor."
    )


async def send_impostor_dm(
    user: discord.User | discord.Member,
) -> None:
    await user.send(
        f"{EMOJI_GAME} **The Impostor — Secret Role**\n\n"
        "🔴 **You are the impostor.**\n"
        "You do **not** know the secret word.\n\n"
        "🎭 Listen carefully, improvise your clues, and try to blend in.\n"
        "Do not let the other players discover that you are the impostor."
    )