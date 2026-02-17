"""Generate a publication schedule for a batch of articles.

Given an ordered list of article slugs (highest priority first) and a start
date, assigns Tue/Thu publication dates and outputs schedule.json entries.

Usage:
    python plan_schedule.py --start 2026-02-25 --slugs "slug1,slug2,slug3"
    python plan_schedule.py --start 2026-02-25 --slugs "slug1,slug2" --cadence mon,wed,fri
    python plan_schedule.py --start 2026-02-25 --input scores.json
    python plan_schedule.py --start 2026-02-25 --slugs "slug1" --crosspost-delay 2
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEDULE_PATH = SCRIPT_DIR / "schedule.json"
ZENN_BASE_URL = "https://zenn.dev/shimo4228/articles"

DAY_MAP = {
    "mon": 0, "tue": 1, "wed": 2, "thu": 3,
    "fri": 4, "sat": 5, "sun": 6,
}

DEFAULT_CADENCE = [1, 3]  # Tuesday, Thursday


def parse_cadence(cadence_str: str) -> list[int]:
    """Parse comma-separated day names into weekday numbers."""
    days = []
    for name in cadence_str.lower().split(","):
        name = name.strip()
        if name not in DAY_MAP:
            print(f"Error: Unknown day '{name}'. Use: {', '.join(DAY_MAP)}", file=sys.stderr)
            raise SystemExit(1)
        days.append(DAY_MAP[name])
    return sorted(days)


def next_publish_date(current: date, publish_days: list[int]) -> date:
    """Find the next date that falls on one of the publish days."""
    for offset in range(7):
        candidate = current + timedelta(days=offset)
        if candidate.weekday() in publish_days:
            return candidate
    # Should never reach here since publish_days is non-empty and we check 7 days
    return current


def generate_schedule(
    slugs: list[str],
    start: date,
    publish_days: list[int] | None = None,
    crosspost_delay: int = 1,
    scores: dict[str, dict] | None = None,
) -> list[dict]:
    """Generate schedule entries for a list of article slugs.

    Args:
        slugs: Article slugs in priority order (publish first → last).
        start: Earliest possible publication date.
        publish_days: Weekday numbers (0=Mon, 6=Sun). Default: [1, 3] (Tue/Thu).
        crosspost_delay: Days between Zenn publish and cross-post. Default: 1.
        scores: Optional dict mapping slug to score dict for traceability.

    Returns:
        List of schedule entry dicts.
    """
    if publish_days is None:
        publish_days = DEFAULT_CADENCE

    entries = []
    current = start

    for slug in slugs:
        zenn_date = next_publish_date(current, publish_days)
        crosspost_date = zenn_date + timedelta(days=crosspost_delay)

        entry: dict = {
            "file": f"articles/{slug}.md",
            "canonical_url": f"{ZENN_BASE_URL}/{slug}",
            "zenn_date": zenn_date.isoformat(),
            "date": crosspost_date.isoformat(),
            "qiita": None,
            "devto": "n/a",
            "hashnode": "n/a",
        }

        if scores and slug in scores:
            entry["score"] = scores[slug]

        entries.append(entry)
        # Next article starts searching from the day after this publish date
        current = zenn_date + timedelta(days=1)

    return entries


def load_scores(path: Path) -> tuple[list[str], dict[str, dict]]:
    """Load scored articles from JSON file.

    Expected format:
    [
      {"slug": "article-slug", "search": 3, "anchor": 1, "ready": 2, "fresh": 1, "total": 7},
      ...
    ]

    Returns (slugs_in_order, scores_dict).
    """
    data = json.loads(path.read_text())
    # Sort by total score descending
    data.sort(key=lambda x: x.get("total", 0), reverse=True)
    slugs = [item["slug"] for item in data]
    scores = {
        item["slug"]: {
            k: item[k] for k in ("search", "anchor", "ready", "fresh", "total")
            if k in item
        }
        for item in data
    }
    return slugs, scores


def merge_into_schedule(new_entries: list[dict]) -> dict:
    """Merge new entries into existing schedule.json."""
    if SCHEDULE_PATH.exists():
        schedule = json.loads(SCHEDULE_PATH.read_text())
    else:
        schedule = {"post_time_utc": "23:00", "articles": []}

    existing_files = {e["file"] for e in schedule["articles"]}
    added = 0
    for entry in new_entries:
        if entry["file"] not in existing_files:
            schedule["articles"].append(entry)
            added += 1
        else:
            print(f"  Skip (already exists): {entry['file']}", file=sys.stderr)

    print(f"Added {added} entries to schedule.", file=sys.stderr)
    return schedule


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate publication schedule for article batches",
    )
    parser.add_argument(
        "--start", required=True, type=date.fromisoformat,
        help="Start date (YYYY-MM-DD). First article publishes on or after this date.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--slugs",
        help="Comma-separated article slugs in priority order (highest first).",
    )
    group.add_argument(
        "--input", type=Path,
        help="JSON file with scored articles (auto-sorted by total score).",
    )
    parser.add_argument(
        "--cadence", default="tue,thu",
        help="Comma-separated publish days (default: tue,thu).",
    )
    parser.add_argument(
        "--crosspost-delay", type=int, default=1,
        help="Days between Zenn publish and cross-post (default: 1).",
    )
    parser.add_argument(
        "--merge", action="store_true",
        help="Merge into existing schedule.json instead of just printing.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show schedule without writing to file.",
    )

    args = parser.parse_args()
    publish_days = parse_cadence(args.cadence)

    scores: dict[str, dict] | None = None
    if args.input:
        slugs, scores = load_scores(args.input)
    else:
        slugs = [s.strip() for s in args.slugs.split(",")]

    entries = generate_schedule(
        slugs=slugs,
        start=args.start,
        publish_days=publish_days,
        crosspost_delay=args.crosspost_delay,
        scores=scores,
    )

    # Display schedule
    print(f"\n{'Date':<14} {'Cross-post':<14} {'Slug':<40} {'Score':>5}")
    print("-" * 78)
    for e in entries:
        score_str = str(e["score"]["total"]) if "score" in e else "-"
        print(f"{e['zenn_date']:<14} {e['date']:<14} {e['file']:<40} {score_str:>5}")
    print()

    if args.merge and not args.dry_run:
        schedule = merge_into_schedule(entries)
        SCHEDULE_PATH.write_text(
            json.dumps(schedule, indent=2, ensure_ascii=False) + "\n",
        )
        print(f"Written to {SCHEDULE_PATH}", file=sys.stderr)
    elif args.merge and args.dry_run:
        print("[DRY-RUN] Would merge into schedule.json", file=sys.stderr)
    else:
        # Just print JSON to stdout
        print(json.dumps(entries, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
