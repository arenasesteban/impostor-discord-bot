# Discord Impostor Bot

A production-deployed Discord application that coordinates the setup and lifecycle of **Impostor** games.

The project started as a locally executed Discord bot and evolved into a modular backend service with PostgreSQL persistence, automated testing, Docker-based execution, Continuous Integration, and automatic production deployment.

The v2.0.0 architecture focuses on maintainability, explicit boundaries, recoverable state, and reproducible operation rather than adding unnecessary infrastructure.

---

## Live Demo

A hosted instance of Discord Impostor Bot is available through a dedicated portfolio demo server.

**[Try the live demo on Discord](https://discord.gg/dyYUrECBhw)**

![Discord Impostor Bot demo](docs/assets/screenshot_live_demo.png)

No local installation or Discord application configuration is required. Open one of the playground channels and use `/create` to interact with the deployed bot.

A complete game requires multiple players. If you are visiting the demo alone, the server also includes a recorded walkthrough showing the complete flow from game creation and player registration to role delivery and game completion.

The hosted instance has been functionally validated with independent and simultaneous sessions across multiple channels and Discord guilds. It is provided exclusively for **portfolio and demonstration purposes** and is not offered as a public scalable service or with availability guarantees.

---

## Overview

Discord Impostor Bot acts as a neutral coordinator for an Impostor game.

It manages the session lifecycle, player registration, role assignment, secret-word selection, and private role delivery while keeping the game state isolated between Discord servers and channels.

From an engineering perspective, the project is designed as a **modular monolith with pragmatic Ports & Adapters boundaries**:

* Discord is treated as an external interface.
* Game rules remain independent from `discord.py`.
* Application use cases orchestrate domain behavior.
* PostgreSQL is accessed through repository abstractions.
* Infrastructure can be replaced without moving business rules into adapters.

The application is containerized and runs permanently on Railway with managed PostgreSQL and automated deployment after successful CI.

---

## Problem

Running an Impostor game manually requires someone to coordinate several pieces of hidden state:

* track participating players;
* choose the impostor;
* select a secret word;
* privately distribute roles;
* manage the lifecycle of the session.

That coordinator should not gain information unavailable to the other players.

The bot automates this setup and acts as the neutral coordinator.

The v2 rewrite also addresses a second problem: making that workflow reliable as software.

The application must support independent sessions, preserve active state across process restarts, isolate business rules from Discord, remain testable without external APIs, and run outside the developer machine.

---

## Features

### Game lifecycle

* Create a game with `/create`.
* Join and leave through Discord buttons.
* Start a game with `/start`.
* Inspect the current session with `/status`.
* Finish an active game with `/finish`.
* Cancel a session with `/cancel`.
* Prevent invalid lifecycle transitions.

### Player and role management

* Prevent duplicate player registration.
* Validate the minimum number of players before starting.
* Select exactly one impostor.
* Select a word from the configured static word provider.
* Deliver roles privately through Discord DMs.

### Session isolation and persistence

* Independent sessions by Discord guild and channel.
* Process-local concurrency protection for simultaneous interactions.
* PostgreSQL persistence for active games and players.
* Recovery of active sessions after process restart.
* Database constraints complement application-level validation.

### Engineering and operations

* Modular architecture with explicit ports and adapters.
* Structured application logging.
* Typed external configuration.
* Unit, application, Discord-adapter, and PostgreSQL integration tests.
* Ruff linting and mypy static type checking.
* Dockerized application runtime.
* Docker Compose development environment.
* GitHub Actions Continuous Integration.
* Railway production deployment.
* Automatic deployment from `main` only after successful CI.

---

## Architecture

The application keeps Discord and PostgreSQL outside the game rules.

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
              │ State / Rules   │
              └────────┬────────┘
                       │ ports
               ┌───────┴───────┐
               │               │
               ▼               ▼
      ┌────────────────┐ ┌────────────────┐
      │   PostgreSQL   │ │ Word Provider  │
      │   Repository   │ │     Static     │
      └────────────────┘ └────────────────┘
```

At repository level, the main responsibilities are organized around:

```text
src/impostor_bot/
├── application/      # use cases and application orchestration
├── discord/          # Discord commands, views and interaction mapping
├── game/             # domain model and game rules
├── infrastructure/   # database and other external implementations
├── ports/            # application/domain interfaces
├── words/            # word-provider implementation
├── config.py         # typed runtime configuration
└── main.py           # application composition and startup
```

The architecture is intentionally pragmatic rather than an attempt to reproduce every Clean Architecture convention.

See [`docs/architecture.md`](docs/architecture.md) for the detailed architecture description.

---

## Game Lifecycle

A game follows an explicit lifecycle.

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

While a game is waiting, players can join or leave.

Starting requires enough registered players. Once started, the bot selects the impostor and secret word and privately distributes the corresponding information.

Finishing or cancelling closes the active session.

Active session information is persisted in PostgreSQL so recoverable games do not depend exclusively on process memory.

See [`docs/game-flow.md`](docs/game-flow.md) for the detailed game flow.

---

## Technology Stack

| Responsibility          | Technology            |
| ----------------------- | --------------------- |
| Language                | Python 3.12           |
| Discord adapter         | `discord.py`          |
| Database                | PostgreSQL            |
| ORM / Data Mapper       | SQLAlchemy 2          |
| Async PostgreSQL driver | `asyncpg`             |
| Database migrations     | Alembic               |
| Testing                 | pytest                |
| Async testing           | pytest-asyncio        |
| Coverage                | pytest-cov            |
| Linting                 | Ruff                  |
| Static type checking    | mypy                  |
| Configuration           | Environment variables |
| Containerization        | Docker                |
| Local orchestration     | Docker Compose        |
| Continuous Integration  | GitHub Actions        |
| Deployment / CD         | Railway               |

The application runtime is pinned to the Python version used by the project Docker and CI environments rather than relying on an unspecified system interpreter.

---

## Requirements

### Recommended: Docker development

* Docker
* Docker Compose
* A Discord application and bot token

Docker Compose provides the application and PostgreSQL environment required for local execution.

### Native Python development

* Python 3.12
* PostgreSQL
* A Discord application and bot token
* Project runtime/development dependencies

The repository also includes environment and requirements files for local Python development, but Docker Compose is the shortest reproducible setup path.

---

## Local Development

### 1. Configure the environment

Copy `.env.example` to `.env` and provide the required local values.

```env
DISCORD_TOKEN=your_discord_bot_token
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/impostor
LOG_LEVEL=INFO
ENVIRONMENT=development
```

The example above contains placeholders only. Never commit the resulting `.env` file.

### 2. Start the local stack

```bash
docker compose up --build
```

The Compose environment provides the PostgreSQL service, applies the database migrations, and starts the bot using the same application runtime used by the Dockerized deployment.

To stop the stack:

```bash
docker compose down
```

Use a volume-removal command only when intentionally resetting local PostgreSQL data.

---

## Configuration

Runtime configuration is external to the application.

| Variable        | Required | Description                                    |
| --------------- | -------: | ---------------------------------------------- |
| `DISCORD_TOKEN` |      Yes | Token used to authenticate the Discord bot     |
| `DATABASE_URL`  |      Yes | Async PostgreSQL connection URL                |
| `LOG_LEVEL`     |       No | Application log level; defaults to `INFO`      |
| `ENVIRONMENT`   |       No | Runtime environment; defaults to `development` |

Supported environments are:

```text
development
test
production
```

Production credentials are managed by the deployment platform and are never stored in the repository.

**Never commit `.env`, Discord tokens, PostgreSQL passwords, or production connection strings.**

---

## Database

Persistent state is stored in PostgreSQL using SQLAlchemy 2 and the asynchronous `asyncpg` driver.

A game session is identified by its Discord context:

```text
GameSessionKey
├── guild_id
└── channel_id
```

This allows sessions in different guilds or channels to remain isolated.

Alembic is the source of truth for schema evolution.

Apply the current schema with:

```bash
alembic upgrade head
```

Database tables must not be modified manually as part of normal development or deployment.

Persistence is also part of the process-recovery strategy: when the bot starts, recoverable active sessions can be reconstructed from PostgreSQL instead of depending exclusively on in-memory state.

---

## Testing

Testing is organized around architectural boundaries rather than around Discord itself.

```text
Domain unit tests
        │
        ▼
Application tests
        │
        ▼
Discord adapter tests
        │
        ▼
PostgreSQL integration tests
        │
        ▼
Controlled smoke validation
```

### Run the complete test suite

```bash
pytest
```

### Run tests without PostgreSQL integration tests

```bash
pytest -m "not integration"
```

### Run PostgreSQL integration tests

```bash
pytest -m integration
```

Integration tests require an available test PostgreSQL database.

### Quality checks

The main local checks are:

```bash
ruff check .
mypy src/
pytest
```

The project also provides a local quality gate:

```bash
python scripts/quality.py
```

GitHub Actions executes the automated CI chain before changes are accepted into `main`:

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

The suite intentionally prioritizes meaningful coverage of domain behavior and critical integration paths rather than targeting an arbitrary 100% coverage number.

---

## Docker

The project uses one production-oriented `Dockerfile` rather than maintaining a separate CI or deployment image definition.

```text
Dockerfile
   │
   └── application runtime

Docker Compose
   │
   ├── PostgreSQL
   ├── migrations
   └── bot
```

The application image:

* uses a pinned Python runtime;
* runs as a non-root user;
* keeps secrets outside the image;
* installs version-controlled dependencies;
* starts the bot as a non-interactive process.

The same Dockerfile is validated by CI before a revision can become a production deployment candidate.

---

## Deployment

Production is hosted on Railway with a managed PostgreSQL service.

The deployment process is intentionally based on the same Dockerized application validated locally and in CI.

```text
Pull Request
     │
     ▼
GitHub Actions CI
     │
     ▼
Merge to main
     │
     ▼
Railway detects new revision
     │
     ▼
WAITING for CI on main
     │
     ▼
CI successful
     │
     ▼
Automatic Railway deployment
     │
     ▼
Docker build
     │
     ▼
Alembic pre-deploy migration
     │
     ▼
Discord Bot + PostgreSQL
```

Production secrets and database credentials remain managed by Railway rather than GitHub Actions.

The bot runs as a **single application instance**, matching the current process-local concurrency model.

Rollback remains an explicit operational action. Application rollback is treated separately from PostgreSQL schema downgrade.

---

## Architecture Decisions

The main architectural decisions behind v2.0.0 are:

* **Modular monolith:** enough separation for the current scale without introducing unnecessary distributed-system complexity.
* **Discord as an adapter:** Discord interactions translate external data into application use cases instead of containing game rules.
* **PostgreSQL persistence:** active sessions survive process lifecycle events and database constraints protect persisted state.
* **Single-instance concurrency:** per-session process-local locking is sufficient while horizontal scaling remains intentionally outside the v2.0 scope.

Detailed decisions are documented under [`docs/adr/`](docs/adr/).

---

## Known Limitations

The following are intentional v2.0.0 boundaries rather than unresolved architectural requirements:

* The application assumes a single running bot instance.
* Concurrency locks are process-local; distributed concurrency is not implemented.
* Horizontal scaling is not supported.
* Words are provided by the static word provider.
* AI-generated words are not part of v2.0.0.
* Discord remains the only user-facing interface; there is no administrative web dashboard.
* The bot coordinates game setup and lifecycle but does not automate the complete social-deduction gameplay, voting, or scoring process.
* Observability is intentionally limited to structured logging and platform-level runtime information.
* Production database rollback is not automatically coupled to application rollback.

These constraints keep the architecture aligned with the actual requirements of the project instead of introducing infrastructure without a demonstrated need.

---

## Documentation

Additional project documentation is kept under `docs/`:

* [`commands.md`](docs/commands.md) — Discord command reference.
* [`game-flow.md`](docs/game-flow.md) — detailed game lifecycle and interactions.
* [`rules.md`](docs/rules.md) — game rules and behavior.
* [`words.md`](docs/words.md) — word-provider behavior and word data.
* [`architecture.md`](docs/architecture.md) — technical architecture.
* [`adr/`](docs/adr/) — architecture decision records.
* [`current-state.md`](docs/current-state.md) — historical baseline captured before the v2.0 refactor.

`current-state.md` is intentionally retained as historical documentation and should not be interpreted as the current v2 architecture.

---

## Roadmap

### v2.0.0

Production-ready backend evolution:

```text
modular architecture
        +
PostgreSQL persistence
        +
recovery
        +
automated testing
        +
Docker
        +
CI/CD
        +
persistent cloud deployment
```

### v2.1.0

A potential next extension is an `AIWordProvider` implemented behind the existing word-provider port, without making AI a dependency of the game domain.

### Future

Additional game configuration or modes may be introduced when a concrete product requirement justifies them.

The project intentionally avoids adding infrastructure or frameworks solely to increase the number of technologies in the stack.

## Credits  

Developed by Esteban Arenas.  
