"""Tests for devto_crosspost.py — Dev.to-only scheduled cross-post."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from devto_crosspost import (
    _is_done,
    _is_en_entry,
    _needs_posting,
    _process_entry,
    publish_due,
    show_status,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_ARTICLE = FIXTURES_DIR / "sample-article.md"

DEVTO_KEY = "test-devto-key"


def _en(**overrides: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "file": "articles-en/test.md",
        "date": "2026-02-26",
        "devto": "pending",
    }
    defaults.update(overrides)
    return defaults


def _jp(**overrides: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "file": "articles/test.md",
        "date": "2026-02-26",
    }
    defaults.update(overrides)
    return defaults


class TestNeedsPosting:
    @pytest.mark.parametrize("value", [None, "", "pending"])
    def test_true(self, value: str | None) -> None:
        assert _needs_posting(value) is True

    @pytest.mark.parametrize("value", ["https://dev.to/user/x", "n/a"])
    def test_false(self, value: str) -> None:
        assert _needs_posting(value) is False


class TestIsEnEntry:
    def test_en_path(self) -> None:
        assert _is_en_entry(_en()) is True

    def test_jp_path(self) -> None:
        assert _is_en_entry(_jp()) is False

    def test_missing_file(self) -> None:
        assert _is_en_entry({"date": "2026-01-01"}) is False


class TestIsDone:
    def test_posted(self) -> None:
        assert _is_done(_en(devto="https://dev.to/user/x")) is True

    def test_pending(self) -> None:
        assert _is_done(_en(devto="pending")) is False

    def test_empty(self) -> None:
        assert _is_done(_en(devto="")) is False

    def test_none(self) -> None:
        assert _is_done(_en(devto=None)) is False


class TestProcessEntry:
    @patch("devto_crosspost.validate_article_path")
    @patch("devto_crosspost.parse_zenn_article")
    @patch("devto_crosspost._try_publish")
    def test_pending_triggers_publish(
        self,
        mock_try_publish: MagicMock,
        mock_parse: MagicMock,
        mock_validate: MagicMock,
    ) -> None:
        mock_validate.return_value = SAMPLE_ARTICLE
        mock_parse.return_value = MagicMock(title="Test Article")
        mock_try_publish.return_value = ("https://dev.to/user/new", False)

        updated, errors = _process_entry(_en(devto="pending"), DEVTO_KEY, dry_run=False)

        mock_try_publish.assert_called_once()
        assert updated["devto"] == "https://dev.to/user/new"
        assert errors == 0

    @patch("devto_crosspost.validate_article_path", return_value=None)
    def test_missing_article_returns_error(
        self, _mock_validate: MagicMock,
    ) -> None:
        updated, errors = _process_entry(
            _en(file="articles-en/missing.md"), DEVTO_KEY, dry_run=False,
        )
        assert errors == 1
        assert updated == _en(file="articles-en/missing.md")

    @patch("devto_crosspost.validate_article_path")
    @patch("devto_crosspost.parse_zenn_article")
    @patch("devto_crosspost._try_publish")
    def test_publish_failure_increments_errors(
        self,
        mock_try_publish: MagicMock,
        mock_parse: MagicMock,
        mock_validate: MagicMock,
    ) -> None:
        mock_validate.return_value = SAMPLE_ARTICLE
        mock_parse.return_value = MagicMock(title="Test Article")
        mock_try_publish.return_value = (None, True)

        updated, errors = _process_entry(_en(), DEVTO_KEY, dry_run=False)
        assert errors == 1
        assert "devto" not in updated or updated["devto"] == "pending"

    @patch("devto_crosspost.validate_article_path")
    @patch("devto_crosspost.parse_zenn_article")
    @patch("devto_crosspost._try_publish")
    def test_dry_run_does_not_modify_entry(
        self,
        mock_try_publish: MagicMock,
        mock_parse: MagicMock,
        mock_validate: MagicMock,
    ) -> None:
        mock_validate.return_value = SAMPLE_ARTICLE
        mock_parse.return_value = MagicMock(title="Test Article")
        mock_try_publish.return_value = (None, False)  # dry-run returns no URL

        entry = _en()
        updated, errors = _process_entry(entry, DEVTO_KEY, dry_run=True)

        assert errors == 0
        assert updated == entry


class TestPublishDue:
    @patch("devto_crosspost._load_devto_key", return_value=None)
    def test_missing_key_returns_error(self, _mock_key: MagicMock) -> None:
        assert publish_due({"articles": []}) == 1

    @patch("devto_crosspost.save_schedule")
    @patch("devto_crosspost._load_devto_key", return_value=DEVTO_KEY)
    @patch("devto_crosspost._process_entry")
    def test_skips_jp_entries(
        self,
        mock_process: MagicMock,
        _mock_key: MagicMock,
        _mock_save: MagicMock,
    ) -> None:
        schedule = {"articles": [_jp(), _jp(file="articles/other.md")]}
        rc = publish_due(schedule, dry_run=False)
        mock_process.assert_not_called()
        assert rc == 0

    @patch("devto_crosspost.save_schedule")
    @patch("devto_crosspost._load_devto_key", return_value=DEVTO_KEY)
    @patch("devto_crosspost._process_entry")
    def test_skips_done_entries(
        self,
        mock_process: MagicMock,
        _mock_key: MagicMock,
        _mock_save: MagicMock,
    ) -> None:
        schedule = {"articles": [_en(devto="https://dev.to/user/x")]}
        rc = publish_due(schedule, dry_run=False)
        mock_process.assert_not_called()
        assert rc == 0

    @patch("devto_crosspost.save_schedule")
    @patch("devto_crosspost._load_devto_key", return_value=DEVTO_KEY)
    @patch("devto_crosspost._process_entry")
    def test_skips_future_entries(
        self,
        mock_process: MagicMock,
        _mock_key: MagicMock,
        _mock_save: MagicMock,
    ) -> None:
        future_entry = _en(date="2099-12-31")
        schedule = {"articles": [future_entry]}
        rc = publish_due(schedule, dry_run=False)
        mock_process.assert_not_called()
        assert rc == 0

    @patch("devto_crosspost.save_schedule")
    @patch("devto_crosspost._load_devto_key", return_value=DEVTO_KEY)
    @patch("devto_crosspost._process_entry")
    def test_processes_due_en_entry(
        self,
        mock_process: MagicMock,
        _mock_key: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        entry = _en(date="2026-01-01")  # past
        expected_updated = {**entry, "devto": "https://dev.to/user/new"}
        mock_process.return_value = (expected_updated, 0)

        schedule = {"articles": [entry]}
        rc = publish_due(schedule, dry_run=False)

        mock_process.assert_called_once()
        assert rc == 0
        # save_schedule called at least once (incremental + final)
        assert mock_save.call_count >= 1

    @patch("devto_crosspost.save_schedule")
    @patch("devto_crosspost._load_devto_key", return_value=DEVTO_KEY)
    @patch("devto_crosspost._process_entry")
    def test_error_returns_nonzero_exit_code(
        self,
        mock_process: MagicMock,
        _mock_key: MagicMock,
        _mock_save: MagicMock,
    ) -> None:
        entry = _en(date="2026-01-01")
        mock_process.return_value = (entry, 1)  # no URL change, 1 error

        rc = publish_due({"articles": [entry]}, dry_run=False)
        assert rc == 1

    @patch("devto_crosspost.save_schedule")
    @patch("devto_crosspost._load_devto_key", return_value=DEVTO_KEY)
    @patch("devto_crosspost._process_entry")
    def test_dry_run_does_not_save(
        self,
        mock_process: MagicMock,
        _mock_key: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        entry = _en(date="2026-01-01")
        mock_process.return_value = (entry, 0)

        publish_due({"articles": [entry]}, dry_run=True)
        mock_save.assert_not_called()


class TestShowStatus:
    def test_runs_without_error(self, caplog: pytest.LogCaptureFixture) -> None:
        schedule = {
            "articles": [
                _en(date="2026-01-01", devto="https://dev.to/user/x"),
                _en(date="2099-12-31", devto="pending"),
                _jp(date="2026-01-01"),
            ],
        }
        # Should not raise
        show_status(schedule)
