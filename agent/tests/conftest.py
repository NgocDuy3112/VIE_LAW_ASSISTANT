"""Shared test configuration for the agent service unit tests.

Sets up sys.path so that both import styles used by the app work:
- ``app.*``  (requires ``agent/`` on sys.path)
- ``modules.*``, ``db.*``, ``graph.*``, ``config`` (requires ``agent/app/`` on sys.path)

Also provides default environment variables required by ``app.config.Settings``
before any application module is imported.
"""

import os
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = AGENT_DIR / "app"

# Required settings (app.config has no defaults for these)
os.environ.setdefault("LLM_BASE_URL", "http://localhost:11434/v1")
os.environ.setdefault("LLM_MODEL", "test-model")
os.environ.setdefault("JWT_SECRET", "test-secret-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("POSTGRES_AGENT_USER", "postgres")
os.environ.setdefault("POSTGRES_AGENT_PASSWORD", "postgres")
os.environ.setdefault("POSTGRES_AGENT_DB", "agent_test")
os.environ.setdefault("POSTGRES_AGENT_URL", "postgresql+asyncpg://postgres:postgres@localhost:5433/agent_test")
os.environ.setdefault("ELASTICSEARCH_URL", "http://localhost:9200")
os.environ.setdefault("ELASTICSEARCH_INDEX", "documents_test")
os.environ.setdefault("EMBEDDING_URL", "http://localhost:8010")
os.environ.setdefault("EMBEDDING_DIMENSION", "768")
os.environ.setdefault("RATE_LIMIT_URI", "redis://localhost:6379/0")
os.environ.setdefault("NUM_REQUESTS_PER_MINUTE", "60")
os.environ.setdefault("REQUEST_TIMEOUT_SECONDS", "30")

for path in (str(AGENT_DIR), str(APP_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)
