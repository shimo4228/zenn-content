---
title: "I Made the Top Model My Session Default, and One Heavy Implementation Plus Its Review Burned Through Fable's Usage Limit"
emoji: "🧭"
type: "tech"
topics: ["claudecode", "aiagents", "agenticcoding", "anthropic"]
published: false
description: "I set the top model as my session default, started one heavy implementation, ran a review right after it, and Fable's usage limit was gone. Built-in skills and built-in subagents inherit the session model and accept no `model:` pin — 65% of my agent launches were built-ins. Here is where the default leaked, why a written convention and an advisory warning both failed to stop it, what a pre-execution block changed, and what dropped once the budget was gone."
tags: claudecode, aiagents, agenticcoding, anthropic
---

On August 22, 2026, I started a heavy implementation in a Fable session and ran a review right after it. Fable's usage limit was gone in an instant. That happened because the built-in skill that handles the review inherited the session's model and ran on it.

Three days later, in the morning, I was chasing a different problem and noticed something. The over-engineering that shows up in my own repositories was happening in the Opus sessions — the ones that picked up design work after Fable's usage limit ran out.

Those two are the first and second half of the same event. When you make the top model your session default, the first thing that breaks is not the work product but the usage limit, and once the limit is gone, judgment itself drops to a lower model. This article is a record of which paths the default leaked into, why a convention and a warning failed to stop it, what did stop it, and what fell once the limit was gone.

## Setup: three models across three tiers

I use Claude Code on a subscription plan (Max) and split three models by role. Fable, the top model, does judgment — checking premises, planning, acceptance. Below it, Opus does implementation, and I hand that work to a new session. Mechanical cross-checking goes to Sonnet. On my plan, Fable's usage limit is separate from Opus's, so Opus still works after Fable runs out. From here on I call the judgment side the judge tier and the implementation side the build tier (in my config files they are literally `judge-tier` and `build-tier`). My `settings.json` default model is `fable`, and I wrote up the division of labor for handing implementation off in [an earlier article](https://dev.to/shimo4228/i-handed-41-tasks-to-an-ai-loop-the-bottleneck-was-judgment-not-code-23dp).

Since the start of August, every subagent I wrote myself carries a `model:` line. Writing the model into the definition file to fix it is what I call pinning below. The 11 files in `~/.claude/agents/*.md` break down as fable 1 / opus 4 / sonnet 5 / haiku 1 as of September 16, the day I started writing this. A lint rejects any I forget.

I thought that was enough to have the tiers in place.

## The default leaks into paths you cannot pin

What leaked on the day the limit ran out were `/code-review` and `/simplify`. Both ship with Claude Code, take no model argument, and run on the session's model. Call them from a Fable session and they run on Fable. That is how the limit arrived in an instant.

There are other leak paths: the built-in subagents, which have no frontmatter. Counting my own log (`~/.claude/metrics/agent-usage.jsonl`), over the three weeks from installing the review hook described below to writing this article, 576 agent launches included 373 built-ins — general-purpose 231, Explore 121, Plan 10, claude-code-guide 11 — or 65%. Writing `model:` into my own agents does not reach two thirds of the launches. (claude-code-guide is fixed to Haiku, so the count that can inherit the session model is 362, or 63%.) The log does not record the model, so I cannot say how many of those ran on Fable. It was a hole I only noticed by counting, and I closed most of it while writing this article. What I closed it with is at the end.

Per the official documentation (as of September 16, 2026), a subagent's model is resolved in this order: the model named at call time, the `model:` in the definition, the `CLAUDE_CODE_SUBAGENT_MODEL` environment variable, then the session's model. Explore inherits the session model but caps at Opus; general-purpose and Plan inherit with no cap. So if the caller names no model and the environment variable is unset, every general-purpose a Fable session launches is Fable. Setting the variable changes general-purpose only; Explore and Plan do not move.

I fell into the same mechanism back in February. At the time, `--model opus` applied only to the main loop, and my subagents ran on Haiku, which I had not intended ([the article from back then](https://dev.to/shimo4228/i-tried-an-opus-orchestrator-and-killed-it-the-roi-of-multi-agent-systems-1f7g); the behavior has changed since). In February it leaked below what I intended, this time above it. Inheritance defaults leak in both directions.

The same report shows up in public issues. #76514, from July 10, says that omitting the per-agent `model` propagates Fable to every subagent; it was closed as not planned. #93894, from September 12, says that one run of `/code-review high` on Fable 5.1 exhausts the session budget and the review never finishes; it is still open.

## The convention did not stop it, and neither did the warning

My fix on the day the limit ran out was a convention. I added a step at the end of every implementation plan — decide in one line whether this session implements — and made heavy implementation go to a new Opus session. I rejected enforcing it with a hook, because that would bury the policy inside the hook.

Two days later, at night, I typed this (my own words, translated):

> ...I put in a convention where Fable handles design and opus does the implementation, but it isn't really being followed. Implementation is one thing, but when review runs straight afterwards — simplify and code-review especially — it wastes a serious amount of tokens....

So I added a hook. The first version was an advisory: warn when a review is launched in a Fable session. What I learned the next morning is that an advisory gets read *after* the review has already run. Seeing the warning, stopping, and re-running the review on Opus means paying twice — once for Fable, once for Opus.

That same morning I rewrote `review-model-notice.sh`. What I had rejected first was burying policy in a hook. What went into the hook this time is only a mechanical test — skill name crossed with session model — while the policy of which model does what stays on the rules side. The response is split by path.

```bash
# ~/.claude/hooks/review-model-notice.sh (excerpt, abridged)
# Split the response by path:
#   Direct skill call (code-review / simplify) -> **block**. The test is purely
#     mechanical (skill name x session model) with no room for a false positive,
#     and as an advisory the skill runs in the same turn and burns judge-tier
#     tokens before the advice is ever read (measured — stopping and re-running
#     the review on Opus meant paying twice). Only a block before execution works.
#   Agent/Task launch with a missing model pin -> stay at advisory. Partial
#     prompt matching is a heuristic and can produce false positives, so it does
#     not get deny authority.
```

The session's model is not in the hook payload. It reads the most recent `"model"` from the tail of the transcript, and stays silent if it cannot read one.

```bash
model=$(tail -c 2000000 "$T" 2>/dev/null | grep -o '"model" *: *"[^"]*"' | tail -n 1) || true
case "$model" in
  *fable*) ;;
  *) exit 0 ;;
esac
# ...(compose the block / advisory text)
if [[ "$mode" == "block" ]]; then
  jq -cn --arg reason "$msg" '{decision:"block", reason:$reason}'
  exit 0
fi
```

A model that reads the block reason switches itself over to `Agent(subagent_type: "general-purpose", model: "opus")`. No human has to stop it and retype the command.

## What broke was the budget, then the judgment

The same morning, in another conversation, I was talking about over-engineering. Just before that I had simplified my weekly-report machinery heavily, cutting thousands of lines of code. I typed this:

> A fair amount of the over-engineering happens on opus, after fable's usage limit is past

> The real problem is that this happens because Fable gets wasted on implementation and review, the usage limit runs past, and I'm forced to make Opus the orchestrator.

Making the top model your default breaks the budget first. But that budget was there to buy the judge tier's model. When it runs out, the judge tier drops to Opus, and the dropped judge tier waves over-engineering through. Putting the top model in the "default" slot works to push it out of the "judge tier" slot. Up to here this is an impression from a handful of cases; I have not counted how many times Opus's judgment let over-engineering through.

So I reversed the direction in which I plug the leaks. The session default stays at the top model; the paths from the default to the judge tier stay open, and the paths that leak from the default to anything else get cut. The judge tier gets pinned. The `architect` agent, which decides whether a thing should be built at all, has been the only `model: fable` in my environment from that day through September 16.

## It still ran out every weekend

Three days later, on Friday, I typed this:

> Fable's usage limit always runs out on Saturdays, Sundays and holidays, which is when I use it most. After it's gone Opus does the design, and I really do feel Fable's absence. I want it focused on design and planning, where Fable is strong, and everything else delegated to other models. Even now it's supposed to delegate to Opus when it can, but a lot of the time Fable just goes ahead and implements.

I had plugged the review path, but implementation itself was running on Fable. My first convention had an escape hatch — if the conditions are not met, this session may implement — and the model itself was making that call.

I changed three things the same day.

1. **Inverting the default.** The default for "does this session implement" became "hand it to Opus." I may implement in place only when I write one line in the plan naming one of three things: prose edits to design documents (decision records such as ADRs), a concrete reason the work cannot be handed off, or an explicit instruction from the user. Accountability moved from the side that hands off to the side that does not
2. **A hook right after plan approval.** A PostToolUse on `ExitPlanMode` reminds Fable sessions, and only Fable sessions, to decide the executor. It fires before the first implementation Edit, the latest safe position available
3. **One line in the resident rules.** So that it reaches implementation that never passes through plan mode, I wrote into my rules: "implementation in a judge-tier session defaults to dispatch to the build tier." One line saying a judge-tier session does not implement; it hands the work to a build-tier session

The hook in (2) has a condition for staying quiet: if the plan body already contains the set phrase "executor decision," it says nothing. At first I also had general words like `dispatch` and `spawn-session` in the suppression list. Running that against 271 past `ExitPlanMode` calls suppressed 31, and 30 of the 31 were false suppressions. A plan that merely mentions handing implementation off — that is, a session doing nothing but routing tasks, exactly where I most want the hook to fire — would go quiet. I narrowed the suppression list to the single set phrase and put "a plan that only mentions dispatch still fires" into the regression tests. Putting only mechanically decidable conditions into the machinery is the same call I made with the review hook.

In the three weeks since, there is no report in my session logs of the usage limit running out. That is the absence of a report, not a record of measured headroom. I still have nothing in my environment that mechanically records how much of the usage limit is left. I also have not looked at whether reviews that ran on Fable were catching anything Opus misses. What I can say goes as far as this: I have not had to write that same report again.

## Four decision rules

If you run a similar setup, these four are what you can take away.

**Don't leave the tiers to the default; pin the judge tier and plug the paths that leak.** My session default is still `fable`. What I changed is not the default but the paths the default flows into. It leaks into built-in skills, built-in subagents, and the session's own implementation, and a `model:` in my own agent definitions reaches none of those three.

**Fill in the built-in subagent defaults with the environment variable and same-named definitions.** Setting `CLAUDE_CODE_SUBAGENT_MODEL=opus` changes the default for general-purpose. Explore and Plan do not move on that variable alone: either fix everything to one model with `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`, or place a same-named agent definition carrying a `model:`. While writing this article I set the environment variable to `opus` and gave Explore a same-named definition on `sonnet`. Of the 362 launches above, what remains is Plan's 10.

**Block when the test is mechanical, advise when it is a heuristic.** Skill name crossed with session model produces no false positives, so it gets stopped before execution. Anything you can only test by partial prompt matching stays a warning. Advice that arrives after execution does not protect a budget.

**Invert the default of a convention.** Most "conventions nobody follows" put no accountability on the side that does not follow them. Put the default on the handing-off side, and you have to write down your reason for not handing off.

I wrote expiry conditions for this wiring. It comes out if model tier distinctions and usage limits disappear, or if Claude Code starts switching models per session on its own. `opusplan` (plan on opus, execution on sonnet) already exists, so once a version that drops from fable to opus arrives, the hook is unnecessary.

## Sources

- [Create custom subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents) — the model resolution order, Explore's cap, `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` (retrieved 2026-09-16)
- [Model configuration - Claude Code Docs](https://code.claude.com/docs/en/model-config) — `opusplan`, `CLAUDE_CODE_SUBAGENT_MODEL` (retrieved 2026-09-16)
- [anthropics/claude-code #76514](https://github.com/anthropics/claude-code/issues/76514) — subagents in a Fable session all inherit Fable (2026-07-10, closed as not planned)
- [anthropics/claude-code #93894](https://github.com/anthropics/claude-code/issues/93894) — one `/code-review high` on Fable 5.1 exhausts the session budget (2026-09-12, open)

## Related links

- [I Handed 41 Tasks to an AI Loop. The Bottleneck Was Judgment, Not Code](https://dev.to/shimo4228/i-handed-41-tasks-to-an-ai-loop-the-bottleneck-was-judgment-not-code-23dp) — how the split of judgment to Fable and implementation to Opus came about
- [I Tried an Opus Orchestrator and Killed It: The ROI of Multi-Agent Systems](https://dev.to/shimo4228/i-tried-an-opus-orchestrator-and-killed-it-the-roi-of-multi-agent-systems-1f7g) — the February record of falling through the same inheritance default, in the downward direction
- [I Cut My AI Review Chain From 6 Stages to 1: Breaking the Loop That Never Hits Zero Findings](https://dev.to/shimo4228/i-cut-my-ai-review-chain-from-6-stages-to-1-breaking-the-loop-that-never-hits-zero-findings-1moi) — cutting the number of review stages, on the same morning I noticed the advisory hook's double payment
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles-en/top-model-as-default-leaks.md) — the Markdown for every article, plus the index (docs/PUBLICATIONS.md), lives in the same repository
- [My GitHub](https://github.com/shimo4228) — my research repositories, with DOIs
- [claude-harness](https://github.com/shimo4228/claude-harness) — the public mirror of this article's hook, `hooks/review-model-notice.sh`, and its tests
