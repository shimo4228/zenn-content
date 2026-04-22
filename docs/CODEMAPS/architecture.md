<!-- Generated: 2026-04-12 | Files scanned: 96 articles + scripts | Token estimate: ~600 -->
# Architecture

## Project Type
Zenn content repository — articles (JP/EN) + automated publishing pipeline.

## Data Flow

```
articles/*.md (JP)  ──→ git push → Zenn (published_at native scheduling)

articles-en/*.md (EN) ─→ git push → devto_crosspost.py
                                     (07:00 JST daily, GitHub Actions)
                                     → Dev.to API
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
│   ├── devto_crosspost.py     Dev.to cross-poster (GitHub Actions 07:00 JST)
│   ├── publish.py             Dev.to API client (format conversion, tagging)
│   ├── plan_schedule.py       schedule.json generator
│   ├── _schedule_utils.py     shared helpers (I/O, JST, path validation)
│   ├── generate_cover.py      cover image generator
│   ├── schedule.json          Dev.to publication schedule
│   └── tests/                 pytest (112 tests)
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
