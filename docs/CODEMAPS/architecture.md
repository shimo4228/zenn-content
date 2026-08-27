<!-- Generated: 2026-08-27 | Files scanned: articles + articles-en + note + substack + scripts | Token estimate: ~700 -->
# Architecture

## Project Type
Zenn content repository — articles (JP/EN) + manual publishing helpers.

## Data Flow

```
articles/*.md (JP)  ──→ git push → Zenn (published_at native scheduling)

articles-en/*.md (EN) ─→ devto_crosspost.py (per-article one-shot launchd @ --at datetime) → Dev.to API

note/*.md (JA canonical) ──→ pasted into note manually (HTML via pandoc)
substack/*-en.md (EN)   ──→ pasted into Substack manually

articles frontmatter + schedule.json (Dev.to URLs) + corpus.yml (essays / papers) + reading_paths.yml
        ──→ generate_article_index.py ──→ docs/PUBLICATIONS.md + README reading-path blocks
            (CI: `npm run check:index` fails on drift; no bot commit — ADR-0009)
```

## Directory Layout

```
zenn-content/
├── articles/          JP articles (Zenn frontmatter; counts live in docs/PUBLICATIONS.md)
├── articles-en/       EN translations (legacy `<slug>-en.md` naming still resolved)
├── note/              JA idea essays — canonical, first published on note (MD + paste HTML)
├── substack/          EN idea essays for Substack (MD + HTML; out of Zenn convention scope)
├── books/             (empty, reserved)
├── images/            article + cover images
├── drafts/            unpublished WIP
├── scripts/           publishing automation (Python)
│   ├── devto_crosspost.py         per-article Dev.to cross-poster (one-shot launchd)
│   ├── generate_article_index.py  renders docs/PUBLICATIONS.md + README reading paths
│   ├── schedule.json              posted-URL ledger (post time is a --at argument)
│   ├── corpus.yml                 essays / papers / research lines (no-frontmatter membership)
│   ├── reading_paths.yml          README curated routes (author judgment)
│   ├── metrics_snapshot.py        Zenn / Dev.to reception snapshots → metrics/
│   └── tests/                     pytest (counts in scripts.md)
├── docs/              PUBLICATIONS.md (generated index), CODEMAPS, adr/, translation-glossary
├── .claude/           project platform skills (4), agent (1), publishing contract, refs
└── .github/workflows/ validate.yml (zenn frontmatter check, push/PR to main)
```

## Agents

Project agent: `devto-translator` (Dev.to-specific draft conversion; publishing remains a separate gated step). Drafting is done by the
orchestrator, not a subagent. Global writing agents are `theme-reviewer`, `editor`, `essay-reviewer`,
`prose-clarity-reviewer`, and `fact-checker`; global `writing-ecosystem` owns their sequence.

## Toolchain
- **Validation**: `zenn list:articles` (frontmatter check) via `npm run validate`.
  No prose/markdown linter — textlint/markdownlint/husky were removed 2026-07 as
  low-signal after the ja-technical-writing preset was dropped.
- **CI**: GitHub Actions `validate.yml` (frontmatter check + `check:index` drift gate on push/PR to main). No publishing cron.
- **Publishing**: Zenn `published_at` (JP, no script) + Dev.to cross-post (EN) via
  `devto_crosspost.py` — `schedule <slug> --at "<datetime>"` arms a per-article
  one-shot launchd job at that datetime; it posts once and self-removes
- **Preview**: `npm run preview` (zenn-cli)
