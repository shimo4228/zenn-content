"""Tests for scheduled_publish.py — scheduled cross-post publisher."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import frontmatter
import pytest

from scheduled_publish import (
    _is_entry_done,
    _needs_posting,
    _process_entry,
    _process_zenn_entries,
    _publish_zenn_article,
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


# ---------------------------------------------------------------------------
# Zenn publishing tests
# ---------------------------------------------------------------------------


class TestPublishZennArticle:
    """_publish_zenn_article frontmatter and git operations."""

    def test_already_published_skips(self, tmp_path: Path) -> None:
        """If frontmatter already has published: true, skip everything."""
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\npublished: true\n---\nBody\n")
        result = _publish_zenn_article(article, dry_run=False)
        assert result is True

    def test_dry_run_does_not_modify_file(self, tmp_path: Path) -> None:
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\npublished: false\n---\nBody\n")
        result = _publish_zenn_article(article, dry_run=True)
        assert result is True
        # File should remain unchanged
        post = frontmatter.load(article)
        assert post.metadata["published"] is False

    @patch("scheduled_publish.subprocess.run")
    def test_success_sets_published_true(
        self, mock_run: MagicMock, tmp_path: Path,
    ) -> None:
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\npublished: false\n---\nBody\n")

        with patch("scheduled_publish.REPO_ROOT", tmp_path):
            result = _publish_zenn_article(article, dry_run=False)

        assert result is True
        post = frontmatter.load(article)
        assert post.metadata["published"] is True
        assert mock_run.call_count == 3  # git add, commit, push

    @patch("scheduled_publish.subprocess.run")
    def test_git_failure_returns_false(
        self, mock_run: MagicMock, tmp_path: Path,
    ) -> None:
        import subprocess

        article = tmp_path / "test.md"
        article.write_text("---\ntitle: Test\npublished: false\n---\nBody\n")
        mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr=b"error")

        with patch("scheduled_publish.REPO_ROOT", tmp_path):
            result = _publish_zenn_article(article, dry_run=False)

        assert result is False


class TestProcessZennEntries:
    """_process_zenn_entries filters and processes due Zenn articles."""

    @patch("scheduled_publish.save_schedule")
    @patch("scheduled_publish._publish_zenn_article", return_value=True)
    @patch("scheduled_publish._validate_article_path")
    def test_publishes_due_entry(
        self, mock_validate: MagicMock, mock_publish: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        mock_validate.return_value = Path("/fake/article.md")
        schedule = {
            "articles": [
                {
                    "file": "articles/test.md",
                    "date": "2026-02-01",
                    "zenn_date": "2026-02-01",
                    "zenn_published": False,
                    "devto": "n/a",
                    "hashnode": "n/a",
                },
            ],
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
    @patch("scheduled_publish._validate_article_path")
    def test_skips_already_published(
        self, mock_validate: MagicMock, mock_publish: MagicMock,
    ) -> None:
        schedule = {
            "articles": [
                {
                    "file": "articles/test.md",
                    "date": "2026-02-01",
                    "zenn_date": "2026-02-01",
                    "zenn_published": True,
                    "devto": "n/a",
                    "hashnode": "n/a",
                },
            ],
        }
        _, count, errors = _process_zenn_entries(schedule, dry_run=False)
        assert count == 0
        assert errors == 0
        mock_publish.assert_not_called()

    @patch("scheduled_publish._publish_zenn_article")
    @patch("scheduled_publish._validate_article_path")
    def test_skips_future_date(
        self, mock_validate: MagicMock, mock_publish: MagicMock,
    ) -> None:
        schedule = {
            "articles": [
                {
                    "file": "articles/test.md",
                    "date": "2026-12-31",
                    "zenn_date": "2026-12-31",
                    "zenn_published": False,
                    "devto": "n/a",
                    "hashnode": "n/a",
                },
            ],
        }
        with patch("scheduled_publish.date") as mock_date:
            mock_date.today.return_value = __import__("datetime").date(2026, 2, 28)
            mock_date.fromisoformat = __import__("datetime").date.fromisoformat
            _, count, errors = _process_zenn_entries(schedule, dry_run=False)

        assert count == 0
        mock_publish.assert_not_called()

    @patch("scheduled_publish._publish_zenn_article")
    @patch("scheduled_publish._validate_article_path")
    def test_skips_entries_without_zenn_date(
        self, mock_validate: MagicMock, mock_publish: MagicMock,
    ) -> None:
        schedule = {
            "articles": [
                {
                    "file": "articles-en/test.md",
                    "date": "2026-02-01",
                    "devto": "pending",
                    "hashnode": "pending",
                },
            ],
        }
        _, count, errors = _process_zenn_entries(schedule, dry_run=False)
        assert count == 0
        mock_publish.assert_not_called()
