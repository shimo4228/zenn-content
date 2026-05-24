<!-- Generated: 2026-05-24 | Files scanned: 122 articles (65 JP / 57 EN) + scripts | Token estimate: ~640 -->
# Architecture

## Project Type
Zenn content repository — articles (JP/EN) + manual publishing helpers.

## Data Flow

```
articles/*.md (JP)  ──→ git push → Zenn (published_at native scheduling)

articles-en/*.md (EN) ─→ publish.py / devto_crosspost.py (manual run) → Dev.to API

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
│   ├── devto_crosspost.py     Dev.to cross-poster (manual run; reads schedule.json)
│   ├── publish.py             Dev.to API client (format conversion, tagging, --update)
│   ├── plan_schedule.py       schedule.json generator
│   ├── _schedule_utils.py     shared helpers (I/O, JST, path validation)
│   ├── generate_cover.py      cover image generator (Pillow)
│   ├── schedule.json          Dev.to publication schedule
│   └── tests/                 pytest (112 tests)
├── docs/              runbook, glossary, CODEMAPS, contribution guide
├── .claude/           project skills (11 + learned/), agents (2), rules, refs, docs/adr/
└── .github/workflows/ lint.yml (textlint + markdownlint, push/PR to main)
```

## Agents

Project agents (2): `zenn-drafter` (article writer), `devto-translator` (JP→EN + Dev.to).
Review agents are global (`~/.claude/agents/`): `editor`, `essay-reviewer`, `fact-checker`.

## Toolchain
- **Lint**: textlint (prh + comments filter) + markdownlint-cli2; `no-dead-link` is a manual `lint:links` command
- **Pre-commit**: husky + lint-staged (staged `articles/`,`books/` .md only)
- **CI**: GitHub Actions `lint.yml` (lint on push/PR to main). No publishing cron.
- **Publishing**: Zenn `published_at` (JP, no script) + manual Dev.to cross-post (EN)
- **Preview**: `npm run preview` (zenn-cli)
