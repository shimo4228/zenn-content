"""Zenn cross-post CLI — Dev.to.

Usage:
    python publish.py articles-en/xxx.md --platform devto --canonical-url URL
    python publish.py articles-en/xxx.md --platform devto --update auto
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
    article_type: str = "tech"
    description: str = ""


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
    post = frontmatter.load(str(path))
    metadata: dict[str, object] = post.metadata  # type: ignore[assignment]
    # Zenn uses "topics" (list), Dev.to-style uses "tags" (comma-separated string or list)
    raw_topics = metadata.get("topics") or metadata.get("tags") or []
    if isinstance(raw_topics, str):
        topics = tuple(t.strip() for t in raw_topics.split(",") if t.strip())
    elif isinstance(raw_topics, (list, tuple)):
        topics = tuple(str(t) for t in raw_topics)
    else:
        topics = ()
    return Article(
        title=str(metadata.get("title", "")),
        body=post.content,
        topics=topics,
        article_type=str(metadata.get("type", "tech")),
        description=str(metadata.get("description", "")),
    )


# ---------------------------------------------------------------------------
# Converter (shared)
# ---------------------------------------------------------------------------

_ZENN_MESSAGE_RE = re.compile(
    r"^:::message\s*\n(.*?)\n^:::\s*$",
    re.MULTILINE | re.DOTALL,
)

_ZENN_DETAILS_RE = re.compile(
    r"^:::details\s+(.*?)\s*\n(.*?)\n^:::\s*$",
    re.MULTILINE | re.DOTALL,
)

_ZENN_IMAGE_RE = re.compile(
    r"!\[([^\]]*)\]\(/images/([^)]+)\)",
)

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/shimo4228/zenn-content/main/images"


def _strip_zenn_syntax(content: str) -> str:
    """Replace Zenn-specific syntax with standard Markdown equivalents."""
    # /images/xxx → GitHub raw URL
    content = _ZENN_IMAGE_RE.sub(
        rf"![\1]({GITHUB_RAW_BASE}/\2)",
        content,
    )
    # :::message → blockquote
    content = _ZENN_MESSAGE_RE.sub(_message_to_blockquote, content)
    # :::details title → <details>
    content = _ZENN_DETAILS_RE.sub(_details_to_html, content)
    return content


def _message_to_blockquote(m: re.Match[str]) -> str:
    lines = m.group(1).strip().splitlines()
    return "\n".join(f"> {line}" for line in lines)


def _details_to_html(m: re.Match[str]) -> str:
    summary = m.group(1).strip()
    body = m.group(2).strip()
    return f"<details><summary>{summary}</summary>\n\n{body}\n\n</details>"


# ---------------------------------------------------------------------------
# Converter — Dev.to
# ---------------------------------------------------------------------------


def map_devto_tags(
    topics: tuple[str, ...],
    article_type: str,
    devto_tags_override: list[str] | None = None,
) -> list[str]:
    """Map Zenn topics to Dev.to tags (max 4).

    Args:
        topics: Zenn article topics (e.g., ("claudecode", "ai", "個人開発"))
        article_type: Zenn article type ("tech" or "idea")
        devto_tags_override: If provided in schedule.json, use these instead.

    Returns:
        List of up to 4 Dev.to-appropriate tags.
    """
    if devto_tags_override:
        return [t.lower() for t in devto_tags_override[:4]]

    # Zenn topic → Dev.to tag mapping
    tag_map: dict[str, str] = {
        "claudecode": "ai",
        "claude": "ai",
        "gemini": "ai",
        "chatgpt": "ai",
        "llm": "ai",
        "機械学習": "machinelearning",
        "個人開発": "programming",
        "開発環境": "productivity",
        "生産性": "productivity",
        "テスト": "testing",
        "shellscript": "programming",
        "automation": "productivity",
        "debugging": "programming",
        "agent": "ai",
        "architecture": "programming",
        "alignment": "alignment",
        "benchmark": "benchmark",
        "rlhf": "ai",
        "ollama": "ai",
        "governance": "governance",
        "capitalism": "discuss",
        "sre": "devops",
        "organization": "discuss",
        "security": "security",
        "ethics": "discuss",
        "devops": "devops",
        "python": "python",
        "typescript": "typescript",
        "javascript": "javascript",
        "react": "react",
        "nextjs": "webdev",
        "docker": "docker",
        "kubernetes": "devops",
        "testing": "testing",
        "ci": "devops",
    }

    # Convert topics, dedup while preserving order
    seen: set[str] = set()
    tags: list[str] = []
    for topic in topics:
        if topic not in tag_map:
            # 日本語 topics などマッピングにないものは skip（mangled pass-through 防止）
            sanitized = re.sub(r"[^a-z0-9]", "", topic.lower())
            if not sanitized or sanitized != topic.lower():
                continue
        mapped = tag_map.get(topic, topic).lower()
        # Strip non-alphanumeric (Dev.to requirement)
        mapped = re.sub(r"[^a-z0-9]", "", mapped)
        if mapped and mapped not in seen:
            seen.add(mapped)
            tags.append(mapped)

    # "idea" articles get "discuss" as first tag
    if article_type == "idea" and "discuss" not in seen:
        tags.insert(0, "discuss")

    return tags[:4]


def convert_to_devto(
    article: Article,
    canonical_url: str | None = None,
    devto_tags_override: list[str] | None = None,
    cover_image_url: str | None = None,
) -> dict[str, Any]:
    """Convert an Article to a Dev.to API request body."""
    body = _strip_zenn_syntax(article.body)
    tags = map_devto_tags(article.topics, article.article_type, devto_tags_override)
    payload: dict[str, Any] = {
        "article": {
            "title": article.title,
            "body_markdown": body,
            "published": True,
            "tags": tags,
        }
    }
    if article.description:
        payload["article"]["description"] = article.description
    if cover_image_url:
        payload["article"]["main_image"] = cover_image_url
    if canonical_url:
        payload["article"]["canonical_url"] = canonical_url
    return payload


# ---------------------------------------------------------------------------
# Publisher — Dev.to
# ---------------------------------------------------------------------------

DEVTO_API_BASE = "https://dev.to/api"
_DEVTO_HEADERS_BASE = {"Accept": "application/vnd.forem.api-v1+json"}


def _devto_headers(api_key: str) -> dict[str, str]:
    return {**_DEVTO_HEADERS_BASE, "api-key": api_key}


def publish_to_devto(payload: dict[str, Any], api_key: str) -> PublishResult:
    """Publish an article to Dev.to via API v1."""
    resp = httpx.post(
        f"{DEVTO_API_BASE}/articles",
        headers=_devto_headers(api_key),
        json=payload,
        timeout=30,
    )
    if resp.status_code == 201:
        data = resp.json()
        return PublishResult("devto", True, data.get("url"), None)
    return PublishResult("devto", False, None, f"{resp.status_code}: {resp.text}")


def update_on_devto(article_id: int, payload: dict[str, Any], api_key: str) -> PublishResult:
    """Update an existing Dev.to article via API v1."""
    resp = httpx.put(
        f"{DEVTO_API_BASE}/articles/{article_id}",
        headers=_devto_headers(api_key),
        json=payload,
        timeout=30,
    )
    if resp.status_code == 200:
        data = resp.json()
        return PublishResult("devto", True, data.get("url"), None)
    return PublishResult("devto", False, None, f"{resp.status_code}: {resp.text}")


def find_devto_article_by_title(title: str, api_key: str) -> int | None:
    """Search authenticated user's published articles for a matching title."""
    page = 1
    while page <= 5:
        resp = httpx.get(
            f"{DEVTO_API_BASE}/articles/me/published",
            headers=_devto_headers(api_key),
            params={"page": page, "per_page": 30},
            timeout=30,
        )
        if resp.status_code != 200:
            return None
        items = resp.json()
        if not items:
            return None
        for item in items:
            if item.get("title") == title:
                return item["id"]
        page += 1
    return None


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
        choices=["devto"],
        required=True,
        help="Target platform",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Convert and display without publishing",
    )
    parser.add_argument(
        "--update",
        metavar="ID",
        help="Update existing article. Use 'auto' to search by title.",
    )
    parser.add_argument(
        "--canonical-url",
        help="Canonical URL of the original article (e.g. Zenn URL)",
    )
    parser.add_argument(
        "--cover-image",
        dest="cover_image",
        help="Cover image URL for Dev.to (auto-detected from images/covers/ if omitted)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip English translation check for devto",
    )
    return parser


def _print_dry_run(platform: str, payload: dict[str, Any]) -> None:
    """Pretty-print a dry-run payload."""
    print(f"\n--- {platform} payload (dry-run) ---")
    art = payload["article"]
    print(f"Title: {art['title']}")
    print(f"Tags:  {art.get('tags', [])}")
    print(f"Canonical: {art.get('canonical_url', '(none)')}")
    body = art["body_markdown"]
    print(f"Body ({len(body)} chars):\n")
    print(body[:500])
    if len(body) > 500:
        print(f"\n... ({len(body) - 500} chars truncated)")


def _run_devto(article: Article, args: argparse.Namespace) -> int:
    cover_url = getattr(args, "cover_image", None)
    if not cover_url:
        # Auto-generate cover URL from slug
        slug = args.article.stem
        cover_path = args.article.parent.parent / "images" / "covers" / f"{slug}.png"
        if cover_path.exists():
            cover_url = f"https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/covers/{slug}.png"
    payload = convert_to_devto(
        article,
        canonical_url=args.canonical_url,
        cover_image_url=cover_url,
    )
    if args.dry_run:
        _print_dry_run("devto", payload)
        return 0

    api_key = os.environ.get("DEVTO_API_KEY")
    if not api_key:
        print("Error: DEVTO_API_KEY is not set", file=sys.stderr)
        return 1

    if args.update:
        article_id_str = args.update
        if article_id_str == "auto":
            print(f"Searching for existing article: {article.title}")
            article_id = find_devto_article_by_title(article.title, api_key)
            if not article_id:
                print("Error: article not found on Dev.to", file=sys.stderr)
                return 1
            print(f"Found: {article_id}")
        else:
            try:
                article_id = int(article_id_str)
            except ValueError:
                print(f"Error: invalid article ID: {article_id_str}", file=sys.stderr)
                return 1
        result = update_on_devto(article_id, payload, api_key)
    else:
        result = publish_to_devto(payload, api_key)

    if result.success:
        action = "Updated" if args.update else "Published"
        print(f"{action} on Dev.to: {result.url}")
        return 0
    print(f"Failed: {result.error}", file=sys.stderr)
    return 1


_RUNNERS = {
    "devto": _run_devto,
}


def _check_english_translation(article_path: Path, args: argparse.Namespace) -> int | None:
    """Warn if a Japanese article is used for devto without --force.

    Returns an exit code if the command should stop, or None to continue.
    """
    if args.platform != "devto":
        return None
    if getattr(args, "force", False):
        return None

    parts = article_path.resolve().parts
    # Only guard articles under "articles/" (not "articles-en/")
    try:
        idx = parts.index("articles")
    except ValueError:
        return None
    # If already under articles-en, no guard needed
    if idx > 0 and parts[idx - 1] == "articles-en":
        return None
    # Also skip if the path literally contains "articles-en"
    if "articles-en" in parts:
        return None

    en_path = article_path.parent.parent / "articles-en" / article_path.name
    if en_path.exists():
        print(
            f"Warning: English version exists at {en_path}\n"
            f"Use the English version for {args.platform}, or pass --force to skip this check.",
            file=sys.stderr,
        )
    else:
        print(
            f"Warning: No English translation found at {en_path}\n"
            f"Run /translate-article first, or pass --force to publish in Japanese.",
            file=sys.stderr,
        )
    return 1


def main() -> int:
    _load_env(Path(__file__).parent / ".env")

    parser = build_parser()
    args = parser.parse_args()

    article_path: Path = args.article
    if not article_path.exists():
        print(f"Error: file not found: {article_path}", file=sys.stderr)
        return 1

    # Guard: Japanese article → devto without --force
    guard = _check_english_translation(article_path, args)
    if guard is not None:
        return guard

    article = parse_zenn_article(article_path)
    print(f"Parsed: {article.title} ({len(article.topics)} topics)")

    runner = _RUNNERS[args.platform]
    return runner(article, args)


if __name__ == "__main__":
    raise SystemExit(main())
