"""Shared test configuration for the data-pipeline unit tests."""

import sys
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = PIPELINE_DIR / "app"

for path in (str(PIPELINE_DIR), str(APP_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)
