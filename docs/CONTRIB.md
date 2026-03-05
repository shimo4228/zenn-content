# Contributing Guide

> Auto-generated from `package.json`, config files, and scripts — 2026-02-15

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | v25+ | Zenn CLI, textlint, markdownlint |
| npm | v11+ | Package management |
| Python | >=3.13 | Cross-post scripts (`scripts/.venv`) |

## Setup

```bash
# 1. Install Node dependencies
npm install

# 2. Setup Python venv for cross-post scripts
cd scripts
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Husky pre-commit hooks are installed automatically via `npm install` (`prepare` script).

## Available npm Scripts

| Script | Command | Description |
|--------|---------|-------------|
| `preview` | `zenn preview` | Start local Zenn preview server |
| `new:article` | `zenn new:article` | Scaffold a new article |
| `new:book` | `zenn new:book` | Scaffold a new book |
| `lint` | `textlint articles/**/*.md books/**/*.md` | Run textlint (Japanese technical writing rules) |
| `lint:md` | `markdownlint-cli2 'articles/**/*.md' 'books/**/*.md'` | Run markdownlint |
| `lint:all` | `npm run lint && npm run lint:md` | Run both linters |
| `lint:fix` | `textlint --fix articles/**/*.md books/**/*.md` | Auto-fix textlint violations |
| `prepare` | `husky` | Install git hooks (runs on `npm install`) |

## Linter Configuration

### textlint (`.textlintrc.json`)

- **preset-ja-technical-writing** — Japanese technical writing rules
  - `no-exclamation-question-mark`: disabled
  - `max-kanji-continuous-len`: 6 (allow: 機械学習, 深層学習, 自然言語処理)
- **no-dead-link** — Broken link checker (3 retries)
- **prh** (`prh.yml`) — Terminology consistency (pdf2anki, Claude-Native, CLI-First, etc.)

### markdownlint (`.markdownlint-cli2.jsonc`)

Disabled rules for Zenn compatibility:
- **MD025** — Zenn uses frontmatter title as H1
- **MD041** — No first-line heading requirement
- **MD060** — Table column style
- **MD013** — Line length (Japanese text is long)

Customized rules:
- **MD033** — HTML allowed: `details`, `summary`, `br`, `sup`, `sub`
- **MD024** — Duplicate headings allowed in siblings only
- **MD012** — Up to 2 blank lines allowed
- **MD026** — Japanese punctuation excluded from trailing-punctuation check

Ignored paths: `node_modules`, `drafts`, `.zenn`

### prh (`prh.yml`)

Enforces consistent terminology:
- `pdf2anki` (not PDF2Anki, Pdf2Anki)
- `Claude-Native`, `CLI-First`
- Japanese katakana: サーバー, ユーザー, プログラマー, インターフェース
- Proper casing: GitHub, TypeScript, JavaScript, Anki

> **Gotcha**: No hyphen-containing regex patterns in prh.yml (Node.js 20+ unicode regex bug).

### lint-staged (pre-commit)

Staged `.md` files in `articles/` and `books/` are automatically linted with both textlint and markdownlint on commit.

> **Gotcha**: Do NOT add globs to `.markdownlint-cli2.jsonc` — it breaks lint-staged (lints ALL files instead of just staged).

## Cross-Post Scripts

### `scripts/publish.py`

Manual CLI for cross-posting Zenn articles.

```bash
# Qiita
python scripts/publish.py articles/xxx.md --platform qiita
python scripts/publish.py articles/xxx.md --platform qiita --update auto

# Dev.to
python scripts/publish.py articles-en/xxx.md --platform devto --canonical-url URL
python scripts/publish.py articles-en/xxx.md --platform devto --update auto

# Hashnode
python scripts/publish.py articles-en/xxx.md --platform hashnode --canonical-url URL

# Dry-run (any platform)
python scripts/publish.py articles/xxx.md --platform qiita --dry-run
```

### `scripts/scheduled_publish.py`

Automated scheduler that reads `scripts/schedule.json` and posts due articles.

```bash
python scripts/scheduled_publish.py              # Post due articles
python scripts/scheduled_publish.py --dry-run    # Preview without posting
python scripts/scheduled_publish.py --status     # Show schedule status
```

### Python Dependencies (`scripts/pyproject.toml`)

| Package | Purpose |
|---------|---------|
| `httpx` | HTTP client for API calls |
| `python-frontmatter` | Parse Zenn article frontmatter |
| `pytest` | Testing (dev) |
| `respx` | HTTP mocking for tests (dev) |
| `pytest-cov` | Coverage reporting (dev, fail_under=80%) |

## Environment Variables

Set in `scripts/.env` (never committed):

| Variable | Required For | Description |
|----------|-------------|-------------|
| `QIITA_ACCESS_TOKEN` | Qiita | Qiita API v2 bearer token |
| `DEVTO_API_KEY` | Dev.to | Dev.to API key (Settings > Extensions) |
| `HASHNODE_API_TOKEN` | Hashnode | Hashnode Personal Access Token |
| `HASHNODE_PUBLICATION_ID` | Hashnode | Hashnode publication ID |

## Testing

```bash
# Run cross-post script tests
cd scripts
source .venv/bin/activate
pytest --cov=publish --cov-report=term-missing

# Run article linters
npm run lint:all
```

## Article Writing Workflow

1. `npm run new:article` — Scaffold article
2. Write content following CLAUDE.md guidelines
3. `npm run preview` — Local preview
4. `npm run lint:all` — Lint check
5. Commit (pre-commit hooks run automatically)
6. Cross-post with `publish.py` or schedule via `schedule.json`
