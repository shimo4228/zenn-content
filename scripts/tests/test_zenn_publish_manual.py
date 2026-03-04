"""Tests for zenn_publish.py — manual publish tracking with zenn_published_at.

Tests the scenario where article is manually set to published: true and pushed,
then zenn_publish.py syncs the tracking flag and records timestamp.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Phase 1: Test for manual publish timestamp recording
# ---------------------------------------------------------------------------


class TestManualPublishTimestampRecording:
    """Tests that zenn_published_at is recorded even for manually published articles."""

    @patch("zenn_publish._is_published")
    @patch("zenn_publish._get_actual_publish_time")
    def test_manual_publish_records_timestamp_when_missing(
        self, mock_get_time: MagicMock, mock_is_published: MagicMock
    ) -> None:
        """When article is already published in file but has no timestamp, record now."""
        from zenn_publish import publish_due

        # Setup: Article already published in file (manual publish)
        mock_is_published.return_value = True
        mock_get_time.return_value = "2026-03-03T07:00:00"

        # Entry with zenn_published=False but file already has published: true
        schedule = {
            "articles": [
                {
                    "file": "articles/test.md",
                    "zenn_date": "2026-03-03",
                    "zenn_published": False,  # Tracking flag not synced yet
                    # zenn_published_at is missing!
                }
            ]
        }

        with patch("zenn_publish._validate_article_path") as mock_validate:
            with patch("zenn_publish.save_schedule") as mock_save:
                mock_validate.return_value = Path("/fake/test.md")

                publish_due(schedule, dry_run=False)

                # Verify _get_actual_publish_time was called with correct args
                mock_get_time.assert_called_once_with("articles/test.md", "2026-03-03")

                # Verify save_schedule was called with zenn_published_at
                mock_save.assert_called_once()
                saved_schedule = mock_save.call_args[0][0]

                assert "zenn_published_at" in saved_schedule["articles"][0]
                assert saved_schedule["articles"][0]["zenn_published_at"] == "2026-03-03T07:00:00"
                assert saved_schedule["articles"][0]["zenn_published"] is True

    @patch("zenn_publish._is_published")
    def test_manual_publish_preserves_existing_timestamp(
        self, mock_is_published: MagicMock
    ) -> None:
        """When article already has zenn_published_at, don't overwrite it."""
        from zenn_publish import publish_due
        
        mock_is_published.return_value = True
        
        # Entry with existing timestamp
        schedule = {
            "articles": [
                {
                    "file": "articles/test.md",
                    "zenn_date": "2026-03-03",
                    "zenn_published": False,
                    "zenn_published_at": "2026-03-03T07:00:00",  # Existing timestamp
                }
            ]
        }
        
        with patch("zenn_publish._validate_article_path") as mock_validate:
            with patch("zenn_publish.save_schedule") as mock_save:
                mock_validate.return_value = Path("/fake/test.md")
                
                publish_due(schedule, dry_run=False)
                
                saved_schedule = mock_save.call_args[0][0]
                # Should preserve original timestamp
                assert saved_schedule["articles"][0]["zenn_published_at"] == "2026-03-03T07:00:00"

    @patch("zenn_publish._is_published")
    def test_normal_publish_records_timestamp_via_changed_path(
        self, mock_is_published: MagicMock
    ) -> None:
        """Normal automated publish should also record timestamp (existing behavior)."""
        from zenn_publish import publish_due
        
        # Setup: Article not yet published in file
        mock_is_published.return_value = False
        
        schedule = {
            "articles": [
                {
                    "file": "articles/test.md",
                    "zenn_date": "2026-03-03",
                    "zenn_published": False,
                }
            ]
        }
        
        with patch("zenn_publish._validate_article_path") as mock_validate:
            with patch("zenn_publish._set_published") as mock_set:
                with patch("zenn_publish._git_add_commit_push") as mock_git:
                    with patch("zenn_publish.save_schedule") as mock_save:
                        with patch("zenn_publish.datetime") as mock_datetime:
                            mock_validate.return_value = Path("/fake/test.md")
                            mock_set.return_value = True
                            mock_git.return_value = True
                            mock_now = MagicMock()
                            mock_now.isoformat.return_value = "2026-03-03T07:00:00"
                            mock_datetime.now.return_value = mock_now
                            
                            publish_due(schedule, dry_run=False)
                            
                            saved_schedule = mock_save.call_args[0][0]
                            assert "zenn_published_at" in saved_schedule["articles"][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
