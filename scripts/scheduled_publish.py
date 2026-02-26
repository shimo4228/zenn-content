"""Scheduled cross-post publisher — reads schedule.json, posts due articles.

Run daily via launchd at 18:00 JST (09:00 UTC).
Only publishes articles whose date <= today and haven't been posted yet.

Usage:
    python scheduled_publish.py              # Post due articles
    python scheduled_publish.py --dry-run    # Preview without posting
    python scheduled_publish.py --status     # Show schedule status
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any, NamedTuple

from publish import (
    PublishResult,
    _load_env,
    convert_to_devto,
    convert_to_hashnode,
    convert_to_qiita,
    find_devto_article_by_title,
    find_hashnode_post_by_title,
    find_qiita_item_by_title,
    parse_zenn_article,
    publish_to_devto,
    publish_to_hashnode,
    publish_to_qiita,
    update_on_devto,
    update_on_hashnode,
    update_on_qiita,
)

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEDULE_PATH = SCRIPT_DIR / "schedule.json"
LOG_PATH = SCRIPT_DIR / "publish.log"

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


def _is_entry_done(entry: dict[str, Any]) -> bool:
    """Check if all configured platforms for an entry are done.
    
    Platform value semantics:
    - None / "" / "pending" -> not done (needs processing)
    - "n/a" -> not applicable (treated as done)
    - URL string -> done (successfully posted)
    """
    def _is_platform_done(value: str | None) -> bool:
        if value is None or value == "":
            return False  # Not posted yet
        if value == "n/a":
            return True   # Platform not applicable for this entry
        if value == "pending":
            return False  # Scheduled but not executed
        return True  # Has URL or other truthy value = done
    
    devto_done = _is_platform_done(entry.get("devto"))
    hashnode_done = _is_platform_done(entry.get("hashnode"))
    qiita_done = _is_platform_done(entry.get("qiita")) if "qiita" in entry else True
    return devto_done and hashnode_done and qiita_done


def show_status(schedule: dict[str, Any]) -> None:
    today = date.today()
    logger.info("Today: %s", today)
    logger.info(
        "%-12s %-45s %-10s %-10s %-10s %s",
        "Date", "File", "Qiita", "Dev.to", "Hashnode", "Status",
    )
    logger.info("-" * 105)
    for entry in schedule["articles"]:
        d = entry["date"]
        f = entry["file"]
        
        # Helper to format platform status for display
        def _fmt_platform(value: str | None, has_field: bool) -> str:
            if not has_field:
                return "n/a"
            if value == "n/a":
                return "n/a"
            if value in (None, "", "pending"):
                return "-"
            return "done"
        
        qiita = _fmt_platform(entry.get("qiita"), "qiita" in entry)
        devto = _fmt_platform(entry.get("devto"), "devto" in entry)
        hashnode = _fmt_platform(entry.get("hashnode"), "hashnode" in entry)
        
        entry_date = date.fromisoformat(d)
        if _is_entry_done(entry):
            status = "posted"
        elif entry_date <= today:
            status = "DUE"
        else:
            status = "scheduled"
        logger.info(
            "%-12s %-45s %-10s %-10s %-10s %s",
            d, f, qiita, devto, hashnode, status,
        )


def _try_publish(
    platform: str,
    publish_fn: Callable[[], PublishResult],
    *,
    dry_run: bool,
    title: str,
) -> tuple[str | None, bool]:
    """Publish to a platform. Returns (url_or_none, had_error)."""
    if dry_run:
        logger.info("  [DRY-RUN] Would publish to %s: %s", platform, title)
        return None, False
    result = publish_fn()
    if result.success:
        logger.info("  %s OK: %s", platform, result.url)
        return result.url, False
    logger.warning("  %s FAIL: %.200s", platform, result.error)
    return None, True


def _validate_article_path(file_path: str) -> Path | None:
    """Resolve article path and validate it stays within REPO_ROOT."""
    article_path = (REPO_ROOT / file_path).resolve()
    if not article_path.is_relative_to(REPO_ROOT.resolve()):
        logger.error("Path traversal detected: %s", file_path)
        return None
    if not article_path.exists():
        logger.warning("File not found: %s", file_path)
        return None
    return article_path


class _Credentials(NamedTuple):
    qiita_token: str
    devto_key: str
    hashnode_token: str
    hashnode_pub_id: str


def _load_credentials() -> _Credentials | None:
    """Load and validate API credentials from environment."""
    _load_env(SCRIPT_DIR / ".env")

    qiita_token = os.environ.get("QIITA_ACCESS_TOKEN")
    devto_key = os.environ.get("DEVTO_API_KEY")
    hashnode_token = os.environ.get("HASHNODE_API_TOKEN")
    hashnode_pub_id = os.environ.get("HASHNODE_PUBLICATION_ID")

    missing: list[str] = []
    if not devto_key:
        missing.append("DEVTO_API_KEY")
    if not hashnode_token or not hashnode_pub_id:
        missing.append("HASHNODE_API_TOKEN/HASHNODE_PUBLICATION_ID")
    if not qiita_token:
        missing.append("QIITA_ACCESS_TOKEN")
    if missing:
        logger.error("Missing env vars: %s", ", ".join(missing))
        return None

    return _Credentials(
        qiita_token=str(qiita_token),
        devto_key=str(devto_key),
        hashnode_token=str(hashnode_token),
        hashnode_pub_id=str(hashnode_pub_id),
    )


def _process_entry(
    entry: dict[str, Any], creds: _Credentials, *, dry_run: bool,
) -> tuple[dict[str, Any], int]:
    """Process a single schedule entry. Returns (updated_entry, error_count)."""
    article_path = _validate_article_path(entry["file"])
    if article_path is None:
        return entry, 1

    article = parse_zenn_article(article_path)
    canonical = entry["canonical_url"]
    logger.info("Processing: %s (date=%s)", article.title, entry["date"])
    updates: dict[str, Any] = {}
    errors = 0

    if "qiita" in entry and not entry["qiita"]:
        def _qiita_upsert() -> PublishResult:
            payload = convert_to_qiita(article)
            existing_id = find_qiita_item_by_title(article.title, creds.qiita_token)
            if existing_id:
                logger.info("  Qiita: existing article found (%s), updating", existing_id)
                return update_on_qiita(existing_id, payload, creds.qiita_token)
            return publish_to_qiita(payload, creds.qiita_token)
        url, failed = _try_publish(
            "Qiita", _qiita_upsert,
            dry_run=dry_run, title=article.title,
        )
        if url:
            updates["qiita"] = url
        errors += failed

    if not entry["devto"]:
        def _devto_upsert() -> PublishResult:
            payload = convert_to_devto(article, canonical_url=canonical)
            existing_id = find_devto_article_by_title(article.title, creds.devto_key)
            if existing_id:
                logger.info("  Dev.to: existing article found (%s), updating", existing_id)
                return update_on_devto(existing_id, payload, creds.devto_key)
            return publish_to_devto(payload, creds.devto_key)
        url, failed = _try_publish(
            "Dev.to", _devto_upsert,
            dry_run=dry_run, title=article.title,
        )
        if url:
            updates["devto"] = url
        errors += failed

    if not entry["hashnode"]:
        def _hashnode_upsert() -> PublishResult:
            existing_id = find_hashnode_post_by_title(
                article.title, creds.hashnode_pub_id, creds.hashnode_token,
            )
            if existing_id:
                logger.info("  Hashnode: existing post found (%s), updating", existing_id)
                return update_on_hashnode(existing_id, article, creds.hashnode_token)
            payload = convert_to_hashnode(article, creds.hashnode_pub_id, canonical_url=canonical)
            return publish_to_hashnode(payload, creds.hashnode_token)
        url, failed = _try_publish(
            "Hashnode", _hashnode_upsert,
            dry_run=dry_run, title=article.title,
        )
        if url:
            updates["hashnode"] = url
        errors += failed

    return {**entry, **updates} if updates else entry, errors


def _is_dependency_satisfied(entry: dict[str, Any], all_entries: list[dict[str, Any]]) -> tuple[bool, str]:
    """Check if entry's dependency (e.g., JP article for EN translation) is satisfied.
    
    Returns (is_satisfied, reason_message).
    """
    depends_on = entry.get("depends_on")
    if not depends_on:
        return True, ""
    
    # Find the dependency entry
    for dep_entry in all_entries:
        if dep_entry["file"] == depends_on:
            if _is_entry_done(dep_entry):
                return True, ""
            else:
                return False, f"Waiting for dependency: {depends_on}"
    
    # Dependency not found in schedule - assume external/satisfied
    logger.warning("Dependency %s not found in schedule for %s", depends_on, entry["file"])
    return True, ""


def publish_due(schedule: dict[str, Any], *, dry_run: bool = False) -> int:
    creds = _load_credentials()
    if creds is None:
        return 1

    today = date.today()
    posted_count = 0
    errors = 0
    skipped_count = 0
    updated_articles: list[dict[str, Any]] = []

    remaining = list(schedule["articles"])
    for i, entry in enumerate(remaining):
        entry_date = date.fromisoformat(entry["date"])
        if entry_date > today or _is_entry_done(entry):
            updated_articles.append(entry)
            continue
        
        # Check dependency satisfaction (e.g., EN article needs JP article done first)
        dep_satisfied, dep_reason = _is_dependency_satisfied(entry, schedule["articles"])
        if not dep_satisfied:
            logger.info("Skipping %s: %s", entry["file"], dep_reason)
            updated_articles.append(entry)
            skipped_count += 1
            continue

        updated_entry, entry_errors = _process_entry(entry, creds, dry_run=dry_run)
        updated_articles.append(updated_entry)
        errors += entry_errors
        posted_count += 1

        # Persist immediately after each entry so a mid-run process kill
        # does not lose progress for already-completed entries.
        if updated_entry is not entry and not dry_run:
            all_articles = updated_articles + remaining[i + 1:]
            save_schedule({**schedule, "articles": all_articles})

    if posted_count == 0 and skipped_count == 0:
        logger.info("Nothing due today.")
    elif not dry_run:
        save_schedule({**schedule, "articles": updated_articles})
        logger.info(
            "Schedule updated. %d article(s) processed, %d skipped (dependencies), %d error(s).",
            posted_count, skipped_count, errors,
        )
    else:
        logger.info("[DRY-RUN] %d article(s) would be posted, %d skipped (dependencies).", 
                    posted_count, skipped_count)

    return 1 if errors > 0 else 0


def main() -> int:
    _setup_logging()
    parser = argparse.ArgumentParser(description="Scheduled cross-post publisher")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without posting",
    )
    parser.add_argument("--status", action="store_true", help="Show schedule status")
    args = parser.parse_args()

    schedule = load_schedule()

    if args.status:
        show_status(schedule)
        return 0

    return publish_due(schedule, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
