"""Tests for devto_crosspost.py — per-article scheduled Dev.to cross-poster."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import httpx
import pytest
import respx

import devto_crosspost as dc

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_ARTICLE = FIXTURES_DIR / "sample-article.md"

DEVTO_KEY = "test-devto-key"
DEVTO_POST_URL = "https://dev.to/api/articles"
DEVTO_ME_URL = "https://dev.to/api/articles/me/published"


def _en(**overrides: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {"file": "articles-en/test.md", "devto": None}
    entry.update(overrides)
    return entry


def _art(**overrides: Any) -> dc.Article:
    defaults: dict[str, Any] = {
        "title": "T",
        "body": "body",
        "topics": (),
        "article_type": "tech",
        "description": "",
    }
    defaults.update(overrides)
    return dc.Article(**defaults)


# ---------------------------------------------------------------------------
# publish_at parsing
# ---------------------------------------------------------------------------


class TestParsePublishAt:
    def test_tz_aware_converts_to_jst(self) -> None:
        # 2026-07-07 09:00 EDT (UTC-4) == 22:00 JST same day
        got = dc.parse_publish_at("2026-07-07 09:00 America/New_York")
        assert got == datetime(2026, 7, 7, 22, 0, tzinfo=ZoneInfo("Asia/Tokyo"))

    def test_bare_time_assumed_jst(self) -> None:
        got = dc.parse_publish_at("2026-07-07 07:00")
        assert got == datetime(2026, 7, 7, 7, 0, tzinfo=ZoneInfo("Asia/Tokyo"))

    def test_malformed_raises(self) -> None:
        with pytest.raises(ValueError):
            dc.parse_publish_at("2026-07-07")

    def test_unknown_tz_raises(self) -> None:
        with pytest.raises(Exception):
            dc.parse_publish_at("2026-07-07 09:00 Mars/Phobos")


# ---------------------------------------------------------------------------
# Zenn → Dev.to conversion
# ---------------------------------------------------------------------------


class TestStripZennSyntax:
    def test_image_rewritten_to_github_raw(self) -> None:
        out = dc.strip_zenn_syntax("![alt](/images/foo/bar.png)")
        assert f"![alt]({dc.GITHUB_RAW_BASE}/foo/bar.png)" == out

    def test_message_becomes_blockquote(self) -> None:
        assert dc.strip_zenn_syntax(":::message\na\nb\n:::") == "> a\n> b"

    def test_details_becomes_html(self) -> None:
        out = dc.strip_zenn_syntax(":::details Title\ninner\n:::")
        assert out.startswith("<details><summary>Title</summary>")
        assert "inner" in out


class TestResolveDevtoTags:
    def test_override_wins_lowercased_max4(self) -> None:
        assert dc.resolve_devto_tags(_art(), ["AI", "X", "Y", "Z", "W"]) == ["ai", "x", "y", "z"]

    def test_override_dedupes(self) -> None:
        assert dc.resolve_devto_tags(_art(), ["ai", "ai", "ml"]) == ["ai", "ml"]

    def test_fallback_keeps_english_alnum(self) -> None:
        assert dc.resolve_devto_tags(_art(topics=("python", "testing")), None) == ["python", "testing"]

    def test_fallback_drops_japanese_and_dotted(self) -> None:
        assert dc.resolve_devto_tags(_art(topics=("個人開発", "next.js", "ai")), None) == ["ai"]

    def test_idea_prepends_discuss(self) -> None:
        assert dc.resolve_devto_tags(_art(topics=("ai",), article_type="idea"), None) == ["discuss", "ai"]


class TestConvertToDevto:
    def test_basic_payload_shape(self) -> None:
        art = dc.parse_zenn_article(SAMPLE_ARTICLE)
        payload = dc.convert_to_devto(art, _en(), "test")["article"]
        assert payload["published"] is True
        assert "raw.githubusercontent.com" in payload["body_markdown"]  # image stripped
        assert payload["tags"] == ["python", "testing", "pytest", "ci"]  # max 4

    def test_explicit_cover_and_description(self) -> None:
        art = _art(description="d")
        entry = _en(cover_image="https://img/x.png")
        payload = dc.convert_to_devto(art, entry, "test")["article"]
        assert payload["description"] == "d"
        assert payload["main_image"] == "https://img/x.png"

    def test_no_cover_when_none_available(self) -> None:
        payload = dc.convert_to_devto(_art(), _en(), "no-such-slug")["article"]
        assert "main_image" not in payload


# ---------------------------------------------------------------------------
# Dev.to API
# ---------------------------------------------------------------------------


class TestPostToDevto:
    @respx.mock
    def test_success_returns_url(self) -> None:
        respx.post(DEVTO_POST_URL).mock(
            return_value=httpx.Response(201, json={"url": "https://dev.to/u/x"}),
        )
        assert dc.post_to_devto({"article": {}}, DEVTO_KEY) == "https://dev.to/u/x"

    @respx.mock
    def test_sends_api_key_header(self) -> None:
        route = respx.post(DEVTO_POST_URL).mock(
            return_value=httpx.Response(201, json={"url": "u"}),
        )
        dc.post_to_devto({"article": {}}, DEVTO_KEY)
        assert route.calls.last.request.headers["api-key"] == DEVTO_KEY

    @respx.mock
    def test_non_201_raises(self) -> None:
        respx.post(DEVTO_POST_URL).mock(return_value=httpx.Response(422, text="bad"))
        with pytest.raises(RuntimeError, match="422"):
            dc.post_to_devto({"article": {}}, DEVTO_KEY)

    @respx.mock
    def test_201_without_url_raises(self) -> None:
        respx.post(DEVTO_POST_URL).mock(return_value=httpx.Response(201, json={}))
        with pytest.raises(RuntimeError, match="no 'url'"):
            dc.post_to_devto({"article": {}}, DEVTO_KEY)


class TestFindExistingDevtoUrl:
    @respx.mock
    def test_returns_url_on_title_match(self) -> None:
        respx.get(DEVTO_ME_URL).mock(
            return_value=httpx.Response(200, json=[{"title": "T", "url": "https://dev.to/u/t"}]),
        )
        assert dc.find_existing_devto_url("T", DEVTO_KEY) == "https://dev.to/u/t"

    @respx.mock
    def test_none_when_absent(self) -> None:
        respx.get(DEVTO_ME_URL).mock(return_value=httpx.Response(200, json=[]))
        assert dc.find_existing_devto_url("T", DEVTO_KEY) is None

    @respx.mock
    def test_non_200_raises_not_returns_none(self) -> None:
        # Must fail closed: a transient 429/5xx is NOT "no duplicate found".
        respx.get(DEVTO_ME_URL).mock(return_value=httpx.Response(429, text="slow down"))
        with pytest.raises(RuntimeError):
            dc.find_existing_devto_url("T", DEVTO_KEY)


# ---------------------------------------------------------------------------
# schedule / find helpers
# ---------------------------------------------------------------------------


class TestScheduleHelpers:
    def test_slug_of(self) -> None:
        assert dc.slug_of("articles-en/foo-bar.md") == "foo-bar"

    def test_find_entry_matches_en_slug(self) -> None:
        sched = {"articles": [_en(file="articles-en/foo.md"), {"file": "articles/foo.md"}]}
        assert dc.find_entry(sched, "foo")["file"] == "articles-en/foo.md"

    def test_find_entry_none_for_unknown(self) -> None:
        assert dc.find_entry({"articles": []}, "x") is None


# ---------------------------------------------------------------------------
# cmd_schedule
# ---------------------------------------------------------------------------


class TestCmdSchedule:
    FUTURE = "2099-01-02 10:00 America/New_York"

    def test_dry_run_renders_without_install(self, monkeypatch: pytest.MonkeyPatch) -> None:
        install = MagicMock()
        monkeypatch.setattr(dc, "install_agent", install)
        monkeypatch.setattr(dc, "validate_article_path", lambda f, **k: SAMPLE_ARTICLE)
        assert dc.cmd_schedule("foo", self.FUTURE, dry_run=True) == 0
        install.assert_not_called()

    def test_installs_agent_with_jst_fire_time(self, monkeypatch: pytest.MonkeyPatch) -> None:
        captured: dict[str, Any] = {}
        monkeypatch.setattr(dc, "validate_article_path", lambda f, **k: SAMPLE_ARTICLE)
        monkeypatch.setattr(dc, "install_agent", lambda slug, fire: captured.update(slug=slug, fire=fire))
        assert dc.cmd_schedule("foo", self.FUTURE, dry_run=False) == 0
        assert captured["slug"] == "foo"
        assert captured["fire"].tzinfo == dc.JST

    def test_does_not_touch_schedule_json(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(dc, "save_schedule", save)
        monkeypatch.setattr(dc, "validate_article_path", lambda f, **k: SAMPLE_ARTICLE)
        monkeypatch.setattr(dc, "install_agent", MagicMock())
        dc.cmd_schedule("foo", self.FUTURE, dry_run=False)
        save.assert_not_called()  # timing is an argument, not persisted state

    def test_unknown_article_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dc, "validate_article_path", lambda f, **k: None)
        assert dc.cmd_schedule("nope", self.FUTURE, dry_run=False) == 1

    def test_past_time_refused(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dc, "validate_article_path", lambda f, **k: SAMPLE_ARTICLE)
        monkeypatch.setattr(dc, "install_agent", MagicMock())
        assert dc.cmd_schedule("foo", "2000-01-01 09:00", dry_run=False) == 1

    def test_bad_at_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dc, "validate_article_path", lambda f, **k: SAMPLE_ARTICLE)
        assert dc.cmd_schedule("foo", "not-a-date", dry_run=False) == 1


# ---------------------------------------------------------------------------
# cmd_post
# ---------------------------------------------------------------------------


class TestCmdPost:
    @respx.mock
    def test_posts_and_records_and_cleans_up(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DEVTO_API_KEY", DEVTO_KEY)
        respx.get(DEVTO_ME_URL).mock(return_value=httpx.Response(200, json=[]))
        route = respx.post(DEVTO_POST_URL).mock(
            return_value=httpx.Response(201, json={"url": "https://dev.to/u/new"}),
        )
        saved: dict[str, Any] = {}
        monkeypatch.setattr(dc, "save_schedule", lambda s, *a, **k: saved.update(s=s))
        monkeypatch.setattr(dc, "validate_article_path", lambda f, **k: SAMPLE_ARTICLE)
        remove = MagicMock()
        monkeypatch.setattr(dc, "remove_agent", remove)

        sched = {"articles": [_en(file="articles-en/test.md")]}
        rc = dc.cmd_post(sched, "test", dry_run=False)

        assert rc == 0
        assert route.called
        assert sched["articles"][0]["devto"] == "https://dev.to/u/new"
        assert saved["s"]["articles"][0]["devto"] == "https://dev.to/u/new"
        remove.assert_called_once_with("test")  # one-shot self-cleanup

    @respx.mock
    def test_idempotent_skip_when_title_already_live(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DEVTO_API_KEY", DEVTO_KEY)
        respx.get(DEVTO_ME_URL).mock(
            return_value=httpx.Response(200, json=[{"title": "テスト用記事タイトル", "url": "https://dev.to/u/dup"}]),
        )
        post_route = respx.post(DEVTO_POST_URL)
        monkeypatch.setattr(dc, "save_schedule", MagicMock())
        monkeypatch.setattr(dc, "validate_article_path", lambda f, **k: SAMPLE_ARTICLE)
        monkeypatch.setattr(dc, "remove_agent", MagicMock())

        sched = {"articles": [_en(file="articles-en/test.md")]}
        rc = dc.cmd_post(sched, "test", dry_run=False)

        assert rc == 0
        assert not post_route.called  # no duplicate POST
        assert sched["articles"][0]["devto"] == "https://dev.to/u/dup"

    def test_already_posted_is_noop_but_cleans_agent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        remove = MagicMock()
        monkeypatch.setattr(dc, "remove_agent", remove)
        sched = {"articles": [_en(file="articles-en/test.md", devto="https://dev.to/u/x")]}
        rc = dc.cmd_post(sched, "test", dry_run=False)
        assert rc == 0
        remove.assert_called_once_with("test")

    @respx.mock
    def test_api_error_returns_nonzero_and_no_save(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DEVTO_API_KEY", DEVTO_KEY)
        respx.get(DEVTO_ME_URL).mock(return_value=httpx.Response(200, json=[]))
        respx.post(DEVTO_POST_URL).mock(return_value=httpx.Response(500, text="boom"))
        save = MagicMock()
        monkeypatch.setattr(dc, "save_schedule", save)
        monkeypatch.setattr(dc, "validate_article_path", lambda f, **k: SAMPLE_ARTICLE)
        monkeypatch.setattr(dc, "remove_agent", MagicMock())

        rc = dc.cmd_post({"articles": [_en(file="articles-en/test.md")]}, "test", dry_run=False)
        assert rc == 1
        save.assert_not_called()

    @respx.mock
    def test_aborts_when_duplicate_check_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Fail closed: if the idempotency search errors, do NOT POST (double-post risk).
        monkeypatch.setenv("DEVTO_API_KEY", DEVTO_KEY)
        respx.get(DEVTO_ME_URL).mock(return_value=httpx.Response(500, text="boom"))
        post_route = respx.post(DEVTO_POST_URL)
        monkeypatch.setattr(dc, "save_schedule", MagicMock())
        monkeypatch.setattr(dc, "validate_article_path", lambda f, **k: SAMPLE_ARTICLE)
        monkeypatch.setattr(dc, "remove_agent", MagicMock())

        rc = dc.cmd_post({"articles": [_en(file="articles-en/test.md")]}, "test", dry_run=False)
        assert rc == 1
        assert not post_route.called

    def test_dry_run_does_not_post(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DEVTO_API_KEY", DEVTO_KEY)
        monkeypatch.setattr(dc, "validate_article_path", lambda f, **k: SAMPLE_ARTICLE)
        # no respx routes registered → any HTTP call would raise
        rc = dc.cmd_post({"articles": [_en(file="articles-en/test.md")]}, "test", dry_run=True)
        assert rc == 0

    def test_missing_key_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("DEVTO_API_KEY", raising=False)
        monkeypatch.setattr(dc, "validate_article_path", lambda f, **k: SAMPLE_ARTICLE)
        rc = dc.cmd_post({"articles": [_en(file="articles-en/test.md")]}, "test", dry_run=False)
        assert rc == 1

    def test_unknown_slug_errors(self) -> None:
        assert dc.cmd_post({"articles": []}, "nope", dry_run=False) == 1


# ---------------------------------------------------------------------------
# launchd rendering + agent lifecycle
# ---------------------------------------------------------------------------


class TestLaunchd:
    def test_render_plist_has_fire_fields_and_no_hardcoded_user(self) -> None:
        fire = datetime(2026, 7, 7, 22, 30, tzinfo=dc.JST)
        xml = dc.render_plist("my-slug", fire)
        assert "<key>Month</key><integer>7</integer>" in xml
        assert "<key>Day</key><integer>7</integer>" in xml
        assert "<key>Hour</key><integer>22</integer>" in xml
        assert "<key>Minute</key><integer>30</integer>" in xml
        assert "dev.shimo4228.devto-my-slug" in xml
        assert "post" in xml and "my-slug" in xml

    def test_install_agent_writes_and_loads(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        monkeypatch.setattr(dc, "LAUNCH_AGENTS_DIR", tmp_path)
        calls: list[tuple[str, ...]] = []
        monkeypatch.setattr(
            dc, "_launchctl",
            lambda *a: calls.append(a) or MagicMock(returncode=0, stderr=""),
        )
        fire = datetime(2099, 7, 7, 22, 0, tzinfo=dc.JST)
        dc.install_agent("foo", fire)
        assert (tmp_path / "dev.shimo4228.devto-foo.plist").exists()
        assert any(c[0] == "load" for c in calls)

    def test_install_agent_rolls_back_plist_on_load_failure(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        monkeypatch.setattr(dc, "LAUNCH_AGENTS_DIR", tmp_path)
        monkeypatch.setattr(
            dc, "_launchctl", lambda *a: MagicMock(returncode=1, stderr="nope"),
        )
        with pytest.raises(SystemExit):
            dc.install_agent("foo", datetime(2099, 7, 7, 22, 0, tzinfo=dc.JST))
        # no phantom plist left behind → list won't falsely report "armed"
        assert not (tmp_path / "dev.shimo4228.devto-foo.plist").exists()

    def test_remove_agent_warns_but_still_unlinks_on_unload_failure(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        monkeypatch.setattr(dc, "LAUNCH_AGENTS_DIR", tmp_path)
        plist = tmp_path / "dev.shimo4228.devto-foo.plist"
        plist.write_text("x")
        monkeypatch.setattr(dc, "_launchctl", lambda *a: MagicMock(returncode=1, stderr="fail"))
        dc.remove_agent("foo")
        assert not plist.exists()

    def test_remove_agent_unloads_and_deletes(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        monkeypatch.setattr(dc, "LAUNCH_AGENTS_DIR", tmp_path)
        plist = tmp_path / "dev.shimo4228.devto-foo.plist"
        plist.write_text("x")
        monkeypatch.setattr(dc, "_launchctl", lambda *a: MagicMock(returncode=0, stderr=""))
        dc.remove_agent("foo")
        assert not plist.exists()

    def test_remove_agent_noop_when_absent(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        monkeypatch.setattr(dc, "LAUNCH_AGENTS_DIR", tmp_path)
        called = MagicMock()
        monkeypatch.setattr(dc, "_launchctl", called)
        dc.remove_agent("absent")  # no plist → no launchctl call
        called.assert_not_called()


# ---------------------------------------------------------------------------
# cmd_list / cmd_unschedule
# ---------------------------------------------------------------------------


class TestListAndUnschedule:
    def test_list_runs(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr(dc, "LAUNCH_AGENTS_DIR", tmp_path)
        sched = {
            "articles": [
                _en(file="articles-en/a.md", devto="https://dev.to/u/a"),
                _en(file="articles-en/b.md"),
                {"file": "articles/jp.md", "date": "2026-01-01"},
            ],
        }
        assert dc.cmd_list(sched) == 0

    def test_unschedule_removes(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr(dc, "LAUNCH_AGENTS_DIR", tmp_path)
        (tmp_path / "dev.shimo4228.devto-foo.plist").write_text("x")
        monkeypatch.setattr(dc, "_launchctl", lambda *a: MagicMock(returncode=0, stderr=""))
        assert dc.cmd_unschedule("foo") == 0
        assert not (tmp_path / "dev.shimo4228.devto-foo.plist").exists()

    def test_unschedule_noop_when_absent(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr(dc, "LAUNCH_AGENTS_DIR", tmp_path)
        assert dc.cmd_unschedule("absent") == 0


# ---------------------------------------------------------------------------
# I/O + env helpers
# ---------------------------------------------------------------------------


class TestScheduleIO:
    def test_load_reads_json(self, tmp_path: Path) -> None:
        p = tmp_path / "s.json"
        p.write_text('{"articles": []}')
        assert dc.load_schedule(p) == {"articles": []}

    def test_load_missing_exits(self, tmp_path: Path) -> None:
        with pytest.raises(SystemExit):
            dc.load_schedule(tmp_path / "nope.json")

    def test_load_bad_json_exits(self, tmp_path: Path) -> None:
        p = tmp_path / "s.json"
        p.write_text("{bad")
        with pytest.raises(SystemExit):
            dc.load_schedule(p)

    def test_save_roundtrip_unicode(self, tmp_path: Path) -> None:
        p = tmp_path / "s.json"
        dc.save_schedule({"articles": [{"notes": "日本語"}]}, p)
        assert json.loads(p.read_text()) == {"articles": [{"notes": "日本語"}]}


class TestLoadEnvAndPaths:
    def test_load_env_sets_missing_key(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        env = tmp_path / ".env"
        env.write_text("# c\nFOO_K=bar\n")
        monkeypatch.delenv("FOO_K", raising=False)
        dc.load_env(env)
        assert os.environ["FOO_K"] == "bar"

    def test_load_env_missing_file_noop(self, tmp_path: Path) -> None:
        dc.load_env(tmp_path / "absent.env")

    def test_validate_path_valid(self) -> None:
        r = dc.validate_article_path("scripts/tests/fixtures/sample-article.md")
        assert r is not None and r.exists()

    def test_validate_path_traversal_rejected(self) -> None:
        assert dc.validate_article_path("../../../etc/passwd") is None

    def test_validate_path_missing(self) -> None:
        assert dc.validate_article_path("articles-en/nope.md") is None


# ---------------------------------------------------------------------------
# main dispatch
# ---------------------------------------------------------------------------


class TestMain:
    def test_main_routes_list(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dc, "load_schedule", lambda *a, **k: {"articles": []})
        assert dc.main(["list"]) == 0

    def test_main_routes_unschedule(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr(dc, "load_schedule", lambda *a, **k: {"articles": []})
        monkeypatch.setattr(dc, "LAUNCH_AGENTS_DIR", tmp_path)
        assert dc.main(["unschedule", "absent"]) == 0
