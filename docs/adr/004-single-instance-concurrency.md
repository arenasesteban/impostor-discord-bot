# ADR 004: Use Single-Instance, Per-Session Concurrency Control

## Status

Accepted

## Context

Discord interactions are asynchronous.

Multiple players can attempt to modify the same game almost simultaneously, for example:

```text
Player A joins
Player B joins

Player A leaves
Host starts game

Two start requests arrive together
```

A normal read-modify-write operation can therefore interleave:

```text
Task A ── read ───────── modify ── save
Task B ─────── read ── modify ─────── save
```

Without coordination, concurrent operations can produce lost updates or inconsistent application behavior.

At the same time, independent games should not block each other.

v2.0.0 explicitly does not require horizontal scaling.

## Decision

Run **one bot application instance** and protect mutable game operations with process-local `asyncio.Lock` instances scoped by game session.

The session identity is:

```text
GameSessionKey
├── guild_id
└── channel_id
```

The critical application sequence is protected conceptually as:

```text
acquire session lock
        ↓
load current state
        ↓
validate / modify domain
        ↓
persist resulting state
        ↓
release session lock
```

Different game sessions use different locks.

Therefore:

```text
Game A ── Lock A
Game B ── Lock B
```

can execute concurrently.

Database constraints remain a secondary protection for persisted invariants but do not replace application-level coordination.

Production is intentionally configured with a single bot replica.

## Alternatives Considered

### One global application lock

A single lock could serialize all game mutations.

This would be simpler but would unnecessarily block unrelated games in different Discord servers or channels.

### Database-only concurrency control

Transactions, optimistic concurrency, row locks, or stronger database coordination could become the primary concurrency mechanism.

This would support more advanced deployment models but would add complexity that the current single-instance architecture does not require.

### Distributed lock

A distributed lock through Redis or another coordination system could support multiple bot replicas.

It was rejected because horizontal scaling is explicitly outside the scope of v2.0.0.

Introducing distributed infrastructure solely for a hypothetical scaling requirement would increase operational complexity without current benefit.

## Consequences

### Positive

* Concurrent mutations of the same session are serialized.
* Independent sessions continue operating concurrently.
* The implementation remains simple and uses native asyncio primitives.
* No additional distributed infrastructure is required.
* The concurrency model matches the current production scale.

### Negative

* Locks only coordinate tasks inside one Python process.
* Multiple bot replicas cannot safely rely on this mechanism.
* Horizontal scaling would require redesigning the concurrency strategy.
* Process-local locks disappear during restart and must not be treated as persistent state.

If future requirements introduce multiple application replicas, this decision must be revisited. Possible replacements include database-level coordination, optimistic concurrency, idempotency controls, or a distributed lock mechanism.
