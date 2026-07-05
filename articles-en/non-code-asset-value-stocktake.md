---
title: "Linters Can't Measure a Non-Code Asset's Value — I Built an LLM Stocktake for It"
emoji: "🧹"
type: "tech"
topics: ["claudecode", "ai", "devtools", "githubactions"]
published: false
description: "Auditing the dead configs, stale workflows, and unread runbooks that pile up in a repo, with a two-tier method: grep for structure, an LLM for value — packaged as a Claude Code skill, but the pattern runs by hand too."
tags: claudecode, ai, devtools, githubactions
---

> **What this article covers**: how to take stock of the "abandoned configs, dead workflows, and runbooks no one reads" that accumulate in a repository, using a two-tier method — **grep for structure, an LLM for value**. You can drop it in as a Claude Code skill, or run the same pattern by hand without the skill.

## Prerequisites

- **If you use it as a skill**: git, plus write access to `~/.claude/skills/` (a Claude Code environment)
- **If you run it by hand**: a shell with `grep`, and any LLM (the thing you hand the judgment to)
- The target is "files that aren't code" in general (configs, CI, docs, runbooks, etc.). Detecting dead code in the code itself is out of scope.

## Develop with an AI agent, and non-code stuff piles up

When you develop alongside an AI agent, files that aren't code quietly accumulate.

- `PLAN_xxx.md`, `HANDOFF_xxx.md`, `PROGRESS_xxx.md` — working notes written once and never read again
- Linter or formatter config files that got added temporarily and never removed
- GitHub Actions workflows that do effectively nothing — either their `on:` conditions are never satisfied so they never fire, or they do fire but every job is skipped by `if: false`
- Runbooks that are still around long after the process they describe has ended

These aren't "broken." The YAML is valid, the Markdown is well-formed. So the linter says nothing. **A linter only looks at "is this structurally correct"** — it can't measure "does this file still deserve to exist."

That was exactly my problem. I started looking for "a skill that detects runbooks nobody references anymore, or workflows that stopped functioning," and what I ended up building was a skill called `repo-asset-stocktake`. This article walks through the core of its design (the parts anyone can reuse), and the story of actually running it against a different repository and finding an "island of orphaned documents."

## The core: structure by grep, value by LLM

The decisive realization before building was this: **the properties I wanted to check split into two kinds.**

| Property | Example | What decides it |
|---|---|---|
| **Structural** (determined by the shape of the bytes) | Is the YAML valid? / Is the link target alive? | **Code** (grep / parse). 100% accurate, instant |
| **Semantic** (requires understanding intent) | Is this config still used? / Does this runbook still describe a process that actually exists? | **LLM** (judgment) |

A `.textlintrc` that nobody runs anymore contradicts no code (structurally, it's healthy). But its value is zero. grep can't bridge that gap.

At the same time, throwing an LLM at every file up front is a waste of money. So I split it: **enumeration is code, judgment is the LLM.**

```
Enumerate all non-code assets
        │
        ▼
tier-1 · structural: measure reachability with grep
        │
        ├─ consumer still alive ──▶ Keep (as-is)
        │
        └─ consumer gone (candidate)
                   │
                   ▼
        tier-2 · semantic: LLM judges value
                   │
                   ▼
        Keep / Update / Retire / Merge
                   │
                   ▼
        Confirm one by one, retire reversibly
```

- **tier-1 (code)**: measure "reachability" (explained below) with grep, and narrow down to only the suspicious candidates
- **tier-2 (LLM)**: judge only the narrowed candidates by "does this still mean anything," and emit a verdict of `Keep` / `Update` / `Retire` / `Merge`. No numeric scores.

### What "reachability" means

Reachability is "whether something that consumes this asset is still alive." **Every non-code asset is alive because something consumes it.**

| Consumer class | Example asset | Reachability check (what grep does) |
|---|---|---|
| Tool invocation | Tool configs like `.textlintrc` | Search for the tool name in `package.json` scripts, pre-commit, Makefile, CI. Zero invocation sites = candidate |
| CI trigger | `.github/workflows/*.yml` | Parse whether the scripts/actions it references actually exist, and whether the `on:` trigger is reachable |
| Human navigation | runbook / docs | Search for inbound links from other docs or the README. Zero inbound links = candidate |

For example, you can measure "tool invocation" reachability like this:

```bash
# Check whether .textlintrc is still "invoked" (not merely installed)
grep -rn "textlint" .github/workflows/ .pre-commit-config.yaml Makefile 2>/dev/null
# For package.json, look only inside scripts (a name in devDependencies is not "invocation")
jq -r '.scripts // {} | values[]' package.json 2>/dev/null | grep textlint
# → If neither prints anything, "zero invocation sites" = a candidate to pass to tier-2
```

This table and these commands are what I most want you to take away from this article. If you mechanically measure, per consumer class, "whether the consumption link (the wiring to whatever calls the asset) is still intact," you can narrow the candidates a lot before ever handing anything to an LLM.

### Why I built it myself (the conclusion after looking for something off the shelf)

:::details The result of checking "surely a tool for this already exists" — twice
At first I assumed "something off the shelf must exist" and went looking. The conclusion splits by layer.

- **For structural checks, off-the-shelf options are plentiful.** MegaLinter and super-linter bundle yamllint, actionlint, markdownlint, and so on. YAML validity has yamllint; dead links have dedicated tools like markdown-link-check or Lychee (both callable from MegaLinter) — note that markdownlint itself does *not* check for dead links, so you need one of those separately. There's no reason to build any of this yourself.
- **For semantic "value" review, off-the-shelf options are thin.** The closest is the commercial service Dosu, but from what's public, drift detection between docs and code is one of its several features (Dosu itself pitches issue triage and an agent-facing knowledge base more broadly), and in any case it isn't a mechanism for judging "does this config or workflow still hold value."

And the mechanism itself — "an LLM reviews an asset by value and emits Keep/Retire" — was already implemented four times inside my own Claude Code environment (stocktake skills targeting configs, rules, skills, and project docs respectively; I wrote up the design process for the skill-targeting version in a [separate article](https://dev.to/shimo4228/offloading-ais-weak-spots-to-shell-scripts-designing-building-and-publishing-a-skill-audit-2ll8)). **What was missing wasn't the mechanism — it was the target.** The one aimed at "a project repository's non-code assets" was the only one that didn't exist. So instead of inventing from scratch, I copied the skeleton of an existing stocktake skill and swapped only the target.
:::

Leave the structural checks to off-the-shelf linters, and **build only the thin "value judgment" layer that's missing** — that was the conclusion.

## Installing it: as a Claude Code skill

The skill is published as a standalone repository. Drop it in `~/.claude/skills/` and you can call it with `/repo-asset-stocktake`.

```bash
git clone https://github.com/shimo4228/repo-asset-stocktake \
  ~/.claude/skills/repo-asset-stocktake
```

To run it, you just pass the path of the repository you want to audit.

```text
/repo-asset-stocktake                  # audit the current directory
/repo-asset-stocktake ~/path/to/repo   # audit a different repository
```

The verdicts are recorded as a ledger in `.repo-asset-stocktake.json` inside the audited repo, so on subsequent runs you can re-evaluate only the assets that changed. It looks like this:

```json
{
  "evaluated_at": "2026-07-05T05:20:00Z",
  "assets": [
    {
      "path": "docs/plans/NEXT_STEPS_fsrs-migration.md",
      "consumer": "human-navigation",
      "reachability": "0 inbound links / not listed in INDEX",
      "verdict": "Retire",
      "reason": "The feature already shipped, so this 'remaining work' note is now hollow"
    }
  ]
}
```

Add this ledger file to `.gitignore` and even a public repo won't leak its audit results.

## Running it for real turned up "an island of 33 orphaned files"

After building it, I ran it against another of my own repositories (an iOS app). It has almost no CI workflows or tool configs; it's mostly Markdown docs. "So it won't find anything," I figured. The opposite happened.

What came out wasn't individual junk files — it was a **structure.**

```
CLAUDE.md (project entry point)
  ├──▶ RUNBOOK.md
  ├──▶ CONTRIB.md
  └╌╌╌ (no link) ╌╌╌▶ PROJECT_TIMELINE.md   ← the missing bridge
                          │
                          ▼
                     plans/INDEX.md
                          │
                          ▼
                     plans / reports (31 files)  ← the isolated island
```

Snapshots of `PLAN` / `PROGRESS` / `HANDOFF` / `BUG` / `REVIEW`, born during a two-week development burst five months earlier, had piled up in `docs/plans/` and `docs/reports/` — **31 files.** The only path to them was a single chain: `PROJECT_TIMELINE.md` → `INDEX.md`. But `PROJECT_TIMELINE.md` itself wasn't linked from `CLAUDE.md` (the project's entry point). Add those two entry-point files, and you get **33 files unreachable from the entry point.**

The division of labor between tier-1's grep and tier-2's LLM paid off exactly here.

- **tier-1 (grep)**: list the structural facts — "`PROJECT_TIMELINE.md` has 0 inbound links," "`INDEX.md` links to the plan set." That the bridge is isolated falls straight out of grep.
- **tier-2 (LLM)**: interpret those facts as "the only bridge to the whole island is severed — reconnect one entry point and 33 files come back to life," and choose reconnection over deletion.

Detection is structural (tier-1); the meaning is the LLM (tier-2). The reason I split enumeration from judgment worked exactly as intended on this island.

The fix wasn't deletion — it was **reconnecting one entry point.** Adding a single line in `CLAUDE.md` linking to `PROJECT_TIMELINE.md` rescues the history of all 33 files at once. That's a conclusion a lint could never produce, and one that only a value review could.

### The moment tier-2 delivered more value than "delete"

The most effective thing this skill did wasn't deletion — it was **vetoing a deletion.**

tier-1 found two files both named `dead-code-analysis.md` and flagged them as a "duplicate" candidate. With naive basename dedup, this is where one of them would have been deleted.

But when tier-2 compared their contents, one was an analysis by Python's vulture and the other was a manual Swift analysis — **different things.** Merging them would lose one of the analyses. The verdict was "cancel the Merge." The semantic layer verifies and overturns the structural signal. That's exactly the point of splitting it into two tiers.

In the same vein, over on the `zenn-content` side it caught an asset of a different class: `.gitignore` declared that `archive/` should "not be published," yet four files committed before that rule was added were still tracked and continued to be published on GitHub — a gap between the intent of a config and reality. The same skill spans assets of different consumer classes: tool configs, workflows, docs, and VCS settings.

## You can run this pattern without the skill

Even without a Claude Code custom skill, the core is reusable. With your own agent (or by hand), just do the following in order:

1. **Enumerate (code)**: list every non-code asset, and measure reachability per consumer class with grep (the table and commands under "What 'reachability' means" above)
2. **Narrow**: take the ones with zero reachability (0 invocation sites / all references dead / 0 inbound links), *plus* the ones that "are reachable but look suspicious" (stale updates, throwaway docs like `PLAN` / `HANDOFF`, notes describing "remaining work" for an already-shipped feature, etc.) — the island in the previous section still had inbound links, yet it was hollow
3. **Judge (LLM)**: judge only the candidates by "does this still mean anything," and emit Keep / Update / Retire / Merge
4. **Delete reversibly**: don't delete a Retire immediately — first move it somewhere recoverable, like renaming to `.disabled` (soft-delete), and confirm one by one

:::message
The biggest pitfall is that **"zero reachability" does not equal "dead."**

When I built this skill, I ran a review by a different model (Codex) in parallel, and it caught a blind spot my own review (Claude) had missed: **when consumption is one step indirect, grep comes up empty.**

- prettier invoked via `lint-staged` has no direct invocation site
- a remote `uses: owner/repo@ref` action is alive even with no local copy present
- a doc listed in the nav of `mkdocs.yml` is reachable even with no Markdown inbound links
- `.claude/skills/*.md` has 0 inbound links, but its consumer isn't a human — it's the Claude Code loader

Treat zero reachability not as a "deletion candidate" but as **"needs investigation."** Mistake the consumer, and you'll kill a live asset. In fact, without this correction I'd have wrongly Retired 9 of the iOS repo's `.claude/skills/*.md` files.
:::

## Summary

- Leave the **structure** of non-code assets (validity, dead links) to off-the-shelf linters. Don't build it yourself.
- Layer a thin LLM only over **value** (does this still deserve to exist). Don't run it on everything — narrow the candidates with grep first.
- Measuring reachability per consumer class (tool invocation / CI trigger / human navigation) is the mechanical axis for that narrowing.
- Zero reachability is "needs investigation," not "delete." Miss an indirect consumer and you'll kill a live asset.
- Always delete reversibly (move to `.disabled` → confirm one by one).

A lint can only answer "is this file correct." "Is this file still needed" is a different question — one that requires understanding meaning. Hand only that part to an LLM, and assets that had slipped through the linter's net start to become visible.

## Related links

- The skill itself: [shimo4228/repo-asset-stocktake](https://github.com/shimo4228/repo-asset-stocktake)
- Design process of a sister skill: [Offloading AI's Weak Spots to Shell Scripts — Designing, Building, and Publishing a Skill Audit](https://dev.to/shimo4228/offloading-ais-weak-spots-to-shell-scripts-designing-building-and-publishing-a-skill-audit-2ll8)
- The author's skills and research repositories: [github.com/shimo4228](https://github.com/shimo4228)
