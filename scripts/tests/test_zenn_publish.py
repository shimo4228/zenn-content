"""Tests for zenn_publish.py — Zenn auto-publisher core functions."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zenn_publish import (
    _already_published_today,
    _get_actual_publish_time,
    _git_add_commit_push,
    _is_published,
    _set_published,
    publish_due,
    show_status,
)


# ---------------------------------------------------------------------------
# _is_published
# ---------------------------------------------------------------------------


class TestIsPublished:
    def test_true_when_published(self, tmp_path: Path) -> None:
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\npublished: true\n---\nBody\n")
        assert _is_published(article) is True

    def test_false_when_not_published(self, tmp_path: Path) -> None:
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\npublished: false\n---\nBody\n")
        assert _is_published(article) is False

    def test_false_when_no_published_field(self, tmp_path: Path) -> None:
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\n---\nBody\n")
        assert _is_published(article) is False


# ---------------------------------------------------------------------------
# _set_published
# ---------------------------------------------------------------------------


class TestSetPublished:
    def test_sets_true(self, tmp_path: Path) -> None:
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\npublished: false\n---\nBody\n")
        result = _set_published(article, dry_run=False)
        assert result is True
        content = article.read_text()
        assert "published: true" in content

    def test_dry_run_does_not_modify(self, tmp_path: Path) -> None:
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\npublished: false\n---\nBody\n")
        result = _set_published(article, dry_run=True)
        assert result is True
        assert "published: false" in article.read_text()

    def test_returns_false_when_already_true(self, tmp_path: Path) -> None:
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\npublished: true\n---\nBody\n")
        result = _set_published(article, dry_run=False)
        assert result is False


# ---------------------------------------------------------------------------
# _git_add_commit_push
# ---------------------------------------------------------------------------


class TestGitAddCommitPush:
    def test_dry_run(self) -> None:
        result = _git_add_commit_push(["test.md"], "msg", dry_run=True)
        assert result is True

    @patch("zenn_publish.subprocess.run")
    def test_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0)
        result = _git_add_commit_push(["test.md"], "msg", dry_run=False)
        assert result is True
        assert mock_run.call_count == 4  # add, commit, pull, push

    @patch("zenn_publish.subprocess.run")
    def test_git_error(self, mock_run: MagicMock) -> None:
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr="error")
        result = _git_add_commit_push(["test.md"], "msg", dry_run=False)
        assert result is False

    @patch("zenn_publish.subprocess.run")
    def test_timeout(self, mock_run: MagicMock) -> None:
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("git", 60)
        result = _git_add_commit_push(["test.md"], "msg", dry_run=False)
        assert result is False


# ---------------------------------------------------------------------------
# _get_actual_publish_time
# ---------------------------------------------------------------------------


class TestGetActualPublishTime:
    @patch("zenn_publish.subprocess.run")
    def test_uses_git_log(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="2026-03-03T07:00:00+09:00\n")
        result = _get_actual_publish_time("articles/test.md")
        assert "2026-03-03" in result

    @patch("zenn_publish.subprocess.run")
    def test_falls_back_to_zenn_date(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="")
        result = _get_actual_publish_time("articles/test.md", "2026-03-03")
        assert result == "2026-03-03T07:00:00"

    @patch("zenn_publish.subprocess.run")
    def test_falls_back_to_now(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="")
        result = _get_actual_publish_time("articles/test.md")
        # Should return an ISO format string
        assert "T" in result


# ---------------------------------------------------------------------------
# _already_published_today
# ---------------------------------------------------------------------------


class TestAlreadyPublishedToday:
    def test_true_when_published_today(self) -> None:
        today = date.today().isoformat()
        articles = [{"zenn_published_at": f"{today}T07:00:00"}]
        assert _already_published_today(articles) is True

    def test_false_when_published_yesterday(self) -> None:
        articles = [{"zenn_published_at": "2020-01-01T07:00:00"}]
        assert _already_published_today(articles) is False

    def test_false_when_no_timestamp(self) -> None:
        articles = [{"file": "test.md"}]
        assert _already_published_today(articles) is False


# ---------------------------------------------------------------------------
# show_status
# ---------------------------------------------------------------------------


class TestShowStatus:
    @patch("zenn_publish.validate_article_path")
    @patch("zenn_publish._is_published")
    def test_logs_entries(
        self, mock_is_pub: MagicMock, mock_validate: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mock_validate.return_value = Path("/fake/test.md")
        mock_is_pub.return_value = True
        schedule = {
            "articles": [
                {
                    "file": "articles/test.md",
                    "zenn_date": "2026-03-03",
                    "zenn_published": True,
                },
            ],
        }
        with caplog.at_level("INFO"):
            show_status(schedule)
        assert "articles/test.md" in caplog.text


# ---------------------------------------------------------------------------
# publish_due (unit-level)
# ---------------------------------------------------------------------------


class TestPublishDue:
    @patch("zenn_publish.validate_article_path", return_value=None)
    def test_skips_missing_files(self, mock_validate: MagicMock) -> None:
        schedule = {
            "articles": [
                {
                    "file": "articles/missing.md",
                    "zenn_date": "2026-01-01",
                    "zenn_published": False,
                },
            ],
        }
        result = publish_due(schedule, dry_run=False)
        assert result == 1  # Error due to missing file
