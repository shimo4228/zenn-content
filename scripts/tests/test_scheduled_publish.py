"""Tests for scheduled_publish.py — scheduled cross-post publisher."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from scheduled_publish import (
    _is_entry_done,
    _needs_posting,
    _process_entry,
    _Credentials,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_ARTICLE = FIXTURES_DIR / "sample-article.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_entry(**overrides: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "file": "articles/test.md",
        "date": "2026-02-26",
        "canonical_url": "https://zenn.dev/shimo4228/articles/test",
        "qiita": "pending",
        "devto": "pending",
        "hashnode": "pending",
    }
    defaults.update(overrides)
    return defaults


def _make_creds() -> _Credentials:
    return _Credentials(
        qiita_token="test-qiita-token",
        devto_key="test-devto-key",
        hashnode_token="test-hashnode-token",
        hashnode_pub_id="test-pub-id",
    )


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
            "https://qiita.com/items/abc123",
            "https://dev.to/user/article-123",
            "https://hashnode.dev/post-abc",
            "some-other-truthy-value",
        ],
    )
    def test_needs_posting_false(self, value: str) -> None:
        assert _needs_posting(value) is False


# ---------------------------------------------------------------------------
# _is_entry_done / _needs_posting consistency
# ---------------------------------------------------------------------------


class TestSemanticConsistency:
    """_is_entry_done and _needs_posting must agree on platform value semantics."""

    @pytest.mark.parametrize(
        "value,expect_needs,expect_done",
        [
            (None, True, False),
            ("", True, False),
            ("pending", True, False),
            ("n/a", False, True),
            ("https://example.com/article", False, True),
        ],
    )
    def test_complementary_semantics(
        self, value: str | None, expect_needs: bool, expect_done: bool
    ) -> None:
        """For any single-platform entry, _needs_posting and _is_entry_done
        should give complementary answers."""
        assert _needs_posting(value) is expect_needs

        # Build a single-platform entry (devto only) to test _is_entry_done
        entry: dict[str, Any] = {
            "file": "articles/test.md",
            "date": "2026-02-26",
            "devto": value,
            "hashnode": "n/a",  # mark other platforms as done
        }
        assert _is_entry_done(entry) is expect_done


# ---------------------------------------------------------------------------
# _process_entry with "pending" values
# ---------------------------------------------------------------------------


class TestProcessEntryPending:
    """_process_entry must attempt publishing when platform values are 'pending'."""

    @patch("scheduled_publish._validate_article_path")
    @patch("scheduled_publish.parse_zenn_article")
    @patch("scheduled_publish._try_publish")
    def test_pending_triggers_qiita_publish(
        self,
        mock_try_publish: MagicMock,
        mock_parse: MagicMock,
        mock_validate: MagicMock,
    ) -> None:
        mock_validate.return_value = SAMPLE_ARTICLE
        mock_parse.return_value = MagicMock(title="テスト記事")
        mock_try_publish.return_value = ("https://qiita.com/items/new", False)

        entry = _make_entry(qiita="pending", devto="n/a", hashnode="n/a")
        updated, errors = _process_entry(entry, _make_creds(), dry_run=False)

        # _try_publish should have been called for Qiita
        mock_try_publish.assert_called_once()
        call_args = mock_try_publish.call_args
        assert call_args[1]["title"] == "テスト記事"
        assert "Qiita" in call_args[0]
        assert updated["qiita"] == "https://qiita.com/items/new"
        assert errors == 0

    @patch("scheduled_publish._validate_article_path")
    @patch("scheduled_publish.parse_zenn_article")
    @patch("scheduled_publish._try_publish")
    def test_pending_triggers_all_platforms(
        self,
        mock_try_publish: MagicMock,
        mock_parse: MagicMock,
        mock_validate: MagicMock,
    ) -> None:
        mock_validate.return_value = SAMPLE_ARTICLE
        mock_parse.return_value = MagicMock(title="テスト記事")
        mock_try_publish.side_effect = [
            ("https://qiita.com/items/new", False),
            ("https://dev.to/user/new-article", False),
            ("https://hashnode.dev/new-post", False),
        ]

        entry = _make_entry(qiita="pending", devto="pending", hashnode="pending")
        updated, errors = _process_entry(entry, _make_creds(), dry_run=False)

        assert mock_try_publish.call_count == 3
        assert updated["qiita"] == "https://qiita.com/items/new"
        assert updated["devto"] == "https://dev.to/user/new-article"
        assert updated["hashnode"] == "https://hashnode.dev/new-post"
        assert errors == 0

    @patch("scheduled_publish._validate_article_path")
    @patch("scheduled_publish.parse_zenn_article")
    @patch("scheduled_publish._try_publish")
    def test_url_value_skips_publish(
        self,
        mock_try_publish: MagicMock,
        mock_parse: MagicMock,
        mock_validate: MagicMock,
    ) -> None:
        """Already-posted platforms (URL values) should NOT trigger publishing."""
        mock_validate.return_value = SAMPLE_ARTICLE
        mock_parse.return_value = MagicMock(title="テスト記事")

        entry = _make_entry(
            qiita="https://qiita.com/existing",
            devto="https://dev.to/existing",
            hashnode="https://hashnode.dev/existing",
        )
        updated, errors = _process_entry(entry, _make_creds(), dry_run=False)

        mock_try_publish.assert_not_called()
        assert errors == 0

    @patch("scheduled_publish._validate_article_path")
    @patch("scheduled_publish.parse_zenn_article")
    @patch("scheduled_publish._try_publish")
    def test_na_value_skips_publish(
        self,
        mock_try_publish: MagicMock,
        mock_parse: MagicMock,
        mock_validate: MagicMock,
    ) -> None:
        """Platforms marked 'n/a' should NOT trigger publishing."""
        mock_validate.return_value = SAMPLE_ARTICLE
        mock_parse.return_value = MagicMock(title="テスト記事")

        # Entry without qiita key, devto/hashnode = "n/a"
        entry = _make_entry(devto="n/a", hashnode="n/a")
        del entry["qiita"]
        updated, errors = _process_entry(entry, _make_creds(), dry_run=False)

        mock_try_publish.assert_not_called()
        assert errors == 0

    @patch("scheduled_publish._validate_article_path")
    @patch("scheduled_publish.parse_zenn_article")
    @patch("scheduled_publish._try_publish")
    def test_empty_string_triggers_publish(
        self,
        mock_try_publish: MagicMock,
        mock_parse: MagicMock,
        mock_validate: MagicMock,
    ) -> None:
        """Empty string values should also trigger publishing (same as pending)."""
        mock_validate.return_value = SAMPLE_ARTICLE
        mock_parse.return_value = MagicMock(title="テスト記事")
        mock_try_publish.return_value = ("https://dev.to/new", False)

        entry = _make_entry(devto="", hashnode="n/a")
        del entry["qiita"]
        updated, errors = _process_entry(entry, _make_creds(), dry_run=False)

        mock_try_publish.assert_called_once()
        assert updated["devto"] == "https://dev.to/new"
