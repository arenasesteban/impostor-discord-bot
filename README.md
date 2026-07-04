# Impostor Discord Bot

A Discord bot built with `discord.py` to manage the setup phase of **The Impostor** game.

The bot acts as a neutral referee at the beginning of each match: it creates a lobby, registers players, selects a secret word, randomly chooses one impostor, and sends each player their role by direct message.

---

## Description

**Impostor Discord Bot** helps organize games of **The Impostor** inside a Discord server.

When a game starts, the bot sends the secret word by direct message to every regular player. One randomly selected player receives a message indicating that they are the impostor, without knowing the secret word.

After sending the roles, the bot finishes its job. The rest of the game — clues, discussion, voting, and deciding the winner — is handled by the players.

---

## Main Features

* Create one game lobby per channel.
* Automatically register the host as a player.
* Public lobby with interactive buttons.
* Join or leave a game using commands or buttons.
* Ephemeral confirmations and error messages.
* Lobby message updates when the player list changes.
* Visual lobby closure when the game starts or is cancelled.
* Random secret word selection.
* Random impostor selection.
* Role distribution through direct messages.
* Configurable word list using a JSON file.

---

## Technologies

* Python
* discord.py
* python-dotenv
* JSON

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd impostor-discord-bot
```

Create and activate a virtual environment.

Example using `micromamba`:

```bash
micromamba create -f environment.yml
micromamba activate impostor-discord-bot-env
```

---

## Discord Bot Setup

Before running the project, you need to create and configure a Discord application.

General steps:

1. Create an application in the Discord Developer Portal.
2. Create a bot inside that application.
3. Copy the bot token.
4. Create a `.env` file in the project root.
5. Add the bot token to the `.env` file.
6. Generate the bot invitation URL.
7. Invite the bot to your Discord server.

The `.env` file must contain:

```env
DISCORD_TOKEN=your_real_token_here
```

The project includes a `.env.example` file as a reference:

```env
DISCORD_TOKEN=place_your_token_here
```

When generating the bot invitation URL, enable the following scopes:

* `bot`
* `applications.commands`

The bot also needs the required permissions to send messages and use slash commands inside the server.

---

## Running the Bot

The project uses a package-based structure inside the `src/` directory.

First, activate the virtual environment if needed:

```bash
micromamba activate impostor-discord-bot-env
```

Then move into the `src` directory:

```bash
cd src
```

Run the bot as a module:

```bash
python -m impostor_bot.main
```

If the configuration is correct, the bot should appear online in Discord.

---

## Basic Usage

The main flow is:

1. The host creates a game.
2. The bot publishes a lobby in the channel.
3. Players join using the **Join** button or the corresponding command.
4. Players may leave before the game starts using the **Leave** button or the corresponding command.
5. The host starts the game when there are at least 3 players.
6. The bot selects a secret word and one impostor.
7. The bot sends the roles by direct message.
8. The lobby is closed and the game continues between the players.

---

## Main Commands

The bot uses slash commands grouped under `/impostor`.

| Command            | Description                                            |
| ------------------ | ------------------------------------------------------ |
| `/impostor create` | Creates a new game in the current channel.             |
| `/impostor join`   | Joins an open game.                                    |
| `/impostor leave`  | Leaves a game before it starts.                        |
| `/impostor status` | Shows the current game status.                         |
| `/impostor start`  | Starts the game and sends the roles by direct message. |
| `/impostor cancel` | Cancels an open game.                                  |
| `/impostor help`   | Shows a quick usage guide.                             |

The host is automatically added to the game when creating a lobby.

---

## Secret Words

Game words are stored in:

```text
data/words.json
```

The file is organized by categories:

```json
{
  "general": [
    "pizza",
    "playa",
    "perro"
  ]
}
```

To add or modify words, edit `data/words.json` while keeping a valid JSON format.

---

## Project Structure

```text
impostor-discord-bot/
├── data/
│   └── words.json
├── docs/
├── src/
│   └── impostor_bot/
│       ├── main.py
│       ├── config.py
│       ├── constants.py
│       ├── discord/
│       ├── game/
│       └── words/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

The `src/impostor_bot/` directory contains the main bot code.

The internal structure separates:

* Discord integration;
* game logic;
* word loading;
* configuration;
* messages;
* interactive views;
* temporary game state.

---

## Additional Documentation

Additional documentation is located in the `docs/` directory.

Some planned or related documents include:

* `docs/commands.md`
* `docs/game-flow.md`
* `docs/rules.md`
* `docs/words.md`

---

## Current Scope

The bot only manages the setup phase of the game.

It includes:

* creating a game;
* registering players;
* displaying a lobby;
* allowing players to join or leave;
* starting the game;
* selecting a secret word;
* selecting one impostor;
* sending roles by direct message;
* cancelling a game.

It does not include:

* turn moderation;
* timers;
* clue registration;
* voting system;
* automatic winner declaration;
* score tracking;
* database persistence;
* server-specific configuration.

---

## Possible Improvements

* Allow word category selection from Discord.
* Add support for multiple impostors.
* Add server-specific configuration.
* Add database persistence.

---

## Credits

Develop by Esteban Arenas.

This project was built as part of a hands-on learning process in Python, discord.py, and modular application design. It was developed incrementally, prioritizing clarity, separation of responsibilities, and understanding of the bot’s internal flow.

### Contact

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/arenasesteban)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-%230A66C2.svg?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/esteban-arenas-álvarez-0813462a1) [![Gmail](https://img.shields.io/badge/Gmail-%23D44638.svg?style=for-the-badge&logo=gmail&logoColor=white)](mailto:esteban.arenas.az@gmail.com)