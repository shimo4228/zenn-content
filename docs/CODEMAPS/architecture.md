<!-- Generated: 2026-04-12 | Files scanned: 96 articles + scripts | Token estimate: ~600 -->
# Architecture

## Project Type
Zenn content repository — articles (JP/EN) + automated publishing pipeline.

## Data Flow

```
articles/*.md (JP)  ──┐
                      ├→ git push → Zenn CDN (auto-deploy)
articles-en/*.md (EN) ┘
                          │
                          ├→ published_at (Zenn native)
                          │    予約投稿。指定時刻に自動公開
                          │
                          └→ scheduled_publish.py (09:00 JST, launchd)
                               Dev.to API (EN cross-post)
```

## Directory Layout

```
zenn-content/
├── articles/          45 JP articles (Zenn frontmatter)
├── articles-en/       51 EN translations
├── books/             (empty, reserved)
├── images/            article images
├── drafts/            unpublished WIP
├── scripts/           publishing automation (Python)
│   ├── zenn_publish.py        Zenn auto-publish (legacy, published_at に移行)
│   ├── scheduled_publish.py   cross-post orchestrator (launchd 09:00)
│   ├── publish.py             cross-post API client (Dev.to)
│   ├── plan_schedule.py       schedule.json generator
│   ├── schedule.json          publication schedule (source of truth)
│   └── tests/                 test files
├── docs/              runbook, glossary, contribution guide
├── .claude/           project skills (10), agents (5), learned (9)
└── .github/workflows/ lint CI (textlint + markdownlint + zenn validate)
```

## Agents (5)
- `editor` — tech 記事レビュー（4段階評価）
- `essay-reviewer` — idea 記事レビュー（論理・トーン）
- `fact-checker` — 事実主張の Web 検索検証
- `devto-translator` — JP→EN 翻訳 + Dev.to 投稿
- `zenn-drafter` — 記事執筆（3フェーズ）

## Toolchain
- **Lint**: textlint (ja-technical-writing) + markdownlint-cli2 + prh
- **Pre-commit**: husky + lint-staged (staged .md only)
- **CI**: GitHub Actions (lint on push/PR to main)
- **Publishing**: Python 3 + uv, Zenn published_at + launchd (Dev.to)
- **Preview**: `npm run preview` (zenn-cli)
