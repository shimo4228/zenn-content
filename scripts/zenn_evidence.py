#!/usr/bin/env python3
"""Deterministic evidence extractor for Zenn articles (``articles/*.md``).

Evidence, not a verdict. This script counts and lists what a reviewer would
otherwise count by eye: frontmatter fields, Zenn syntax structure, file
existence, and the link conventions the channel contract requires. It never
decides whether an article may be published — that judgment belongs to the
fresh-context reviewers and the author. There is no exit 1.

Canonical sources for the values checked here:

- ``.claude/rules/publishing-channels.md`` — channel table, Zenn frontmatter,
  Zenn-specific syntax, Related links, Project terminology
- ``.claude/skills/zenn-format/SKILL.md`` — frontmatter fields, emoji / topics,
  code blocks, images, links, message blocks

Two output layers, deliberately separated:

- ``deviations`` — a rule the contract states, broken by this article
- ``grandfathered`` — the same rule, broken by an article that was already
  published before the check existed. Reported, not counted as a deviation, so
  the check is not red on day one.
- ``signals`` — hybrid counts the script can measure but cannot interpret
  (register mixing, term variants, self-link placement). A reviewer reads these.

Usage::

    python zenn_evidence.py ../articles/some-article.md
    python zenn_evidence.py ../articles/ --text
    python zenn_evidence.py ../articles/ --online     # adds URL liveness
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

CANONICAL_REPO = "https://github.com/shimo4228/zenn-content"
AUTHOR_HUB = "https://github.com/shimo4228"

# Contract: 原則 50 字以内、正確さに必要なら 60 字まで
TITLE_SOFT_LIMIT = 50
TITLE_HARD_LIMIT = 60

VALID_TYPES = {"tech", "idea"}
TOPICS_MIN, TOPICS_MAX = 1, 5

# Project terminology — Use / Do not rewrite as
TERMINOLOGY = {
    "pdf2anki": ["PDF2Anki", "pdf-to-anki", "Pdf2Anki"],
    "Claude-Native": ["Claude-first", "Claude based"],
    "CLI-First": ["CLI first", "command-line first"],
    "半自動": ["semi-automatic", "partially automated"],
    "Anki card": [],
    "LLM critique": ["AI critique", "model critique"],
    "TDD": ["test driven", "test-first"],
}

# Personal-path detection is username-based on purpose. A bare ``/Users/`` match
# fires on every sanitised placeholder: measured 2026-08-27 over 70 articles, all
# 3 hits were documented examples (``/Users/you/`` ×2, ``/Users/hanma/`` ×1) and
# real-username occurrences were 0. Matching the placeholder is a false positive,
# not a leak.
PATH_PLACEHOLDERS = {"you", "username", "user", "hanma", "example", "yourname", "me"}
PERSONAL_PATH = re.compile(r"/Users/([A-Za-z0-9_.-]+)")

SECRET_PATTERNS = [
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b")),
    ("private-key-block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
]

HEADING = re.compile(r"^(#{1,6}) +(.*)$", re.M)
FENCE = re.compile(r"^(`{3,})(.*)$")
PUBLISHED_AT = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
LIST_LINK = re.compile(r"^\s*[-*] +\[", re.M)
MD_LINK = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")
IMAGE = re.compile(r"!\[[^\]]*\]\((/images/[^)\s]+)\)")

# ですます / だ・である. Sentence-final only — mid-sentence ``だ`` is a particle.
# ``した`` needs the lookbehind: without it the polite ``書きました。`` also counts
# as a plain ending and every article reads as register-mixed.
POLITE_END = re.compile(r"(?:です|ます|ません|ました|でした|ください)[。.！？!?]")
PLAIN_END = re.compile(r"(?:である|だった|(?<!ま)した|する|ない|られる)[。.！？!?]")


@dataclass
class Article:
    """One parsed article: frontmatter text, prose body, and fence-free prose."""

    path: Path
    raw: str
    frontmatter: str
    body: str
    #: body with fenced code blocks removed — heading and prose checks use this,
    #: otherwise a shell comment ``# foo`` reads as an H1 (measured: 2 articles).
    prose: str
    fences: list[tuple[int, str]] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return self.path.stem

    def fm(self, key: str) -> str | None:
        m = re.search(rf"^{re.escape(key)}:\s*(.*)$", self.frontmatter, re.M)
        return m.group(1).strip() if m else None

    @property
    def published(self) -> bool:
        return (self.fm("published") or "").lower() == "true"


def parse(path: Path) -> Article:
    raw = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n?", raw, re.S)
    frontmatter, body = (m.group(1), raw[m.end():]) if m else ("", raw)

    prose_lines: list[str] = []
    fences: list[tuple[int, str]] = []
    inside = False
    for i, line in enumerate(body.split("\n"), 1):
        fm_ = FENCE.match(line)
        if fm_:
            fences.append((i, fm_.group(2).strip()))
            inside = not inside
            continue
        if not inside:
            prose_lines.append(line)
    return Article(path, raw, frontmatter, body, "\n".join(prose_lines), fences)


def strip_quotes(value: str) -> str:
    v = value.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def emoji_count(value: str) -> int:
    """Count user-perceived emoji, joining ZWJ sequences and variation selectors."""
    n = 0
    prev_joined = False
    for ch in strip_quotes(value):
        if ch == "‍":
            prev_joined = True
            continue
        if unicodedata.category(ch) in {"Mn", "Cf"} or ch in "️︎":
            continue
        if prev_joined:
            prev_joined = False
            continue
        n += 1
    return n


def related_links_section(article: Article) -> str | None:
    """Text of the last heading containing 関連リンク, through the section end."""
    heads = [m for m in re.finditer(r"^(#{2,6}) +(.*関連リンク.*)$", article.body, re.M)]
    if not heads:
        return None
    last = heads[-1]
    level = len(last.group(1))
    rest = article.body[last.end():]
    for m in re.finditer(r"^(#{1,6}) +|^---\s*$", rest, re.M):
        if m.group(1) and len(m.group(1)) <= level:
            return rest[: m.start()]
        if not m.group(1):  # top-level --- separator (AI disclosure block)
            return rest[: m.start()]
    return rest


def check_frontmatter(a: Article, dev: list, grand: list, info: dict) -> None:
    for key in ("title", "emoji", "type", "topics", "published"):
        if a.fm(key) is None:
            dev.append({"rule": "frontmatter-field-missing", "field": key})

    typ = strip_quotes(a.fm("type") or "")
    if typ and typ not in VALID_TYPES:
        dev.append({"rule": "type-invalid", "value": typ, "allowed": sorted(VALID_TYPES)})

    emoji = a.fm("emoji")
    if emoji is not None and emoji_count(emoji) != 1:
        dev.append({"rule": "emoji-not-single", "value": strip_quotes(emoji)})

    raw_topics = a.fm("topics")
    if raw_topics is not None:
        topics = [strip_quotes(t) for t in re.findall(r'"[^"]*"|\'[^\']*\'|[^,\[\]\s]+', raw_topics)]
        topics = [t for t in topics if t]
        info["topics"] = topics
        if not TOPICS_MIN <= len(topics) <= TOPICS_MAX:
            dev.append({"rule": "topics-count", "count": len(topics), "allowed": [TOPICS_MIN, TOPICS_MAX]})
        upper = [t for t in topics if t != t.lower()]
        if upper:
            dev.append({"rule": "topics-not-lowercase", "values": upper})

    title = strip_quotes(a.fm("title") or "")
    info["title_length"] = len(title)
    if len(title) > TITLE_HARD_LIMIT:
        bucket = grand if a.published else dev
        bucket.append({"rule": "title-over-hard-limit", "length": len(title), "limit": TITLE_HARD_LIMIT})
    elif len(title) > TITLE_SOFT_LIMIT:
        info["title_over_soft_limit"] = True

    if a.published:
        pa = a.fm("published_at")
        if pa is None:
            dev.append({"rule": "published-at-missing"})
        elif not PUBLISHED_AT.match(strip_quotes(pa)):
            dev.append({"rule": "published-at-format", "value": strip_quotes(pa), "expected": "YYYY-MM-DD HH:MM"})


def check_structure(a: Article, dev: list, grand: list, info: dict) -> None:
    if len(a.fences) % 2 != 0:
        dev.append({"rule": "code-fence-unbalanced", "count": len(a.fences)})
    no_lang = [line for (line, lang), is_open in zip(a.fences, [i % 2 == 0 for i in range(len(a.fences))]) if is_open and not lang]
    if no_lang:
        bucket = grand if a.published else dev
        bucket.append({"rule": "code-fence-without-language", "lines": no_lang})

    opens = len(re.findall(r"^:::\S", a.prose, re.M))
    closes = len(re.findall(r"^:::\s*$", a.prose, re.M))
    if opens != closes:
        dev.append({"rule": "message-block-unbalanced", "open": opens, "close": closes})

    first = HEADING.search(a.prose)
    if first:
        level = len(first.group(1))
        info["first_heading_level"] = level
        if level != 2:
            bucket = grand if a.published else dev
            bucket.append({"rule": "body-heading-not-h2", "level": level, "heading": first.group(2)[:60]})


def check_links(a: Article, root: Path, dev: list, info: dict) -> None:
    rel = re.findall(r"\]\((/articles/[^)\s]+)\)", a.body)
    if rel:
        dev.append({"rule": "internal-link-relative", "values": sorted(set(rel)), "expected": "https://zenn.dev/shimo4228/articles/<slug>"})

    for img in sorted(set(IMAGE.findall(a.body))):
        if not (root / img.lstrip("/")).exists():
            dev.append({"rule": "image-missing", "path": img})

    section = related_links_section(a)
    if section is None:
        dev.append({"rule": "related-links-section-missing"})
        return

    canonical = f"{CANONICAL_REPO}/blob/main/articles/{a.slug}.md"
    if canonical not in section:
        wrong = re.findall(rf"{re.escape(CANONICAL_REPO)}/blob/main/articles/([a-z0-9-]+)\.md", section)
        dev.append({"rule": "canonical-link-missing", "expected": canonical, "found_slugs": wrong})

    if not re.search(rf"{re.escape(AUTHOR_HUB)}(?![/\w])", section):
        dev.append({"rule": "author-hub-missing", "expected": AUTHOR_HUB})

    info["related_links_count"] = len(LIST_LINK.findall(section))


def check_safety(a: Article, dev: list, info: dict) -> None:
    users = {u for u in PERSONAL_PATH.findall(a.body)}
    real = sorted(u for u in users if u.lower() not in PATH_PLACEHOLDERS)
    if real:
        dev.append({"rule": "personal-path", "users": real})
    if users - set(real):
        info["path_placeholders"] = sorted(users - set(real))

    for name, pattern in SECRET_PATTERNS:
        if pattern.search(a.body):
            dev.append({"rule": "secret-pattern", "kind": name})


def check_terminology(a: Article, dev: list) -> None:
    # Prose only. An article *about* terminology rules quotes the wrong forms
    # inside code blocks on purpose — measured 2026-08-27: the single corpus hit
    # was ``Claude based`` inside a prh.yml example in claude-code-zenn-writing-env.
    for correct, wrong_forms in TERMINOLOGY.items():
        hits = [w for w in wrong_forms if re.search(re.escape(w), a.prose)]
        if hits:
            dev.append({"rule": "terminology", "use": correct, "found": hits})


def collect_signals(a: Article) -> dict:
    """Hybrid layer: the script counts, a reviewer interprets."""
    polite = len(POLITE_END.findall(a.prose))
    plain = len(PLAIN_END.findall(a.prose))
    section = related_links_section(a) or ""
    body_self_links = len(re.findall(r"github\.com/shimo4228", a.body)) - len(
        re.findall(r"github\.com/shimo4228", section)
    )
    paragraphs = [p for p in re.split(r"\n\s*\n", a.prose) if p.strip()]
    return {
        "register": {"polite_endings": polite, "plain_endings": plain},
        "self_links": {"in_body": max(body_self_links, 0), "in_related_links": len(re.findall(r"github\.com/shimo4228", section))},
        "paragraphs": len(paragraphs),
        "headings": len(HEADING.findall(a.prose)),
        "external_urls": len(set(MD_LINK.findall(a.body))),
    }


def check_online(a: Article, dev: list) -> None:
    """URL liveness. Off by default — the only class with a measured catch rate
    (56bf025 broken external links, 62c3110 a private repo returning 404)."""
    import urllib.error
    import urllib.request

    for url in sorted(set(MD_LINK.findall(a.body))):
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "zenn-evidence/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310 - article URLs only
                code = resp.status
        except urllib.error.HTTPError as exc:
            code = exc.code
        except Exception as exc:  # network unreachable, DNS, TLS
            dev.append({"rule": "url-unreachable", "url": url, "error": type(exc).__name__})
            continue
        if code >= 400:
            dev.append({"rule": "url-dead", "url": url, "status": code})


def evaluate(path: Path, root: Path, online: bool = False) -> dict:
    a = parse(path)
    dev: list[dict] = []
    grand: list[dict] = []
    info: dict = {}

    check_frontmatter(a, dev, grand, info)
    check_structure(a, dev, grand, info)
    check_links(a, root, dev, info)
    check_safety(a, dev, info)
    check_terminology(a, dev)
    if online:
        check_online(a, dev)

    return {
        "file": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
        "slug": a.slug,
        "published": a.published,
        "deviations": dev,
        "grandfathered": grand,
        "info": info,
        "signals": collect_signals(a),
    }


def render_text(results: list[dict]) -> str:
    lines: list[str] = []
    total_dev = sum(len(r["deviations"]) for r in results)
    total_grand = sum(len(r["grandfathered"]) for r in results)
    lines.append(f"articles: {len(results)}  deviations: {total_dev}  grandfathered: {total_grand}")
    for r in results:
        if not r["deviations"] and not r["grandfathered"]:
            continue
        lines.append(f"\n{r['file']}")
        for d in r["deviations"]:
            extra = ", ".join(f"{k}={v}" for k, v in d.items() if k != "rule")
            lines.append(f"  deviation    {d['rule']}" + (f" ({extra})" if extra else ""))
        for g in r["grandfathered"]:
            extra = ", ".join(f"{k}={v}" for k, v in g.items() if k != "rule")
            lines.append(f"  grandfathered {g['rule']}" + (f" ({extra})" if extra else ""))
    if total_dev == 0:
        lines.append("\nno deviations")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("path", type=Path, help="article file or directory of articles")
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--text", action="store_true", help="human-readable output instead of JSON")
    ap.add_argument("--online", action="store_true", help="also check external URL liveness (network)")
    ns = ap.parse_args(argv)

    root = ns.root.resolve()
    target = ns.path if ns.path.is_absolute() else (Path.cwd() / ns.path)
    target = target.resolve()
    if target.is_dir():
        paths = sorted(target.glob("*.md"))
    elif target.exists():
        paths = [target]
    else:
        print(f"error: no such path: {ns.path}", file=sys.stderr)
        return 2

    results = [evaluate(p, root, online=ns.online) for p in paths]
    print(render_text(results) if ns.text else json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
