# ADR 001: Use a Modular Monolith

## Status

Accepted

## Context

Discord Impostor Bot is a single application responsible for coordinating the lifecycle of Impostor games through Discord.

The original implementation was small enough to run as a single process, but increasing responsibilities introduced distinct concerns:

* Discord interactions;
* game rules and state transitions;
* application orchestration;
* persistence;
* configuration;
* logging;
* recovery;
* external word providers.

Keeping these responsibilities in a flat or tightly coupled structure would make changes harder to test and would allow Discord or persistence concerns to spread into game logic.

At the same time, the application does not require independently deployable services, independent scaling, or distributed communication between bounded contexts.

## Decision

v2.0.0 is implemented as a **modular monolith** with pragmatic Ports & Adapters boundaries.

The application remains one deployable Python process while responsibilities are separated into explicit modules such as:

```text
application/
discord/
game/
infrastructure/
ports/
words/
```

The domain contains game behavior.

The application layer coordinates use cases.

Ports define boundaries to replaceable capabilities.

Discord and PostgreSQL remain external adapters.

All modules are built, tested, containerized, and deployed together.

## Alternatives Considered

### Flat monolithic structure

This would reduce the initial number of abstractions but would encourage business rules, Discord interactions, and persistence behavior to become coupled again.

It was rejected because maintainability and testability are primary goals of v2.0.0.

### Microservices

The application could be separated into independently deployable services.

This was rejected because the current product does not require independent scaling, distributed ownership, or separate deployment lifecycles.

Microservices would introduce additional concerns such as:

* service communication;
* network failures;
* distributed transactions;
* additional deployment units;
* service discovery;
* more complex observability.

Those costs do not solve a current requirement.

## Consequences

### Positive

* Business responsibilities have explicit boundaries.
* The application remains simple to deploy and operate.
* Domain behavior can be tested without external infrastructure.
* Refactoring one adapter does not require redesigning the complete application.
* Database transactions remain straightforward.
* Local development remains simple.

### Negative

* Architectural boundaries depend partly on code discipline.
* Modules cannot be scaled or deployed independently.
* The application remains one runtime failure boundary.

These trade-offs are acceptable for the current scale of the project.
