# Commands

This document describes the commands available in **Impostor Discord Bot**.

The main game commands are grouped under:

```text
/impostor
```

## General Summary

| Command            | Purpose                                | Main Use                      |
| ------------------ | -------------------------------------- | ----------------------------- |
| `/impostor help`   | Shows brief help.                      | Check the basic flow.         |
| `/impostor create` | Creates a game in the current channel. | Start a lobby.                |
| `/impostor join`   | Adds a player to an open game.         | Join manually.                |
| `/impostor leave`  | Removes a player from an open game.    | Leave before the game starts. |
| `/impostor status` | Shows the current game status.         | Review joined players.        |
| `/impostor start`  | Starts the game and sends roles by DM. | Begin the game.               |
| `/impostor cancel` | Cancels an open game.                  | Close the lobby.              |

## Command Details

| Command            | Description                                                                                                                                                                      | Who Can Use It                 |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| `/impostor help`   | Shows a brief guide with the main commands and basic rules.                                                                                                                      | Any user.                      |
| `/impostor create` | Creates a new game in the current channel. The user is registered as the host and is automatically added as a player. The bot publishes a lobby with `Join` and `Leave` buttons. | Any user.                      |
| `/impostor join`   | Allows a user to manually join an open game. It updates the lobby and shows a confirmation visible only to that user.                                                            | Users who have not joined yet. |
| `/impostor leave`  | Allows a user to manually leave a game before it starts. It updates the lobby and shows a confirmation visible only to that user.                                                | Joined players.                |
| `/impostor status` | Shows the game status, host, number of players, and list of joined players.                                                                                                      | Any user.                      |
| `/impostor start`  | Starts the game. The bot validates the host, checks the minimum number of players, chooses a secret word, selects one impostor, and sends the roles by direct message.           | Host only.                     |
| `/impostor cancel` | Cancels an open game. The lobby is visually closed and the buttons are disabled.                                                                                                 | Host only.                     |

## Usage Flow

1. The host runs `/impostor create`.
2. The bot publishes a lobby in the channel.
3. Players join using **Join** or `/impostor join`.
4. Players may leave using **Leave** or `/impostor leave`.
5. The game status can be checked with `/impostor status`.
6. The host starts the game with `/impostor start`.
7. The bot sends the roles by direct message.
8. The lobby is closed and the game continues between the players.

## Command Rules

| Rule                                                            | Related Command            |
| --------------------------------------------------------------- | -------------------------- |
| Only one active game can exist per channel.                     | `/impostor create`         |
| The host is automatically registered as a player.               | `/impostor create`         |
| A user cannot join the same game twice.                         | `/impostor join`, `Join`   |
| The host is already part of the game and does not need to join. | `/impostor join`, `Join`   |
| Only joined players can leave.                                  | `/impostor leave`, `Leave` |
| The host cannot leave the game. The host must cancel the lobby. | `/impostor leave`, `Leave` |
| Only the host can start the game.                               | `/impostor start`          |
| At least 3 players are required to start.                       | `/impostor start`          |
| Only the host can cancel the game.                              | `/impostor cancel`         |
| The secret word is never shown in the public channel.           | `/impostor start`          |
| The impostor is never revealed in the public channel.           | `/impostor start`          |

## Expected Responses

| Action       | Expected Result                                                                      |
| ------------ | ------------------------------------------------------------------------------------ |
| Create game  | The bot publishes a lobby with the host, player count, and `Join` / `Leave` buttons. |
| Join         | The bot adds the user, updates the lobby, and shows an ephemeral confirmation.       |
| Leave        | The bot removes the user, updates the lobby, and shows an ephemeral confirmation.    |
| Check status | The bot shows the current status, host, and player list.                             |
| Start        | The bot sends the roles by DM, closes the lobby, and disables the buttons.           |
| Cancel       | The bot cancels the game, closes the lobby, and disables the buttons.                |

## Main Errors

| Case                                  | Expected Response                                                 |
| ------------------------------------- | ----------------------------------------------------------------- |
| A game already exists in the channel. | The bot reports that there is already an open game.               |
| There is no open game.                | The bot reports that there is no game in the channel.             |
| The user is already joined.           | The bot reports that the player is already part of the game.      |
| The user is not joined.               | The bot reports that the player is not part of the game.          |
| The host tries to join.               | The bot reports that the host is already part of the game.        |
| The host tries to leave.              | The bot reports that the host must cancel the game.               |
| A non-host user tries to start.       | The bot reports that only the host can start the game.            |
| A non-host user tries to cancel.      | The bot reports that only the host can cancel the game.           |
| There are fewer than 3 players.       | The bot reports that at least 3 players are required.             |
| A DM cannot be sent.                  | The bot reports which players could not receive a direct message. |
| No words are available.               | The bot reports an error related to the words file.               |

## Starting a Game

When `/impostor start` is executed, the bot performs the following actions:

1. Checks that an open game exists.
2. Checks that the user is the host.
3. Checks that there are at least 3 players.
4. Gets a secret word from `data/words.json`.
5. Randomly selects one impostor.
6. Sends the secret word by DM to regular players.
7. Sends the impostor role by DM to the impostor.
8. Visually closes the lobby.
9. Disables the buttons.
10. Removes the active game from memory.

The public channel does not show the secret word or the impostor player.

## Direct Messages

| Player Type    | Received Message                                                                          |
| -------------- | ----------------------------------------------------------------------------------------- |
| Regular player | Receives the secret word and a brief gameplay instruction.                                |
| Impostor       | Receives a message indicating that they are the impostor and do not know the secret word. |

If one or more players have direct messages disabled, the bot reports the issue and the game does not continue normally.

## Interactive Buttons

In addition to manual commands, the bot includes buttons to simplify player registration.

```text
Join | Leave
```

| Button  | Equivalent To     | Function                             |
| ------- | ----------------- | ------------------------------------ |
| `Join`  | `/impostor join`  | Adds the user to the open game.      |
| `Leave` | `/impostor leave` | Removes the user from the open game. |

### Considerations

* Buttons work while the game is open.
* When a user joins or leaves, the lobby is updated.
* Confirmations and errors are shown through messages visible only to the user who performs the action.
* Buttons are disabled when the game starts or is cancelled.
* Discord does not allow disabling buttons in a public message for specific users; therefore, invalid actions are handled through internal validations.
* Manual commands are kept as a fallback.
