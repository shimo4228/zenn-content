"""Zenn → Qiita cross-post CLI.

Usage:
    python publish.py articles/ecc-cheatsheet.md --platform qiita
    python publish.py articles/ecc-cheatsheet.md --platform qiita --dry-run
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import frontmatter
import httpx


# ---------------------------------------------------------------------------
# Env
# ---------------------------------------------------------------------------

def _load_env(env_path: Path) -> None:
    """Load KEY=VALUE pairs from a .env file into os.environ."""
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Article:
    title: str
    body: str
    topics: tuple[str, ...]
    emoji: str
    article_type: str


@dataclass(frozen=True)
class PublishResult:
    platform: str
    success: bool
    url: str | None
    error: str | None


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_zenn_article(path: Path) -> Article:
    """Parse a Zenn article markdown file into an Article object."""
    post = frontmatter.load(path)
    return Article(
        title=post.metadata.get("title", ""),
        body=post.content,
        topics=tuple(post.metadata.get("topics", [])),
        emoji=post.metadata.get("emoji", ""),
        article_type=post.metadata.get("type", "tech"),
    )


# ---------------------------------------------------------------------------
# Converter
# ---------------------------------------------------------------------------

_ZENN_MESSAGE_RE = re.compile(
    r"^:::message\s*\n(.*?)\n^:::\s*$",
    re.MULTILINE | re.DOTALL,
)

_ZENN_DETAILS_RE = re.compile(
    r"^:::details\s+(.*?)\s*\n(.*?)\n^:::\s*$",
    re.MULTILINE | re.DOTALL,
)


def convert_to_qiita(article: Article) -> dict:
    """Convert an Article to a Qiita API v2 request body."""
    body = _strip_zenn_syntax(article.body)
    tags = [{"name": t} for t in article.topics[:5]]
    return {
        "title": article.title,
        "body": body,
        "tags": tags,
        "private": False,
    }


def _strip_zenn_syntax(content: str) -> str:
    """Replace Zenn-specific syntax with standard Markdown equivalents."""
    # :::message → blockquote
    content = _ZENN_MESSAGE_RE.sub(_message_to_blockquote, content)
    # :::details title → <details>
    content = _ZENN_DETAILS_RE.sub(_details_to_html, content)
    return content


def _message_to_blockquote(m: re.Match) -> str:
    lines = m.group(1).strip().splitlines()
    return "\n".join(f"> {line}" for line in lines)


def _details_to_html(m: re.Match) -> str:
    summary = m.group(1).strip()
    body = m.group(2).strip()
    return f"<details><summary>{summary}</summary>\n\n{body}\n\n</details>"


# ---------------------------------------------------------------------------
# Publisher
# ---------------------------------------------------------------------------

QIITA_API_BASE = "https://qiita.com/api/v2"


def publish_to_qiita(payload: dict, token: str) -> PublishResult:
    """Publish an article to Qiita via API v2."""
    resp = httpx.post(
        f"{QIITA_API_BASE}/items",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=30,
    )
    if resp.status_code == 201:
        data = resp.json()
        return PublishResult("qiita", True, data.get("url"), None)
    return PublishResult("qiita", False, None, f"{resp.status_code}: {resp.text}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cross-post Zenn articles to other platforms",
    )
    parser.add_argument(
        "article",
        type=Path,
        help="Path to the Zenn article markdown file",
    )
    parser.add_argument(
        "--platform",
        choices=["qiita"],
        required=True,
        help="Target platform",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Convert and display without publishing",
    )
    return parser


def main() -> int:
    _load_env(Path(__file__).parent / ".env")

    parser = build_parser()
    args = parser.parse_args()

    article_path: Path = args.article
    if not article_path.exists():
        print(f"Error: file not found: {article_path}", file=sys.stderr)
        return 1

    article = parse_zenn_article(article_path)
    print(f"Parsed: {article.title} ({len(article.topics)} topics)")

    if args.platform == "qiita":
        payload = convert_to_qiita(article)

        if args.dry_run:
            print("\n--- Qiita payload (dry-run) ---")
            print(f"Title: {payload['title']}")
            print(f"Tags:  {[t['name'] for t in payload['tags']]}")
            print(f"Body ({len(payload['body'])} chars):\n")
            print(payload["body"][:500])
            if len(payload["body"]) > 500:
                print(f"\n... ({len(payload['body']) - 500} chars truncated)")
            return 0

        token = os.environ.get("QIITA_ACCESS_TOKEN")
        if not token:
            print("Error: QIITA_ACCESS_TOKEN is not set", file=sys.stderr)
            return 1

        result = publish_to_qiita(payload, token)
        if result.success:
            print(f"Published to Qiita: {result.url}")
            return 0
        else:
            print(f"Failed to publish: {result.error}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
