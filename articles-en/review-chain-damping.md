---
title: "I Cut My AI Review Chain From 6 Stages to 1: Breaking the Loop That Never Hits Zero Findings"
emoji: "📉"
type: "tech"
topics: ["claudecode", "aiagents", "codereview", "agenticcoding"]
published: false
description: "My pre-commit AI review chain grew to 6 standing stages — around 10 agents per change — in 10 days. When I counted, the chain had produced exactly one proven discovery, and the review-fix-review loop never reached zero findings. The problem was structural: the loop had no damping term. Here is what I measured, what I cut, and the rollback conditions I attached."
tags: claudecode, aiagents, codereview, agenticcoding
---

On the night of August 24, 2026, I typed this to an AI:

> Isn't this a huge waste of tokens?

The target was an AI review setup I had built myself. Before every commit it ran multiple reviews in sequence, fixed the findings, then ran review again on the fixed diff. In this article I call that whole arrangement the "review chain."

Every time a repair finished, the next review came back with new findings. There was no sign the back-and-forth would ever end.

Let me state the conclusion up front. The loop never ended not because of the content or accuracy of the findings, but because of its structure. An LLM reviewer, when asked, will usually return something even against sound work. My operation never once reached the termination condition "stop when findings hit zero."

So what I cut was not the quality of the findings but the number of review stages. Six standing stages — in my case, a setup where a single change could spin up around 10 agents when everything fired — became one standing stage plus one conditional. This article traces the path by which the chain grew to six stages, and the measurements behind the decision to shrink it.

## The chain grew to 6 stages in 10 days

In my personal Claude Code environment, I manage the pre-commit review procedure as a table: for each kind of change, which reviews run. One row is one stage.

As of August 22, the standing reviews were six:

- Code simplification (Simplify)
- Code review (correctness)
- Security review
- Silent-failure detection
- Cross-check by a different model (OpenAI Codex)
- Consistency review against design records

And one stage does not mean one agent. Both Simplify and the code review internally spin up multiple perspective agents in parallel.

In my environment, Simplify alone launched four agents. With all six stages firing, roughly 10 agents were reviewing a single change.

This setup was not built in one night. Counting through git history, the buildup concentrated in the 10 days from August 13 to 22.

```text
8/13  Orthogonalized the review axes into "bug detection" and "quality"
8/15  Added a hook to enforce Simplify's execution order
8/16  Swapped the code review for the built-in /code-review; pinned effort (review depth) to high for features and refactors
8/22  Added the silent-failure review
8/22  Added a plan-stage cross-model refutation step (an extension to the design stage, separate from the six pre-commit stages)
```

Every single move was a serious improvement at the time. The review axes overlapped, so orthogonalize them. The order was not being followed, so enforce it with a hook. A missed class of defects turned up, so add a dedicated axis.

The problem was that nobody was counting the sum.

### Strengthening one row distorts the density of the whole

The swap on August 16 mattered most. I replaced one homegrown review agent with Claude Code's built-in `/code-review`.

The built-in version is a multi-angle review that dynamically spins up several perspectives and investigates them in parallel. So while the swap looked like a one-row replacement on the table, in practice it multiplied that row's bandwidth several times over.

And I did not trim the surrounding five stages. I was aware I had strengthened one row. I was not aware, at that point, that the chain's total density had reached several times the official recommendation.

Review bloat does not only advance by adding stages. It also advances when the contents of an existing row get stronger. The latter leaves the table's row count unchanged, which makes it hard to notice.

## When I counted: how many reviews actually changed an outcome?

From the night of August 24 — "isn't this a huge waste of tokens?" — I recounted what this chain had delivered.

First, the proven discoveries: one. On July 31, the code review of the time found a CRITICAL command-injection-class flaw in the git-target extraction shared by seven hooks. I confirmed with a PoC that it was actually reachable before fixing it — a record of a reachable flaw being discovered, not of damage occurring.

Hooks that run unattended are a trust boundary receiving repository-controlled data. This one finding was a reasoning-based discovery that no mechanical check would produce, and it became the reason I did not abolish review entirely.

Meanwhile, the dedicated security review itself produced no proven discovery of the same caliber.

Next, I counted the recent operations. Under the rules of the time, findings outside the change's diff were filed to the task ledger if HIGH or above. Here is what happened to the six out-of-diff HIGH findings that came in under that rule:

- 4 were filed as tasks and handled immediately
- The remaining 2 were never filed and were actually handled about a day late — the outcome did not change (this part is measured)
- Tracing back, only 1 of the filed findings could be judged as "picking it up on the spot contributed to the outcome": a blind spot where the verification script did not see untracked files — in other words, a defect that breaks the review loop itself
- The other 3 filed findings I judged as "delaying them would not have changed the outcome." Note that these 3 are a retroactive counterfactual judgment — "what if we had delayed" — not a measured delay

Even so, against the cost of a setup where up to six review stages could run on every change, this count was the return.

## The loop had no damping term

What the recount exposed was not a problem with the quality of individual findings but a problem with the shape of the loop.

The review → repair → re-review cycle has no term that shrinks the amplitude over time — what control engineering calls a damping term. Worse, every cycle supplies new findings.

A system without damping keeps swinging until you throttle the input from outside. In this article I call that state oscillation.

An LLM reviewer asked to find gaps will usually return something, even against healthy code. That is its job. Claude Code's official best practices name this phenomenon outright:

> A reviewer prompted to find gaps will usually report some, even when the work is sound, because that is what it was asked to do. Chasing every finding leads to over-engineering: extra abstraction layers, defensive code, and tests for cases that can't happen. Tell the reviewer to flag only gaps that affect correctness or the stated requirements, and treat the rest as optional.

The implicit termination condition — "iterate until zero findings and you are safe" — is one this loop effectively never reaches. At least in my environment, it never did. A loop that cannot reach its termination condition has to be cut from outside.

The same structure had already surfaced in another of my projects. In Contemplative Agent, where I had AI agents doing unattended weekly pipeline repairs, 8 of the 11 findings across the most recent three weeks were about the pipeline itself, not about the agent being repaired.

The measurement readout script grew from 327 lines to 998. One week's instrument repair produced the next week's findings — a self-feeding loop. That weekly chain was collapsed from seven sessions to one on August 24.

## What I cut

On August 27, I contracted the standing reviews. The change has three parts:

| Item | Before | After |
|---|---|---|
| Standing review stages | 6 | 1 + 1 conditional |
| Code review effort | pinned high (features, refactors) | explicit medium for all change types |
| Filing out-of-diff findings | HIGH and above | only defects that break the loop itself |

The four stages removed from standing duty: Simplify, silent-failure, the cross-model check, and design-record consistency. The quality axis Simplify covered is built into `/code-review`, and the cross-model check moved to opt-in on explicit request only.

The one standing stage that remains is the built-in `/code-review` running in fresh context. A separate subagent that does not inherit the implementation context inspects the diff alone for correctness.

The security review moved out of standing duty into a conditional stage that fires only when the diff touches a trust boundary. The July 31 finding was a trust-boundary discovery — that is the rationale for keeping it in this form.

For effort, I dropped the high pin and specify medium explicitly for all change types. In `/code-review`'s effort definitions, levels up to medium restrict reports to high-confidence findings; high and above cast a wider net that includes uncertain ones.

That wide net was the flip side of the over-engineering supply. Note also that with no level specified, `/code-review` reuses "the level you typed last," so I specify it every time — partly to keep the behavior independent of session state.

I narrowed out-of-diff filing too. Of the six HIGH findings, immediacy contributed to the outcome for exactly one — the defect that broke the loop itself.

So what about the review → repair → re-review cycle? I did not ban it.

In fact, on the day of the contraction I briefly introduced a "one round-trip rule" that forbade re-review after repairs. But re-reading the relevant official section, the motion of fixing findings and re-reviewing is described as a natural one — a benefit of the subagent architecture.

If the main cause of the oscillation is the stage count, there is no reason to constrain the round-trips after shrinking to one stage. I removed the round-trip ban the same day and kept only one rule: keep each repair to the minimal diff that answers the finding.

If repair cascades oscillate even with one stage, I will reintroduce a round-trip cap at that point.

I also aligned the reviewer instructions with the official prescription: report only gaps that affect correctness or the stated requirements, and treat the rest as optional — not applied.

There was one option I considered and discarded: keep the review density and build new monitoring instrumentation to detect bloat.

But instruments and brakes are themselves new machinery. That would contradict the Contemplative Agent history, where instrument-building is what bloated the pipeline. The only thing that reduces the total amount of machinery is deletion.

## The official docs show a one-step setup, not an upper bound

A distinction worth keeping clear: what the official best practices recommend is adding one adversarial review step.

They set no upper bound on the number of stages. On round-trips, they describe the friction-free "fix and re-review" motion as a benefit of the subagent architecture.

So "at most one standing stage" is not an official recommendation. It is my local judgment, based on the measurement that six stages produced one proven discovery. On the round-trip side, I follow the official's natural motion. Nor am I claiming the same number is optimal in your environment.

The judgment ships with rollback conditions. The expiry conditions written into the design record include, for example:

- Even with one standing stage, a review-triggered repair cascade oscillates (reintroduce the round-trip cap at that point)
- The first time the contracted setup misses real damage in a diff touching a trust boundary
- The first time I observe real silent-failure-class damage (reconsider reviving the dedicated axis)
- The first correctness damage that effort medium missed and that I can judge high would likely have caught

The contraction is not doctrine. It is a provisional judgment that holds until one of these refutations appears.

## First, count your own chain

If you are running multi-stage AI review, before debating the quality of the findings, I recommend counting three numbers:

1. **Stage count** — how many standing review stages can run on a single change. Look not only at the number of rows but at whether the contents of each row have multiplied. In my case, one row's bandwidth grew several-fold while the row count stayed flat
2. **Effort** — is each review set to return only high-confidence findings, or to cast a wide net including uncertain ones? The latter doubles as a supply source for over-engineering
3. **Round-trip count** — re-review after repair is itself a natural motion the official docs describe as a benefit. But if the round-trips run two, three cycles without converging, suspect the stage count and the effort, not the quality of the findings

Then count the chain's output. How many proven discoveries, and is that worth the cost? In my case, that recount was the entire basis for shrinking six stages to one.

To be honest, some things are still unknown. "The main cause of the oscillation is the stage count" is, at this point, a judgment, not a proof.

But because I left the round-trips unconstrained, future operation will do the disambiguation. If oscillation does not recur with one stage plus natural round-trips, the cause was the stage count. If it recurs, I reintroduce a round-trip cap and move to the next measurement.

The token savings are, right after the contraction, still a projection with no after-the-fact measurement. Nor is there yet a before/after comparison of how safety changed.

Still, the measurements so far support one statement. The premise "more review means more safety" was not supported by the numbers in my environment. The six stages I added returned one proven discovery, and the round-trips never came to an end.

The adjacent question — where review findings should be sent — is covered in [a previous article](https://dev.to/shimo4228/ai-review-kept-creating-work-why-i-deleted-4541-lines-22ec). What I cut this time is not the destination of the findings, but the number of taps producing them.

## Sources and references

- [ADR-0055: Contract the review chain to one fresh-context pass plus conditional security](https://github.com/shimo4228/claude-harness/blob/main/docs/adr/0055-review-chain-single-pass-regression.md) (the contraction decision, the measurements, and the record of the July 31 discovery)
- [ADR-0042: The buildup-side predecessor (moving to /code-review and pinning effort high)](https://github.com/shimo4228/claude-harness/blob/main/docs/adr/0042-retire-code-reviewer-and-scope-security-review-to-threat-surface.md)
- [Contemplative Agent ADR-0098: Collapsing the weekly chain from 7 sessions to 1](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0098-weekly-single-session-and-triage-delegation.ja.md)
- [Claude Code official best practices, "Add an adversarial review step"](https://code.claude.com/docs/en/best-practices) (retrieved August 27, 2026)

## Related links

- [Public mirror of my Claude Code harness (the configuration and ADRs behind this article)](https://github.com/shimo4228/claude-harness)
- [Contemplative Agent](https://github.com/shimo4228/contemplative-agent)
- [My GitHub](https://github.com/shimo4228)
