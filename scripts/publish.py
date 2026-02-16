"""Zenn cross-post CLI — Qiita, Dev.to, Hashnode.

Usage:
    python publish.py articles/xxx.md --platform qiita
    python publish.py articles/xxx.md --platform devto --canonical-url URL
    python publish.py articles/xxx.md --platform devto --update auto
    python publish.py articles-en/xxx.md --platform hashnode --canonical-url URL
"""

from __future__ import annotations

import argparse
import json
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


def _message_to_blockquote(m: re.Match) -> str:
    lines = m.group(1).strip().splitlines()
    return "\n".join(f"> {line}" for line in lines)


def _details_to_html(m: re.Match) -> str:
    summary = m.group(1).strip()
    body = m.group(2).strip()
    return f"<details><summary>{summary}</summary>\n\n{body}\n\n</details>"


# ---------------------------------------------------------------------------
# Converter — Qiita
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Converter — Dev.to
# ---------------------------------------------------------------------------


def convert_to_devto(article: Article, canonical_url: str | None = None) -> dict:
    """Convert an Article to a Dev.to API request body."""
    body = _strip_zenn_syntax(article.body)
    payload: dict = {
        "article": {
            "title": article.title,
            "body_markdown": body,
            "published": True,
            "tags": list(article.topics[:4]),
        }
    }
    if canonical_url:
        payload["article"]["canonical_url"] = canonical_url
    return payload


# ---------------------------------------------------------------------------
# Converter — Hashnode
# ---------------------------------------------------------------------------

_HASHNODE_PUBLISH_MUTATION = """\
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) {
    post {
      id
      slug
      title
      url
    }
  }
}"""

_HASHNODE_UPDATE_MUTATION = """\
mutation UpdatePost($input: UpdatePostInput!) {
  updatePost(input: $input) {
    post {
      id
      slug
      title
      url
    }
  }
}"""


def convert_to_hashnode(
    article: Article,
    publication_id: str,
    canonical_url: str | None = None,
) -> dict:
    """Convert an Article to a Hashnode GraphQL request body."""
    body = _strip_zenn_syntax(article.body)
    input_data: dict = {
        "title": article.title,
        "contentMarkdown": body,
        "publicationId": publication_id,
    }
    if canonical_url:
        input_data["originalArticleURL"] = canonical_url
    return {
        "query": _HASHNODE_PUBLISH_MUTATION,
        "variables": {"input": input_data},
    }


# ---------------------------------------------------------------------------
# Publisher — Qiita
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


def update_on_qiita(item_id: str, payload: dict, token: str) -> PublishResult:
    """Update an existing Qiita article via API v2."""
    resp = httpx.patch(
        f"{QIITA_API_BASE}/items/{item_id}",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=30,
    )
    if resp.status_code == 200:
        data = resp.json()
        return PublishResult("qiita", True, data.get("url"), None)
    return PublishResult("qiita", False, None, f"{resp.status_code}: {resp.text}")


def find_qiita_item_by_title(title: str, token: str) -> str | None:
    """Search authenticated user's items for a matching title."""
    page = 1
    while page <= 5:
        resp = httpx.get(
            f"{QIITA_API_BASE}/authenticated_user/items",
            headers={"Authorization": f"Bearer {token}"},
            params={"page": page, "per_page": 20},
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
# Publisher — Dev.to
# ---------------------------------------------------------------------------

DEVTO_API_BASE = "https://dev.to/api"
_DEVTO_HEADERS_BASE = {"Accept": "application/vnd.forem.api-v1+json"}


def _devto_headers(api_key: str) -> dict:
    return {**_DEVTO_HEADERS_BASE, "api-key": api_key}


def publish_to_devto(payload: dict, api_key: str) -> PublishResult:
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


def update_on_devto(article_id: int, payload: dict, api_key: str) -> PublishResult:
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
# Publisher — Hashnode
# ---------------------------------------------------------------------------

HASHNODE_API_URL = "https://gql.hashnode.com"


def publish_to_hashnode(payload: dict, token: str) -> PublishResult:
    """Publish an article to Hashnode via GraphQL API."""
    resp = httpx.post(
        HASHNODE_API_URL,
        headers={"Authorization": token, "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    if resp.status_code != 200:
        return PublishResult("hashnode", False, None, f"{resp.status_code}: {resp.text}")
    data = resp.json()
    if "errors" in data:
        return PublishResult("hashnode", False, None, json.dumps(data["errors"]))
    post = data.get("data", {}).get("publishPost", {}).get("post", {})
    return PublishResult("hashnode", True, post.get("url"), None)


def update_on_hashnode(post_id: str, article: Article, token: str) -> PublishResult:
    """Update an existing Hashnode article via GraphQL API."""
    body = _strip_zenn_syntax(article.body)
    payload = {
        "query": _HASHNODE_UPDATE_MUTATION,
        "variables": {
            "input": {
                "id": post_id,
                "title": article.title,
                "contentMarkdown": body,
            }
        },
    }
    resp = httpx.post(
        HASHNODE_API_URL,
        headers={"Authorization": token, "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    if resp.status_code != 200:
        return PublishResult("hashnode", False, None, f"{resp.status_code}: {resp.text}")
    data = resp.json()
    if "errors" in data:
        return PublishResult("hashnode", False, None, json.dumps(data["errors"]))
    post = data.get("data", {}).get("updatePost", {}).get("post", {})
    return PublishResult("hashnode", True, post.get("url"), None)


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
        choices=["qiita", "devto", "hashnode"],
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
        "--force",
        action="store_true",
        help="Skip English translation check for devto/hashnode",
    )
    return parser


def _print_dry_run(platform: str, payload: dict) -> None:
    """Pretty-print a dry-run payload."""
    print(f"\n--- {platform} payload (dry-run) ---")
    if platform == "qiita":
        print(f"Title: {payload['title']}")
        print(f"Tags:  {[t['name'] for t in payload['tags']]}")
        body = payload["body"]
    elif platform == "devto":
        art = payload["article"]
        print(f"Title: {art['title']}")
        print(f"Tags:  {art.get('tags', [])}")
        print(f"Canonical: {art.get('canonical_url', '(none)')}")
        body = art["body_markdown"]
    elif platform == "hashnode":
        inp = payload["variables"]["input"]
        print(f"Title: {inp['title']}")
        print(f"Publication: {inp['publicationId']}")
        print(f"Canonical: {inp.get('originalArticleURL', '(none)')}")
        body = inp["contentMarkdown"]
    else:
        body = ""
    print(f"Body ({len(body)} chars):\n")
    print(body[:500])
    if len(body) > 500:
        print(f"\n... ({len(body) - 500} chars truncated)")


def _run_qiita(article: Article, args: argparse.Namespace) -> int:
    payload = convert_to_qiita(article)
    if args.dry_run:
        _print_dry_run("qiita", payload)
        return 0

    token = os.environ.get("QIITA_ACCESS_TOKEN")
    if not token:
        print("Error: QIITA_ACCESS_TOKEN is not set", file=sys.stderr)
        return 1

    if args.update:
        item_id = args.update
        if item_id == "auto":
            print(f"Searching for existing article: {article.title}")
            item_id = find_qiita_item_by_title(article.title, token)
            if not item_id:
                print("Error: article not found on Qiita", file=sys.stderr)
                return 1
            print(f"Found: {item_id}")
        result = update_on_qiita(item_id, payload, token)
    else:
        result = publish_to_qiita(payload, token)

    if result.success:
        action = "Updated" if args.update else "Published"
        print(f"{action} on Qiita: {result.url}")
        return 0
    print(f"Failed: {result.error}", file=sys.stderr)
    return 1


def _run_devto(article: Article, args: argparse.Namespace) -> int:
    payload = convert_to_devto(article, canonical_url=args.canonical_url)
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


def _run_hashnode(article: Article, args: argparse.Namespace) -> int:
    publication_id = os.environ.get("HASHNODE_PUBLICATION_ID", "PLACEHOLDER")

    payload = convert_to_hashnode(
        article, publication_id, canonical_url=args.canonical_url
    )
    if args.dry_run:
        _print_dry_run("hashnode", payload)
        return 0

    token = os.environ.get("HASHNODE_API_TOKEN")
    if not token:
        print("Error: HASHNODE_API_TOKEN is not set", file=sys.stderr)
        return 1

    if publication_id == "PLACEHOLDER":
        print("Error: HASHNODE_PUBLICATION_ID is not set", file=sys.stderr)
        return 1

    if args.update:
        post_id = args.update
        if post_id == "auto":
            print("Error: auto-search not supported for Hashnode", file=sys.stderr)
            return 1
        result = update_on_hashnode(post_id, article, token)
    else:
        result = publish_to_hashnode(payload, token)

    if result.success:
        action = "Updated" if args.update else "Published"
        print(f"{action} on Hashnode: {result.url}")
        return 0
    print(f"Failed: {result.error}", file=sys.stderr)
    return 1


_RUNNERS = {
    "qiita": _run_qiita,
    "devto": _run_devto,
    "hashnode": _run_hashnode,
}


def _check_english_translation(article_path: Path, args: argparse.Namespace) -> int | None:
    """Warn if a Japanese article is used for devto/hashnode without --force.

    Returns an exit code if the command should stop, or None to continue.
    """
    if args.platform not in ("devto", "hashnode"):
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

    # Guard: Japanese article → devto/hashnode without --force
    guard = _check_english_translation(article_path, args)
    if guard is not None:
        return guard

    article = parse_zenn_article(article_path)
    print(f"Parsed: {article.title} ({len(article.topics)} topics)")

    runner = _RUNNERS[args.platform]
    return runner(article, args)


if __name__ == "__main__":
    raise SystemExit(main())
