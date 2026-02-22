"""Zenn auto-publisher — reads schedule.json, sets published: true for due articles.

Run daily via launchd at 07:00 JST.
Only publishes articles whose zenn_date <= today and aren't yet published.

Usage:
    python zenn_publish.py              # Publish due articles
    python zenn_publish.py --dry-run    # Preview without changing files
    python zenn_publish.py --status     # Show Zenn publish status
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEDULE_PATH = SCRIPT_DIR / "schedule.json"
LOG_PATH = SCRIPT_DIR / "zenn_publish.log"

logger = logging.getLogger(__name__)


def _setup_logging() -> None:
    if logger.handlers:
        return
    fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setFormatter(fmt)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)


def load_schedule() -> dict[str, Any]:
    try:
        return json.loads(SCHEDULE_PATH.read_text())
    except FileNotFoundError:
        logger.error("Schedule file not found: %s", SCHEDULE_PATH)
        raise SystemExit(1)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in schedule file: %s", e)
        raise SystemExit(1)


def save_schedule(schedule: dict[str, Any]) -> None:
    SCHEDULE_PATH.write_text(json.dumps(schedule, indent=2, ensure_ascii=False) + "\n")


def _validate_article_path(file_path: str) -> Path | None:
    article_path = (REPO_ROOT / file_path).resolve()
    if not article_path.is_relative_to(REPO_ROOT.resolve()):
        logger.error("Path traversal detected: %s", file_path)
        return None
    if not article_path.exists():
        logger.warning("File not found: %s", file_path)
        return None
    return article_path


def _is_published(article_path: Path) -> bool:
    """Check if article frontmatter already has published: true."""
    content = article_path.read_text()
    m = re.search(r"^published:\s*(true|false)", content, re.MULTILINE)
    return m is not None and m.group(1) == "true"


def _set_published(article_path: Path, *, dry_run: bool) -> bool:
    """Set published: true in frontmatter. Returns True if a change was made."""
    content = article_path.read_text()
    new_content, n = re.subn(
        r"^(published:\s*)false",
        r"\1true",
        content,
        flags=re.MULTILINE,
    )
    if n == 0:
        return False
    if not dry_run:
        article_path.write_text(new_content)
    return True


def _git_add_commit_push(file_paths: list[str], commit_msg: str, *, dry_run: bool) -> bool:
    """Stage files, commit, and push. Returns True on success."""
    if dry_run:
        logger.info("  [DRY-RUN] Would commit %d file(s) and push.", len(file_paths))
        return True
    try:
        for fp in file_paths:
            subprocess.run(
                ["git", "-C", str(REPO_ROOT), "add", fp],
                check=True, capture_output=True, text=True,
            )
        subprocess.run(
            ["git", "-C", str(REPO_ROOT), "commit", "-m", commit_msg],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "-C", str(REPO_ROOT), "push", "origin", "main"],
            check=True, capture_output=True, text=True,
        )
        logger.info("  git push OK")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Git error: %s", (e.stderr or e.stdout or "").strip())
        return False


def show_status(schedule: dict[str, Any]) -> None:
    today = date.today()
    logger.info("Today: %s", today)
    logger.info("%-12s %-45s %-15s %s", "zenn_date", "File", "zenn_published", "Status")
    logger.info("-" * 90)
    for entry in schedule["articles"]:
        zenn_date_str = entry.get("zenn_date")
        if not zenn_date_str:
            continue
        article_path = _validate_article_path(entry["file"])
        published_in_file = _is_published(article_path) if article_path else False
        tracked = entry.get("zenn_published", False)
        zenn_date = date.fromisoformat(zenn_date_str)
        if tracked or published_in_file:
            status = "published"
        elif zenn_date <= today:
            status = "DUE"
        else:
            status = "scheduled"
        logger.info(
            "%-12s %-45s %-15s %s",
            zenn_date_str, entry["file"], str(tracked or published_in_file), status,
        )


def publish_due(schedule: dict[str, Any], *, dry_run: bool = False) -> int:
    today = date.today()
    updated_articles: list[dict[str, Any]] = []
    files_to_push: list[str] = []
    tracking_updated = False
    published_count = 0
    errors = 0

    for entry in schedule["articles"]:
        zenn_date_str = entry.get("zenn_date")
        if not zenn_date_str or entry.get("zenn_published"):
            updated_articles.append(entry)
            continue

        zenn_date = date.fromisoformat(zenn_date_str)
        if zenn_date > today:
            updated_articles.append(entry)
            continue

        article_path = _validate_article_path(entry["file"])
        if article_path is None:
            updated_articles.append(entry)
            errors += 1
            continue

        if _is_published(article_path):
            # Already published in file — just sync the tracking flag
            logger.info("Already published (marking tracked): %s", entry["file"])
            updated_articles.append({**entry, "zenn_published": True})
            tracking_updated = True
            continue

        logger.info("Publishing: %s (zenn_date=%s)", entry["file"], zenn_date_str)
        changed = _set_published(article_path, dry_run=dry_run)
        if changed:
            files_to_push.append(entry["file"])
            published_count += 1
            updated_articles.append({**entry, "zenn_published": True})
        else:
            logger.warning("Could not set published: true in %s", entry["file"])
            updated_articles.append(entry)
            errors += 1

    # Commit + push all changed files in a single git operation
    if files_to_push:
        commit_msg = f"feat: Zenn 自動公開 ({today})"
        success = _git_add_commit_push(files_to_push, commit_msg, dry_run=dry_run)
        if not success:
            errors += 1
            published_count = 0  # Don't count as published if push failed
        elif not dry_run:
            save_schedule({**schedule, "articles": updated_articles})
    elif tracking_updated and not dry_run:
        # No new files to push, but tracking flags need saving
        save_schedule({**schedule, "articles": updated_articles})

    if not files_to_push and not tracking_updated and not errors:
        logger.info("Nothing due today.")

    if published_count or errors:
        logger.info("%d article(s) published, %d error(s).", published_count, errors)

    # Run cross-post for articles due today (after Zenn publish)
    try:
        import scheduled_publish as _sp
        _sp._setup_logging()
        logger.info("=== Cross-post ===")
        updated_schedule = load_schedule()
        crosspost_result = _sp.publish_due(updated_schedule, dry_run=dry_run)
        if crosspost_result != 0:
            errors += 1
    except ImportError as e:
        logger.warning("scheduled_publish not available (venv required): %s", e)
    except Exception as e:
        logger.error("Cross-post failed with unexpected error: %s", e)
        errors += 1

    return 1 if errors > 0 else 0


def main() -> int:
    _setup_logging()
    parser = argparse.ArgumentParser(description="Zenn auto-publisher")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changing files")
    parser.add_argument("--status", action="store_true", help="Show Zenn publish status")
    args = parser.parse_args()

    schedule = load_schedule()

    if args.status:
        show_status(schedule)
        return 0

    return publish_due(schedule, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
