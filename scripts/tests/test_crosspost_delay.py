"""Tests for cross-post delay feature — TDD Phase 2 (Implementation).

This module tests:
1. Skipping entries recently published to Zenn (within 30 minutes)
2. Scheduling delayed cross-post from zenn_publish.py
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from scheduled_publish import _should_skip_due_to_recent_zenn_publish


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def _make_entry_with_zenn_publish_time(
    zenn_date: str = "2026-03-03",
    zenn_published: bool = False,
    zenn_published_at: str | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    """Create a schedule entry with optional Zenn publish timestamp."""
    entry: dict[str, Any] = {
        "file": "articles/test.md",
        "canonical_url": "https://zenn.dev/shimo4228/articles/test",
        "zenn_date": zenn_date,
        "date": zenn_date,
        "zenn_published": zenn_published,
        "qiita": None,
        "devto": "n/a",
        "hashnode": "n/a",
    }
    if zenn_published_at:
        entry["zenn_published_at"] = zenn_published_at
    entry.update(overrides)
    return entry


# ---------------------------------------------------------------------------
# Phase 2: Tests for "skip recently published" feature
# ---------------------------------------------------------------------------


class TestSkipRecentlyPublished:
    """Tests for skipping entries published to Zenn within last 15 minutes."""

    def test_entry_published_5_minutes_ago_is_skipped(self) -> None:
        """Entry published 5 minutes ago should be skipped (too recent)."""
        five_minutes_ago = (datetime.now() - timedelta(minutes=5)).isoformat()
        entry = _make_entry_with_zenn_publish_time(
            zenn_published=True,
            zenn_published_at=five_minutes_ago,
        )
        
        result = _should_skip_due_to_recent_zenn_publish(entry)
        
        assert result is True

    def test_entry_published_35_minutes_ago_is_not_skipped(self) -> None:
        """Entry published 35 minutes ago should NOT be skipped (safe to cross-post)."""
        thirty_five_minutes_ago = (datetime.now() - timedelta(minutes=35)).isoformat()
        entry = _make_entry_with_zenn_publish_time(
            zenn_published=True,
            zenn_published_at=thirty_five_minutes_ago,
        )
        
        result = _should_skip_due_to_recent_zenn_publish(entry)
        
        assert result is False

    def test_entry_without_zenn_published_at_is_not_skipped(self) -> None:
        """Entry without timestamp should NOT be skipped (backward compatibility)."""
        entry = _make_entry_with_zenn_publish_time(
            zenn_published=True,
            zenn_published_at=None,
        )
        
        result = _should_skip_due_to_recent_zenn_publish(entry)
        
        assert result is False

    def test_entry_not_yet_published_is_not_skipped(self) -> None:
        """Entry not yet published to Zenn should NOT be skipped."""
        entry = _make_entry_with_zenn_publish_time(
            zenn_published=False,
            zenn_published_at=None,
        )
        
        result = _should_skip_due_to_recent_zenn_publish(entry)
        
        assert result is False

    def test_entry_with_invalid_timestamp_is_not_skipped(self) -> None:
        """Entry with invalid timestamp should NOT be skipped (safe default)."""
        entry = _make_entry_with_zenn_publish_time(
            zenn_published=True,
            zenn_published_at="invalid-timestamp",
        )
        
        result = _should_skip_due_to_recent_zenn_publish(entry)
        
        assert result is False


# ---------------------------------------------------------------------------
# Phase 2: Tests for "schedule delayed cross-post" feature
# These require importing from zenn_publish
# ---------------------------------------------------------------------------


class TestScheduleDelayedCrosspost:
    """Tests for scheduling cross-post after delay from zenn_publish.py."""

    @patch("zenn_publish.subprocess.run")
    def test_schedule_delayed_crosspost_creates_job(self, mock_run: MagicMock) -> None:
        """schedule_delayed_crosspost should create a delayed job using `at` command."""
        from zenn_publish import schedule_crosspost_after_delay
        
        mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")
        
        schedule_crosspost_after_delay(delay_minutes=15, dry_run=False)
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        # Check that 'at' command is called with correct arguments
        assert call_args[0][0] == ["at", "now + 15 minutes"]
        # Check that the command script is passed via input
        assert "scheduled_publish.py" in call_args[1].get("input", "")

    def test_schedule_delayed_crosspost_respects_dry_run(self) -> None:
        """schedule_delayed_crosspost in dry-run mode should not actually schedule."""
        from zenn_publish import schedule_crosspost_after_delay
        
        with patch("zenn_publish.subprocess.run") as mock_run:
            with patch("zenn_publish.logger") as mock_logger:
                schedule_crosspost_after_delay(delay_minutes=15, dry_run=True)
                
                mock_run.assert_not_called()
                mock_logger.info.assert_called_once()
                assert "DRY-RUN" in mock_logger.info.call_args[0][0]


# ---------------------------------------------------------------------------
# Phase 2: Tests for "prevent duplicate processing" feature
# ---------------------------------------------------------------------------


class TestPreventDuplicateProcessing:
    """Tests for preventing duplicate cross-post when both 7:00 and 9:00 jobs run."""

    def test_9am_job_skips_entry_already_posted_at_715am(self) -> None:
        """9:00 job should skip entry already cross-posted at 7:15."""
        # Entry that was Zenn published at 7:00
        # If we check at 7:05 (within 15 minutes), it should be skipped
        five_minutes_ago = (datetime.now() - timedelta(minutes=5)).isoformat()
        entry = _make_entry_with_zenn_publish_time(
            zenn_published=True,
            zenn_published_at=five_minutes_ago,
        )
        
        result = _should_skip_due_to_recent_zenn_publish(entry)
        
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
