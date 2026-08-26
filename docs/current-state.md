# Discord Impostor Bot — Current State Baseline

## 1. Purpose

This document freezes the verified behavior and technical state of Discord Impostor Bot immediately before development of v2.0.0.

Its purpose is to provide a behavioral and architectural reference during the refactor so that:

* existing behavior can be preserved intentionally;
* regressions can be distinguished from architectural changes;
* known defects are not mistaken for desired behavior;
* new v2 functionality can be identified explicitly.

This document describes the pre-v2 system. It does not describe the target v2 architecture.

---

## 2. Baseline

| Property                     | Value                                      |
| ---------------------------- | ------------------------------------------ |
| Branch                       | `main`                                     |
| Commit                       | `78db61f9d40d10792ae9ad89aaaf05b4aece5a2f` |
| Baseline tag                 | `pre-v2.0.0-baseline`                      |
| Python                       | `3.12.13`                                  |
| Test result                  | `29 passed`                                |
| Total coverage               | `26%`                                      |
| Working tree before baseline | Clean                                      |

The baseline tag points to the unmodified pre-v2 application.

Temporary import changes used during the manual smoke test were restored before the baseline was frozen.

---

## 3. Current Repository Structure

The application already contains an initial separation between Discord-specific code, game logic and word loading.

```text
src/impostor_bot/
├── main.py
├── config.py
├── constants.py
│
├── discord/
│   ├── client.py
│   ├── commands.py
│   ├── lobby.py
│   ├── messages.py
│   ├── state.py
│   └── views.py
│
├── game/
│   ├── session.py
│   └── exceptions.py
│
└── words/
    ├── loader.py
    └── exceptions.py
```

The project therefore does not start v2 as a single monolithic Discord script.

There is already a partially isolated game module, but there is no explicit application/use-case layer and infrastructure boundaries are not represented as ports.

---

## 4. Runtime and Configuration

The application entry point creates the Discord bot and starts it using a Discord token loaded from environment configuration.

The current project uses:

* Python;
* `discord.py`;
* `python-dotenv`;
* pytest;
* pytest-cov.

The application is primarily designed to execute locally.

There is currently no:

* PostgreSQL persistence;
* migration system;
* Docker runtime;
* CI pipeline;
* continuous deployment;
* permanent cloud deployment.

---

## 5. Known Startup Defect

### BUG-001 — Inconsistent package imports

The pre-v2 source tree mixes package roots such as:

```python
from impostor_bot...
```

and:

```python
from src.impostor_bot...
```

### Observed behavior

The documented application startup does not execute successfully from the unmodified baseline because Python fails during import resolution.

### Verification

Temporarily normalizing the affected imports allowed:

```bash
python -m impostor_bot.main
```

to start the Discord bot successfully.

Those temporary modifications were reverted after the smoke test.

### Classification

Known baseline defect.

This startup failure is not behavior that v2 must preserve.

---

## 6. Discord Interface

The current application exposes the following slash-command group:

```text
/impostor
```

with the following commands:

| Command            | Responsibility                      |
| ------------------ | ----------------------------------- |
| `/impostor create` | Create a game lobby                 |
| `/impostor join`   | Join an existing lobby              |
| `/impostor leave`  | Leave an existing lobby             |
| `/impostor status` | Display current game/lobby state    |
| `/impostor start`  | Start the game and distribute roles |
| `/impostor cancel` | Cancel the current lobby            |
| `/impostor help`   | Display command help                |

The lobby also exposes two Discord buttons:

```text
Join
Leave
```

The buttons reuse the same general lobby operations as the equivalent slash commands.

---

## 7. Current Game Model

The current game model is represented primarily by `Session`.

Relevant state includes conceptually:

```text
host_id
players
status
secret_word
impostor_id
```

The host is automatically registered as a player when the session is created.

---

## 8. Current States

The pre-v2 session uses the following states:

```text
OPEN
STARTED
CANCELLED
```

There is no explicit `FINISHED` state.

The current bot is primarily responsible for preparing and starting the game rather than managing the complete gameplay lifecycle.

---

## 9. Current Game Rules

### Create

* A lobby may be created when no active lobby exists in the channel.
* The creator becomes the host.
* The host is automatically included in the player collection.
* A second active lobby in the same channel is rejected.

### Join

* A player may join an open lobby.
* Duplicate registration is rejected.
* The host cannot join again because the host already belongs to the session.
* Join is available through both slash command and interactive button.

### Leave

* A player may leave an open lobby.
* A user that does not belong to the lobby cannot leave.
* The host cannot leave their own lobby.
* Leave is available through both slash command and interactive button.

### Start

* Only the host may start the game.
* At least 3 players are required.
* A secret word is selected.
* Exactly one player becomes the impostor.
* Non-impostor players receive the secret word.
* The impostor receives an impostor-specific private message.

### Cancel

* The host may cancel the active lobby.
* The current user-facing authorization failure does not distinguish between a non-host participant and a user that is not part of the lobby.

### Finish

There is no explicit finish operation in the pre-v2 application.

`FinishGame` is therefore new v2 functionality rather than behavior extracted from the baseline.

---

## 10. Current Lifecycle

The effective lifecycle of the current application is:

```text
create
  ↓
OPEN
 ├── cancel
 │      ↓
 │   removed
 │
 └── start
        ↓
     STARTED
        ↓
   distribute roles
        ↓
     removed
```

After a successful start and role distribution, the game is removed from active in-memory state.

The bot does not retain a managed `STARTED` game until an explicit finish command.

As a result, a new lobby can be created immediately in the same channel after role distribution succeeds.

---

## 11. State Management

The current Discord adapter stores active runtime state in memory.

Conceptually, the relevant structures are:

```python
active_games: dict[int, Session]
active_lobby_messages: dict[int, int]
```

The key is the Discord channel identifier.

This means the existing application already supports simultaneous games in different Discord channels.

Manual smoke testing confirmed that games can run independently in separate channels.

### Limitations

State:

* exists only inside the running Python process;
* disappears when the bot restarts;
* is not persisted;
* is not protected by explicit per-session concurrency controls;
* has no recovery strategy.

---

## 12. Multi-session Baseline

The baseline already supports:

```text
Channel A → Game A
Channel B → Game B
```

at the same time.

Therefore, v2 multi-session work must preserve this capability.

The v2 objective is not simply to introduce multiple games, but to:

* model session identity explicitly;
* guarantee isolation;
* introduce concurrency protection;
* test simultaneous operations.

---

## 13. Word Selection

Words are currently loaded from the project's static word data.

The word module is responsible for:

* loading the available words;
* selecting words by category;
* selecting a random word;
* reporting invalid or unavailable word data.

There is currently no `WordProvider` abstraction.

The v2 architecture will introduce this boundary while preserving the static provider behavior.

AI-based word generation is not part of v2.0.0.

---

## 14. Role Assignment

When the host successfully starts a game:

1. the minimum-player rule is validated;
2. a secret word is selected;
3. exactly one impostor is selected;
4. private role messages are sent to all players.

The manual smoke test with the minimum of three users confirmed:

* one user receives the impostor role;
* the remaining users receive the secret word;
* the active game is subsequently released;
* a new game can then be created in the same channel.

---

## 15. Known Discord Interaction Defect

### BUG-002 — `/start` validation can raise `InteractionResponded`

The game/domain validation correctly rejects invalid start attempts.

However, when the adapter tries to report some expected failures to the user, it attempts to respond through an interaction that has already been responded to or deferred.

Discord then raises:

```text
InteractionResponded
```

### Confirmed scenarios

#### Host starts without enough players

The underlying operation correctly raises the minimum-player validation error.

The subsequent Discord error notification fails with `InteractionResponded`.

#### Non-host starts the game

The authorization validation correctly rejects the request.

The subsequent Discord notification also fails with `InteractionResponded`.

This applies whether the non-host user is already a player or is external to the lobby.

### Classification

Known adapter defect.

The underlying validation rules must be preserved.

The `InteractionResponded` exception must not be preserved as desired behavior.

---

## 16. DM Failure Scenario

The source code contains handling for failures while sending private Discord messages.

This scenario was not manually reproduced during the baseline smoke test.

Its status is therefore:

```text
Implemented but not manually verified.
```

v2 must define and test the expected behavior explicitly.

---

## 17. Existing Tests

The baseline test suite executes successfully.

```text
29 passed
```

Total measured coverage:

```text
26%
```

The existing tests primarily protect game/session rules and word-loading behavior.

Coverage is significantly lower around Discord integration and orchestration.

The 26% value is retained as the quantitative pre-v2 baseline. It is not a target for v2.

---

## 18. Baseline Smoke Test

A manual Discord smoke test was performed after temporarily correcting the package-import problem.

The following behaviors were confirmed:

* application starts successfully after import normalization;
* game creation works;
* users can join through interactive buttons;
* `/join` works;
* `/leave` works;
* duplicate game creation in the same channel is rejected;
* valid game start works with the minimum number of users;
* exactly one impostor is assigned;
* normal players receive the secret word;
* the game is released after role distribution;
* a new game can immediately be created in the same channel;
* `/cancel` works;
* simultaneous games in different channels work;
* invalid `/start` operations expose the known `InteractionResponded` defect.

DM-blocked behavior was not manually verified.

---

## 19. Behavior to Preserve During Refactor

Unless intentionally changed and documented, v2 must preserve:

* host creation behavior;
* automatic host registration;
* duplicate lobby rejection;
* join behavior;
* duplicate-player rejection;
* leave behavior;
* host leave restriction;
* minimum of three players;
* host-only start authorization;
* exactly one impostor;
* secret-word distribution to normal players;
* static word source behavior;
* cancellation capability;
* simultaneous games in separate channels.

Existing technical defects are not part of this compatibility contract.

---

## 20. Intentional v2 Behavior Changes

The following changes are expected to alter the baseline behavior intentionally:

* explicit `FINISHED` game state;
* explicit finish operation;
* persistence beyond process lifetime;
* restart/recovery policy;
* explicit application use cases;
* explicit repository abstraction;
* explicit session identity;
* concurrency protection;
* consistent Discord error handling.

Each behavioral change must be introduced through an explicit Issue and tests.

---

## 21. Current Technical Limitations

The pre-v2 application currently has:

* in-memory-only state;
* no persistence;
* no restart recovery;
* no explicit application layer;
* no repository port;
* no WordProvider port;
* no explicit concurrency control;
* no PostgreSQL;
* no migrations;
* no structured operational logging;
* no Ruff quality gate;
* no mypy quality gate;
* no Docker runtime;
* no Docker Compose development environment;
* no CI pipeline;
* no continuous deployment;
* no permanent production deployment.

The package import strategy is also inconsistent and prevents the unmodified documented runtime command from starting successfully.

---

## 22. v2.0.0 Scope

v2.0.0 will evolve the existing application toward a maintainable backend service with:

* explicit game lifecycle;
* Discord adapter separation;
* application use cases;
* domain rules independent from Discord;
* session isolation;
* concurrency protection;
* PostgreSQL persistence;
* migrations;
* automated testing at multiple levels;
* linting;
* static type checking;
* structured error handling;
* logging;
* external configuration;
* Docker;
* Docker Compose;
* GitHub Actions;
* permanent deployment;
* continuous deployment;
* architecture documentation.

---

## 23. v2.0.0 Non-goals

The following are explicitly outside the v2.0.0 scope:

* AI-generated words;
* microservices;
* Kubernetes;
* Kafka;
* Redis;
* Terraform;
* administrative web dashboard;
* separate frontend application;
* advanced usage analytics;
* horizontal bot scaling;
* complex observability platforms;
* monetization.

AI-based word generation is deferred to a future v2.1.0 extension.

---

## 24. Baseline Conclusion

The pre-v2 bot already provides a functional Discord game setup workflow, a partially isolated game model, static word selection, basic automated tests and independent channel-scoped sessions.

Its main limitations are not the absence of core gameplay setup, but the lack of explicit application boundaries, persistence, concurrency protection, comprehensive adapter testing and production-grade operational infrastructure.

v2.0.0 will evolve this verified baseline incrementally rather than replacing it wholesale.
