---
title: "Growing a Zenn Writing Environment from Scratch with Claude Code"
emoji: "🛠️"
type: "tech"
topics: ["claudecode", "zenn", "textlint", "python"]
published: true
---

I write Zenn articles with Claude Code. My role is to set the direction, read the finished article end-to-end, and provide fact-checks and feedback. Claude Code handles the actual edits.

After two weeks of this workflow, I noticed a natural cycle forming: every time a problem comes up, it gets turned into a reusable mechanism so it never happens again. Verbal instructions become skills, manual tasks become scripts, and pitfalls become learned skills. Everything stays in the environment in a reusable form.

This article documents the problems I encountered and what each one was turned into.

## First: Turning Tone into a Skill

Before writing the first article, I defined the writing tone. "Technical but not too casual," "no AI slop," "be honest about failures" — I gave Claude Code detailed style instructions and saved them as a `zenn-writer` skill.

Before creating the skill, I had to repeat "use polite Japanese" and "no AI slop" every time I started a new session. With the skill in place, the same tone is maintained from the next article onward without any instructions. Verbal instructions are forgotten, but skill files persist. This was the starting point of systematization.

## 28 Lint Errors → Pre-commit Hook

After writing three articles, I ran the linter on all of them and got 28 errors. Full-width space infiltration, heading level jumps, inconsistent terminology. Pointing them out one by one was inefficient, so I told Claude Code: "I want a mechanism that stops commits automatically before they go through."

It set up a pre-commit hook with husky + lint-staged.

```text
package.json             ← lint-staged config
.husky/pre-commit        ← husky hook (runs npx lint-staged)
.textlintrc.json         ← textlint rules
.markdownlint-cli2.jsonc ← markdownlint rules
prh.yml                  ← terminology consistency dictionary
```

textlint uses `preset-ja-technical-writing` as a base, with `no-dead-link` (broken link detection) and `prh` (terminology consistency) added on top. markdownlint has Zenn-specific rules disabled.

```jsonc
// .markdownlint-cli2.jsonc — Zenn-specific overrides
{
  "config": {
    "MD013": false,  // Japanese lines tend to be long
    "MD025": false,  // Zenn uses frontmatter title as H1
    "MD041": false,  // First line is frontmatter
    "MD060": false   // False positive on :::message syntax
  }
}
```

There was a gotcha here. Claude Code initially added `"globs": ["articles/**/*.md"]` to `.markdownlint-cli2.jsonc`. However, when run via lint-staged, the config-side globs override the file specification, causing **all files to be linted**. When I reported this behavior, Claude Code removed the globs and switched to controlling file patterns on the lint-staged side.

```json
// package.json — let lint-staged control file selection
{
  "lint-staged": {
    "articles/**/*.md": ["textlint", "markdownlint-cli2"],
    "books/**/*.md": ["textlint", "markdownlint-cli2"]
  }
}
```

**What it became**: The 28 errors became a pre-commit hook. The globs pitfall was auto-extracted as a `learned/zenn-markdownlint-config` skill, preventing Claude Code from making the same mistake again.

## Node.js 20 Crash → Learned Skill

Without changing a single line of code, textlint crashed.

```text
SyntaxError: Invalid regular expression: /Claude\-first/gmu: Invalid escape
```

The cause was Node.js 20's Unicode mode (`u` flag). prh automatically appends `gmu` flags to its internal regular expressions. Under the `u` flag, `\-` outside a character class is treated as an invalid escape, so any pattern with a hyphen in `prh.yml` crashes immediately.

When I showed Claude Code the error log, it identified the cause right away.

```yaml
# NG: Crashes on Node.js 20+
- expected: Claude-Native
  pattern: /Claude\-Native/

# OK: patterns (literal strings) are safe
- expected: Claude-Native
  patterns:
    - claude native
    - Claude based
```

Claude Code scanned the entire prh.yml and rewrote all hyphen-containing patterns to use `patterns` (literal string matching) instead.

**What it became**: This workaround was auto-extracted as a `learned/prh-hyphen-regex-escape` skill. From then on, Claude Code automatically avoids hyphen-containing patterns when editing prh.yml. The harder a bug is to reproduce — like a runtime version-specific crash — the more valuable it is to capture as a skill.

## Fake Character Count → MCP Server

Zenn articles are generally most readable around 2,000–4,000 characters. When I asked Claude Code "How many characters is this article?", it replied "approximately 2,800 characters." The actual count was 3,200. A 400-character gap.

LLMs can't accurately handle Japanese token boundaries. English can be split on whitespace, but Japanese has no spaces between words, so the response is estimation-based.

When I said "I need an accurate way to count," Claude Code suggested connecting a kuromoji.js-based Japanese text analysis tool as an MCP server. It only requires adding a config entry to `~/.claude.json`.

```json
{
  "mcpServers": {
    "JapaneseTextAnalyzer": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "github:Mistizz/mcp-JapaneseTextAnalyzer"]
    }
  }
}
```

```text
me: Check the character count of this article
Claude Code: [Runs JapaneseTextAnalyzer.count_chars]
→ 3,201 characters (excluding line breaks and spaces)
```

**What it became**: Since it's in `~/.claude.json` (global config), it works across all projects. Instead of relying on LLM estimation, it returns accurate dictionary-based values. The decision to "delegate what LLMs are bad at to external tools" itself became a mechanism — an MCP server.

## Cross-posting → Python Script

When several articles had accumulated, I told Claude Code "I want to cross-post to Qiita too." It immediately pointed out: "Zenn's `:::message` and `:::details` won't render on Qiita. Format conversion is needed." An obvious point in retrospect, but I hadn't thought of it.

Claude Code built a conversion script, and `scripts/publish.py` was born.

Three conversion rules:

- `:::message` → blockquote (`>` syntax)
- `:::details title` → HTML `<details>` tag
- `/images/` → GitHub raw URL

```bash
# Publish to Qiita
python scripts/publish.py articles/my-article.md --platform qiita

# Update existing article (auto-search by title)
python scripts/publish.py articles/my-article.md --platform qiita --update auto
```

`--update auto` searches for existing articles by exact title match and updates them. Edit on Zenn, run `--update auto`, and Qiita follows — all in one command.

Later, support was extended to Dev.to and Hashnode. A `--force` guard was added to prevent accidentally posting Japanese articles to English-language platforms by checking whether a translated file exists.

**What it became**: The risk of format breakage from manual copy-paste was replaced by the `publish.py` script. The entire cross-posting workflow was auto-extracted as `learned/zenn-qiita-crosspost-workflow`, serving as a procedure guide when Claude Code suggests cross-posting.

## Pre-publish Review with a Strict Editor → Agent

As the tooling came together, the next concern was article quality itself. Linting mechanically checks formatting rules, but it can't judge "will this explanation make sense to readers?", "has AI slop crept in?", or "is anything technically inaccurate?"

I used Claude Code's agent feature to define a strict editor agent in `.claude/agents/editor.md`. It reviews articles on six criteria:

1. **Technical accuracy** — Are code snippets executable? Are explanations truthful?
2. **Code quality** — Missing imports, syntax errors, unnecessary information?
3. **Narrative flow** — Opening hook, motivation, logical progression, conclusion coherence?
4. **Terminology consistency** — Following project-specific style rules?
5. **AI slop detection** — Empty phrases like "powerful tool" or "seamless"?
6. **Audience fit** — Right level of explanation for the target reader?

Reviews use a 4-tier scale (EXCELLENT / GOOD / NEEDS REVISION / MAJOR ISSUES), with issues classified as CRITICAL / MEDIUM / MINOR. This article itself went through this editor's review.

**What it became**: The vague anxiety of "is this article good enough?" became a reproducible review process. Since it's stored as an agent definition file, review criteria persist across sessions.

## The Systematization Cycle

Here's the full picture of the environment:

```text
Write article (zenn-writer skill maintains tone)
  → git commit → pre-commit hook auto-runs lint
  → "How many chars?" → MCP server counts accurately
  → editor agent reviews quality
  → publish.py → converts format, posts to Qiita/Dev.to
```

Each problem and what it became:

| Problem | Became | Type |
|---------|--------|------|
| Tone inconsistency | `zenn-writer` | Skill |
| 28 lint errors | pre-commit hook | Config |
| markdownlint globs trap | `learned/zenn-markdownlint-config` | Learned skill |
| prh × Node.js 20 crash | `learned/prh-hyphen-regex-escape` | Learned skill |
| LLM's fake char count | JapaneseTextAnalyzer MCP | External tool |
| Ad-hoc quality checks | `editor` agent | Agent |
| Cross-post format breakage | `scripts/publish.py` | Script |
| Cross-post workflow | `learned/zenn-qiita-crosspost-workflow` | Learned skill |

None of these were planned from the start. Problems came up while writing articles, Claude Code and I solved them together, and the knowledge stayed in the environment as skills and scripts. The environment gets a little smarter with every problem. That's what it means to "grow" a writing environment with Claude Code.
