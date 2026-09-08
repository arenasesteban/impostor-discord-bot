# Architecture

This document describes the architecture of Discord Impostor Bot v2.0.0.

It focuses on system boundaries, dependency direction, runtime behavior, persistence, concurrency, recovery, and deployment topology.

For a high-level project overview, see the repository [`README.md`](../README.md). Game rules and user-facing behavior are documented separately under `docs/`.

---

## 1. Architectural Goals

The v2.0.0 architecture was designed around a small set of goals:

* keep game rules independent from Discord;
* keep application logic independent from PostgreSQL and SQLAlchemy;
* isolate external systems behind explicit boundaries;
* make the game lifecycle testable without network access;
* support independent games across Discord guilds and channels;
* preserve active state across process restarts;
* protect session mutations from concurrent Discord interactions;
* keep deployment reproducible and operationally simple;
* avoid distributed-system complexity that the current scale does not require.

The project intentionally favors a **modular monolith with pragmatic Ports & Adapters boundaries** rather than a strict or framework-heavy implementation of Clean Architecture.

The central dependency rule is:

> Discord, PostgreSQL, configuration providers, and deployment infrastructure are external details. Game rules must not depend on them.

---

## 2. System Context

At runtime, the application interacts with two primary external systems:

```text
                     Discord
                        │
                        │ interactions / responses
                        ▼
              ┌──────────────────┐
              │  Impostor Bot    │
              │                  │
              │  Python process  │
              └────────┬─────────┘
                       │
                       │ persistence
                       ▼
                ┌─────────────┐
                │ PostgreSQL  │
                └─────────────┘
```

Discord is the user-facing interface.

PostgreSQL is the persistent source of game-session state.

The application itself remains a single deployable process.

---

## 3. Architectural Style

The application follows a Ports & Adapters structure organized as a modular monolith.

Conceptually:

```text
┌──────────────────────────────────────┐
│            Discord Adapter           │
│                                      │
│ commands · buttons · views · mapping │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│          Application Layer           │
│                                      │
│ create · join · leave · start        │
│ finish · cancel · queries            │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│                Domain                │
│                                      │
│ Game · Player · State · Rules        │
│ Domain errors                        │
└──────────────────┬───────────────────┘
                   │
                  ports
          ┌────────┴─────────┐
          │                  │
          ▼                  ▼
┌──────────────────┐  ┌──────────────────┐
│ PostgreSQL       │  │ Word Provider    │
│ Repository       │  │                  │
│                  │  │ Static           │
│ SQLAlchemy       │  │ implementation   │
│ asyncpg          │  │                  │
└──────────────────┘  └──────────────────┘
```

The layers describe responsibilities rather than deployment units.

All modules are part of the same Python application and are deployed together.

---

## 4. Repository Structure

The main application package is organized around architectural responsibilities:

```text
src/impostor_bot/
├── application/
├── discord/
├── game/
├── infrastructure/
├── ports/
├── words/
├── config.py
└── main.py
```

### `game/`

Contains the core game model and game-specific rules.

This layer owns concepts such as:

* game state;
* players;
* session identity;
* valid and invalid state transitions;
* player membership rules;
* start/finish/cancel behavior;
* domain-specific errors.

It must not import:

* `discord.py`;
* SQLAlchemy;
* asyncpg;
* Railway-specific code;
* environment-variable access.

### `application/`

Coordinates use cases.

Typical responsibilities include:

* loading the current game through a repository port;
* invoking domain behavior;
* coordinating external collaborators;
* saving resulting state;
* enforcing the application-level sequence of a command.

Examples include the flows for:

```text
Create Game
Join Game
Leave Game
Start Game
Finish Game
Cancel Game
```

The application layer knows the ports it needs, but not their concrete infrastructure implementations.

### `ports/`

Defines contracts used by the application or domain to communicate with external capabilities.

The most important boundary is the game repository.

Conceptually:

```python
class GameRepository(Protocol):
    async def get(self, key: GameSessionKey) -> Game | None:
        ...

    async def save(self, game: Game) -> None:
        ...
```

Other replaceable behavior follows the same principle where appropriate.

Ports point outward conceptually, but the dependency direction remains inward:

```text
Application
     │
     ▼
Port abstraction

Infrastructure
     │
     └── implements that abstraction
```

### `infrastructure/`

Contains technical implementations for external systems.

The main persistence adapter uses:

```text
PostgreSQL
SQLAlchemy 2
asyncpg
Alembic
```

Infrastructure is responsible for:

* database models;
* sessions/transactions;
* persistence mapping;
* PostgreSQL-specific behavior;
* translating infrastructure failures into application-safe errors.

Infrastructure must not become the owner of game rules.

### `discord/`

Acts as the user-interface adapter.

It contains the Discord-specific boundary:

```text
Discord interaction
        │
        ▼
command / button handler
        │
        ▼
application request
        │
        ▼
use case
        │
        ▼
application result / error
        │
        ▼
Discord response
```

Discord handlers are responsible for:

* extracting Discord identifiers and input;
* invoking the correct use case;
* rendering application outcomes;
* managing Discord views/components;
* translating expected errors into user-facing messages.

They should not independently implement game-state transitions or persistence rules.

### `words/`

Contains the current word-provider implementation.

v2.0.0 uses a static word source.

The word-selection capability is intentionally isolated so a future provider can replace it without requiring the game domain to know where words originate.

### `config.py`

Owns typed runtime configuration.

Configuration is created from external values and passed into the runtime rather than being read throughout the application as global state.

### `main.py`

Acts as the composition root and application entry point.

Its responsibility is to assemble the concrete runtime:

```text
configuration
      ↓
logging
      ↓
database infrastructure
      ↓
repository implementations
      ↓
application use cases
      ↓
Discord adapter
      ↓
bot runtime
```

Dependency construction belongs here rather than inside the domain or use cases.

---

## 5. Dependency Direction

The intended dependency direction is:

```text
                 ┌──────────────┐
                 │   Discord    │
                 │   Adapter    │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Application  │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │    Domain    │
                 └──────────────┘
                        ▲
                        │ contracts
                 ┌──────┴───────┐
                 │    Ports     │
                 └──────▲───────┘
                        │ implements
              ┌─────────┴─────────┐
              │                   │
      ┌───────────────┐   ┌───────────────┐
      │ PostgreSQL    │   │ Word Provider │
      │ Infrastructure│   │ Adapter       │
      └───────────────┘   └───────────────┘
```

The important rule is not the visual position of a package but the source-code dependency.

The domain must remain usable without:

```text
Discord
PostgreSQL
SQLAlchemy
asyncpg
Railway
environment variables
```

This makes the game rules deterministic and directly testable.

---

## 6. Domain Model

### Game Session Identity

A game is scoped by Discord context rather than by process-global state.

The session key is conceptually:

```text
GameSessionKey
├── guild_id
└── channel_id
```

Therefore:

```text
Guild A / Channel 1 → Game A
Guild A / Channel 2 → Game B
Guild B / Channel 1 → Game C
```

can coexist independently.

This identity is used consistently across application coordination, concurrency protection, and persistence.

---

## 7. Game State Machine

The game lifecycle is modeled explicitly.

```text
                   create
                     │
                     ▼
                  WAITING
                 /       \
            start           cancel
              │               │
              ▼               ▼
           STARTED        CANCELLED
           /     \
      finish       cancel
        │             │
        ▼             ▼
    FINISHED       CANCELLED
```

State transitions belong to the game model rather than to Discord handlers.

Invalid operations produce expected domain errors.

Examples include:

```text
join after start
start without enough players
finish before start
modify a completed game
duplicate player registration
unauthorized lifecycle action
```

The application layer coordinates these rules but does not redefine them.

---

## 8. Request Flow

A typical write operation follows the same architectural path.

For example, joining a game:

```text
Discord button
      │
      ▼
Discord adapter
      │
      │ guild_id
      │ channel_id
      │ user_id
      ▼
Join application use case
      │
      ▼
Acquire session lock
      │
      ▼
GameRepository.get()
      │
      ▼
Game.add_player()
      │
      ▼
GameRepository.save()
      │
      ▼
Release lock
      │
      ▼
Application result
      │
      ▼
Discord response
```

This shape is deliberately repeated across state-changing interactions.

It prevents Discord UI code from becoming the location where business behavior accumulates.

---

## 9. Concurrency Model

Discord interactions are asynchronous and multiple users may act on the same game almost simultaneously.

A vulnerable sequence would be:

```text
Player A ─────┐
              ├── read current game
Player B ─────┘

Player A ─────┐
              ├── modify independently
Player B ─────┘

              ↓
lost or inconsistent update
```

v2.0.0 protects the application-level read-modify-write sequence with an `asyncio.Lock` associated with each game session.

Conceptually:

```text
GameSessionKey
      │
      ▼
session lock
      │
      ▼
read
      ↓
validate / modify
      ↓
save
```

Locks are scoped by session rather than globally.

Therefore operations against unrelated games can proceed concurrently:

```text
Game A lock ── operation A

Game B lock ── operation B
```

without unnecessarily serializing the entire bot.

### Concurrency Boundary

These locks exist inside one Python process.

They do **not** provide distributed locking across multiple replicas.

For that reason, v2.0.0 intentionally operates with:

```text
bot replicas = 1
```

Supporting horizontal scaling would require a different concurrency strategy, such as database-level coordination or another distributed locking mechanism.

That complexity is outside the scope of v2.0.0.

---

## 10. Persistence Architecture

The application accesses persistence through the repository port.

Conceptually:

```text
Application
     │
     ▼
GameRepository
     │
     ▼
PostgreSQL adapter
     │
     ▼
SQLAlchemy
     │
     ▼
asyncpg
     │
     ▼
PostgreSQL
```

The application layer does not directly execute SQL or depend on ORM models.

### Persistent Session Identity

Games are persisted using their Discord session identity:

```text
(guild_id, channel_id)
```

Player persistence is associated with the corresponding game.

Database constraints complement domain validation so persisted state does not rely exclusively on Python-level checks.

Examples include protection against:

* duplicate game-session identity;
* duplicate player membership;
* orphaned player records.

---

## 11. Database Migrations

Alembic is the source of truth for schema evolution.

The expected lifecycle is:

```text
model/schema change
       │
       ▼
Alembic migration
       │
       ▼
alembic upgrade head
       │
       ▼
application runtime
```

Normal operation must not depend on manually modifying production tables.

The same migration chain is used in development, integration validation, and production deployment.

Production migrations execute before the new application runtime is started.

---

## 12. Process Lifecycle and Recovery

Application process state and game state are deliberately treated as different lifecycles.

```text
process stops
      │
      ▼
in-memory objects disappear

PostgreSQL
      │
      └── persistent active game remains
```

When the application starts again, the runtime reconnects to PostgreSQL and executes its recovery behavior for persisted active sessions.

Conceptually:

```text
Bot startup
    │
    ▼
Database available
    │
    ▼
Load recoverable sessions
    │
    ▼
Reconstruct runtime state
    │
    ▼
Discord bot ready
```

Therefore:

> restarting the process does not imply cancelling an active game.

This property is required both for normal service restarts and for deployment updates.

Recovery policy belongs to the application/runtime boundary; persisted game rules remain represented by domain state.

---

## 13. Discord Adapter Boundary

Discord is intentionally treated as an external UI.

A command or button should primarily perform three operations:

```text
map Discord input
        ↓
invoke application behavior
        ↓
render Discord output
```

It should not:

* make independent persistence decisions;
* bypass application locking;
* directly implement state transitions;
* select game roles by itself;
* mutate shared dictionaries as authoritative state;
* expose technical infrastructure exceptions to users.

This keeps Discord replaceable as an interface boundary and keeps tests focused on project behavior rather than `discord.py` internals.

---

## 14. Word Provider Boundary

The game requires a secret word but should not depend on how that word is obtained.

v2.0.0 uses a static provider:

```text
Application
     │
     ▼
Word Provider abstraction
     │
     ▼
Static Word Provider
```

This boundary allows future implementations such as:

```text
DatabaseWordProvider
AIWordProvider
```

without requiring the `Game` domain model to depend on a database SDK or AI API.

AI-based generation is deliberately outside the v2.0.0 scope.

---

## 15. Configuration Architecture

Runtime configuration is externalized through environment variables.

The application configuration includes:

```text
DISCORD_TOKEN
DATABASE_URL
LOG_LEVEL
ENVIRONMENT
```

These values are parsed into typed configuration at the application boundary.

Conceptually:

```text
Environment
    │
    ▼
Configuration loader
    │
    ▼
Typed Settings
    │
    ▼
Composition root
    │
    ├── Discord adapter
    ├── database infrastructure
    └── logging
```

Domain and application modules do not read environment variables directly.

### Environment Separation

The same application code is used across:

```text
development
test
production
```

Only external configuration and adapters vary as required.

Production secrets remain outside the Git repository and outside the Docker image.

---

## 16. Error Boundaries

Errors are separated by responsibility.

### Domain / expected application errors

Examples include:

```text
GameAlreadyExists
PlayerAlreadyJoined
PlayerNotFound
NotEnoughPlayers
InvalidGameState
UnauthorizedAction
```

These represent expected business outcomes.

The Discord adapter translates them into appropriate user-facing responses.

### Infrastructure errors

Examples include failures originating from:

```text
PostgreSQL
Discord API
word-provider infrastructure
runtime configuration
```

Infrastructure failures are translated before they cross inward into layers that should not know implementation-specific exceptions.

Users should not receive raw SQLAlchemy, asyncpg, or internal stack-trace information.

---

## 17. Logging

Logging is treated as an operational boundary rather than game behavior.

Structured events provide runtime context such as:

```text
event
guild_id
channel_id
game/session identity
environment
```

where appropriate.

Typical operational events include:

```text
bot startup
game creation
player join/leave
game start
game finish/cancel
recovery
database failures
Discord API failures
shutdown
```

Logs must not contain:

* Discord tokens;
* PostgreSQL passwords;
* complete production connection strings;
* other secrets;
* unnecessary private Discord content.

The current observability strategy intentionally relies on structured application logs and hosting-platform runtime information rather than a dedicated observability stack.

---

## 18. Testability by Architecture

Testing is a consequence of the boundaries rather than an independent architecture.

Because game rules do not depend on Discord or PostgreSQL:

```text
Domain
→ direct unit tests
```

Because application use cases depend on ports:

```text
Application
→ fake repository
→ fake word provider
→ deterministic collaborators
```

Because PostgreSQL is an adapter:

```text
Repository implementation
→ integration tests
→ real PostgreSQL
```

Because Discord is an adapter:

```text
Discord mapping/rendering
→ adapter tests
→ mocked external Discord boundary
```

This produces the testing structure:

```text
                  Smoke
                    ▲
                    │
             Integration
                    ▲
                    │
        Application / Adapter
                    ▲
                    │
               Domain Unit
```

The majority of game behavior can therefore be validated without network access.

---

## 19. Composition Root

`main.py` is the runtime assembly boundary.

The composition process can be summarized as:

```text
Load environment
       │
       ▼
Load typed settings
       │
       ▼
Configure logging
       │
       ▼
Create database infrastructure
       │
       ▼
Create repository adapters
       │
       ▼
Create application services/use cases
       │
       ▼
Create Discord adapter
       │
       ▼
Run bot
```

This is where concrete implementations are selected.

The domain itself does not construct:

```text
PostgreSQL repositories
Discord clients
configuration loaders
```

This prevents a service-locator pattern from spreading through the codebase.

---

## 20. Local Runtime Topology

The reproducible local environment is containerized with Docker Compose.

Conceptually:

```text
Docker Compose
│
├── PostgreSQL
│
├── migration step
│      └── alembic upgrade head
│
└── Discord Bot
       └── waits for required infrastructure
```

The application container uses the same production-oriented Dockerfile validated by Continuous Integration.

There is no separate Dockerfile dedicated to CI or production.

---

## 21. Production Runtime Topology

Production runs on Railway.

```text
                    Discord
                       ▲
                       │
                       │ persistent gateway connection
                       │
             ┌─────────┴─────────┐
             │   Railway Bot     │
             │                   │
             │ Docker container  │
             │ single replica    │
             └─────────┬─────────┘
                       │
                       │ private DB connection
                       ▼
             ┌───────────────────┐
             │ Railway-managed   │
             │ PostgreSQL        │
             └───────────────────┘
```

The bot does not expose a public HTTP API because Discord communication does not require one.

Process health is determined through actual runtime behavior:

```text
deployment running
+
Discord connected
+
PostgreSQL available
+
commands responding
+
logs healthy
```

An artificial HTTP endpoint is therefore not part of the v2.0.0 architecture.

---

## 22. CI/CD Architecture

Continuous Integration and Continuous Deployment have separate responsibilities.

### Continuous Integration

GitHub Actions validates revisions through:

```text
Install
   ↓
Ruff
   ↓
mypy
   ↓
Unit / non-integration tests
   ↓
PostgreSQL integration tests
   ↓
Docker build
```

A Pull Request must satisfy the repository quality gates before it can become part of `main`.

### Continuous Deployment

Railway is connected to `main`.

The production flow is:

```text
Pull Request
     │
     ▼
CI
     │
     ▼
Merge
     │
     ▼
new commit on main
     │
     ├──────────────┐
     ▼              ▼
GitHub CI       Railway candidate
     │              │
     │           WAITING
     │              │
     └────PASS──────┘
                    │
                    ▼
              Railway build
                    │
                    ▼
           Alembic pre-deploy
                    │
                    ▼
            production runtime
```

Railway owns production configuration and production secrets.

GitHub Actions does not require:

```text
DISCORD_TOKEN
production DATABASE_URL
Railway deployment token
```

This keeps CI responsible for validation and Railway responsible for production execution.

---

## 23. Deployment and Database Compatibility

Application rollback and database rollback are separate operations.

```text
Application deployment
        │
        └── can roll back to an earlier application image

PostgreSQL
        │
        └── is not automatically downgraded
```

The deployment strategy therefore assumes that schema evolution should remain compatible with the immediately previous application version when practical.

For potentially breaking schema evolution, a staged approach is preferred:

```text
expand
   ↓
deploy application changes
   ↓
migrate usage/data
   ↓
contract later
```

Automatic `alembic downgrade` is intentionally not part of the production rollback mechanism.

---

## 24. Architectural Constraints

### Single Application Instance

v2.0.0 assumes exactly one running bot process.

This is required by the process-local concurrency model.

### Static Word Provider

The current implementation deliberately uses a local/static source of words.

External AI availability is not a dependency of the game.

### No Public Application API

Discord is the application interface.

There is no REST API or administrative web frontend.

### No Distributed Infrastructure

The architecture intentionally excludes:

```text
Redis
Kafka
microservices
Kubernetes
distributed locks
horizontal bot scaling
```

because the current product requirements do not justify them.

---

## 25. Extension Points

The architecture leaves several capabilities replaceable without redesigning the game domain.

### Word source

```text
WordProvider
├── StaticWordProvider
├── future DatabaseWordProvider
└── future AIWordProvider
```

### Persistence

The application depends on repository abstractions rather than SQLAlchemy directly.

A different persistence implementation could therefore be introduced without moving database concerns into the game model.

### Discord presentation

Business rules are isolated from `discord.py`.

Changes to Discord commands, buttons, or rendering should not require redefining game rules.

### Concurrency

The current locking strategy can be replaced if the application eventually requires multiple replicas.

That would be an architectural evolution rather than something hidden inside Discord handlers.

---

## 26. Architectural Trade-offs

### Why a modular monolith?

The application needs strong internal boundaries but does not need independent service deployment.

A modular monolith provides:

* simple deployment;
* straightforward local development;
* low operational overhead;
* explicit code boundaries;
* direct transactions;
* easy testing.

Microservices would add network, deployment, consistency, and observability complexity without solving a current requirement.

### Why PostgreSQL?

Persistent sessions require stronger guarantees than process memory alone.

PostgreSQL provides:

* durable state;
* relational constraints;
* transactional updates;
* mature SQLAlchemy support;
* reproducible schema migrations.

### Why one replica?

The product does not currently require horizontal scaling.

One replica allows per-session `asyncio.Lock` coordination to remain sufficient and keeps Discord event handling predictable.

### Why keep Discord outside the domain?

Discord is an external platform and can change independently from game rules.

Keeping the boundary explicit makes game behavior:

* deterministic;
* testable;
* reusable;
* independent from Discord interaction objects.

---

## 27. Known Architectural Limitations

The following limitations are intentional in v2.0.0:

* concurrency coordination is process-local;
* the bot cannot safely scale horizontally without a new coordination strategy;
* word generation uses a static provider;
* there is no administrative web interface;
* there is no distributed cache;
* there is no event bus;
* there is no automatic database downgrade;
* application rollback assumes compatible database evolution;
* observability is based on structured logs and hosting-platform metrics rather than a dedicated telemetry stack.

These are documented constraints, not accidental hidden behavior.

---

## 28. Architecture Decision Records

The major architectural decisions are documented separately under `docs/adr/`.

Planned v2.0.0 ADRs:

```text
docs/adr/
├── 001-modular-monolith.md
├── 002-postgresql.md
├── 003-domain-discord-separation.md
└── 004-single-instance-concurrency.md
```

The purpose of the ADRs is to preserve the reasoning and trade-offs behind these choices.

This document describes **how the architecture fits together**; the ADRs explain **why the important decisions were made**.

---

## 29. Architecture Summary

The complete v2.0.0 system can be summarized as:

```text
                         Discord
                            │
                            ▼
                  ┌─────────────────┐
                  │ Discord Adapter │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Application   │
                  │    Use Cases    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │     Domain      │
                  │                 │
                  │ Game            │
                  │ Player          │
                  │ State Machine   │
                  │ Rules           │
                  └───────┬─────────┘
                          │ ports
                  ┌───────┴────────┐
                  │                │
                  ▼                ▼
          ┌──────────────┐  ┌──────────────┐
          │ PostgreSQL   │  │ WordProvider │
          │ Repository   │  │ Static       │
          └──────┬───────┘  └──────────────┘
                 │
                 ▼
            PostgreSQL


Production:

GitHub
   │
   ▼
CI
   │
   ▼
Railway CD
   │
   ▼
Dockerized Bot
   │
   ▼
Managed PostgreSQL
```

The architecture intentionally demonstrates a focused set of engineering properties:

```text
clear boundaries
+
explicit state
+
safe async coordination
+
durable persistence
+
restart recovery
+
automated validation
+
reproducible deployment
```

without introducing distributed infrastructure that the product does not currently need.
