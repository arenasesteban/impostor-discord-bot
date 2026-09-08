# Game Flow

This document describes how a typical game progresses in **Discord Impostor Bot**, from creating the lobby to closing the session.

The bot coordinates the game setup and session lifecycle. The social part of the game—giving clues, discussing suspects, voting, and deciding the winner—takes place between the players.

## Flow Summary

```text
/impostor create
→ players join the lobby
→ optionally check /impostor status
→ host runs /impostor start
→ roles are sent by DM
→ players conduct the game
→ host runs /impostor finish
→ session ends
```

A game may also be cancelled by the host instead of reaching the normal finish.

## 1. Create a Game

A game begins when a user runs:

```text
/impostor create
```

The user becomes the host and is automatically added as the first player.

The bot publishes a lobby in the current channel showing the game information and the available registration controls:

```text
Join | Leave
```

From this point, other players can enter the lobby.

## 2. Join the Game

Players can join through either:

| Option           | Action                        |
| ---------------- | ----------------------------- |
| `Join` button    | Joins directly from the lobby |
| `/impostor join` | Joins through the command     |

After a successful join:

```text
player joins
→ player list changes
→ lobby is updated
→ player receives confirmation
```

Multiple players can continue joining until the host is ready to start.

## 3. Leave the Game

A player who joined the lobby may leave before the game starts.

They can use:

| Option            | Action                         |
| ----------------- | ------------------------------ |
| `Leave` button    | Leaves directly from the lobby |
| `/impostor leave` | Leaves through the command     |

After a successful leave:

```text
player leaves
→ player list changes
→ lobby is updated
→ player receives confirmation
```

The lobby remains available for the remaining players.

## 4. Check the Game Status

Players can inspect the current session with:

```text
/impostor status
```

The bot shows the current game information, including the host and registered players.

This can be used before starting to confirm that the lobby is ready.

It can also be used while the game remains active after starting.

## 5. Start the Game

When the group is ready, the host runs:

```text
/impostor start
```

The bot prepares the game by:

1. selecting a secret word;
2. selecting one player as the impostor;
3. preparing one private role for every player;
4. sending the roles through direct messages.

If role delivery succeeds, the bot announces that the game has started and closes the registration controls in the lobby.

The game then moves from lobby preparation to the social gameplay stage.

## 6. Receive Roles by Direct Message

Each player receives their role privately.

| Player Type    | Received Information                                                        |
| -------------- | --------------------------------------------------------------------------- |
| Regular player | Receives the secret word                                                    |
| Impostor       | Is informed that they are the impostor but does not receive the secret word |

The public channel does not reveal the secret word or the identity of the impostor.

Once the roles have been delivered, the players have the information required to begin playing.

## 7. Play the Game

The social game now takes place between the players.

A typical round may look like:

```text
players give clues
→ players observe each other's answers
→ group discusses suspicions
→ players vote
→ group determines the result
```

The bot does not control turns, evaluate clues, collect votes, or decide the winner.

The Discord session nevertheless remains active until the host explicitly finishes or cancels it.

## 8. Finish the Game

After the players have completed the game, the host closes the session with:

```text
/impostor finish
```

The bot then:

```text
game completed by players
→ host runs /impostor finish
→ lobby is marked as finished
→ session ends
```

After the session has ended, another game can be created in the same channel.

## 9. Cancel a Game

The host may decide to stop the session instead of completing the normal flow.

Cancellation is performed with:

```text
/impostor cancel
```

A game can be cancelled while players are still preparing the lobby or after the game has already started.

The resulting flow is:

```text
active game
→ host runs /impostor cancel
→ lobby is marked as cancelled
→ session ends
```

---

## Alternative Flows

### Player Leaves Before Starting

```text
lobby open
→ player uses Leave or /impostor leave
→ player is removed
→ lobby is updated
→ remaining players continue preparing
```

### Host Cancels Before Starting

```text
lobby open
→ host runs /impostor cancel
→ lobby is closed
→ session ends
```

### Host Cancels After Starting

```text
roles already delivered
→ game is in progress
→ host runs /impostor cancel
→ session is cancelled
```

### Direct Message Delivery Fails

The bot may be unable to deliver a role to one or more players.

In that case:

```text
host starts game
→ bot attempts role delivery
→ one or more deliveries fail
→ game does not continue
→ session is cancelled
```

The affected players are reported so the group can correct the problem before creating another game.

---

## Private Information

During the game flow, the bot does not publicly reveal:

* the secret word;
* the identity of the impostor.

Role information is delivered privately to the corresponding players.

---

## Flow Boundaries

The bot coordinates:

```text
lobby
→ registration
→ role distribution
→ active session
→ session closure
```

The players conduct:

```text
clues
→ discussion
→ voting
→ result
```

---

## Related Documentation

* [`commands.md`](commands.md) — how to use the bot commands.
* [`rules.md`](rules.md) — game restrictions and allowed actions.
* [`words.md`](words.md) — secret-word behavior.
