---
title: "Setting Up textlint + markdownlint Hooks for Zenn Writing with Claude Code"
emoji: "🔧"
type: "tech"
topics: ["claudecode", "zenn", "textlint", "markdownlint"]
published: true
---

After writing three Zenn articles with Claude Code, I ran the linter on all of them at once and got 28 errors. Full-width space contamination, skipped heading levels, inconsistent terminology -- all things that slip through manual review.

"If it stopped me automatically before commit, I wouldn't have this rework."

So I set up a pre-commit hook that enforces textlint and markdownlint on every commit.

## Overall Structure

```text
package.json          ← lint-staged configuration
.husky/pre-commit     ← husky hook
.textlintrc.json      ← textlint configuration
.markdownlint-cli2.jsonc ← markdownlint configuration
prh.yml               ← terminology consistency dictionary
```

## Setup

### 1. Install Packages

```bash
npm install -D textlint textlint-rule-preset-ja-technical-writing \
  textlint-rule-prh textlint-rule-no-dead-link \
  textlint-filter-rule-comments \
  markdownlint-cli2 husky lint-staged
```

### 2. Initialize husky

```bash
npx husky init
```

Write the following in `.husky/pre-commit`:

```bash
npx lint-staged
```

### 3. Configure lint-staged

Add this to `package.json`:

```json
{
  "lint-staged": {
    "articles/**/*.md": [
      "textlint",
      "markdownlint-cli2"
    ],
    "books/**/*.md": [
      "textlint",
      "markdownlint-cli2"
    ]
  }
}
```

Only staged `.md` files are linted.

### 4. Configure textlint

Create `.textlintrc.json`:

```json
{
  "filters": {
    "comments": true
  },
  "rules": {
    "preset-ja-technical-writing": {
      "no-exclamation-question-mark": false,
      "ja-no-mixed-period": {
        "periodMark": "。",
        "allowPeriodMarks": ["："]
      }
    },
    "no-dead-link": {
      "checkRelative": true,
      "ignore": ["https://localhost*"],
      "retry": 3
    },
    "prh": {
      "rulePaths": ["prh.yml"]
    }
  }
}
```

Enabling `filters.comments` lets you selectively disable rules with `<!-- textlint-disable -->`. This is useful when you intentionally use casual language in parts of a Zenn article.

### 5. Configure markdownlint

Create `.markdownlint-cli2.jsonc`:

```jsonc
{
  "config": {
    "MD013": false,
    "MD025": false,
    "MD041": false,
    "MD060": false,
    "MD034": false,
    "MD036": false,
    "MD033": {
      "allowed_elements": ["details", "summary", "br"]
    }
  },
  "ignores": ["node_modules", "drafts", ".zenn"]
}
```

Here is why each Zenn-specific rule is disabled:

- **MD013** (line length limit): Japanese text naturally produces long lines, so this limit is impractical
- **MD025** (single H1 only): Zenn treats the frontmatter `title` as the H1 equivalent. `#` in the body is not actually H1
- **MD041** (first line should be a heading): The frontmatter comes first, making this rule irrelevant
- **MD034** (no bare URLs): Zenn automatically converts standalone URLs into rich embeds
- **MD036** (no emphasis as heading): Zenn articles commonly use bold text as sub-headings
- **MD060** (no space in code spans): False positives when writing Zenn-specific syntax like `:::message` in inline code

### 6. prh (Terminology Consistency Dictionary)

Use `prh.yml` to enforce consistent terminology:

```yaml
version: 1
rules:
  - expected: GitHub
    patterns:
      - Github

  - expected: サーバー
    pattern: /サーバ(?!ー)/
```

## Two Gotchas

### Do Not Put Globs in the markdownlint Config

If you write patterns in the `globs` field of `.markdownlint-cli2.jsonc`, those patterns take priority even when running through lint-staged. The result is that **all files get linted**, not just the staged ones.

```jsonc
// BAD: conflicts with lint-staged
{
  "globs": ["articles/**/*.md"]
}
```

Leave glob handling to lint-staged and keep it out of the config file.

### Do Not Use Hyphenated Patterns in prh

Starting with Node.js 20, Unicode mode is enabled by default for regular expressions. `\-` (escaped hyphen) is no longer recognized as a literal hyphen, which causes textlint to crash.

```yaml
# BAD: crashes on Node.js 20+
- expected: Claude-Native
  pattern: /Claude\-Native/

# OK: use patterns (literal string matching)
- expected: Claude-Native
  patterns:
    - claude-native
    - Claude native
```

Use `patterns` (string matching) as a workaround, or rewrite the regex to avoid hyphens.

## Verification

```bash
# Lint all files manually
npm run lint:all

# Auto-lint on Git commit (staged files only)
git add articles/my-article.md
git commit -m "feat: add new article"
# → textlint and markdownlint run automatically
```

If there are errors, the commit is blocked. Fix them and commit again.

## What Changed After This Setup

Before the setup, I would write five or six articles, then batch-run the linter and fight through a mountain of errors. With the pre-commit hook, I fix one or two issues per commit instead.

One remaining issue: the `no-dead-link` rule requires network access, so the pre-commit hook can time out in offline environments. An alternative is to run dead link checks in CI and temporarily skip the hook locally with `--no-verify`.
