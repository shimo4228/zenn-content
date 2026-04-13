"""Tests for scheduled_publish.py — scheduled publisher (Zenn + Dev.to)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import frontmatter
import pytest

from scheduled_publish import (
    _is_entry_done,
    _load_devto_key,
    _needs_posting,
    _process_entry,
    _process_zenn_entries,
    _publish_zenn_article,
    _should_skip_due_to_recent_zenn_publish,
    _try_publish,
    publish_due,
    show_status,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_ARTICLE = FIXTURES_DIR / "sample-article.md"

DEVTO_KEY = "test-devto-key"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_jp_entry(**overrides: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "file": "articles/test.md",
        "zenn_date": "2026-02-26",
        "date": "2026-02-26",
        "zenn_published": True,
    }
    defaults.update(overrides)
    return defaults


def _make_en_entry(**overrides: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "file": "articles-en/test.md",
        "date": "2026-02-26",
        "devto": "pending",
    }
    defaults.update(overrides)
    return defaults


# ---------------------------------------------------------------------------
# _needs_posting
# ---------------------------------------------------------------------------


class TestNeedsPosting:
    """_needs_posting should return True for values that need publishing."""

    @pytest.mark.parametrize("value", [None, "", "pending"])
    def test_needs_posting_true(self, value: str | None) -> None:
        assert _needs_posting(value) is True

    @pytest.mark.parametrize(
        "value",
        [
            "n/a",
            "https://dev.to/user/article-123",
            "some-other-truthy-value",
        ],
    )
    def test_needs_posting_false(self, value: str) -> None:
        assert _needs_posting(value) is False


# ---------------------------------------------------------------------------
# _is_entry_done
# ---------------------------------------------------------------------------


class TestIsEntryDone:
    """_is_entry_done checks completion for JP (Zenn) and EN (Dev.to) entries."""

    def test_jp_published_is_done(self) -> None:
        assert _is_entry_done(_make_jp_entry(zenn_published=True)) is True

    def test_jp_not_published_is_not_done(self) -> None:
        assert _is_entry_done(_make_jp_entry(zenn_published=False)) is False

    def test_jp_legacy_no_zenn_field_is_done(self) -> None:
        entry = {"file": "articles/old.md", "date": "2026-01-01"}
        assert _is_entry_done(entry) is True

    def test_en_with_url_is_done(self) -> None:
        assert _is_entry_done(_make_en_entry(devto="https://dev.to/x")) is True

    def test_en_pending_is_not_done(self) -> None:
        assert _is_entry_done(_make_en_entry(devto="pending")) is False

    def test_en_empty_is_not_done(self) -> None:
        assert _is_entry_done(_make_en_entry(devto="")) is False


# ---------------------------------------------------------------------------
# _process_entry (Dev.to only)
# ---------------------------------------------------------------------------


class TestProcessEntry:
    """_process_entry handles EN articles for Dev.to cross-posting."""

    @patch("scheduled_publish.validate_article_path")
    @patch("scheduled_publish.parse_zenn_article")
    @patch("scheduled_publish._try_publish")
    def test_pending_triggers_devto_publish(
        self,
        mock_try_publish: MagicMock,
        mock_parse: MagicMock,
        mock_validate: MagicMock,
    ) -> None:
        mock_validate.return_value = SAMPLE_ARTICLE
        mock_parse.return_value = MagicMock(title="Test Article")
        mock_try_publish.return_value = ("https://dev.to/user/new", False)

        entry = _make_en_entry(devto="pending")
        updated, errors = _process_entry(entry, DEVTO_KEY, dry_run=False)

        mock_try_publish.assert_called_once()
        assert "Dev.to" in mock_try_publish.call_args[0]
        assert updated["devto"] == "https://dev.to/user/new"
        assert errors == 0

    @patch("scheduled_publish.validate_article_path")
    @patch("scheduled_publish.parse_zenn_article")
    @patch("scheduled_publish._try_publish")
    def test_url_value_skips_publish(
        self,
        mock_try_publish: MagicMock,
        mock_parse: MagicMock,
        mock_validate: MagicMock,
    ) -> None:
        mock_validate.return_value = SAMPLE_ARTICLE
        mock_parse.return_value = MagicMock(title="Test Article")

        entry = _make_en_entry(devto="https://dev.to/existing")
        updated, errors = _process_entry(entry, DEVTO_KEY, dry_run=False)

        mock_try_publish.assert_not_called()
        assert errors == 0

    @patch("scheduled_publish.validate_article_path")
    @patch("scheduled_publish.parse_zenn_article")
    @patch("scheduled_publish._try_publish")
    def test_empty_string_triggers_publish(
        self,
        mock_try_publish: MagicMock,
        mock_parse: MagicMock,
        mock_validate: MagicMock,
    ) -> None:
        mock_validate.return_value = SAMPLE_ARTICLE
        mock_parse.return_value = MagicMock(title="Test Article")
        mock_try_publish.return_value = ("https://dev.to/new", False)

        entry = _make_en_entry(devto="")
        updated, errors = _process_entry(entry, DEVTO_KEY, dry_run=False)

        mock_try_publish.assert_called_once()
        assert updated["devto"] == "https://dev.to/new"

    @patch("scheduled_publish.validate_article_path")
    @patch("scheduled_publish.parse_zenn_article")
    @patch("scheduled_publish._try_publish")
    def test_no_canonical_url_passed(
        self,
        mock_try_publish: MagicMock,
        mock_parse: MagicMock,
        mock_validate: MagicMock,
    ) -> None:
        """Dev.to articles should be posted without canonical URL."""
        mock_validate.return_value = SAMPLE_ARTICLE
        mock_parse.return_value = MagicMock(title="Test Article")
        mock_try_publish.return_value = ("https://dev.to/new", False)

        entry = _make_en_entry(devto="pending")
        _process_entry(entry, DEVTO_KEY, dry_run=False)

        mock_try_publish.assert_called_once()


# ---------------------------------------------------------------------------
# Zenn publishing tests
# ---------------------------------------------------------------------------


class TestPublishZennArticle:
    """_publish_zenn_article frontmatter and git operations."""

    def test_already_published_skips(self, tmp_path: Path) -> None:
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\npublished: true\n---\nBody\n")
        result = _publish_zenn_article(article, dry_run=False)
        assert result is True

    def test_dry_run_does_not_modify_file(self, tmp_path: Path) -> None:
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\npublished: false\n---\nBody\n")
        result = _publish_zenn_article(article, dry_run=True)
        assert result is True
        post = frontmatter.load(article)
        assert post.metadata["published"] is False

    @patch("scheduled_publish._git_add_commit_push", return_value=True)
    def test_success_sets_published_true(
        self, mock_git: MagicMock, tmp_path: Path,
    ) -> None:
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\npublished: false\n---\nBody\n")

        with patch("scheduled_publish.REPO_ROOT", tmp_path):
            result = _publish_zenn_article(article, dry_run=False)

        assert result is True
        post = frontmatter.load(article)
        assert post.metadata["published"] is True
        mock_git.assert_called_once()

    @patch("scheduled_publish._git_add_commit_push", return_value=False)
    def test_git_failure_returns_false(
        self, mock_git: MagicMock, tmp_path: Path,
    ) -> None:
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\npublished: false\n---\nBody\n")

        with patch("scheduled_publish.REPO_ROOT", tmp_path):
            result = _publish_zenn_article(article, dry_run=False)

        assert result is False


class TestProcessZennEntries:
    """_process_zenn_entries filters and processes due Zenn articles."""

    @patch("scheduled_publish.save_schedule")
    @patch("scheduled_publish._publish_zenn_article", return_value=True)
    @patch("scheduled_publish.validate_article_path")
    def test_publishes_due_entry(
        self, mock_validate: MagicMock, mock_publish: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        mock_validate.return_value = Path("/fake/article.md")
        schedule = {
            "articles": [_make_jp_entry(zenn_published=False)],
        }
        with patch("scheduled_publish.date") as mock_date:
            mock_date.today.return_value = __import__("datetime").date(2026, 2, 28)
            mock_date.fromisoformat = __import__("datetime").date.fromisoformat
            updated, count, errors = _process_zenn_entries(schedule, dry_run=False)

        assert count == 1
        assert errors == 0
        assert updated["articles"][0]["zenn_published"] is True
        mock_publish.assert_called_once()
        mock_save.assert_called_once()

    @patch("scheduled_publish._publish_zenn_article")
    @patch("scheduled_publish.validate_article_path")
    def test_skips_already_published(
        self, mock_validate: MagicMock, mock_publish: MagicMock,
    ) -> None:
        schedule = {
            "articles": [_make_jp_entry(zenn_published=True)],
        }
        _, count, errors = _process_zenn_entries(schedule, dry_run=False)
        assert count == 0
        assert errors == 0
        mock_publish.assert_not_called()

    @patch("scheduled_publish._publish_zenn_article")
    @patch("scheduled_publish.validate_article_path")
    def test_skips_future_date(
        self, mock_validate: MagicMock, mock_publish: MagicMock,
    ) -> None:
        schedule = {
            "articles": [_make_jp_entry(
                zenn_date="2026-12-31", date="2026-12-31", zenn_published=False,
            )],
        }
        with patch("scheduled_publish.date") as mock_date:
            mock_date.today.return_value = __import__("datetime").date(2026, 2, 28)
            mock_date.fromisoformat = __import__("datetime").date.fromisoformat
            _, count, errors = _process_zenn_entries(schedule, dry_run=False)

        assert count == 0
        mock_publish.assert_not_called()

    @patch("scheduled_publish._publish_zenn_article")
    @patch("scheduled_publish.validate_article_path")
    def test_skips_en_entries(
        self, mock_validate: MagicMock, mock_publish: MagicMock,
    ) -> None:
        schedule = {
            "articles": [_make_en_entry()],
        }
        _, count, errors = _process_zenn_entries(schedule, dry_run=False)
        assert count == 0
        mock_publish.assert_not_called()


# ---------------------------------------------------------------------------
# show_status
# ---------------------------------------------------------------------------


class TestShowStatus:
    def test_logs_entries(self, caplog: pytest.LogCaptureFixture) -> None:
        schedule = {
            "articles": [
                _make_jp_entry(zenn_published=True),
                _make_en_entry(devto="https://dev.to/x"),
            ],
        }
        with caplog.at_level("INFO"):
            show_status(schedule)
        assert "articles/test.md" in caplog.text


# ---------------------------------------------------------------------------
# _try_publish
# ---------------------------------------------------------------------------


class TestTryPublish:
    def test_dry_run_returns_none(self, caplog: pytest.LogCaptureFixture) -> None:
        url, error = _try_publish(
            "Test", lambda: None,  # type: ignore[arg-type]
            dry_run=True, title="Test Title",
        )
        assert url is None
        assert error is False

    def test_success_returns_url(self) -> None:
        from publish import PublishResult
        url, error = _try_publish(
            "Test",
            lambda: PublishResult("test", True, "https://example.com", None),
            dry_run=False, title="Test",
        )
        assert url == "https://example.com"
        assert error is False

    def test_failure_returns_error(self) -> None:
        from publish import PublishResult
        url, error = _try_publish(
            "Test",
            lambda: PublishResult("test", False, None, "oops"),
            dry_run=False, title="Test",
        )
        assert url is None
        assert error is True


# ---------------------------------------------------------------------------
# _load_devto_key
# ---------------------------------------------------------------------------


class TestLoadDevtoKey:
    @patch.dict(os.environ, {"DEVTO_API_KEY": "test-key"}, clear=True)
    def test_returns_key(self) -> None:
        assert _load_devto_key() == "test-key"

    @patch("scheduled_publish._load_env")
    @patch.dict(os.environ, {}, clear=True)
    def test_returns_none_when_missing(self, mock_env: MagicMock) -> None:
        assert _load_devto_key() is None


# ---------------------------------------------------------------------------
# publish_due (integration-level)
# ---------------------------------------------------------------------------


class TestPublishDue:
    @patch("scheduled_publish._load_devto_key", return_value=None)
    @patch("scheduled_publish._process_zenn_entries")
    def test_returns_1_on_missing_devto_key(
        self, mock_zenn: MagicMock, mock_key: MagicMock,
    ) -> None:
        mock_zenn.return_value = ({"articles": []}, 0, 0)
        result = publish_due({"articles": []})
        assert result == 1

    @patch("scheduled_publish.save_schedule")
    @patch("scheduled_publish._process_entry")
    @patch("scheduled_publish._load_devto_key", return_value="key")
    @patch("scheduled_publish._process_zenn_entries")
    def test_processes_due_en_entries(
        self, mock_zenn: MagicMock, mock_key: MagicMock,
        mock_entry: MagicMock, mock_save: MagicMock,
    ) -> None:
        en_entry = _make_en_entry(devto="pending")
        mock_zenn.return_value = ({"articles": [en_entry]}, 0, 0)
        mock_entry.return_value = ({**en_entry, "devto": "https://dev.to/x"}, 0)
        with patch("scheduled_publish.date") as mock_date:
            mock_date.today.return_value = __import__("datetime").date(2026, 2, 28)
            mock_date.fromisoformat = __import__("datetime").date.fromisoformat
            result = publish_due({"articles": [en_entry]})
        assert result == 0
