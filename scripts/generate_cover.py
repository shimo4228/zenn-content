"""Generate Dev.to cover images from article titles.

Dev.to recommended size: 1000x420px.

Usage:
    python generate_cover.py articles-en/xxx.md
    python generate_cover.py articles-en/xxx.md --output images/covers/xxx.png
    python generate_cover.py --all  # Generate for all EN articles missing covers
"""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

import frontmatter
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
COVERS_DIR = REPO_ROOT / "images" / "covers"
GITHUB_RAW_BASE = (
    "https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/covers"
)

# Dev.to recommended cover image size
WIDTH = 1000
HEIGHT = 420

# Colors — dark gradient with accent
BG_COLOR_TOP = (15, 23, 42)  # slate-900
BG_COLOR_BOTTOM = (30, 41, 59)  # slate-800
ACCENT_COLOR = (99, 102, 241)  # indigo-500
TEXT_COLOR = (248, 250, 252)  # slate-50
SUB_TEXT_COLOR = (148, 163, 184)  # slate-400

# Font config
FONT_PATH = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_PATH_JP = str(Path.home() / "Library/Fonts/MoralerspaceNeon-Bold.ttf")
TITLE_FONT_SIZE = 36
AUTHOR_FONT_SIZE = 16


def _make_gradient(width: int, height: int) -> Image.Image:
    """Create a vertical gradient background."""
    img = Image.new("RGB", (width, height))
    for y in range(height):
        ratio = y / height
        r = int(BG_COLOR_TOP[0] + (BG_COLOR_BOTTOM[0] - BG_COLOR_TOP[0]) * ratio)
        g = int(BG_COLOR_TOP[1] + (BG_COLOR_BOTTOM[1] - BG_COLOR_TOP[1]) * ratio)
        b = int(BG_COLOR_TOP[2] + (BG_COLOR_BOTTOM[2] - BG_COLOR_TOP[2]) * ratio)
        for x in range(width):
            img.putpixel((x, y), (r, g, b))
    return img


def _draw_accent_bar(draw: ImageDraw.ImageDraw) -> None:
    """Draw a subtle accent bar at the top."""
    draw.rectangle([(0, 0), (WIDTH, 4)], fill=ACCENT_COLOR)


def _load_font(size: int, *, japanese: bool = False) -> ImageFont.FreeTypeFont:
    """Load font, falling back to default if not available."""
    path = FONT_PATH_JP if japanese else FONT_PATH
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        return ImageFont.load_default()


def _has_japanese(text: str) -> bool:
    """Check if text contains Japanese characters."""
    return any("\u3000" <= ch <= "\u9fff" or "\uf900" <= ch <= "\ufaff" for ch in text)


def _wrap_title(title: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap title text to fit within max_width pixels."""
    # Start with a rough character estimate, then refine
    avg_char_width = font.getlength("A")
    chars_per_line = int(max_width / avg_char_width) if avg_char_width > 0 else 40
    lines = textwrap.wrap(title, width=chars_per_line)

    # Refine: if any line is too wide, re-wrap with fewer chars
    for _ in range(5):
        too_wide = any(font.getlength(line) > max_width for line in lines)
        if not too_wide:
            break
        chars_per_line -= 3
        lines = textwrap.wrap(title, width=max(chars_per_line, 10))

    return lines[:4]  # Max 4 lines


def generate_cover(title: str, output_path: Path) -> Path:
    """Generate a cover image for the given title."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = _make_gradient(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    _draw_accent_bar(draw)

    is_jp = _has_japanese(title)
    title_font = _load_font(TITLE_FONT_SIZE, japanese=is_jp)
    author_font = _load_font(AUTHOR_FONT_SIZE)

    # Wrap and center title
    padding_x = 80
    max_text_width = WIDTH - padding_x * 2
    lines = _wrap_title(title, title_font, max_text_width)

    line_height = TITLE_FONT_SIZE + 12
    total_text_height = len(lines) * line_height
    y_start = (HEIGHT - total_text_height) // 2 - 20

    for i, line in enumerate(lines):
        line_width = title_font.getlength(line)
        x = (WIDTH - line_width) // 2
        y = y_start + i * line_height
        draw.text((x, y), line, font=title_font, fill=TEXT_COLOR)

    # Author line at bottom
    author = "@shimo4228"
    author_width = author_font.getlength(author)
    draw.text(
        ((WIDTH - author_width) // 2, HEIGHT - 50),
        author,
        font=author_font,
        fill=SUB_TEXT_COLOR,
    )

    img.save(output_path, "PNG", optimize=True)
    return output_path


def cover_url(slug: str) -> str:
    """Return the GitHub raw URL for a cover image."""
    return f"{GITHUB_RAW_BASE}/{slug}.png"


def _process_article(article_path: Path, output: Path | None = None) -> Path:
    """Generate cover for a single article."""
    post = frontmatter.load(str(article_path))
    title = str(post.metadata.get("title", article_path.stem))
    slug = article_path.stem
    out = output or (COVERS_DIR / f"{slug}.png")
    return generate_cover(title, out)


def _process_all() -> list[Path]:
    """Generate covers for all EN articles that don't have one yet."""
    en_dir = REPO_ROOT / "articles-en"
    generated: list[Path] = []
    for md in sorted(en_dir.glob("*.md")):
        cover_path = COVERS_DIR / f"{md.stem}.png"
        if cover_path.exists():
            continue
        path = _process_article(md)
        generated.append(path)
        print(f"Generated: {path.relative_to(REPO_ROOT)}")
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Dev.to cover images")
    parser.add_argument("article", nargs="?", help="Path to article .md file")
    parser.add_argument("--output", "-o", help="Output image path")
    parser.add_argument("--all", action="store_true", help="Generate all missing covers")
    args = parser.parse_args()

    if args.all:
        generated = _process_all()
        print(f"\n{len(generated)} cover(s) generated.")
        return 0

    if not args.article:
        parser.error("Provide an article path or use --all")

    article_path = Path(args.article)
    if not article_path.exists():
        print(f"Error: {article_path} not found")
        return 1

    out = Path(args.output) if args.output else None
    result = _process_article(article_path, out)
    print(f"Generated: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
