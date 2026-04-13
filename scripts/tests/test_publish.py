"""Tests for publish.py — Zenn cross-post CLI (Dev.to only)."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import respx

from publish import (
    Article,
    PublishResult,
    _load_env,
    _strip_zenn_syntax,
    build_parser,
    convert_to_devto,
    find_devto_article_by_title,
    main,
    parse_zenn_article,
    publish_to_devto,
    update_on_devto,
    _run_devto,
    GITHUB_RAW_BASE,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_ARTICLE = FIXTURES_DIR / "sample-article.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_article(**overrides: object) -> Article:
    defaults = {
        "title": "テスト記事",
        "body": "本文テスト",
        "topics": ("python", "testing", "ci"),
    }
    defaults.update(overrides)
    return Article(**defaults)


def _make_args(**overrides: object) -> argparse.Namespace:
    defaults = {
        "article": SAMPLE_ARTICLE,
        "platform": "devto",
        "dry_run": False,
        "update": None,
        "canonical_url": None,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


# ===========================================================================
# 1. Converter tests (pure functions, no mocks)
# ===========================================================================


class TestStripZennSyntax:
    def test_images(self) -> None:
        md = "![alt](/images/screenshot.png)"
        result = _strip_zenn_syntax(md)
        assert result == f"![alt]({GITHUB_RAW_BASE}/screenshot.png)"

    def test_message_to_blockquote(self) -> None:
        md = ":::message\n注意してください。\n行2です。\n:::"
        result = _strip_zenn_syntax(md)
        assert "> 注意してください。" in result
        assert "> 行2です。" in result
        assert ":::message" not in result

    def test_details_to_html(self) -> None:
        md = ":::details タイトル\n中身のテキスト\n:::"
        result = _strip_zenn_syntax(md)
        assert "<details><summary>タイトル</summary>" in result
        assert "中身のテキスト" in result
        assert "</details>" in result
        assert ":::details" not in result

    def test_no_zenn_syntax(self) -> None:
        md = "普通の Markdown テキスト"
        assert _strip_zenn_syntax(md) == md


class TestConvertToDevto:
    def test_with_canonical_url(self) -> None:
        article = _make_article()
        payload = convert_to_devto(article, canonical_url="https://zenn.dev/x")
        art = payload["article"]
        assert art["title"] == "テスト記事"
        assert art["canonical_url"] == "https://zenn.dev/x"
        assert art["published"] is True

    def test_without_canonical_url(self) -> None:
        article = _make_article()
        payload = convert_to_devto(article)
        assert "canonical_url" not in payload["article"]

    def test_tags_limited_to_4(self) -> None:
        article = _make_article(topics=("a", "b", "c", "d", "e"))
        payload = convert_to_devto(article)
        assert len(payload["article"]["tags"]) == 4

    def test_description_included(self) -> None:
        article = _make_article(description="Test description")
        payload = convert_to_devto(article)
        assert payload["article"]["description"] == "Test description"

    def test_cover_image_included(self) -> None:
        article = _make_article()
        payload = convert_to_devto(article, cover_image_url="https://example.com/img.png")
        assert payload["article"]["main_image"] == "https://example.com/img.png"


# ===========================================================================
# 2. Parser tests
# ===========================================================================


class TestParseZennArticle:
    def test_parse_sample_article(self) -> None:
        article = parse_zenn_article(SAMPLE_ARTICLE)
        assert article.title == "テスト用記事タイトル"
        assert article.topics == ("python", "testing", "pytest", "ci", "automation")
        assert "テスト用の記事" in article.body


# ===========================================================================
# 3. Publisher tests (respx mocked HTTP)
# ===========================================================================


class TestPublishToDevto:
    @respx.mock
    def test_success(self) -> None:
        respx.post("https://dev.to/api/articles").mock(
            return_value=httpx.Response(
                201, json={"url": "https://dev.to/user/article"}
            )
        )
        result = publish_to_devto({"article": {"title": "t"}}, "key")
        assert result == PublishResult("devto", True, "https://dev.to/user/article", None)

    @respx.mock
    def test_failure(self) -> None:
        respx.post("https://dev.to/api/articles").mock(
            return_value=httpx.Response(422, text="Invalid")
        )
        result = publish_to_devto({"article": {"title": "t"}}, "key")
        assert result.success is False


class TestUpdateOnDevto:
    @respx.mock
    def test_success(self) -> None:
        respx.put("https://dev.to/api/articles/42").mock(
            return_value=httpx.Response(
                200, json={"url": "https://dev.to/user/article"}
            )
        )
        result = update_on_devto(42, {"article": {"title": "t"}}, "key")
        assert result.success is True


class TestFindDevtoArticleByTitle:
    @respx.mock
    def test_found(self) -> None:
        respx.get("https://dev.to/api/articles/me/published").mock(
            return_value=httpx.Response(
                200,
                json=[{"id": 99, "title": "Target"}],
            )
        )
        assert find_devto_article_by_title("Target", "key") == 99

    @respx.mock
    def test_not_found(self) -> None:
        respx.get("https://dev.to/api/articles/me/published").mock(
            return_value=httpx.Response(200, json=[])
        )
        assert find_devto_article_by_title("Missing", "key") is None


# ===========================================================================
# 4. CLI Runner tests
# ===========================================================================


class TestRunDevto:
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key(self, capsys: pytest.CaptureFixture[str]) -> None:
        article = _make_article()
        args = _make_args(platform="devto")
        ret = _run_devto(article, args)
        assert ret == 1
        assert "DEVTO_API_KEY" in capsys.readouterr().err

    @patch.dict(os.environ, {"DEVTO_API_KEY": "test-key"}, clear=True)
    def test_invalid_update_id(self, capsys: pytest.CaptureFixture[str]) -> None:
        article = _make_article()
        args = _make_args(platform="devto", update="not-a-number")
        ret = _run_devto(article, args)
        assert ret == 1
        assert "invalid article ID" in capsys.readouterr().err

    def test_dry_run(self, capsys: pytest.CaptureFixture[str]) -> None:
        article = _make_article()
        args = _make_args(platform="devto", dry_run=True, canonical_url="https://z.dev")
        ret = _run_devto(article, args)
        assert ret == 0
        out = capsys.readouterr().out
        assert "dry-run" in out
        assert "https://z.dev" in out

    @respx.mock
    @patch.dict(os.environ, {"DEVTO_API_KEY": "test-key"}, clear=True)
    def test_publish_success(self) -> None:
        respx.post("https://dev.to/api/articles").mock(
            return_value=httpx.Response(201, json={"url": "https://dev.to/user/x"})
        )
        article = _make_article()
        args = _make_args(platform="devto")
        assert _run_devto(article, args) == 0

    @respx.mock
    @patch.dict(os.environ, {"DEVTO_API_KEY": "test-key"}, clear=True)
    def test_update_auto(self, capsys: pytest.CaptureFixture[str]) -> None:
        respx.get("https://dev.to/api/articles/me/published").mock(
            return_value=httpx.Response(
                200, json=[{"id": 42, "title": "テスト記事"}]
            )
        )
        respx.put("https://dev.to/api/articles/42").mock(
            return_value=httpx.Response(
                200, json={"url": "https://dev.to/user/article"}
            )
        )
        article = _make_article()
        args = _make_args(platform="devto", update="auto")
        assert _run_devto(article, args) == 0
        assert "Updated" in capsys.readouterr().out


# ===========================================================================
# 5. Utility tests
# ===========================================================================


class TestLoadEnv:
    def test_loads_env_file(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("MY_TEST_KEY=hello\n# comment\n\nOTHER=world\n")
        with patch.dict(os.environ, {}, clear=True):
            _load_env(env_file)
            assert os.environ["MY_TEST_KEY"] == "hello"
            assert os.environ["OTHER"] == "world"

    def test_does_not_overwrite_existing(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("KEY=new_value\n")
        with patch.dict(os.environ, {"KEY": "existing"}, clear=True):
            _load_env(env_file)
            assert os.environ["KEY"] == "existing"

    def test_missing_file(self) -> None:
        _load_env(Path("/nonexistent/.env"))


class TestBuildParser:
    def test_platform_choices(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["article.md", "--platform", "devto"])
        assert args.platform == "devto"

    def test_canonical_url(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["a.md", "--platform", "devto", "--canonical-url", "https://z.dev"]
        )
        assert args.canonical_url == "https://z.dev"


class TestMain:
    def test_file_not_found(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch("sys.argv", ["publish.py", "/nonexistent.md", "--platform", "devto"]):
            ret = main()
        assert ret == 1
        assert "not found" in capsys.readouterr().err
