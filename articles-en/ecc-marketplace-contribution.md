---
title: "I Found the Shortest Route to Ship My Claude Code Skills to 57,000 Developers"
emoji: "🌐"
type: "tech"
topics: ["claudecode", "oss", "skill", "agentskills"]
published: false
---

All 8 PRs I submitted in February were merged. That alone isn't remarkable.

The target was a **57,302-star** OSS repo — one built to automatically deliver every contributor's skills to every user who installs it. By the time I noticed, distribution had already started.

Claude Code has an extension system called "skills." These are Markdown files that define Claude's behavior patterns — rules like "always search for existing libraries before writing code" or "write tests first." Writing your own and keeping them in a repository is essentially building a personal Claude configuration library.

## ECC — 57K Stars in 6 Weeks

ECC (Everything Claude Code) is an OSS project maintained at `affaan-m/everything-claude-code`. A curated collection of skills, commands, and agents for Claude Code, launched January 18, 2026. Built by an Anthropic Hackathon Winner.

What makes it useful? **Just 2 commands** to install, and dozens of community-reviewed skills land in your local cache at once. Copy the skills you need from the cache to `~/.claude/skills/` and you're running. No more hunting down individual repositories.

57,302 stars in 6 weeks. About 1,350 per day.

Why? It rode the adoption curve of Claude Code itself. Demand for "I want a bundle of ready-to-use skills" converged on a single destination, and ECC became the de facto entry point. Curation beats products in the early days of an ecosystem — a classic pattern.

For more on ECC and what it's like to use day-to-day, see my earlier write-ups:

- [10 Days of Real Development with Everything Claude Code (Japanese)](https://zenn.dev/shimo4228/articles/ecc-journey-part1)
- [15 Days of Skill Sprawl — Lessons from 3 Audits (Japanese)](https://zenn.dev/shimo4228/articles/ecc-journey-part3)

## 8 for 8: Behind a Perfect Merge Rate

When I checked whether my own skills had made it in, all 8 PRs submitted in February were merged.

| PR # | Type    | Name                                                                                  | Summary                                                                              |
| ---- | ------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| #219 | skill   | cost-aware-llm-pipeline                                                               | LLM API cost optimization: model routing by task complexity, budget tracking, retry  |
| #220 | skill   | swift-protocol-di-testing                                                             | Testable Swift code via Protocol-based dependency injection                          |
| #221 | skill   | swift-actor-persistence                                                               | Thread-safe data persistence layer using Actor                                       |
| #222 | skill   | content-hash-cache-pattern                                                            | Cache expensive file processing results with SHA-256 hashes                          |
| #223 | skill   | regex-vs-llm-structured-text                                                          | Decision framework: regex vs LLM for structured text parsing                         |
| #262 | skill   | search-first                                                                          | Search for existing tools and libraries before writing code                          |
| #263 | command | learn-eval                                                                            | Extract patterns from a session, evaluate quality, then save                         |
| #265 | skill   | [skill-stocktake](https://zenn.dev/shimo4228/articles/skill-stocktake-design-journey) | Audit skills using quantitative quality scores                                       |

8 for 8. The acceptance criteria are clearly documented, so I only swung at pitches I could hit. ECC has three rules: English only, no personal references, all required sections present. Required sections are Purpose, When to Use, Workflow, and Output. One PR per file keeps review overhead low. Merge time: a few days to a week.

## The Moment a PR Merges, Distribution Begins

This part was unexpected.

```bash
claude plugin marketplace add affaan-m/everything-claude-code
claude plugin install everything-claude-code@everything-claude-code
```

I verified this myself. `marketplace add` copies the entire repository locally, and `plugin install` activates the skills. That means **the moment a PR merges, every user who installs afterward gets your skills automatically**.

![Skill list after ECC installation — contributed skills including search-first and skill-stocktake appear in the directory](/images/ecc-skills-cache.png)

Keeping skills in your own repo means waiting for someone to stumble across them in search. Via ECC, the discovery cost drops to zero. The same skill reaches a completely different order of magnitude depending on where you put it.

If just 1% of stars translates to installs, that's roughly 570 people. My own repo was getting a handful of visitors per month — the gap isn't double or 10x, it's orders of magnitude.

:::message
Side note: "ecc-tools on GitHub Marketplace" is a completely separate GitHub Actions app for auto-generating skills (123 installs). Don't mix them up in search results.
:::

## The 6-Phase Process: From Personal to Universal

Once the submission workflow was solid, I systematized it as an `ecc-contribute` command (a custom command in `~/.claude/commands/` that I still use locally). The full flow is 6 phases, but the core work is the transformation and validation in the middle.

1. **Pre-flight** — Sync fork with upstream
2. **Selection** — `/skill-stocktake` score ≥ 20 (out of 100) and no similar skill already in ECC
3. **Transformation** — Frontmatter cleanup + translation + personal reference removal
4. **Validation** — Automated checks for non-ASCII remnants, personal references, required sections
5. **PR Creation** — `gh pr create` (one PR per file)
6. **Post-flight** — Progress logging, branch cleanup

Phase 3 was the most labor-intensive. Here's what it actually involves.

**Frontmatter**: Local skills contain management metadata like `origin: original`. ECC only needs `description`, so everything else gets stripped.

```yaml
# Before (local)
---
name: search-first
description: Research-before-coding workflow. ...
origin: original
---
# After (for ECC submission)
---
name: search-first
description: Research-before-coding workflow. ...
---
```

**Personal reference removal**: The tricky part. Project names and file paths get buried inside skills — things like `baki-trainer` or `/Users/hanma/`. Grep handles the mechanical catches, but context-dependent references like "used in the baki app" require manual generalization.

:::message
`baki-trainer` and `/Users/hanma/` are placeholder substitutions. Actual project names and paths vary per person.
:::

**Translation**: Skills written in Japanese get translated to English. Delegated to Claude — though terminology consistency (e.g., "棚卸し" → "stocktake" vs "audit" vs "inventory") required human judgment.

For Phase 4, `LC_ALL=C grep -rn '[^\x00-\x7F]'` checks for any remaining non-ASCII characters (works on macOS and Linux). One character left over means rejection. Adding this automated check brought errors to zero starting from the second submission.

## Skills as a Shared Resource

Behind that 57,302 number are engineers around the world using Claude Code — every one of them running into the same problems. How to write prompts, automating code review, enforcing TDD. If you've written a solution as a skill, there's no reason to keep it to yourself.

When my 8 skills were sitting in my own repo, a handful of people visited per month. Now that they're in ECC, those same skills are on the doorstep of 57,000 people. Knowing a path exists versus not knowing makes all the difference in whether you bother to try.

---

A Claude Code skill is too good to leave as something only its author uses. Contributing to ECC means one file, translated to English, required sections filled in. The problem you solved is probably frustrating someone else right now. Share your skills — and let's grow the Claude Code ecosystem together.
