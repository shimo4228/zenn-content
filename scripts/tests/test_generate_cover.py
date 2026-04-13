"""Tests for generate_cover.py — Dev.to cover image generator."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from unittest.mock import patch

from generate_cover import (
    COVERS_DIR,
    GITHUB_RAW_BASE,
    HEIGHT,
    WIDTH,
    _draw_accent_bar,
    _has_japanese,
    _load_font,
    _make_gradient,
    _process_all,
    _process_article,
    _wrap_title,
    cover_url,
    generate_cover,
    main,
)


# ---------------------------------------------------------------------------
# Pure function tests
# ---------------------------------------------------------------------------


class TestHasJapanese:
    def test_ascii_only(self) -> None:
        assert _has_japanese("Hello World") is False

    def test_japanese_hiragana(self) -> None:
        assert _has_japanese("こんにちは") is True

    def test_japanese_katakana(self) -> None:
        assert _has_japanese("テスト") is True

    def test_japanese_kanji(self) -> None:
        assert _has_japanese("記事") is True

    def test_mixed(self) -> None:
        assert _has_japanese("Article 記事") is True

    def test_empty(self) -> None:
        assert _has_japanese("") is False


class TestCoverUrl:
    def test_returns_github_raw_url(self) -> None:
        url = cover_url("my-article")
        assert url == f"{GITHUB_RAW_BASE}/my-article.png"


# ---------------------------------------------------------------------------
# Image generation tests
# ---------------------------------------------------------------------------


class TestMakeGradient:
    def test_returns_correct_size(self) -> None:
        img = _make_gradient(100, 50)
        assert img.size == (100, 50)
        assert img.mode == "RGB"

    def test_top_color_matches(self) -> None:
        img = _make_gradient(100, 50)
        # Top-left pixel should be close to BG_COLOR_TOP
        r, g, b = img.getpixel((0, 0))
        assert r < 30  # slate-900 range
        assert g < 40
        assert b < 60

    def test_bottom_color_differs_from_top(self) -> None:
        img = _make_gradient(100, 50)
        top_pixel = img.getpixel((0, 0))
        bottom_pixel = img.getpixel((0, 49))
        assert top_pixel != bottom_pixel


class TestWrapTitle:
    def test_short_title_single_line(self) -> None:
        from PIL import ImageFont
        font = ImageFont.load_default()
        lines = _wrap_title("Short", font, 500)
        assert len(lines) == 1
        assert lines[0] == "Short"

    def test_max_4_lines(self) -> None:
        from PIL import ImageFont
        font = ImageFont.load_default()
        long_title = "This is a very long title " * 20
        lines = _wrap_title(long_title, font, 200)
        assert len(lines) <= 4


class TestGenerateCover:
    def test_creates_png_file(self, tmp_path: Path) -> None:
        output = tmp_path / "test-cover.png"
        result = generate_cover("Test Article Title", output)
        assert result == output
        assert output.exists()
        img = Image.open(output)
        assert img.size == (WIDTH, HEIGHT)
        assert img.format == "PNG"

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        output = tmp_path / "nested" / "dir" / "cover.png"
        generate_cover("Title", output)
        assert output.exists()

    def test_japanese_title(self, tmp_path: Path) -> None:
        output = tmp_path / "jp-cover.png"
        generate_cover("日本語タイトル", output)
        assert output.exists()
        img = Image.open(output)
        assert img.size == (WIDTH, HEIGHT)


class TestLoadFont:
    def test_returns_font_object(self) -> None:
        font = _load_font(16)
        assert font is not None

    def test_japanese_font(self) -> None:
        font = _load_font(16, japanese=True)
        assert font is not None


class TestDrawAccentBar:
    def test_draws_without_error(self) -> None:
        img = Image.new("RGB", (100, 50))
        draw = ImageDraw.Draw(img)
        _draw_accent_bar(draw)
        # Accent bar at top should have changed pixels
        top_pixel = img.getpixel((50, 2))
        assert top_pixel != (0, 0, 0)


class TestProcessArticle:
    def test_generates_from_markdown(self, tmp_path: Path) -> None:
        article = tmp_path / "test-article.md"
        article.write_text("---\ntitle: Test Title\n---\nBody\n")
        output = tmp_path / "covers" / "test-article.png"
        result = _process_article(article, output)
        assert result == output
        assert output.exists()

    def test_default_output_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("generate_cover.COVERS_DIR", tmp_path / "covers")
        article = tmp_path / "my-slug.md"
        article.write_text("---\ntitle: My Title\n---\nBody\n")
        result = _process_article(article)
        assert result.name == "my-slug.png"


class TestProcessAll:
    def test_generates_missing_covers(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        # Setup: repo with articles-en/ and images/covers/
        en_dir = tmp_path / "articles-en"
        en_dir.mkdir()
        covers_dir = tmp_path / "images" / "covers"
        covers_dir.mkdir(parents=True)

        # Create articles
        (en_dir / "article1.md").write_text("---\ntitle: Article 1\n---\nBody\n")
        (en_dir / "article2.md").write_text("---\ntitle: Article 2\n---\nBody\n")
        # article1 already has a cover
        generate_cover("existing", covers_dir / "article1.png")

        monkeypatch.setattr("generate_cover.REPO_ROOT", tmp_path)
        monkeypatch.setattr("generate_cover.COVERS_DIR", covers_dir)

        generated = _process_all()
        assert len(generated) == 1  # Only article2
        assert generated[0].name == "article2.png"


class TestMainCli:
    def test_generate_single_article(self, tmp_path: Path) -> None:
        article = tmp_path / "test.md"
        article.write_text("---\ntitle: CLI Test\n---\nBody\n")
        output = tmp_path / "output.png"
        with patch("sys.argv", ["generate_cover.py", str(article), "-o", str(output)]):
            result = main()
        assert result == 0
        assert output.exists()

    def test_missing_article_returns_1(self) -> None:
        with patch("sys.argv", ["generate_cover.py", "/nonexistent.md"]):
            result = main()
        assert result == 1

    def test_all_flag(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        en_dir = tmp_path / "articles-en"
        en_dir.mkdir()
        covers_dir = tmp_path / "images" / "covers"
        covers_dir.mkdir(parents=True)
        (en_dir / "a.md").write_text("---\ntitle: A\n---\n")

        monkeypatch.setattr("generate_cover.REPO_ROOT", tmp_path)
        monkeypatch.setattr("generate_cover.COVERS_DIR", covers_dir)

        with patch("sys.argv", ["generate_cover.py", "--all"]):
            result = main()
        assert result == 0
