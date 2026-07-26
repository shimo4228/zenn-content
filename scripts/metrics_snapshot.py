#!/usr/bin/env python3
"""Append-only metrics snapshot collector for published articles.

Zenn (public API) と Dev.to (DEVTO_API_KEY) から記事単位の実測メトリクスと
フォロワー総数を取得し、metrics/snapshots.jsonl に追記する。正規化・分析は
読み出し側 (article-stocktake skill) の責務で、ここは raw 値のみを記録する。

Usage:
    uv run python metrics_snapshot.py            # collect and append
    uv run python metrics_snapshot.py --dry-run  # collect and print only
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from devto_crosspost import (
    DEVTO_API_BASE,
    _devto_headers,
    load_env,
    load_schedule,
    slug_of,
)

SCRIPT_DIR = Path(__file__).resolve().parent
SNAPSHOTS_PATH = SCRIPT_DIR / "metrics" / "snapshots.jsonl"

ZENN_API_BASE = "https://zenn.dev/api"
ZENN_USERNAME = "shimo4228"

MAX_PAGES = 100  # runaway-pagination guard for every paged endpoint

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Fetchers (fail-soft: each returns empty/None on error, caller logs on)
# ---------------------------------------------------------------------------


def fetch_zenn_articles(
    client: httpx.Client, username: str = ZENN_USERNAME
) -> list[dict[str, Any]]:
    """All published Zenn articles for the user, paged until next_page is null."""
    articles: list[dict[str, Any]] = []
    page = 1
    while page <= MAX_PAGES:
        resp = client.get(
            f"{ZENN_API_BASE}/articles",
            params={"username": username, "order": "latest", "page": page},
        )
        resp.raise_for_status()
        data = resp.json()
        articles.extend(data.get("articles", []))
        if not data.get("next_page"):
            break
        page = data["next_page"]
    return articles


def fetch_zenn_follower_count(
    client: httpx.Client, username: str = ZENN_USERNAME
) -> int | None:
    resp = client.get(f"{ZENN_API_BASE}/users/{username}")
    resp.raise_for_status()
    return resp.json().get("user", {}).get("follower_count")


def fetch_devto_articles(client: httpx.Client, api_key: str) -> list[dict[str, Any]]:
    """All published Dev.to articles for the authed user."""
    articles: list[dict[str, Any]] = []
    for page in range(1, MAX_PAGES + 1):
        resp = client.get(
            f"{DEVTO_API_BASE}/articles/me/published",
            headers=_devto_headers(api_key),
            params={"per_page": 100, "page": page},
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        articles.extend(batch)
    return articles


def fetch_devto_follower_count(client: httpx.Client, api_key: str) -> int | None:
    """Dev.to exposes followers only as a paged list; count by paging through."""
    count = 0
    for page in range(1, MAX_PAGES + 1):
        resp = client.get(
            f"{DEVTO_API_BASE}/followers/users",
            headers=_devto_headers(api_key),
            params={"per_page": 100, "page": page},
        )
        resp.raise_for_status()
        batch = resp.json()
        count += len(batch)
        if len(batch) < 100:
            break
    return count


# ---------------------------------------------------------------------------
# Record building
# ---------------------------------------------------------------------------


def build_devto_slug_map(schedule: dict[str, Any]) -> dict[str, str]:
    """Map Dev.to article URL → JP slug (EN file basename == JP slug by repo convention)."""
    mapping: dict[str, str] = {}
    for entry in schedule.get("articles", []):
        url = entry.get("devto")
        file = entry.get("file", "")
        if url and file.startswith("articles-en/"):
            mapping[url.rstrip("/")] = slug_of(file)
    return mapping


def zenn_records(ts: str, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "ts": ts,
            "source": "zenn",
            "slug": a.get("slug"),
            "liked": a.get("liked_count"),
            "bookmarked": a.get("bookmarked_count"),
            "comments": a.get("comments_count"),
            "published_at": a.get("published_at"),
        }
        for a in articles
    ]


def devto_records(
    ts: str, articles: list[dict[str, Any]], slug_map: dict[str, str]
) -> list[dict[str, Any]]:
    records = []
    for a in articles:
        url = (a.get("url") or "").rstrip("/")
        records.append(
            {
                "ts": ts,
                "source": "devto",
                "slug": slug_map.get(url, a.get("slug")),
                "devto_url": url or None,
                "reactions": a.get("public_reactions_count"),
                "comments": a.get("comments_count"),
                "views": a.get("page_views_count"),
                "published_at": a.get("published_at"),
            }
        )
    return records


def follower_record(ts: str, zenn: int | None, devto: int | None) -> dict[str, Any]:
    return {"ts": ts, "type": "followers", "zenn": zenn, "devto": devto}


def append_snapshots(
    records: list[dict[str, Any]], path: Path = SNAPSHOTS_PATH
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Collection orchestration
# ---------------------------------------------------------------------------


def collect_all(
    client: httpx.Client, schedule: dict[str, Any], api_key: str | None, ts: str
) -> list[dict[str, Any]]:
    """Collect every source fail-soft; a dead source logs a warning and yields nothing."""
    records: list[dict[str, Any]] = []
    zenn_followers: int | None = None
    devto_followers: int | None = None

    try:
        records.extend(zenn_records(ts, fetch_zenn_articles(client)))
    except httpx.HTTPError as e:
        logger.warning("Zenn articles fetch failed: %s", e)
    try:
        zenn_followers = fetch_zenn_follower_count(client)
    except httpx.HTTPError as e:
        logger.warning("Zenn follower fetch failed: %s", e)

    if api_key:
        slug_map = build_devto_slug_map(schedule)
        try:
            records.extend(
                devto_records(ts, fetch_devto_articles(client, api_key), slug_map)
            )
        except httpx.HTTPError as e:
            logger.warning("Dev.to articles fetch failed: %s", e)
        try:
            devto_followers = fetch_devto_follower_count(client, api_key)
        except httpx.HTTPError as e:
            logger.warning("Dev.to follower fetch failed: %s", e)
    else:
        logger.warning("DEVTO_API_KEY not set; skipping Dev.to metrics")

    records.append(follower_record(ts, zenn_followers, devto_followers))
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true", help="collect and print, do not append"
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    load_env()
    api_key = os.environ.get("DEVTO_API_KEY")
    schedule = load_schedule()
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with httpx.Client(timeout=30) as client:
        records = collect_all(client, schedule, api_key, ts)

    article_count = sum(1 for r in records if r.get("source"))
    if article_count == 0:
        logger.error("No article metrics collected from any source")
        return 1

    if args.dry_run:
        for record in records:
            print(json.dumps(record, ensure_ascii=False))
    else:
        append_snapshots(records)
        logger.info("Appended %d records to %s", len(records), SNAPSHOTS_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
