# Internal Rules

This document summarizes the internal rules used by **Impostor Discord Bot** to manage a game.

---

## General Principle

The bot only manages the initial stage of a **The Impostor** game.

Its responsibility is to create the lobby, register players, select a secret word, choose one impostor, send the roles by direct message, and close the lobby when the game starts or is cancelled.

The bot does not control the round, voting, scoring, or winner declaration.

---

## Game States

| State       | Description                                             |
| ----------- | ------------------------------------------------------- |
| `open`      | The game is open and allows players to join or leave.   |
| `started`   | The game has started and the roles have been generated. |
| `cancelled` | The game was cancelled before starting.                 |

Active games are stored temporarily in memory. If the bot restarts, active games are lost.

---

## Main Rules

| Area    | Rules                                                                                                                                                                                          |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Games   | Only one active game can exist per channel. Every new game starts with the `open` status. When a game starts or is cancelled, it is closed and removed from memory.                            |
| Host    | The user who creates the game is registered as the host and is automatically added as a player. Only the host can start or cancel the game. The host cannot leave the game.                    |
| Players | A player can only join if there is an open game. A player cannot join twice. A player can only leave if they are already registered. Players cannot be added or removed after the game starts. |
| Start   | To start the game, an open game must exist, the user must be the host, there must be at least 3 players, and a secret word must be available.                                                  |
| Roles   | Only one impostor is selected randomly. Regular players receive the secret word. The impostor does not receive the word. Each player receives exactly one role.                                |
| Memory  | The bot stores active games and lobby messages temporarily in memory. It does not store history, scores, or statistics.                                                                        |

---

## Lobby and Buttons

The public lobby shows:

```text
Join | Leave
```

| Element | Rule                                                                                              |
| ------- | ------------------------------------------------------------------------------------------------- |
| `Join`  | Equivalent to `/impostor join`; adds the user to the open game.                                   |
| `Leave` | Equivalent to `/impostor leave`; removes the user from the open game.                             |
| Lobby   | Updated whenever a player joins or leaves.                                                        |
| Closure | When the game starts or is cancelled, the lobby is marked as closed and the buttons are disabled. |

Buttons are visible to all users in the channel.

Discord does not allow disabling buttons in a public message for specific users. For this reason, invalid actions are handled through internal validations and responses visible only to the user who interacts with the button.

---

## Starting a Game

When running:

```text
/impostor start
```

the bot follows this flow:

1. validates that an open game exists;
2. validates that the user is the host;
3. validates that there are at least 3 players;
4. gets a secret word from `data/words.json`;
5. chooses a random impostor;
6. generates one role for each player;
7. sends the roles by direct message;
8. announces that the game has started;
9. visually closes the lobby;
10. disables the buttons;
11. removes the active game from memory.

---

## Secret Information

The bot must never publicly show:

* the secret word;
* who the impostor is.

This information is only delivered through direct messages.

| Player Type    | Message Received                                                                          |
| -------------- | ----------------------------------------------------------------------------------------- |
| Regular player | Receives the secret word and a brief instruction.                                         |
| Impostor       | Receives a message indicating that they are the impostor and do not know the secret word. |

If the bot cannot send a direct message to one or more players, it must report the issue. In that case, the game should not continue normally and the lobby must be closed to avoid an inconsistent state.

---

## Secret Words

Words are loaded from:

```text
data/words.json
```

| Rule             | Description                                          |
| ---------------- | ---------------------------------------------------- |
| Default category | The bot uses the `general` category.                 |
| Required format  | The file must use valid JSON format.                 |
| Categories       | Each category must contain a list of words.          |
| Empty categories | An empty category must produce a handled error.      |
| Missing file     | If the file does not exist, the game must not start. |

If a valid secret word cannot be obtained, the game must not start.

---

## Invalid Actions

The bot must prevent the following actions:

| Invalid Action                          | Expected Result                                            |
| --------------------------------------- | ---------------------------------------------------------- |
| Creating two games in the same channel. | The bot reports that there is already an open game.        |
| Joining twice.                          | The bot reports that the user is already registered.       |
| Joining as the host.                    | The bot reports that the host is already part of the game. |
| Leaving without being registered.       | The bot reports that the user is not part of the game.     |
| Leaving as the host.                    | The bot reports that the host must cancel the game.        |
| Starting without being the host.        | The bot reports that only the host can start.              |
| Starting with fewer than 3 players.     | The bot reports that at least 3 players are required.      |
| Cancelling without being the host.      | The bot reports that only the host can cancel.             |

---

## Out of Scope

The bot does not include:

* voting inside the bot;
* winner declaration;
* scoring;
* rankings;
* game history;
* database;
* server-specific configuration;
* multiple impostors;
* timer;
* turn control;
* moderation of words or clues;
* automatic final reveal of the word or the impostor.

---

## Completion Criteria

The rules are considered fulfilled if the bot allows this flow to be completed without revealing secret information publicly:

```text
/impostor create
→ players join with Join or /impostor join
→ /impostor status shows the list
→ /impostor start validates the game
→ the bot sends roles by DM
→ the lobby is closed
→ the game is removed from memory
```
