"""Tests for plan_schedule.py — publication schedule generator."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from plan_schedule import (
    DEFAULT_CADENCE,
    generate_schedule,
    load_scores,
    merge_into_schedule,
    next_publish_date,
    parse_cadence,
)


# ---------------------------------------------------------------------------
# parse_cadence
# ---------------------------------------------------------------------------


class TestParseCadence:
    def test_default_tue_thu(self) -> None:
        result = parse_cadence("tue,thu")
        assert result == [1, 3]

    def test_single_day(self) -> None:
        assert parse_cadence("mon") == [0]

    def test_multiple_days_sorted(self) -> None:
        result = parse_cadence("fri,mon,wed")
        assert result == [0, 2, 4]

    def test_all_days(self) -> None:
        result = parse_cadence("mon,tue,wed,thu,fri,sat,sun")
        assert result == [0, 1, 2, 3, 4, 5, 6]

    def test_unknown_day_exits(self) -> None:
        with pytest.raises(SystemExit):
            parse_cadence("funday")

    def test_case_insensitive(self) -> None:
        result = parse_cadence("Mon,TUE")
        assert result == [0, 1]

    def test_spaces_stripped(self) -> None:
        result = parse_cadence(" tue , thu ")
        assert result == [1, 3]


# ---------------------------------------------------------------------------
# next_publish_date
# ---------------------------------------------------------------------------


class TestNextPublishDate:
    def test_same_day_if_matches(self) -> None:
        # 2026-02-24 is a Tuesday (weekday=1)
        result = next_publish_date(date(2026, 2, 24), [1, 3])
        assert result == date(2026, 2, 24)

    def test_next_matching_day(self) -> None:
        # 2026-02-25 is Wednesday, next Tuesday is 2026-03-03, but Thursday is 2026-02-27
        result = next_publish_date(date(2026, 2, 25), [1, 3])
        assert result == date(2026, 2, 26)  # Thursday

    def test_wraps_to_next_week(self) -> None:
        # 2026-02-27 is Thursday, next Tue is 2026-03-03
        result = next_publish_date(date(2026, 2, 28), [1])  # Only Tuesdays
        assert result == date(2026, 3, 3)

    def test_single_day_schedule(self) -> None:
        # 2026-02-24 is Tuesday
        result = next_publish_date(date(2026, 2, 24), [0])  # Mondays only
        assert result == date(2026, 3, 2)


# ---------------------------------------------------------------------------
# generate_schedule
# ---------------------------------------------------------------------------


class TestGenerateSchedule:
    def test_single_slug(self) -> None:
        entries = generate_schedule(
            slugs=["my-article"],
            start=date(2026, 2, 25),  # Tuesday
        )
        assert len(entries) == 1
        entry = entries[0]
        assert entry["file"] == "articles/my-article.md"
        assert "date" in entry
        assert "canonical_url" in entry
        # New schema: no zenn_date / zenn_published — Zenn handles via published_at
        assert "zenn_date" not in entry
        assert "zenn_published" not in entry

    def test_multiple_slugs_get_different_dates(self) -> None:
        entries = generate_schedule(
            slugs=["a", "b", "c"],
            start=date(2026, 2, 25),
        )
        assert len(entries) == 3
        dates = [e["date"] for e in entries]
        assert len(set(dates)) == 3  # All different

    def test_crosspost_delay_applies_to_en_entry(self) -> None:
        entries = generate_schedule(
            slugs=["test"],
            start=date(2026, 2, 25),
            crosspost_delay=2,
            include_en_translation=True,
            en_same_day=False,
        )
        jp_date = date.fromisoformat(entries[0]["date"])
        en_date = date.fromisoformat(entries[1]["date"])
        assert (en_date - jp_date).days == 2

    def test_custom_publish_days(self) -> None:
        entries = generate_schedule(
            slugs=["x"],
            start=date(2026, 2, 24),  # Tuesday
            publish_days=[0],  # Mondays only
        )
        publish_date = date.fromisoformat(entries[0]["date"])
        assert publish_date.weekday() == 0

    def test_with_scores(self) -> None:
        scores = {"slug1": {"total": 7, "search": 3}}
        entries = generate_schedule(
            slugs=["slug1"],
            start=date(2026, 2, 25),
            scores=scores,
        )
        assert entries[0]["score"] == scores["slug1"]

    def test_include_en_translation(self) -> None:
        entries = generate_schedule(
            slugs=["test"],
            start=date(2026, 2, 25),
            include_en_translation=True,
        )
        assert len(entries) == 2
        assert entries[0]["file"] == "articles/test.md"
        assert entries[1]["file"] == "articles-en/test.md"
        assert entries[1]["devto"] == "pending"
        # No hashnode or depends_on fields
        assert "hashnode" not in entries[1]
        assert "depends_on" not in entries[1]

    def test_no_deprecated_fields(self) -> None:
        entries = generate_schedule(
            slugs=["test"],
            start=date(2026, 2, 25),
        )
        entry = entries[0]
        assert "qiita" not in entry
        assert "hashnode" not in entry
        assert "devto" not in entry  # JP entries don't have devto
        assert "zenn_date" not in entry  # Zenn handles via published_at frontmatter
        assert "zenn_published" not in entry
        assert "zenn_published_at" not in entry


# ---------------------------------------------------------------------------
# load_scores
# ---------------------------------------------------------------------------


class TestLoadScores:
    def test_loads_and_sorts(self, tmp_path: Path) -> None:
        data = [
            {"slug": "low", "total": 3, "search": 1},
            {"slug": "high", "total": 9, "search": 5},
            {"slug": "mid", "total": 6, "search": 3},
        ]
        path = tmp_path / "scores.json"
        path.write_text(json.dumps(data))

        slugs, scores = load_scores(path)
        assert slugs == ["high", "mid", "low"]  # Sorted by total desc
        assert scores["high"]["total"] == 9
        assert scores["low"]["search"] == 1


# ---------------------------------------------------------------------------
# merge_into_schedule
# ---------------------------------------------------------------------------


class TestMergeIntoSchedule:
    def test_merge_new_entries(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        # Create existing schedule
        existing = {"post_time_utc": "23:00", "articles": [
            {"file": "articles/existing.md", "date": "2026-01-01"},
        ]}
        schedule_path = tmp_path / "schedule.json"
        schedule_path.write_text(json.dumps(existing))
        monkeypatch.setattr("plan_schedule.SCHEDULE_PATH", schedule_path)

        new_entries = [
            {"file": "articles/new1.md", "date": "2026-02-01"},
            {"file": "articles/existing.md", "date": "2026-01-01"},  # Duplicate
        ]
        result = merge_into_schedule(new_entries)
        assert len(result["articles"]) == 2  # 1 existing + 1 new
        files = [a["file"] for a in result["articles"]]
        assert "articles/new1.md" in files

    def test_creates_new_schedule_if_missing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        schedule_path = tmp_path / "nonexistent.json"
        monkeypatch.setattr("plan_schedule.SCHEDULE_PATH", schedule_path)

        new_entries = [{"file": "articles/first.md", "date": "2026-01-01"}]
        result = merge_into_schedule(new_entries)
        assert len(result["articles"]) == 1


# ---------------------------------------------------------------------------
# main (CLI integration)
# ---------------------------------------------------------------------------


class TestMain:
    def test_print_schedule(self, capsys: pytest.CaptureFixture[str]) -> None:
        from plan_schedule import main
        with patch("sys.argv", [
            "plan_schedule.py",
            "--start", "2026-03-01",
            "--slugs", "test-slug",
        ]):
            result = main()
        assert result == 0
        out = capsys.readouterr().out
        assert "test-slug" in out

    def test_merge_dry_run(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from plan_schedule import main
        schedule_path = tmp_path / "schedule.json"
        schedule_path.write_text('{"post_time_utc": "23:00", "articles": []}')
        monkeypatch.setattr("plan_schedule.SCHEDULE_PATH", schedule_path)
        with patch("sys.argv", [
            "plan_schedule.py",
            "--start", "2026-03-01",
            "--slugs", "new-article",
            "--merge", "--dry-run",
        ]):
            result = main()
        assert result == 0

    def test_merge_write(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from plan_schedule import main
        schedule_path = tmp_path / "schedule.json"
        schedule_path.write_text('{"post_time_utc": "23:00", "articles": []}')
        monkeypatch.setattr("plan_schedule.SCHEDULE_PATH", schedule_path)
        with patch("sys.argv", [
            "plan_schedule.py",
            "--start", "2026-03-01",
            "--slugs", "new-article",
            "--merge",
        ]):
            result = main()
        assert result == 0
        written = json.loads(schedule_path.read_text())
        assert len(written["articles"]) == 1

    def test_with_input_file(self, tmp_path: Path) -> None:
        from plan_schedule import main
        scores = [
            {"slug": "a", "total": 5, "search": 2, "anchor": 1, "ready": 1, "fresh": 1},
            {"slug": "b", "total": 3, "search": 1, "anchor": 1, "ready": 0, "fresh": 1},
        ]
        input_file = tmp_path / "scores.json"
        input_file.write_text(json.dumps(scores))
        with patch("sys.argv", [
            "plan_schedule.py",
            "--start", "2026-03-01",
            "--input", str(input_file),
        ]):
            result = main()
        assert result == 0

    def test_include_en(self, capsys: pytest.CaptureFixture[str]) -> None:
        from plan_schedule import main
        with patch("sys.argv", [
            "plan_schedule.py",
            "--start", "2026-03-01",
            "--slugs", "test-slug",
            "--include-en",
        ]):
            result = main()
        assert result == 0
        out = capsys.readouterr().out
        assert "articles-en/test-slug.md" in out
