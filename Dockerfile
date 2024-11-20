FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock /app/

RUN mkdir /app/src

COPY broker/ /app/src/broker/
COPY common/ /app/src/common/
COPY watcher/ /app/src/watcher/
COPY reviewer/ /app/src/reviewer/

RUN uv pip install --system .

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
