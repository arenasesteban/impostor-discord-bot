# Commands

This document provides a reference for the Discord commands and interactive controls available in **Discord Impostor Bot**.

All commands are grouped under:

```text
/impostor
```

Commands use the Discord guild and channel where they are executed as their game context.

## Command Reference

| Command            | Description                               | Access            |
| ------------------ | ----------------------------------------- | ----------------- |
| `/impostor help`   | Shows a short usage guide.                | Any user          |
| `/impostor create` | Creates a game in the current channel.    | Any user          |
| `/impostor join`   | Joins the current lobby.                  | Any eligible user |
| `/impostor leave`  | Leaves the current lobby.                 | Joined players    |
| `/impostor status` | Shows information about the current game. | Any user          |
| `/impostor start`  | Starts the current game.                  | Host              |
| `/impostor finish` | Finishes the current game.                | Host              |
| `/impostor cancel` | Cancels the current game.                 | Host              |

---

## `/impostor help`

```text
/impostor help
```

Shows a brief guide to the available bot commands.

**Response:** private to the requesting user.

---

## `/impostor create`

```text
/impostor create
```

Creates a new game in the Discord channel where the command is executed.

The bot publishes a lobby containing the current game information and the available registration controls.

**Response:** public lobby message.

---

## `/impostor join`

```text
/impostor join
```

Adds the requesting user to the current lobby.

The lobby is updated after a successful join.

This command is also available through the **Join** button.

**Response:** private confirmation and public lobby update.

---

## `/impostor leave`

```text
/impostor leave
```

Removes the requesting user from the current lobby.

The lobby is updated after a successful leave.

This command is also available through the **Leave** button.

**Response:** private confirmation and public lobby update.

---

## `/impostor status`

```text
/impostor status
```

Shows information about the current active game, including its current status and registered players.

**Response:** private to the requesting user.

---

## `/impostor start`

```text
/impostor start
```

Starts the current game.

This command is available to the game host.

When successful, players receive their private role information through Discord direct messages and the channel is notified that the game has started.

**Response:** private role messages and public start confirmation.

---

## `/impostor finish`

```text
/impostor finish
```

Closes a game that has been completed normally.

This command is available to the game host after the game has started.

**Response:** public completion message.

---

## `/impostor cancel`

```text
/impostor cancel
```

Cancels the current active game.

This command is available to the game host and can be used whether the group is still preparing the lobby or the game has already started.

**Response:** public cancellation message.

---

## Interactive Controls

The game lobby includes:

```text
Join | Leave
```

These controls provide shortcuts for player registration.

| Button  | Equivalent Command | Description              |
| ------- | ------------------ | ------------------------ |
| `Join`  | `/impostor join`   | Joins the current lobby  |
| `Leave` | `/impostor leave`  | Leaves the current lobby |

Button interactions produce the same result as their corresponding slash commands.

---

## Command Feedback

When a command cannot be completed in the current context, the bot returns a private message explaining why the action was rejected.

Examples include attempting to use a command when:

* no applicable game exists;
* the requester cannot perform that command;
* the requested action is not currently available.

Detailed game restrictions are documented in [`rules.md`](rules.md).

---

## Related Documentation

* [`game-flow.md`](game-flow.md) — how a game progresses from lobby creation to completion.
* [`rules.md`](rules.md) — game restrictions and allowed actions.
* [`words.md`](words.md) — secret-word behavior.
