# ADR 002: Use PostgreSQL for Persistent Game State

## Status

Accepted

## Context

The initial bot stored active games in process memory.

That approach is simple but makes game state dependent on the lifetime of the Python process:

```text
process stops
    ↓
memory disappears
    ↓
active games disappear
```

v2.0.0 requires active sessions to survive process restarts and production deployments.

The persistence mechanism must also support:

* multiple independent Discord sessions;
* player membership;
* relational constraints;
* transactional updates;
* asynchronous Python access;
* reproducible schema evolution.

## Decision

Use **PostgreSQL** as the persistent database for game-session state.

Database access is implemented through:

```text
Application
    ↓
Repository Port
    ↓
PostgreSQL Repository
    ↓
SQLAlchemy 2
    ↓
asyncpg
    ↓
PostgreSQL
```

Alembic is used as the source of truth for schema migrations.

Application and domain code interact with repository abstractions rather than directly depending on SQLAlchemy models or PostgreSQL-specific APIs.

The session identity is based on Discord context:

```text
guild_id + channel_id
```

Database constraints complement domain-level validation.

## Alternatives Considered

### In-memory persistence

The simplest implementation and useful for early development.

It was rejected as the production persistence mechanism because process restart would destroy active state.

### SQLite

SQLite would reduce local infrastructure requirements.

It was not selected because PostgreSQL better represents the intended production environment and provides stronger alignment with concurrent asynchronous access, relational constraints, and managed cloud deployment.

### Redis

Redis could maintain external state and could later participate in distributed coordination.

It was rejected because the current data is relational and durable persistence is required. Introducing Redis would add infrastructure without replacing the need for a persistent relational database.

## Consequences

### Positive

* Active sessions survive process restarts.
* Recovery can reconstruct runtime state after startup.
* Database constraints protect persisted invariants.
* Production and integration testing use the same database technology.
* Schema changes are reproducible through Alembic.
* Persistence remains replaceable through repository ports.

### Negative

* The application now depends operationally on an external database.
* Database availability becomes part of application startup requirements.
* Schema migrations must be managed as part of deployment.
* Database evolution must consider compatibility with application rollback.

These costs are justified by the persistence and recovery requirements of v2.0.0.
