# syntax=docker/dockerfile:1

FROM python:3.12.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN groupadd --system app \
    && useradd \
        --system \
        --gid app \
        --create-home \
        app

COPY requirements.txt ./

RUN python -m pip install \
    --no-cache-dir \
    -r requirements.txt

COPY --chown=app:app src ./src
COPY --chown=app:app data ./data
COPY --chown=app:app migrations ./migrations
COPY --chown=app:app alembic.ini ./

USER app

CMD ["python", "-m", "impostor_bot.main"]