"""Shared utilities for scheduled publishing scripts.

Extracted from scheduled_publish.py and zenn_publish.py to eliminate
duplication of schedule I/O, path validation, and logging setup.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEDULE_PATH = SCRIPT_DIR / "schedule.json"


def setup_logging(logger: logging.Logger, log_path: Path) -> None:
    """Configure file + stream logging for a module logger."""
    if logger.handlers:
        return
    fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(fmt)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)


def load_schedule(schedule_path: Path = SCHEDULE_PATH) -> dict[str, Any]:
    """Load schedule.json, raising SystemExit on errors."""
    logger = logging.getLogger(__name__)
    try:
        return json.loads(schedule_path.read_text())
    except FileNotFoundError:
        logger.error("Schedule file not found: %s", schedule_path)
        raise SystemExit(1)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in schedule file: %s", e)
        raise SystemExit(1)


def save_schedule(
    schedule: dict[str, Any], schedule_path: Path = SCHEDULE_PATH,
) -> None:
    """Write schedule dict back to JSON file."""
    schedule_path.write_text(
        json.dumps(schedule, indent=2, ensure_ascii=False) + "\n",
    )


def now_jst() -> datetime:
    """Return the current time in JST (Asia/Tokyo)."""
    return datetime.now(tz=JST)


def validate_article_path(
    file_path: str, repo_root: Path = REPO_ROOT,
) -> Path | None:
    """Resolve article path and validate it stays within repo root."""
    logger = logging.getLogger(__name__)
    article_path = (repo_root / file_path).resolve()
    if not article_path.is_relative_to(repo_root.resolve()):
        logger.error("Path traversal detected: %s", file_path)
        return None
    if not article_path.exists():
        logger.warning("File not found: %s", file_path)
        return None
    return article_path
