<!-- Generated: 2026-05-24 | Files scanned: 122 articles (65 JP / 57 EN) + scripts | Token estimate: ~640 -->
# Architecture

## Project Type
Zenn content repository — articles (JP/EN) + manual publishing helpers.

## Data Flow

```
articles/*.md (JP)  ──→ git push → Zenn (published_at native scheduling)

articles-en/*.md (EN) ─→ devto_crosspost.py (per-article one-shot launchd @ --at datetime) → Dev.to API

substack/*.md|.html  ──→ pasted into Substack manually (mirror only; not published from this repo)
```

## Directory Layout

```
zenn-content/
├── articles/          65 JP articles (Zenn frontmatter, 48 published)
├── articles-en/       57 EN translations (35 published)
├── substack/          Substack essay mirrors (MD + HTML; out of Zenn convention scope)
├── books/             (empty, reserved)
├── images/            article + cover images
├── drafts/            unpublished WIP
├── scripts/           publishing automation (Python)
│   ├── devto_crosspost.py     per-article Dev.to cross-poster (one-shot launchd)
│   ├── schedule.json          posted-URL ledger (post time is a --at argument)
│   └── tests/                 pytest (56 tests)
├── docs/              CODEMAPS, adr/ (design decisions), translation-glossary
├── .claude/           project skills (11 + learned/), agents (2), rules, refs
└── .github/workflows/ validate.yml (zenn frontmatter check, push/PR to main)
```

## Agents

Project agents (2): `zenn-drafter` (article writer), `devto-translator` (JP→EN + Dev.to).
Review agents are global (`~/.claude/agents/`): `editor`, `essay-reviewer`, `fact-checker`.

## Toolchain
- **Validation**: `zenn list:articles` (frontmatter check) via `npm run validate`.
  No prose/markdown linter — textlint/markdownlint/husky were removed 2026-07 as
  low-signal after the ja-technical-writing preset was dropped.
- **CI**: GitHub Actions `validate.yml` (frontmatter check on push/PR to main). No publishing cron.
- **Publishing**: Zenn `published_at` (JP, no script) + Dev.to cross-post (EN) via
  `devto_crosspost.py` — `schedule <slug> --at "<datetime>"` arms a per-article
  one-shot launchd job at that datetime; it posts once and self-removes
- **Preview**: `npm run preview` (zenn-cli)
