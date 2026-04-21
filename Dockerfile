FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.10.9 /uv /uvx /bin/

ENV UV_COMPILE_BYTE=1

ENV UV_LINK_MODE=copy

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

COPY ./pyproject.toml ./uv.lock ./.python-version /app/

FROM base AS prod

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY ./src /app/src
COPY ./migrations /app/migrations
COPY ./alembic.ini /app/alembic.ini
COPY ./env.py /app/env.py

CMD ["uv", "run", "fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS dev

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

COPY . /app

CMD ["uv", "run", "fastapi", "dev", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]