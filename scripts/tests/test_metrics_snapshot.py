"""Tests for metrics_snapshot.py — record building, pagination, fail-soft collection."""

from __future__ import annotations

import json

import httpx
import respx
from metrics_snapshot import (
    DEVTO_API_BASE,
    ZENN_API_BASE,
    append_snapshots,
    build_devto_slug_map,
    collect_all,
    devto_records,
    fetch_devto_follower_count,
    fetch_zenn_articles,
    fetch_zenn_follower_count,
    follower_record,
    zenn_records,
)

TS = "2026-07-27T00:00:00+00:00"

SCHEDULE = {
    "articles": [
        {
            "file": "articles/foo.md",
            "canonical_url": "https://zenn.dev/shimo4228/articles/foo",
        },
        {
            "file": "articles-en/foo.md",
            "devto": "https://dev.to/shimo4228/foo-en-slug-123/",
        },
        {"file": "articles-en/bar.md"},  # not yet cross-posted → no mapping
    ]
}


def test_build_devto_slug_map_maps_url_to_jp_slug():
    mapping = build_devto_slug_map(SCHEDULE)
    assert mapping == {"https://dev.to/shimo4228/foo-en-slug-123": "foo"}


def test_zenn_records_shape():
    articles = [
        {
            "slug": "foo",
            "liked_count": 5,
            "bookmarked_count": 2,
            "comments_count": 1,
            "published_at": "2026-07-01T09:00:00+09:00",
        }
    ]
    (record,) = zenn_records(TS, articles)
    assert record == {
        "ts": TS,
        "source": "zenn",
        "slug": "foo",
        "liked": 5,
        "bookmarked": 2,
        "comments": 1,
        "published_at": "2026-07-01T09:00:00+09:00",
    }


def test_devto_records_prefers_jp_slug_and_falls_back():
    slug_map = {"https://dev.to/shimo4228/foo-en-slug-123": "foo"}
    articles = [
        {
            "url": "https://dev.to/shimo4228/foo-en-slug-123/",
            "slug": "foo-en-slug-123",
            "public_reactions_count": 3,
            "comments_count": 0,
            "page_views_count": 120,
            "published_at": "2026-07-01T00:00:00Z",
        },
        {
            "url": "https://dev.to/shimo4228/unmapped-456",
            "slug": "unmapped-456",
            "public_reactions_count": 1,
            "comments_count": 0,
            "page_views_count": 10,
            "published_at": "2026-07-02T00:00:00Z",
        },
    ]
    mapped, unmapped = devto_records(TS, articles, slug_map)
    assert mapped["slug"] == "foo"
    assert mapped["views"] == 120
    assert unmapped["slug"] == "unmapped-456"  # falls back to Dev.to's own slug


def test_append_snapshots_appends_jsonl(tmp_path):
    path = tmp_path / "metrics" / "snapshots.jsonl"
    append_snapshots([follower_record(TS, 12, None)], path)
    append_snapshots([follower_record(TS, 13, 4)], path)
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[1]) == {
        "ts": TS,
        "type": "followers",
        "zenn": 13,
        "devto": 4,
    }


@respx.mock
def test_fetch_zenn_articles_paginates():
    respx.get(f"{ZENN_API_BASE}/articles", params={"page": 1}).respond(
        json={"articles": [{"slug": "a"}], "next_page": 2}
    )
    respx.get(f"{ZENN_API_BASE}/articles", params={"page": 2}).respond(
        json={"articles": [{"slug": "b"}], "next_page": None}
    )
    with httpx.Client() as client:
        articles = fetch_zenn_articles(client)
    assert [a["slug"] for a in articles] == ["a", "b"]


@respx.mock
def test_fetch_zenn_follower_count():
    respx.get(f"{ZENN_API_BASE}/users/shimo4228").respond(
        json={"user": {"follower_count": 12}}
    )
    with httpx.Client() as client:
        assert fetch_zenn_follower_count(client) == 12


@respx.mock
def test_fetch_devto_follower_count_pages_until_short_batch():
    respx.get(f"{DEVTO_API_BASE}/followers/users", params={"page": 1}).respond(
        json=[{"id": i} for i in range(100)]
    )
    respx.get(f"{DEVTO_API_BASE}/followers/users", params={"page": 2}).respond(
        json=[{"id": 1}, {"id": 2}]
    )
    with httpx.Client() as client:
        assert fetch_devto_follower_count(client, "k") == 102


@respx.mock
def test_collect_all_fail_soft_when_zenn_down(caplog):
    respx.get(f"{ZENN_API_BASE}/articles").respond(status_code=500)
    respx.get(f"{ZENN_API_BASE}/users/shimo4228").respond(status_code=500)
    respx.get(f"{DEVTO_API_BASE}/articles/me/published", params={"page": 1}).respond(
        json=[
            {
                "url": "https://dev.to/shimo4228/foo-en-slug-123",
                "slug": "foo-en-slug-123",
                "public_reactions_count": 3,
                "comments_count": 0,
                "page_views_count": 9,
                "published_at": "2026-07-01T00:00:00Z",
            }
        ]
    )
    respx.get(f"{DEVTO_API_BASE}/articles/me/published", params={"page": 2}).respond(
        json=[]
    )
    respx.get(f"{DEVTO_API_BASE}/followers/users").respond(json=[{"id": 1}])

    with httpx.Client() as client:
        records = collect_all(client, SCHEDULE, "k", TS)

    sources = [r.get("source") for r in records if r.get("source")]
    assert sources == ["devto"]  # Zenn dead, Dev.to still collected
    assert records[-1] == {"ts": TS, "type": "followers", "zenn": None, "devto": 1}
    assert "Zenn articles fetch failed" in caplog.text


@respx.mock
def test_collect_all_without_api_key_skips_devto(caplog):
    respx.get(f"{ZENN_API_BASE}/articles").respond(
        json={"articles": [{"slug": "a", "liked_count": 1}], "next_page": None}
    )
    respx.get(f"{ZENN_API_BASE}/users/shimo4228").respond(
        json={"user": {"follower_count": 7}}
    )
    with httpx.Client() as client:
        records = collect_all(client, SCHEDULE, None, TS)

    sources = [r.get("source") for r in records if r.get("source")]
    assert sources == ["zenn"]
    assert records[-1]["zenn"] == 7
    assert records[-1]["devto"] is None
    assert "DEVTO_API_KEY not set" in caplog.text
