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
import logging
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

from _schedule_utils import (
    REPO_ROOT,
    load_schedule,
    now_jst,
    save_schedule,
    setup_logging,
    validate_article_path,
)

SCRIPT_DIR = Path(__file__).parent
LOG_PATH = SCRIPT_DIR / "zenn_publish.log"

DEFAULT_PUBLISH_HOUR = 7  # launchd scheduled publish time (JST)

logger = logging.getLogger(__name__)


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
                ["git", "add", fp],
                cwd=REPO_ROOT, check=True, capture_output=True, text=True,
            )
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=REPO_ROOT, check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=REPO_ROOT, check=True, capture_output=True, text=True, timeout=60,
        )
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=REPO_ROOT, check=True, capture_output=True, text=True, timeout=60,
        )
        logger.info("  git push OK")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Git error: %s", (e.stderr or e.stdout or "").strip())
        return False
    except subprocess.TimeoutExpired:
        logger.error("Git operation timed out")
        return False


def _get_actual_publish_time(file_path: str, zenn_date: str | None = None) -> str:
    """Get the actual Zenn publish time via fallback chain.

    1. git log: commit time when 'published: true' was set
    2. zenn_date at 07:00 (scheduled publish time)
    3. now_jst() (last resort)
    """
    try:
        result = subprocess.run(
            [
                "git", "log", "-1", "--format=%aI",
                "-S", "published: true", "--", file_path,
            ],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10,
        )
        timestamp = result.stdout.strip()
        if timestamp:
            return timestamp
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass

    if zenn_date:
        return f"{zenn_date}T{DEFAULT_PUBLISH_HOUR:02d}:00:00"

    return now_jst().isoformat()


def show_status(schedule: dict[str, Any]) -> None:
    today = date.today()
    logger.info("Today: %s", today)
    logger.info("%-12s %-45s %-15s %s", "zenn_date", "File", "zenn_published", "Status")
    logger.info("-" * 90)
    for entry in schedule["articles"]:
        zenn_date_str = entry.get("zenn_date")
        if not zenn_date_str:
            continue
        article_path = validate_article_path(entry["file"])
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


def _already_published_today(articles: list[dict[str, Any]]) -> bool:
    """Check if any article was already published today (via zenn_published_at)."""
    today_str = date.today().isoformat()
    return any(
        entry.get("zenn_published_at", "").startswith(today_str)
        for entry in articles
    )


def publish_due(schedule: dict[str, Any], *, dry_run: bool = False) -> int:
    today = date.today()
    updated_articles: list[dict[str, Any]] = []
    files_to_push: list[str] = []
    tracking_updated = False
    published_count = 0
    errors = 0

    # --- 1-article-per-day guard ---
    # Check if we already published an article today
    if _already_published_today(schedule["articles"]):
        logger.info("今日は既に1記事公開済み。残りは翌日以降に繰り越し。")
        # Still sync tracking flags for manually-published articles
        # (fall through to the loop below, but skip actual publishing)

    # Collect due entries (zenn_date <= today, not yet published) for sorting
    due_indices: list[int] = []
    for i, entry in enumerate(schedule["articles"]):
        zenn_date_str = entry.get("zenn_date")
        if not zenn_date_str or entry.get("zenn_published"):
            continue
        if date.fromisoformat(zenn_date_str) > today:
            continue
        due_indices.append(i)

    # Sort due entries by zenn_date (oldest first) to pick the one to publish
    due_indices.sort(key=lambda i: schedule["articles"][i]["zenn_date"])

    # Determine which single entry (if any) is eligible for publishing today
    publish_target_index: int | None = None
    if not _already_published_today(schedule["articles"]) and due_indices:
        publish_target_index = due_indices[0]
        deferred_count = len(due_indices) - 1
        if deferred_count > 0:
            logger.info(
                "1日1記事制限: 最も古い1件を公開、残り%d件は翌日以降に繰り越し",
                deferred_count,
            )

    for i, entry in enumerate(schedule["articles"]):
        zenn_date_str = entry.get("zenn_date")
        if not zenn_date_str or entry.get("zenn_published"):
            updated_articles.append(entry)
            continue

        zenn_date = date.fromisoformat(zenn_date_str)
        if zenn_date > today:
            updated_articles.append(entry)
            continue

        article_path = validate_article_path(entry["file"])
        if article_path is None:
            updated_articles.append(entry)
            errors += 1
            continue

        if _is_published(article_path):
            # Already published in file — just sync the tracking flag
            logger.info("Already published (marking tracked): %s", entry["file"])
            # Record timestamp if missing (for manual publish scenario)
            updates: dict[str, Any] = {"zenn_published": True}
            if not entry.get("zenn_published_at"):
                updates["zenn_published_at"] = _get_actual_publish_time(
                    entry["file"], entry.get("zenn_date"),
                )
                logger.info("  Recorded zenn_published_at: %s", updates["zenn_published_at"])
            updated_articles.append({**entry, **updates})
            tracking_updated = True
            continue

        # Only publish the single target entry per day
        if i != publish_target_index:
            updated_articles.append(entry)
            continue

        logger.info("Publishing: %s (zenn_date=%s)", entry["file"], zenn_date_str)
        changed = _set_published(article_path, dry_run=dry_run)
        if changed:
            files_to_push.append(entry["file"])
            published_count += 1
            # Record timestamp for cross-post delay calculation
            updated_articles.append({
                **entry,
                "zenn_published": True,
                "zenn_published_at": now_jst().isoformat(),
            })
        else:
            logger.warning("Could not set published: true in %s", entry["file"])
            updated_articles.append(entry)
            errors += 1

    # Commit + push all changed files in a single git operation
    if files_to_push:
        commit_msg = f"feat: Zenn 自動公開 ({today})"
        push_success = _git_add_commit_push(files_to_push, commit_msg, dry_run=dry_run)
        if not push_success:
            errors += 1
            logger.warning("Git push failed. Frontmatter changed locally but not deployed.")

    # Save tracking state regardless of push success —
    # schedule.json records *what happened*, not *what was deployed*.
    if (files_to_push or tracking_updated) and not dry_run:
        save_schedule({**schedule, "articles": updated_articles})

    if not files_to_push and not tracking_updated and not errors:
        logger.info("Nothing due today.")

    if published_count or errors:
        logger.info("%d article(s) published, %d error(s).", published_count, errors)

    return 1 if errors > 0 else 0


def main() -> int:
    setup_logging(logger, LOG_PATH)
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
