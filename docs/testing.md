# Testing

The project uses a layered testing strategy to validate business rules, application behavior, persistence, Discord adapters, and critical end-to-end flows.

The goal is **meaningful confidence**, not maximizing the number of tests or reaching 100% coverage.

## Test Strategy

```text
             Manual Smoke / E2E
                    │
              Discord Adapter
                    │
          PostgreSQL Integration
                    │
               Application
                    │
                 Domain
```

| Layer                      | Purpose                                                       | External dependencies |
| -------------------------- | ------------------------------------------------------------- | --------------------- |
| **Domain**                 | Game rules, invariants and state transitions                  | None                  |
| **Application**            | Use-case orchestration and concurrency                        | None                  |
| **Infrastructure Unit**    | Mapping, error translation, locks, logging, providers         | None                  |
| **PostgreSQL Integration** | Persistence, constraints, recovery and full application flows | PostgreSQL            |
| **Discord Adapter**        | Interaction mapping, responses, views and role delivery       | None                  |
| **Smoke / E2E**            | Critical flows in a real Discord environment                  | PostgreSQL + Discord  |

The classification is based on the **real boundary crossed by the test**, not on whether it is asynchronous or uses mocks.

For example:

```text
StartGame + in-memory repository
→ Application test

StartGame + PostgresGameRepository + PostgreSQL
→ Integration test
```

## Test Organization

```text
tests/
├── helpers/
├── integration/
│   ├── test_postgres_game_flow.py
│   ├── test_postgres_game_repository.py
│   ├── test_postgres_lobby_message_repository.py
│   └── test_session_recovery.py
└── unit/
    ├── application/
    ├── discord/
    ├── errors/
    ├── game/
    ├── infrastructure/
    ├── observability/
    └── words/
```

### Domain & Application

The core suite validates:

* game creation and player management;
* state transitions and invalid transitions;
* minimum-player requirements;
* exactly one impostor and role consistency;
* host authorization;
* create/join/leave/start/finish/cancel/status use cases;
* concurrent operations and session isolation.

These tests are deterministic and require neither PostgreSQL nor Discord.

### PostgreSQL Integration

Integration tests use a real PostgreSQL test database to validate behavior that cannot be demonstrated by an in-memory implementation alone:

* aggregate persistence and round trips;
* player ordering and aggregate synchronization;
* composite session identity;
* database constraints and foreign keys;
* cascade deletion;
* lobby-message persistence;
* recovery and recovery idempotency;
* persistence across runtime lifecycle;
* complete application flows.

Integration test modules are marked at module level with:

```python
pytestmark = pytest.mark.integration
```

The marker means that the tests in that module require real PostgreSQL infrastructure. It does not mean that the tests are merely asynchronous, slow, or large.

### Discord Adapter

Discord tests validate **our adapter code**, not `discord.py` internals.

They cover:

* Discord IDs → application input mapping;
* slash commands and persistent buttons;
* deferred responses and follow-ups;
* lobby lifecycle;
* persistent view IDs;
* role delivery and controlled DM failures;
* safe infrastructure-error responses;
* unexpected-error boundaries;
* startup, shutdown and recovery behavior.

They do not access the Discord network and do not require a valid Discord token.

## Running Tests

| Goal                   | Command                                                                | PostgreSQL required |
| ---------------------- | ---------------------------------------------------------------------- | ------------------: |
| Fast suite             | `pytest -m "not integration"`                                          |                  No |
| PostgreSQL integration | `pytest -m integration`                                                |                 Yes |
| Complete suite         | `pytest`                                                               |                 Yes |
| Line coverage          | `pytest --cov=src/impostor_bot --cov-report=term-missing`              |                 Yes |
| Branch coverage audit  | `pytest --cov=src/impostor_bot --cov-branch --cov-report=term-missing` |                 Yes |

Integration tests require an isolated test database configured through:

```powershell
$env:TEST_DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/impostor_bot_test"
```

Use local test credentials and never commit the real value.

If the integration environment is missing or PostgreSQL is unavailable, the integration suite must fail rather than silently report a successful run.

## Coverage Policy

Coverage is used as a **diagnostic signal**, not as a target by itself.

Domain and Application behavior are expected to remain strongly covered because they are deterministic and inexpensive to isolate.

The project intentionally does not add low-value tests solely to increase a percentage.

Branch coverage is also used during audits to identify missing conditional behavior, but is not currently enforced as a percentage gate.

## Manual Smoke Testing

Automated tests provide deterministic coverage of the application. A small manual smoke suite validates the few scenarios that benefit from a real Discord environment.

<details>
<summary><strong>Smoke A — Complete Game Lifecycle</strong></summary>

### Preconditions

* PostgreSQL running.
* Database migrations up to date.
* Bot connected to a development Discord guild.
* At least three test users available.

### Steps

1. Create a game.
2. Join with two additional players.
3. Start the game.
4. Verify role DMs.
5. Check game status.
6. Finish the game.

### Expected

* Lobby is created successfully.
* Each player is registered once.
* Game reaches `STARTED`.
* Exactly one player receives the impostor role.
* Normal players receive the secret word.
* Status reflects the active game.
* Finish releases the session.
* Another game can subsequently be created in the same channel.

</details>

<details>
<summary><strong>Smoke B — Restart Recovery</strong></summary>

### Preconditions

* PostgreSQL running.
* Database migrations up to date.
* Bot connected to a development Discord guild.

### Steps

1. Create a game and join players.
2. Stop the bot without deleting the lobby message.
3. Start the bot again using the same database.
4. Use the original Join/Leave controls.
5. Start the recovered game.
6. Check its status.
7. Finish the game.

### Expected

* Persisted session is discovered.
* Lobby metadata is recovered.
* Persistent controls remain usable.
* Recovery does not duplicate state.
* The recovered game can continue and finish normally.

</details>

<details>
<summary><strong>Smoke C — DM Delivery Failure</strong></summary>

### Preconditions

* PostgreSQL running.
* Bot connected to a development Discord guild.
* Enough users to start a game.
* One test user unable to receive DMs from the bot.

### Steps

1. Create a game.
2. Join enough players.
3. Start the game.

### Expected

* DM failure is handled as a controlled condition.
* The configured compensation path runs.
* The game does not remain stuck in an invalid `STARTED` state.
* Users receive a safe response.
* Diagnostic logging is produced.
* Persistent state remains consistent.

</details>

Multi-guild and concurrency behavior are primarily covered by automated tests and are not part of the mandatory manual smoke suite.

## Scope Boundaries

The current strategy intentionally does not include:

* real Discord connections inside pytest;
* production Discord credentials in automated tests;
* pytest parallelization;
* property-based or mutation testing solely to increase coverage;
* artificial tests for composition code.

Linting, static typing, Docker execution and CI enforcement belong to later roadmap phases.
