# Game Flow

This document describes the main usage flow of **Impostor Discord Bot** during a game.

The bot only manages the setup phase of the game: it creates the lobby, registers players, selects a secret word, chooses one impostor, and sends the roles by direct message.

After that, the game continues between the players.

## Flow Summary

```text
/impostor create
→ players join with Join or /impostor join
→ optionally check /impostor status
→ the host runs /impostor start
→ the bot sends roles by DM
→ the lobby is closed
→ the game continues between the players
```

## 1. Create a Game

A game begins when a user runs:

```text
/impostor create
```

That user is registered as the host of the game and is also automatically added as a player.

The bot publishes a lobby in the channel with:

* game status;
* host;
* number of joined players;
* player list;
* `Join` button;
* `Leave` button;
* useful commands for the host.

Only one active game can exist per channel.

## 2. Join the Game

Players can join while the game is open.

There are two ways to do this:

| Option           | Action                           |
| ---------------- | -------------------------------- |
| `Join` button    | Adds the user from the lobby.    |
| `/impostor join` | Adds the user through a command. |

When a user joins successfully:

* the user is added to the player list;
* the lobby is updated;
* the user receives a confirmation visible only to them.

The host does not need to join, because they are automatically registered when creating the game.

## 3. Leave the Game

Before the game starts, a joined player can leave.

There are two ways to do this:

| Option            | Action                              |
| ----------------- | ----------------------------------- |
| `Leave` button    | Removes the user from the lobby.    |
| `/impostor leave` | Removes the user through a command. |

When a user leaves successfully:

* the user is removed from the player list;
* the lobby is updated;
* the user receives a confirmation visible only to them.

The host cannot leave the game. To close the lobby, the host must use:

```text
/impostor cancel
```

## 4. Check the Game Status

At any time before starting, users can check the status with:

```text
/impostor status
```

The bot shows:

* current status;
* host;
* number of joined players;
* player list.

This command is useful for confirming who has joined before starting.

## 5. Start the Game

When the group is ready, the host runs:

```text
/impostor start
```

To start correctly, these conditions must be met:

* an open game must exist;
* the user running the command must be the host;
* at least 3 players must be joined;
* at least one word must be available in the words file.

When the game starts, the bot performs these actions:

1. gets a secret word from `data/words.json`;
2. randomly selects one impostor;
3. generates the roles for all players;
4. sends direct messages to each player;
5. informs the channel that the game has started;
6. visually closes the lobby;
7. disables the buttons;
8. removes the active game from memory.

The public channel does not show the secret word or who the impostor is.

## 6. Receive the Role by Direct Message

Once the game starts, each player receives a direct message.

| Player Type    | Received Information                                                                            |
| -------------- | ----------------------------------------------------------------------------------------------- |
| Regular player | Receives the secret word.                                                                       |
| Impostor       | Receives a message indicating that they are the impostor, but does not receive the secret word. |

Regular players should say a word related to the secret word while avoiding making it too obvious.

The impostor should listen to the other players' clues and try to blend in.

## 7. Continue the Game Outside the Bot

After distributing the roles, the bot finishes its participation.

From that moment on, the players continue the game on their own:

1. each player says a related word;
2. players try to identify the impostor;
3. the impostor tries to avoid suspicion;
4. the group votes for who they think the impostor is;
5. the result is decided by the players.

The bot does not control this stage.

## 8. Cancel a Game

If the host decides not to continue, they can cancel the game before starting it by using:

```text
/impostor cancel
```

When cancelled:

* the lobby is marked as cancelled;
* the buttons are disabled;
* the game is removed from the bot's memory;
* players can no longer join or leave that game.

Only the host can cancel a game.

## Alternative Flows

### Player Leaves Before Starting

```text
Open game
→ player presses Leave or uses /impostor leave
→ the bot removes the player
→ the lobby is updated
→ the game remains open
```

### Host Cancels

```text
Open game
→ host uses /impostor cancel
→ the bot visually closes the lobby
→ the buttons are disabled
→ the game is no longer available
```

### Direct Messages Disabled

The bot may be unable to send direct messages to one or more players.

This usually happens when a user has disabled direct messages from server members.

In that case, the bot reports the issue and the game does not continue normally. Players must enable direct messages and create a new game.

## Private Information

During the game flow, the bot never publicly shows:

* the secret word;
* who the impostor is.

That information is only delivered by direct message to the corresponding players.

## Bot Responsibility

The bot is responsible for:

* creating the lobby;
* registering players;
* updating the participant list;
* selecting the secret word;
* selecting the impostor;
* sending roles by direct message;
* closing the lobby when the game starts or is cancelled.

The bot is not responsible for:

* controlling turns;
* moderating the words spoken by players;
* receiving votes;
* declaring winners;
* tracking scores;
* saving game history.
