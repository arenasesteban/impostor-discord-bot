# Game Rules

This document summarizes the rules enforced by **Discord Impostor Bot** to manage a game.

## General Principle

The bot manages the game session: it creates the lobby, registers players, selects a secret word, chooses one impostor, sends the roles by direct message, and allows the host to finish or cancel the game.

The bot does not control the round itself, voting, scoring, or winner declaration.

## Game States

| State       | Description                                               |
| ----------- | --------------------------------------------------------- |
| `WAITING`   | The lobby is open and players can join or leave.          |
| `STARTED`   | The game has started and roles have been distributed.     |
| `FINISHED`  | The game was completed normally by the host.              |
| `CANCELLED` | The game was cancelled by the host or could not continue. |

Valid transitions are:

```text
WAITING → STARTED
WAITING → CANCELLED
STARTED → FINISHED
STARTED → CANCELLED
```

## Main Rules

| Area    | Rules                                                                                                                                                                       |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Games   | Only one active game can exist per channel. Every new game starts in `WAITING`.                                                                                             |
| Host    | The user who creates the game becomes the host and is automatically added as a player. Only the host can start, finish, or cancel the game. The host cannot leave the game. |
| Players | Players can join or leave only while the game is `WAITING`. A player cannot join twice and can leave only if already registered.                                            |
| Start   | A game can start only from `WAITING`, only by the host, with at least 3 players and a valid secret word available.                                                          |
| Finish  | A game can be finished only from `STARTED` and only by the host.                                                                                                            |
| Cancel  | The host can cancel a game while it is `WAITING` or `STARTED`.                                                                                                              |
| Roles   | Exactly one impostor is selected. Regular players receive the secret word. The impostor does not receive it. Each player receives exactly one role.                         |

## Lobby and Buttons

The public lobby shows:

```text
Join | Leave
```

| Element | Rule                                                                                     |
| ------- | ---------------------------------------------------------------------------------------- |
| `Join`  | Equivalent to `/impostor join`; adds an eligible user while the game is `WAITING`.       |
| `Leave` | Equivalent to `/impostor leave`; removes an eligible player while the game is `WAITING`. |
| Lobby   | Updated whenever a player joins or leaves.                                               |
| Closure | Registration controls are disabled when the game starts or the session ends.             |

Buttons are visible to all users in the channel.

Discord does not allow disabling buttons in a public message for specific users. Invalid actions are therefore rejected by the same rules applied to the equivalent commands.

## Starting a Game

When running:

```text
/impostor start
```

the bot must:

1. verify that an active game exists;
2. verify that the game is `WAITING`;
3. verify that the user is the host;
4. verify that at least 3 players are registered;
5. obtain a valid secret word;
6. select exactly one impostor;
7. assign one role to every player;
8. send the roles by direct message.

If all roles are delivered successfully, the game becomes:

```text
STARTED
```

If one or more roles cannot be delivered, the game must not continue as a valid started game.

## Secret Information

The bot must never publicly reveal:

* the secret word;
* the identity of the impostor.

This information is delivered only through direct messages.

| Player Type    | Message Received                                                                               |
| -------------- | ---------------------------------------------------------------------------------------------- |
| Regular player | Receives the secret word and a brief instruction.                                              |
| Impostor       | Receives a message indicating that they are the impostor and does not receive the secret word. |

## Secret Words

A valid secret word must be available before the game can start.

If no valid word can be obtained, the game must not start.

The source and format of the available words are documented in [`words.md`](words.md).

## Invalid Actions

The bot must prevent the following actions:

| Invalid Action                                | Expected Result                                         |
| --------------------------------------------- | ------------------------------------------------------- |
| Creating two active games in the same channel | Creation is rejected                                    |
| Joining twice                                 | Join is rejected                                        |
| Joining as the host                           | Join is rejected because the host is already registered |
| Leaving without being registered              | Leave is rejected                                       |
| Leaving as the host                           | Leave is rejected; the host must cancel the game        |
| Joining after the game starts                 | Join is rejected                                        |
| Leaving after the game starts                 | Leave is rejected                                       |
| Starting without being the host               | Start is rejected                                       |
| Starting with fewer than 3 players            | Start is rejected                                       |
| Starting a game that is not `WAITING`         | Start is rejected                                       |
| Finishing without being the host              | Finish is rejected                                      |
| Finishing a game that is not `STARTED`        | Finish is rejected                                      |
| Cancelling without being the host             | Cancel is rejected                                      |

## Out of Scope

The bot does not include:

* voting inside the bot;
* winner declaration;
* scoring;
* rankings;
* completed-game history;
* multiple impostors;
* timers;
* turn control;
* moderation of words or clues;
* automatic final reveal of the word or the impostor.

## Completion Criteria

The core rules are fulfilled when the following normal flow can be completed without revealing secret information publicly:

```text
/impostor create
→ players join
→ /impostor start
→ roles are delivered privately
→ game reaches STARTED
→ players conduct the game
→ /impostor finish
→ game reaches FINISHED
```

Cancellation remains available as an alternative ending from an active game.

---

## Related Documentation

* [`commands.md`](commands.md) — how to use the bot commands.
* [`game-flow.md`](game-flow.md) — how a game progresses from lobby creation to completion.
* [`words.md`](words.md) — secret-word behavior.