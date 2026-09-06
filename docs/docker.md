# Docker

This project can run locally using Docker Compose without requiring Python or PostgreSQL to be installed on the host.

The Docker environment contains three services:

```text
Docker Compose
├── postgres
├── migrate
└── bot
```

* `postgres` runs the PostgreSQL database.
* `migrate` runs `alembic upgrade head` and exits after the database schema is up to date.
* `bot` starts only after PostgreSQL is healthy and migrations complete successfully.

## Requirements

* Docker
* Docker Compose
* A valid Discord bot token available as `DISCORD_TOKEN`

No local Python environment or PostgreSQL installation is required to run the containerized application.

## Start the application

Build and start the complete environment:

```bash
docker compose up --build
```

To run it in the background:

```bash
docker compose up -d --build
```

Compose will automatically:

```text
start PostgreSQL
        ↓
wait until PostgreSQL is healthy
        ↓
run Alembic migrations
        ↓
start the Discord bot
```

## Check service status

```bash
docker compose ps -a
```

The expected state is conceptually:

```text
postgres    running / healthy
migrate     exited (0)
bot         running
```

`migrate` finishing with exit code `0` is expected. It is a one-shot service and does not remain running after migrations complete.

## Logs

Show all service logs:

```bash
docker compose logs
```

Follow bot logs:

```bash
docker compose logs -f bot
```

PostgreSQL logs:

```bash
docker compose logs postgres
```

Migration logs:

```bash
docker compose logs migrate
```

## Stop the environment

```bash
docker compose down
```

This removes the containers and Compose network but preserves the PostgreSQL volume.

As a result, persisted games and database state remain available the next time the environment starts.

## Restart

After stopping the environment:

```bash
docker compose up
```

The existing PostgreSQL volume is reused.

Alembic runs again against the persisted database. If the schema is already at the latest revision, the migration step completes successfully without recreating the database.

The bot then performs its normal startup and recovery process.

## Reset the local database

To remove the PostgreSQL volume together with the containers:

```bash
docker compose down -v
```

> **Warning:** this permanently deletes the local Docker PostgreSQL data for this Compose project.

The next:

```bash
docker compose up
```

starts with an empty PostgreSQL database and rebuilds the schema exclusively through Alembic migrations.

## Access PostgreSQL

A PostgreSQL client does not need to be installed on the host.

Open `psql` inside the database container:

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Useful commands inside `psql`:

```text
\dt
```

Display the current Alembic revision:

```sql
SELECT * FROM alembic_version;
```

Exit:

```text
\q
```

## Clean rebuild

To verify the application from a clean Docker build:

```bash
docker compose down -v
docker compose build --no-cache --pull
docker compose up
```

This verifies that the environment does not depend on an existing application image or PostgreSQL volume.

## Configuration

Secrets are provided at runtime and are not stored in the Docker image.

At minimum, the bot requires a valid:

```text
DISCORD_TOKEN
```

Database connectivity between containers uses Docker Compose service discovery. The application connects to the PostgreSQL service using the service hostname rather than `localhost`.

Runtime configuration will be documented separately as configuration management is expanded.

## Notes

The bot does not expose an HTTP service and therefore does not publish an application port.

PostgreSQL is intended for communication between Compose services and does not need to be exposed to the host for normal operation.

The application image runs the bot as a non-root user.

The same application image is used by both the `bot` and `migrate` services, ensuring that the migrations executed by Compose correspond to the application version being started.
