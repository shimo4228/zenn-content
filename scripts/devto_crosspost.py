"""Per-article scheduled Dev.to cross-poster.

Dev.to has no future-publish API, so each EN article is posted by a one-shot
launchd agent that fires at the article's exact `publish_at` datetime (tuned to
the overseas buzz window). This is the local scheduler; Zenn (JP) schedules
itself natively via `published_at` frontmatter and is NOT handled here.

Commands:
    devto_crosspost.py schedule <slug> [--at "<datetime tz>"]  # arm a one-shot job
    devto_crosspost.py post <slug>                             # post now (what launchd runs)
    devto_crosspost.py list                                    # show scheduled / posted
    devto_crosspost.py unschedule <slug>                       # cancel a pending job

`publish_at` accepts an IANA timezone so you can think in the target audience's
clock, e.g. "2026-07-07 09:00 America/New_York"; it is converted to JST (this
Mac's clock, which is what launchd fires on). A bare "YYYY-MM-DD HH:MM" is JST.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import frontmatter
import httpx

JST = ZoneInfo("Asia/Tokyo")

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEDULE_PATH = SCRIPT_DIR / "schedule.json"
ENV_PATH = SCRIPT_DIR / ".env"
LOG_PATH = SCRIPT_DIR / "devto_crosspost.log"
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"

DEVTO_API_BASE = "https://dev.to/api"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/shimo4228/zenn-content/main/images"
AGENT_PREFIX = "dev.shimo4228.devto-"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Env + schedule I/O
# ---------------------------------------------------------------------------


def load_env(env_path: Path = ENV_PATH) -> None:
    """Load KEY=VALUE pairs from a .env file into os.environ."""
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def load_schedule(schedule_path: Path = SCHEDULE_PATH) -> dict[str, Any]:
    """Load schedule.json, raising SystemExit on errors."""
    try:
        return json.loads(schedule_path.read_text())
    except FileNotFoundError:
        logger.error("Schedule file not found: %s", schedule_path)
        raise SystemExit(1)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in schedule file: %s", e)
        raise SystemExit(1)


def save_schedule(schedule: dict[str, Any], schedule_path: Path = SCHEDULE_PATH) -> None:
    """Write schedule dict back to JSON (Unicode preserved)."""
    schedule_path.write_text(json.dumps(schedule, indent=2, ensure_ascii=False) + "\n")


def validate_article_path(file_path: str, repo_root: Path = REPO_ROOT) -> Path | None:
    """Resolve an article path and validate it stays within the repo root."""
    article_path = (repo_root / file_path).resolve()
    if not article_path.is_relative_to(repo_root.resolve()):
        logger.error("Path traversal detected: %s", file_path)
        return None
    if not article_path.exists():
        logger.warning("File not found: %s", file_path)
        return None
    return article_path


def slug_of(file_path: str) -> str:
    """articles-en/foo-bar.md → foo-bar."""
    return Path(file_path).stem


def find_entry(schedule: dict[str, Any], slug: str) -> dict[str, Any] | None:
    """Find the EN schedule entry whose file basename matches slug."""
    for entry in schedule["articles"]:
        file = entry.get("file", "")
        if file.startswith("articles-en/") and slug_of(file) == slug:
            return entry
    return None


# ---------------------------------------------------------------------------
# publish_at parsing (tz-aware → JST)
# ---------------------------------------------------------------------------


def parse_publish_at(value: str) -> datetime:
    """Parse "YYYY-MM-DD HH:MM [IANA/Tz]" into a JST-aware datetime.

    A trailing timezone (e.g. "America/New_York") is honored and converted to
    JST; without one, the time is assumed to already be JST. Raises ValueError
    on malformed input.
    """
    parts = value.strip().split()
    if len(parts) == 3:
        date_s, time_s, tz_s = parts
        tz = ZoneInfo(tz_s)
    elif len(parts) == 2:
        date_s, time_s = parts
        tz = JST
    else:
        raise ValueError(f"bad publish_at (want 'YYYY-MM-DD HH:MM [Tz]'): {value!r}")
    naive = datetime.strptime(f"{date_s} {time_s}", "%Y-%m-%d %H:%M")
    return naive.replace(tzinfo=tz).astimezone(JST)


def now_jst() -> datetime:
    return datetime.now(tz=JST)


# ---------------------------------------------------------------------------
# Zenn → Dev.to conversion (proven rules — kept verbatim)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Article:
    title: str
    body: str
    topics: tuple[str, ...]
    article_type: str = "tech"
    description: str = ""


def parse_zenn_article(path: Path) -> Article:
    """Parse a Zenn article markdown file into an Article."""
    post = frontmatter.load(str(path))
    metadata: dict[str, object] = post.metadata  # type: ignore[assignment]
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


_ZENN_MESSAGE_RE = re.compile(r"^:::message\s*\n(.*?)\n^:::\s*$", re.MULTILINE | re.DOTALL)
_ZENN_DETAILS_RE = re.compile(r"^:::details\s+(.*?)\s*\n(.*?)\n^:::\s*$", re.MULTILINE | re.DOTALL)
_ZENN_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(/images/([^)]+)\)")


def _message_to_blockquote(m: re.Match[str]) -> str:
    lines = m.group(1).strip().splitlines()
    return "\n".join(f"> {line}" for line in lines)


def _details_to_html(m: re.Match[str]) -> str:
    summary = m.group(1).strip()
    body = m.group(2).strip()
    return f"<details><summary>{summary}</summary>\n\n{body}\n\n</details>"


def strip_zenn_syntax(content: str) -> str:
    """Replace Zenn-specific syntax with standard Markdown / HTML equivalents."""
    content = _ZENN_IMAGE_RE.sub(rf"![\1]({GITHUB_RAW_BASE}/\2)", content)
    content = _ZENN_MESSAGE_RE.sub(_message_to_blockquote, content)
    content = _ZENN_DETAILS_RE.sub(_details_to_html, content)
    return content


def resolve_devto_tags(article: Article, override: list[str] | None) -> list[str]:
    """Resolve Dev.to tags (max 4, deduped).

    Prefer the schedule's explicit `devto_tags`; that is how entries should set
    tags. Without an override, fall back to the article's own alphanumeric
    English topics (Dev.to rejects non-alphanumeric tags, so Japanese / dotted
    topics are dropped). `idea` articles get `discuss` prepended.
    """
    seen: set[str] = set()
    tags: list[str] = []
    source = override if override else article.topics
    for raw in source:
        low = raw.lower()
        sanitized = re.sub(r"[^a-z0-9]", "", low)
        if not override and (not sanitized or sanitized != low):
            continue  # fallback path drops non-ascii / dotted topics
        tag = sanitized if not override else low
        if tag and tag not in seen:
            seen.add(tag)
            tags.append(tag)
    if not override and article.article_type == "idea" and "discuss" not in seen:
        tags.insert(0, "discuss")
    return tags[:4]


def cover_url(entry: dict[str, Any], slug: str) -> str | None:
    """Cover image URL: explicit override, else a manual PNG if one exists."""
    if entry.get("cover_image"):
        return str(entry["cover_image"])
    if (REPO_ROOT / "images" / "covers" / f"{slug}.png").exists():
        return f"{GITHUB_RAW_BASE}/covers/{slug}.png"
    return None


def convert_to_devto(article: Article, entry: dict[str, Any], slug: str) -> dict[str, Any]:
    """Convert an Article + schedule entry to a Dev.to API request body."""
    payload: dict[str, Any] = {
        "article": {
            "title": article.title,
            "body_markdown": strip_zenn_syntax(article.body),
            "published": True,
            "tags": resolve_devto_tags(article, entry.get("devto_tags")),
        }
    }
    if article.description:
        payload["article"]["description"] = article.description
    cover = cover_url(entry, slug)
    if cover:
        payload["article"]["main_image"] = cover
    return payload


# ---------------------------------------------------------------------------
# Dev.to API
# ---------------------------------------------------------------------------


def _devto_headers(api_key: str) -> dict[str, str]:
    return {"Accept": "application/vnd.forem.api-v1+json", "api-key": api_key}


def post_to_devto(payload: dict[str, Any], api_key: str) -> str:
    """POST a new article to Dev.to. Returns the published URL; raises on failure."""
    resp = httpx.post(
        f"{DEVTO_API_BASE}/articles",
        headers=_devto_headers(api_key),
        json=payload,
        timeout=30,
    )
    if resp.status_code != 201:
        raise RuntimeError(f"POST failed {resp.status_code}: {resp.text[:200]}")
    try:
        url = resp.json().get("url")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"POST 201 but non-JSON body: {e}")
    if not url:
        raise RuntimeError("POST 201 but response had no 'url'")
    return url


def find_existing_devto_url(title: str, api_key: str) -> str | None:
    """Search the authed user's published articles for a matching title.

    Idempotency guard: publishing is an irreversible outward action, so before a
    new POST we check whether this exact title is already live (e.g. a prior run
    posted it but crashed before save_schedule, or it was posted by hand).

    Returns the URL if found, None if confirmed absent. Raises RuntimeError if the
    search cannot be completed (non-200) — the caller must fail closed rather than
    treat an unfinished check as "no duplicate".
    """
    for page in range(1, 6):
        resp = httpx.get(
            f"{DEVTO_API_BASE}/articles/me/published",
            headers=_devto_headers(api_key),
            params={"page": page, "per_page": 30},
            timeout=30,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"duplicate check failed {resp.status_code}: {resp.text[:200]}")
        items = resp.json()
        if not items:
            return None
        for item in items:
            if item.get("title") == title:
                return item.get("url")
    return None


# ---------------------------------------------------------------------------
# launchd one-shot agent
# ---------------------------------------------------------------------------


def agent_label(slug: str) -> str:
    return f"{AGENT_PREFIX}{slug}"


def agent_plist_path(slug: str) -> Path:
    return LAUNCH_AGENTS_DIR / f"{agent_label(slug)}.plist"


def render_plist(slug: str, fire: datetime) -> str:
    """Render a one-shot launchd plist firing at `fire` (JST) to post `slug`.

    Paths use the running interpreter and this script's resolved location, so no
    username is hard-coded in tracked source — the rendered file lives only in
    the user's untracked ~/Library/LaunchAgents.
    """
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{agent_label(slug)}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{Path(__file__).resolve()}</string>
        <string>post</string>
        <string>{slug}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{SCRIPT_DIR}</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Month</key><integer>{fire.month}</integer>
        <key>Day</key><integer>{fire.day}</integer>
        <key>Hour</key><integer>{fire.hour}</integer>
        <key>Minute</key><integer>{fire.minute}</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{LOG_PATH}</string>
    <key>StandardErrorPath</key>
    <string>{LOG_PATH}</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
"""


def _launchctl(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["launchctl", *args], capture_output=True, text=True, check=False,
    )


def install_agent(slug: str, fire: datetime) -> None:
    LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    path = agent_plist_path(slug)
    path.write_text(render_plist(slug, fire))
    _launchctl("unload", str(path))  # replace any stale job for this slug
    result = _launchctl("load", str(path))
    if result.returncode != 0:
        # Don't leave a phantom plist that makes `list` report a rejected job as armed.
        path.unlink(missing_ok=True)
        logger.error("launchctl load failed: %s", result.stderr.strip())
        raise SystemExit(1)


def remove_agent(slug: str) -> None:
    """Best-effort unload + delete of a slug's launchd agent (self-cleanup)."""
    path = agent_plist_path(slug)
    if not path.exists():
        return
    result = _launchctl("unload", str(path))
    if result.returncode != 0:
        # Surface it: the job may remain resident even though we remove the file.
        logger.warning("launchctl unload failed for %s: %s (removing plist anyway)", slug, result.stderr.strip())
    path.unlink()


def agent_installed(slug: str) -> bool:
    return agent_plist_path(slug).exists()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_schedule(slug: str, at: str, *, dry_run: bool) -> int:
    """Arm a one-shot launchd job at the datetime given on the command line.

    The time is an argument, not stored state — nothing is written to
    schedule.json. `at` accepts 'YYYY-MM-DD HH:MM [IANA/Tz]' (tz optional → JST).
    """
    file = f"articles-en/{slug}.md"
    if validate_article_path(file) is None:
        logger.error("Article not found: %s", file)
        return 1
    try:
        fire = parse_publish_at(at)
    except (ValueError, KeyError) as e:
        logger.error("Cannot parse --at %r (want 'YYYY-MM-DD HH:MM [Tz]'): %s", at, e)
        return 1
    if fire <= now_jst():
        logger.error("--at is in the past (JST %s); refusing to schedule.", fire)
        return 1

    if dry_run:
        logger.info("[DRY-RUN] would fire %s (JST) for %s", fire, slug)
        logger.info("Plist:\n%s", render_plist(slug, fire))
        return 0

    install_agent(slug, fire)
    logger.info("Scheduled %s → Dev.to at %s JST (launchd agent %s)", slug, fire, agent_label(slug))
    return 0


def cmd_post(schedule: dict[str, Any], slug: str, *, dry_run: bool) -> int:
    """Post an EN article to Dev.to now (what the launchd job runs).

    Resolves articles-en/<slug>.md directly. A matching schedule.json entry (if
    any) supplies tag/cover overrides and is used as the posted-URL ledger; it is
    not required. Idempotent: skips if already recorded or already live by title.
    """
    file = f"articles-en/{slug}.md"
    entry = find_entry(schedule, slug) or {"file": file}

    existing = entry.get("devto")
    if existing and existing != "pending":
        logger.info("Already posted (%s); nothing to do.", existing)
        remove_agent(slug)
        return 0

    article_path = validate_article_path(file)
    if article_path is None:
        return 1
    article = parse_zenn_article(article_path)

    api_key = os.environ.get("DEVTO_API_KEY")
    if not api_key:
        logger.error("Missing env var: DEVTO_API_KEY")
        return 1

    if dry_run:
        payload = convert_to_devto(article, entry, slug)
        logger.info("[DRY-RUN] would POST %r with tags %s", article.title, payload["article"]["tags"])
        return 0

    # Idempotency: skip a live duplicate if the title already exists on Dev.to.
    # Fail closed — if the check can't complete, don't risk a second public post.
    try:
        already = find_existing_devto_url(article.title, api_key)
    except (httpx.HTTPError, RuntimeError) as e:
        logger.error("Duplicate check failed (%s); aborting to avoid a double post.", e)
        return 1
    if already:
        logger.info("Title already live on Dev.to (%s); recording, not re-posting.", already)
        url = already
    else:
        try:
            url = post_to_devto(convert_to_devto(article, entry, slug), api_key)
        except (httpx.HTTPError, RuntimeError) as e:
            logger.error("Dev.to post failed for %s: %s", slug, e)
            return 1
        logger.info("Posted %s → %s", slug, url)

    # Record the URL only if this article is tracked in the schedule.json ledger.
    ledger_entry = find_entry(schedule, slug)
    if ledger_entry is not None:
        ledger_entry["devto"] = url
        try:
            save_schedule(schedule)
        except OSError as e:
            logger.error("Posted but failed to save schedule.json (%s); remove agent manually.", e)
            return 1
    remove_agent(slug)  # one-shot: don't fire again next year
    return 0


def cmd_list(schedule: dict[str, Any]) -> int:
    logger.info("%-45s %-26s %-10s %s", "File", "publish_at", "launchd", "Dev.to")
    logger.info("-" * 100)
    for entry in schedule["articles"]:
        file = entry.get("file", "")
        if not file.startswith("articles-en/"):
            continue
        slug = slug_of(file)
        devto = entry.get("devto")
        state = "posted" if devto and devto != "pending" else ("armed" if agent_installed(slug) else "-")
        logger.info(
            "%-45s %-26s %-10s %s",
            file, entry.get("publish_at", "-"), state, devto or "-",
        )
    return 0


def cmd_unschedule(slug: str) -> int:
    if not agent_installed(slug):
        logger.info("No launchd agent for %s.", slug)
        return 0
    remove_agent(slug)
    logger.info("Unscheduled %s.", slug)
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _setup_logging() -> None:
    if logger.handlers:
        return
    fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    for handler in (logging.FileHandler(LOG_PATH), logging.StreamHandler()):
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Per-article scheduled Dev.to cross-poster")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sched = sub.add_parser("schedule", help="Arm a one-shot launchd job for an article")
    p_sched.add_argument("slug", help="Article slug (articles-en/<slug>.md)")
    p_sched.add_argument("--at", required=True, help="Post datetime: 'YYYY-MM-DD HH:MM [IANA/Tz]' (tz optional → JST)")
    p_sched.add_argument("--dry-run", action="store_true", help="Show the plist without installing")

    p_post = sub.add_parser("post", help="Post an article to Dev.to now (what launchd runs)")
    p_post.add_argument("slug")
    p_post.add_argument("--dry-run", action="store_true", help="Convert without posting")

    sub.add_parser("list", help="Show scheduled / posted articles")

    p_unsched = sub.add_parser("unschedule", help="Cancel a pending launchd job")
    p_unsched.add_argument("slug")
    return parser


def main(argv: list[str] | None = None) -> int:
    _setup_logging()
    load_env()
    args = build_parser().parse_args(argv)
    schedule = load_schedule()

    if args.command == "schedule":
        return cmd_schedule(args.slug, args.at, dry_run=args.dry_run)
    if args.command == "post":
        return cmd_post(schedule, args.slug, dry_run=args.dry_run)
    if args.command == "list":
        return cmd_list(schedule)
    if args.command == "unschedule":
        return cmd_unschedule(args.slug)
    return 1  # pragma: no cover — argparse enforces a valid subcommand


if __name__ == "__main__":
    raise SystemExit(main())
