#!/bin/sh
set -e

export DATABASE_URL="postgresql+asyncpg://${POSTGRES_AGENT_USER}:${POSTGRES_AGENT_PASSWORD}@postgresql-agent:5432/${POSTGRES_AGENT_DB}"

exec uvicorn app.main:app --host 0.0.0.0 --port 8001
