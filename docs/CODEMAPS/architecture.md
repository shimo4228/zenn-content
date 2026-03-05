<!-- Generated: 2026-03-06 | Files scanned: 63 articles + 1736 LOC scripts | Token estimate: ~600 -->
# Architecture

## Project Type
Zenn content repository — articles (JP/EN) + automated publishing pipeline.

## Data Flow

```
articles/*.md (JP)  ──┐
                      ├→ git push → Zenn CDN (auto-deploy)
articles-en/*.md (EN) ┘
                          │
                          ├→ zenn_publish.py (07:00 JST, launchd)
                          │    published: false → true, git commit+push
                          │
                          └→ scheduled_publish.py (09:00 JST, launchd)
                               Qiita API (JP), Dev.to API (EN), Hashnode GraphQL (EN)
```

## Directory Layout

```
zenn-content/
├── articles/          28 JP articles (Zenn frontmatter)
├── articles-en/       35 EN translations
├── books/             (empty, reserved)
├── images/            article images
├── drafts/            unpublished WIP
├── scripts/           publishing automation (Python, 1736 LOC)
│   ├── zenn_publish.py        Zenn auto-publish (launchd 07:00)
│   ├── scheduled_publish.py   cross-post orchestrator (launchd 09:00)
│   ├── publish.py             cross-post API client (Qiita/Dev.to/Hashnode)
│   ├── plan_schedule.py       schedule.json generator
│   ├── schedule.json          publication schedule (source of truth)
│   └── tests/                 4 test files
├── docs/              runbook, glossary, contribution guide
├── .claude/           project skills (10), agents (1: editor)
└── .github/workflows/ lint CI (textlint + markdownlint + zenn validate)
```

## Toolchain
- **Lint**: textlint (ja-technical-writing) + markdownlint-cli2 + prh
- **Pre-commit**: husky + lint-staged (staged .md only)
- **CI**: GitHub Actions (lint on push/PR to main)
- **Publishing**: Python 3 + uv, launchd schedulers
- **Preview**: `npm run preview` (zenn-cli)
