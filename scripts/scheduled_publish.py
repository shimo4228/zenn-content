"""Scheduled publisher — reads schedule.json, posts due articles.

Run daily via launchd at 07:00 JST (Zenn) and 09:00 JST (Dev.to).
- JP articles: Zenn only (frontmatter + git push)
- EN articles: Dev.to only (API cross-post)

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
from datetime import date, datetime
from pathlib import Path
from typing import Any

import frontmatter

from zenn_publish import (
    _git_add_commit_push,
)
from publish import (
    PublishResult,
    _load_env,
    convert_to_devto,
    find_devto_article_by_title,
    parse_zenn_article,
    publish_to_devto,
    update_on_devto,
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


def _needs_posting(value: str | None) -> bool:
    """Check if a platform value indicates posting is needed."""
    return value is None or value == "" or value == "pending"


def _is_entry_done(entry: dict[str, Any]) -> bool:
    """Check if an entry is fully processed.

    - EN articles (articles-en/ path): done when devto has a URL
    - JP articles: done when zenn_published is True
    - Legacy entries (no zenn_published, not EN): treated as done
    """
    is_en = entry.get("file", "").startswith("articles-en/")
    if is_en:
        value = entry.get("devto")
        return value is not None and value != "" and value != "pending"
    return entry.get("zenn_published", True) is True


# Minimum delay (in minutes) before cross-posting after Zenn publish
MIN_CROSSPOST_DELAY_MINUTES = 15


def _should_skip_due_to_recent_zenn_publish(entry: dict[str, Any]) -> bool:
    """Check if entry should be skipped because it was published to Zenn too recently.

    This prevents cross-posting before Zenn deployment is complete.
    Zenn deployment can take 5-30 minutes after git push.
    """
    if not entry.get("zenn_published"):
        return False

    zenn_published_at = entry.get("zenn_published_at")
    if not zenn_published_at:
        return False

    try:
        publish_time = datetime.fromisoformat(zenn_published_at)
        elapsed = datetime.now() - publish_time
        elapsed_minutes = elapsed.total_seconds() / 60

        if elapsed_minutes < MIN_CROSSPOST_DELAY_MINUTES:
            logger.info(
                "Skipping %s: Zenn published %d minutes ago (need %d min delay)",
                entry.get("file", "unknown"),
                int(elapsed_minutes),
                MIN_CROSSPOST_DELAY_MINUTES,
            )
            return True

        return False
    except (ValueError, TypeError):
        logger.warning(
            "Invalid zenn_published_at format for %s: %s",
            entry.get("file", "unknown"),
            zenn_published_at,
        )
        return False


def show_status(schedule: dict[str, Any]) -> None:
    today = date.today()
    logger.info("Today: %s", today)
    logger.info(
        "%-12s %-45s %-6s %-10s %s",
        "Date", "File", "Zenn", "Dev.to", "Status",
    )
    logger.info("-" * 90)
    for entry in schedule["articles"]:
        d = entry["date"]
        f = entry["file"]

        # Zenn status
        if "zenn_published" not in entry:
            zenn = "n/a"
        elif entry["zenn_published"] is True:
            zenn = "done"
        else:
            zenn = "-"

        # Dev.to status
        if "devto" not in entry:
            devto = "n/a"
        elif entry["devto"] in (None, "", "pending"):
            devto = "-"
        else:
            devto = "done"

        entry_date = date.fromisoformat(d)
        if _is_entry_done(entry):
            status = "posted"
        elif entry_date <= today:
            status = "DUE"
        else:
            status = "scheduled"
        logger.info(
            "%-12s %-45s %-6s %-10s %s",
            d, f, zenn, devto, status,
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


# ---------------------------------------------------------------------------
# Zenn publishing (frontmatter + git push)
# ---------------------------------------------------------------------------


def _publish_zenn_article(article_path: Path, *, dry_run: bool) -> bool:
    """Set published: true in frontmatter and git push.

    Returns True on success, False on error.
    """
    post = frontmatter.load(str(article_path))
    if post.metadata.get("published") is True:
        logger.info("  Zenn: already published (frontmatter)")
        return True

    if dry_run:
        logger.info("  [DRY-RUN] Would set published: true in %s", article_path.name)
        return True

    post.metadata["published"] = True
    article_path.write_text(frontmatter.dumps(post) + "\n")
    logger.info("  Zenn: set published: true in %s", article_path.name)

    rel_path = str(article_path.relative_to(REPO_ROOT))
    commit_msg = f"feat: Zenn 自動公開 ({date.today()})"
    return _git_add_commit_push([rel_path], commit_msg, dry_run=False)


def _process_zenn_entries(
    schedule: dict[str, Any], *, dry_run: bool,
) -> tuple[dict[str, Any], int, int]:
    """Publish due Zenn articles (max 1 per day). Returns (updated_schedule, publish_count, error_count)."""
    today = date.today()
    today_str = today.isoformat()
    updated_articles = list(schedule["articles"])
    published = 0
    errors = 0

    # 1-article-per-day guard: check if already published today
    already_published_today = any(
        entry.get("zenn_published_at", "").startswith(today_str)
        for entry in updated_articles
    )
    if already_published_today:
        logger.info("今日は既に1記事公開済み。残りは翌日以降に繰り越し。")
        return {**schedule, "articles": updated_articles}, 0, 0

    # Collect due entries and sort by zenn_date (oldest first)
    due_indices: list[int] = []
    for i, entry in enumerate(updated_articles):
        zenn_date_str = entry.get("zenn_date")
        if not zenn_date_str:
            continue
        if entry.get("zenn_published") is not False:
            continue
        if date.fromisoformat(zenn_date_str) > today:
            continue
        due_indices.append(i)

    if not due_indices:
        return {**schedule, "articles": updated_articles}, 0, 0

    due_indices.sort(key=lambda idx: updated_articles[idx]["zenn_date"])
    deferred_count = len(due_indices) - 1
    if deferred_count > 0:
        logger.info(
            "1日1記事制限: 最も古い1件を公開、残り%d件は翌日以降に繰り越し",
            deferred_count,
        )

    # Publish only the oldest due entry
    target_i = due_indices[0]
    entry = updated_articles[target_i]

    article_path = _validate_article_path(entry["file"])
    if article_path is None:
        errors += 1
    else:
        logger.info("Zenn publishing: %s", entry["file"])
        if _publish_zenn_article(article_path, dry_run=dry_run):
            if not dry_run:
                updated_articles[target_i] = {
                    **entry,
                    "zenn_published": True,
                    "zenn_published_at": datetime.now().isoformat(),
                }
            published += 1
        else:
            errors += 1

    updated_schedule = {**schedule, "articles": updated_articles}
    if published > 0 and not dry_run:
        save_schedule(updated_schedule)
    return updated_schedule, published, errors


def _load_devto_key() -> str | None:
    """Load Dev.to API key from environment."""
    _load_env(SCRIPT_DIR / ".env")
    devto_key = os.environ.get("DEVTO_API_KEY")
    if not devto_key:
        logger.error("Missing env var: DEVTO_API_KEY")
        return None
    return devto_key


def _process_entry(
    entry: dict[str, Any], devto_key: str, *, dry_run: bool,
) -> tuple[dict[str, Any], int]:
    """Process a single EN schedule entry for Dev.to. Returns (updated_entry, error_count)."""
    article_path = _validate_article_path(entry["file"])
    if article_path is None:
        return entry, 1

    article = parse_zenn_article(article_path)
    logger.info("Processing: %s (date=%s)", article.title, entry["date"])
    errors = 0

    if _needs_posting(entry.get("devto")):
        devto_tags = entry.get("devto_tags")
        cover_image = entry.get("cover_image")
        def _devto_upsert() -> PublishResult:
            payload = convert_to_devto(
                article,
                devto_tags_override=devto_tags,
                cover_image_url=cover_image,
            )
            existing_id = find_devto_article_by_title(article.title, devto_key)
            if existing_id:
                logger.info("  Dev.to: existing article found (%s), updating", existing_id)
                return update_on_devto(existing_id, payload, devto_key)
            return publish_to_devto(payload, devto_key)
        url, failed = _try_publish(
            "Dev.to", _devto_upsert,
            dry_run=dry_run, title=article.title,
        )
        if url:
            return {**entry, "devto": url}, errors
        errors += failed

    return entry, errors


def publish_due(schedule: dict[str, Any], *, dry_run: bool = False) -> int:
    # Phase 1: Zenn auto-publish (re-enabled 2026-04-12)
    # 1日1記事ガード付きで再有効化。zenn_publish.py 側で制限を実施。
    logger.info("=== Phase 1: Zenn auto-publish ===")
    schedule, zenn_count, zenn_errors = _process_zenn_entries(
        schedule, dry_run=dry_run,
    )
    if zenn_count > 0:
        logger.info("Zenn: %d article(s) published, %d error(s)", zenn_count, zenn_errors)
    else:
        logger.info("Zenn: nothing to publish today.")

    # Phase 2: Cross-post EN articles to Dev.to
    logger.info("=== Phase 2: Dev.to cross-post ===")
    devto_key = _load_devto_key()
    if devto_key is None:
        return 1

    today = date.today()
    posted_count = 0
    errors = zenn_errors
    skipped_count = 0
    updated_articles: list[dict[str, Any]] = []

    remaining = list(schedule["articles"])
    for i, entry in enumerate(remaining):
        entry_date = date.fromisoformat(entry["date"])
        if entry_date > today or _is_entry_done(entry):
            updated_articles.append(entry)
            continue

        # EN articles only — skip JP entries
        is_en = entry.get("file", "").startswith("articles-en/")
        if not is_en:
            updated_articles.append(entry)
            continue

        # Already posted (devto has a real URL)
        if "devto" in entry and not _needs_posting(entry.get("devto")):
            updated_articles.append(entry)
            continue

        # Check if Zenn was published too recently (need delay for deployment)
        if _should_skip_due_to_recent_zenn_publish(entry):
            updated_articles.append(entry)
            skipped_count += 1
            continue

        updated_entry, entry_errors = _process_entry(entry, devto_key, dry_run=dry_run)
        updated_articles.append(updated_entry)
        errors += entry_errors
        posted_count += 1

        if updated_entry is not entry and not dry_run:
            all_articles = updated_articles + remaining[i + 1:]
            save_schedule({**schedule, "articles": all_articles})

    if posted_count == 0 and skipped_count == 0:
        logger.info("Nothing due today.")
    elif not dry_run:
        save_schedule({**schedule, "articles": updated_articles})
        logger.info(
            "Schedule updated. %d article(s) processed, %d skipped, %d error(s).",
            posted_count, skipped_count, errors,
        )
    else:
        logger.info("[DRY-RUN] %d article(s) would be posted, %d skipped.",
                    posted_count, skipped_count)

    return 1 if errors > 0 else 0


def main() -> int:
    _setup_logging()
    parser = argparse.ArgumentParser(description="Scheduled publisher")
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
