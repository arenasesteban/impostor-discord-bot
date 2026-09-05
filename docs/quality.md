# Code Quality

The project uses a reproducible local quality gate combining linting, static type analysis, and automated behavioral verification.

```text
Ruff
  ↓
mypy
  ↓
pytest
  ↓
QUALITY PASS
```

The complete gate is executed with:

```bash
python scripts/quality.py
```

A successful execution confirms that:

* the configured linting policy passes;
* production code passes static type analysis;
* the complete automated test suite passes;
* PostgreSQL integration tests remain green.

The baseline established during the v2.0.0 quality phase is:

* **259 automated tests passing**;
* **90% code coverage**;
* **Ruff passing with no violations**;
* **mypy passing with no type errors**.

---

# Quality Model

| Tool           | Responsibility           | Scope                                  |
| -------------- | ------------------------ | -------------------------------------- |
| **Ruff**       | Linting and code hygiene | Source, tests, migrations, and scripts |
| **mypy**       | Static type safety       | Production code under `src/`           |
| **pytest**     | Behavioral verification  | Unit and integration tests             |
| **pytest-cov** | Coverage diagnostics     | Application code                       |

The tools intentionally provide different guarantees:

```text
Static correctness
        +
Behavioral correctness
        =
Local quality gate
```

---

# Quick Start

## Complete Quality Gate

With the development environment active and the PostgreSQL test database available:

```bash
python scripts/quality.py
```

The runner executes:

```text
ruff check .
      ↓
mypy src/
      ↓
pytest
```

Execution is **fail-fast**.

A failure in Ruff prevents mypy and pytest from running.

A failure in mypy prevents pytest from running.

Only a successful execution of every stage returns exit code `0`.

---

## Individual Checks

### Linting

```bash
ruff check .
```

### Static Type Checking

```bash
mypy src/
```

Without the incremental cache:

```bash
mypy src/ --no-incremental
```

### Complete Test Suite

```bash
pytest
```

### Tests Without PostgreSQL Integration

```bash
pytest -m "not integration"
```

### PostgreSQL Integration Tests

```bash
pytest -m integration
```

The testing architecture, markers, database requirements, and controlled smoke scenarios are documented in:

```text
docs/testing.md
```

---

# Configuration

Quality configuration is separated from orchestration.

```text
pyproject.toml
├── Ruff configuration
└── mypy configuration

pytest.ini
└── pytest configuration

scripts/quality.py
└── quality-gate orchestration
```

The configuration files define how each tool behaves.

`scripts/quality.py` only defines which checks execute and in what order.

---

# Requirements

The complete quality gate assumes:

1. the project development environment is active;
2. development dependencies are installed;
3. the PostgreSQL test database is available;
4. the database configuration required by the test suite is valid.

Infrastructure provisioning is intentionally outside the responsibility of the quality runner.

---

# Development Workflow

Fast feedback during implementation can use:

```bash
ruff check .
mypy src/
pytest -m "not integration"
```

Persistence-related changes can additionally run:

```bash
pytest -m integration
```

Final automated local validation uses:

```bash
python scripts/quality.py
```

Controlled Discord smoke testing remains separate and is documented in:

```text
docs/testing.md
```

---

# Design Decisions

<details>

<summary><strong>Why use a single quality runner?</strong></summary>

A single entry point provides a reproducible local quality check:

```bash
python scripts/quality.py
```

It also establishes a stable quality contract that can later be reused by CI automation.

The runner intentionally contains no Ruff, mypy, or pytest policy. It only executes the tools in the required order.

This prevents configuration from being duplicated between:

* local scripts;
* documentation;
* CI workflows.

Tool policy remains owned by `pyproject.toml` and `pytest.ini`.

</details>

<details>

<summary><strong>Why is the quality gate fail-fast?</strong></summary>

Later stages provide little useful information when an earlier quality requirement has already failed.

The execution model is therefore:

```text
Ruff FAIL
→ stop

Ruff PASS
→ mypy

mypy FAIL
→ stop

mypy PASS
→ pytest
```

This also gives the runner a clear process-level contract:

```text
all checks pass
→ exit code 0

any check fails
→ non-zero exit code
```

The same behavior can later be reproduced by CI.

</details>

<details>

<summary><strong>Why does the gate run the complete pytest suite?</strong></summary>

The quality gate represents final local automated validation.

Therefore it includes PostgreSQL integration tests rather than silently using:

```bash
pytest -m "not integration"
```

The faster test subset remains useful during implementation, but a complete quality pass also verifies the real persistence boundary.

This distinction keeps:

```text
fast development feedback
```

separate from:

```text
complete local verification
```

</details>

<details>

<summary><strong>Why doesn't the quality script start PostgreSQL?</strong></summary>

The quality runner validates code; it does not provision infrastructure.

Its responsibility is:

```text
consume prepared environment
        ↓
execute quality checks
```

It does not manage:

* environment creation;
* PostgreSQL lifecycle;
* containers;
* runtime configuration;
* secrets.

Containerized development and automated infrastructure provisioning belong to the Docker and CI phases.

</details>

<details>

<summary><strong>Why is mypy limited to production code?</strong></summary>

mypy analyzes:

```text
src/
```

Production code benefits strongly from static contracts across architectural boundaries such as:

* Domain;
* Application;
* Ports and Protocols;
* repositories;
* asynchronous interfaces;
* Discord adapters;
* persistence;
* lifecycle and recovery components.

The test suite contains substantially more dynamic constructs:

* fixtures;
* fakes;
* `MagicMock`;
* `AsyncMock`;
* test factories;
* Discord interaction doubles.

At the current project scale, Ruff and pytest provide the required protection for test code without introducing additional typing complexity.

The resulting policy is:

```text
Production code
→ Ruff + mypy + pytest

Test code
→ Ruff + pytest
```

</details>

<details>

<summary><strong>Why isn't mypy strict mode enabled?</strong></summary>

The project uses an explicit mypy policy rather than enabling `strict = true` as a single preset.

The configuration includes checks selected for the current codebase, such as typed definitions, typed generic collections, return-value analysis, and detection of stale ignores or redundant casts.

This makes the static-analysis contract explicit and prevents its meaning from depending entirely on the evolving contents of a predefined strict-mode bundle.

The objective is not to obtain a particular mypy label.

The objective is to maintain a static typing policy whose individual guarantees are understood.

</details>

<details>

<summary><strong>Why are global typing ignores avoided?</strong></summary>

Typing errors are normally resolved by correcting the underlying contract or control flow.

The following are therefore not used as generic solutions:

```text
Any everywhere
ignore_errors
global ignore_missing_imports
cast(...) without a runtime guarantee
unqualified # type: ignore
```

When a third-party boundary requires an exception, it remains localized to the narrowest practical scope.

Rule-specific ignores are preferred:

```python
value = external_call()  # type: ignore[arg-type]
```

over:

```python
value = external_call()  # type: ignore
```

This prevents isolated typing limitations from weakening static guarantees across the entire project.

</details>

<details>

<summary><strong>Why use SQLAlchemy 2 native typing?</strong></summary>

The persistence layer uses SQLAlchemy 2's native typing model.

ORM definitions use modern annotations such as:

```python
Mapped[int]
Mapped[str]
Mapped[list[...]]
```

Database boundaries and asynchronous session factories are also explicitly typed where applicable.

The project does not rely on:

```text
sqlalchemy.ext.mypy.plugin
legacy SQLAlchemy typing stubs
```

This keeps persistence typing aligned with the SQLAlchemy 2 model already used by the application instead of introducing a separate legacy typing layer.

</details>

<details>

<summary><strong>Why isn't 100% coverage required?</strong></summary>

A coverage percentage does not demonstrate that important behavior has been tested.

The project therefore treats coverage as a **diagnostic signal**, not as the objective of the test suite.

Testing prioritizes behavior such as:

* Domain invariants;
* Application workflows;
* state transitions;
* concurrency;
* PostgreSQL persistence;
* database constraints;
* Discord adapter behavior;
* recovery;
* error handling;
* operationally critical flows.

Tests are not added solely to execute:

* imports;
* constants;
* trivial glue;
* implementation details;
* unreachable defensive paths.

The **90% baseline** records the coverage reached during the v2.0.0 quality phase. It is not a permanent numerical target.

</details>

<details>

<summary><strong>Why are Ruff suppressions kept narrow?</strong></summary>

Lint violations are corrected at their source whenever possible.

Suppressions are reserved for intentional patterns where the rule does not represent a defect.

Generic suppression:

```python
# noqa
```

is avoided.

A rule-specific exception is preferred:

```python
# noqa: F401
```

This keeps exceptions auditable and prevents unrelated lint violations from being hidden.

</details>

<details>

<summary><strong>Why doesn't the quality phase add GitHub Actions?</strong></summary>

The local quality policy and its CI automation are treated as separate concerns.

This phase establishes the contract:

```text
ruff check .
mypy src/
pytest
```

The CI phase will automate that existing contract.

The relationship is:

```text
Quality policy
     │
     ├── Local
     │    └── scripts/quality.py
     │
     └── CI
          └── GitHub Actions
```

This avoids defining one quality standard locally and another inside CI.

</details>

---

# Quality Gate Result

A successful execution of:

```bash
python scripts/quality.py
```

produces the following technical state:

```text
Ruff PASS
    │
    ▼
mypy PASS
    │
    ▼
pytest PASS
    │
    ▼
QUALITY PASS
```

For changes involving real Discord behavior, controlled smoke validation provides the additional integration verification described in `docs/testing.md`.

The same quality contract is intended to be automated later through GitHub Actions.
