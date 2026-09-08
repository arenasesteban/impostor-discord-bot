# ADR 003: Separate the Game Domain from Discord

## Status

Accepted

## Context

Discord is the primary user interface of the application, but Discord-specific concepts are not game rules.

Examples of Discord-specific concerns include:

* interactions;
* slash commands;
* buttons;
* views;
* message responses;
* direct messages;
* Discord API exceptions.

Examples of game concerns include:

* whether a player can join;
* whether a game can start;
* minimum player requirements;
* role assignment;
* game state transitions;
* session ownership rules.

If these responsibilities are implemented together, domain behavior becomes dependent on `discord.py`, making the core harder to test and encouraging interaction handlers to become the authoritative location for business rules.

## Decision

Treat Discord as an **external adapter**.

Discord handlers are responsible for:

```text
Discord input
     ↓
input mapping
     ↓
application use case
     ↓
application result
     ↓
Discord response
```

Game rules remain in the domain.

Application use cases orchestrate domain behavior and external ports.

Discord-specific objects are not passed into the domain as business entities.

Expected application/domain failures are translated by the Discord boundary into appropriate user-facing responses.

The domain must not import `discord.py`.

## Alternatives Considered

### Place game logic directly in command handlers

This is initially simpler because each command contains the complete operation.

It was rejected because business behavior becomes coupled to Discord interactions and difficult to test independently.

### Introduce a generic UI framework abstraction

A broader interface abstraction could be created to support multiple user interfaces from the start.

This was rejected because Discord is currently the only product interface. Creating abstractions for hypothetical interfaces would add complexity without a demonstrated requirement.

The chosen boundary isolates Discord where it matters without generalizing beyond current needs.

## Consequences

### Positive

* Game rules can be tested without connecting to Discord.
* Discord interaction objects do not leak into the domain.
* Command and button handlers remain focused on input/output concerns.
* Domain errors and infrastructure errors can be handled at appropriate boundaries.
* Future changes to Discord presentation do not require rewriting game rules.
* A future alternative interface could reuse application behavior if needed.

### Negative

* Additional mapping is required between Discord data and application/domain inputs.
* Some interactions require coordination across adapter and application layers.
* Developers must preserve the boundary instead of placing convenient business logic directly in handlers.

The additional separation is considered worthwhile because testability and maintainability are primary v2.0.0 goals.
