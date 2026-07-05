---
title: "I Built a Skill for Easy Codex Reviews from Claude Code"
emoji: "🔀"
type: "tech"
topics: ["claudecode", "codex", "codereview", "skills", "harness"]
published: true
description: "A thin read-only wrapper around the OpenAI Codex CLI, built as a Claude Code skill for cross-model review. Why it works isn't 'more review' but 'a different class of blind spot' — with a real example from the Contemplative Agent repository."
tags: codereview, codex, claudecode, skills
---

> What this article covers: how to add exactly one cross-model review step to Claude Code using the OpenAI Codex CLI, and why it works — not because of "more" review, but because it catches "a different class of blind spot."

## Prerequisites

- [Codex CLI](https://github.com/openai/codex) installed and authenticated (verify with `codex login` or `codex doctor`)
- Working inside a `git` repository from Claude Code

## Usage — a read-only second opinion in one command

`codex-review` is a read-only skill that thinly wraps `codex review` (the OpenAI Codex CLI). It shows the current diff to a model from a different lineage than Claude Code and has it review the work.

`/codex-review` isn't a command that ships with Zenn or Claude Code out of the box — it's a small wrapper script I placed in my own Claude Code harness.

The skill itself is published as [shimo4228/codex-review](https://github.com/shimo4228/codex-review), so you can reproduce the same setup by copying `skills/codex-review/` from that repository into `~/.claude/skills/codex-review/`.

All it does is a single shell script that passes only the allow-listed flags straight through to `codex review` and rejects everything else.

The script itself isn't Claude Code-specific. If you look inside, the string "Claude" only appears in comments — the actual execution logic is just `bash` + `git` + the `codex` CLI.

You can run it straight from a terminal, call it from a different agent CLI, or use it as a plain pre-commit hook with no Claude Code in the loop, and it works the same way. Being "a Claude Code skill" is just a matter of where you put it and how you invoke it.

```bash
# current branch vs. auto-detected base branch (PR style)
/codex-review

# staged + unstaged + untracked files (for a pre-commit check)
/codex-review --uncommitted

# against a specific branch or commit
/codex-review --base main
/codex-review --commit <sha>

# prompt-driven (review the whole working tree with no scope flag)
/codex-review "just look at the auth-related changes"
```

Read-only is enforced at the code level. Internally it only ever calls `codex review` (which never rewrites code), and any flag not on the allow list is rejected outright. Even if the Codex CLI adds a write-capable flag in the future, it won't run unless it's added to the allow list.

I don't paste Codex's output straight into the parent conversation — I verify it first, then summarize.

```text
Agent: codex-review
Verdict: <CRITICAL | HIGH | MEDIUM | LOW | CLEAN>
Findings (top 3): <only what's been confirmed>
Files touched: <path:line>
Next action: <continue | stop | re-plan>
```

I treat Codex's findings as "external input that isn't necessarily correct," and keep only the ones I can confirm by reading the code and reproducing the issue. Deciding the verdict is still on me (the Claude side).

## Wiring it into the harness as an "automatically-run check"

Calling `/codex-review` manually every time is already useful, but it really pays off once it becomes something you can't forget to call. Write the condition into your project rules (`CLAUDE.md` or `.claude/rules/*.md`) and, once implementation reaches a natural checkpoint, Claude will follow it on its own — without you asking.

That said, this isn't deterministic enforcement like a hook. A rule only conditions Claude's judgment; whether it actually runs is still up to Claude in the end (if you want a 100% guarantee, you need to enforce it with a PostToolUse hook).

Even so, just writing "once you've made a non-trivial diff" into the rule as an explicit condition changes the pattern from "ask each time" to "it runs on its own once the condition is met." The full rule I actually use (with its Chain Matrix and early-stop conditions) is published in [claude-harness's `planning.md`](https://github.com/shimo4228/claude-harness/blob/main/rules/common/planning.md).

```markdown
<!-- Example: write this into CLAUDE.md or .claude/rules/*.md -->
## Review step (right after implementation, before commit)

When a feat/fix produces a non-trivial diff, run the following in parallel before committing:
- a normal code review (a subagent on your own model)
- codex-review (cross-model, read-only)

If either one returns CRITICAL, stop the commit and report to the user.
```

Two things matter here:

1. **Make the trigger "a non-trivial diff was written," not "the user asked for it."** This structurally prevents forgetting to call it.
2. **Stop early on a CRITICAL finding.** If a different model flags something serious, the rule itself gates on stopping the commit right there and deferring to human judgment.

Set up this way, findings aren't "something I happened to notice" — they get caught in the same place every time. This article itself ended up being a live demonstration of that.

`codex-review` doesn't just review code diffs — in prompt-driven mode it can review prose too. This repository's pre-publish checklist says "articles get reviewed in parallel by editor / fact-checker / codex-review," and this article went through codex-review without me explicitly asking for it either.

And it actually caught something. The paragraph right before this one had originally overclaimed that "writing it into a rule makes it run automatically" — that's the finding, and the current wording already reflects the fix.

Not just blind spots in code — a different model diligently catches overclaiming in prose too.

## What it actually found — a different model sees a different blind spot

It's tempting to describe the value of codex-review as "it's good at finding bugs Claude alone would miss," but framed as a frequency claim, that's hard to verify. Here's what actually happened, described plainly.

This is from a review on [Contemplative Agent](https://github.com/shimo4228/contemplative-agent), another research repository of mine, when I added a single monitoring instrument module ([ADR-0071](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0071-read-only-pattern-composition-instruments.md), [the commit in question](https://github.com/shimo4228/contemplative-agent/commit/224fdd97b740df7bf1b2a18bc77f6e8cc4980ec0)). This instrument is observation-only by design: it never touches pipeline behavior and only reads and displays the distribution and aggregates of embedding vectors. I ran `codex-review` (a different model lineage) and Claude's own regular review (`python-reviewer`) in parallel against the same diff.

| Reviewer | What it found | Kind |
|---|---|---|
| codex-review | A crash path in the aggregation logic when embedding vector dimensions are inconsistent | Numeric / data-shape mismatch |
| codex-review | A filter condition in the aggregation was off by one step from the processing it was supposed to observe | Semantic drift in aggregation logic |
| codex-review | The dry-run aggregation was counting candidates that should have been dropped by downstream deduplication | Semantic drift in aggregation (scope) |
| python-reviewer | An unexpected input (e.g., a non-numeric embedding) propagates an exception that stops the host pipeline it was only supposed to be observing | Exception-handling / robustness contract |

The 3:1 split is just the result of this one run — the point isn't the count, it's the difference in the level of abstraction of the findings (more on that right after the table).

I confirmed all four by reading the code and reproducing the issue, then fixed them and added regression tests (the primary record is in the [commit message](https://github.com/shimo4228/contemplative-agent/commit/224fdd97b740df7bf1b2a18bc77f6e8cc4980ec0)). All tests stayed green the whole time these four bugs existed. In other words, "it runs" and "it's correct" are separate axes of checking, and review was covering the axis tests weren't.

What's interesting is finding #1 (codex-review: crash on dimension mismatch) and finding #4 (python-reviewer: host pipeline halted by exception propagation). On the surface, both look like the same "broken embedding row" problem.

They aren't, though — the findings sit at different levels of abstraction.

- **codex-review** — a specific failure mode: the aggregation function crashes when dimensions don't match
- **python-reviewer** — a broader contract that failure mode sits inside: the design principle that "an observation-only instrument must never halt the host pipeline, no matter what abnormal input arrives" was missing entirely

Around the same underlying phenomenon — a "broken row" — the two reviewers pointed at different levels of abstraction, different variants of the same problem. That's what happened here.

I can't claim that running the same model lineage twice would only ever surface one or the other. What I can say is that, in this one run at least, there was no overlap.

## Pitfalls / Tips

:::details If you hit one of these

- **Scope flags and a free-form prompt are mutually exclusive.** Passing `--uncommitted` (or similar) together with a free-form prompt gets rejected with exit code 64.
- **If you run with no scope argument and HEAD is already on the base branch** (e.g., running with no flags while on `main`), the diff comes out empty, so it automatically falls back to `--uncommitted`. This auto-fallback does not kick in if you specify a scope explicitly, e.g. `--base main`.
- **If the CLI isn't installed**, the wrapper itself checks upfront and fails early. **If it's not authenticated**, that's outside the wrapper's scope — `codex review` itself returns the error (check with `codex login` / `codex doctor`). Either way, just continue with Claude's own review alone.
:::

## Summary

`codex-review` itself is a thin wrapper, but what makes it work is the combination of two things: the design choice to mix in exactly one other model, and the operational choice to write "a non-trivial diff makes you a review target" explicitly into a rule. Add a few lines to your own project rules and you can reproduce the same setup starting today.

## Related links

- [The codex-review skill itself](https://github.com/shimo4228/codex-review) — install it by copying `skills/codex-review/` to `~/.claude/skills/codex-review/`
- [claude-harness's `planning.md`](https://github.com/shimo4228/claude-harness/blob/main/rules/common/planning.md) — the full review step, Chain Matrix, and early-stop conditions
- [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) / [ADR-0071](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0071-read-only-pattern-composition-instruments.md) / [the commit in question](https://github.com/shimo4228/contemplative-agent/commit/224fdd97b740df7bf1b2a18bc77f6e8cc4980ec0) — the real example used here
- [Codex CLI (upstream)](https://github.com/openai/codex)
- [shimo4228 on GitHub](https://github.com/shimo4228) — list of other public repositories
