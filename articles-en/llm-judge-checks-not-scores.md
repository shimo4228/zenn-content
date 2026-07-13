---
title: "LLM-as-Judge Shouldn't Aggregate Scores: Binary Checks as Evidence, One Holistic Verdict"
emoji: "⚖️"
type: "tech"
topics: ["llm", "promptengineering", "evaluation", "claudecode"]
published: true
description: "A design pattern for LLM-as-judge: collect evidence with binary Yes/No checks, pick one named verdict holistically, and never aggregate into a score. With a copy-paste judge prompt structure."
tags: llm, promptengineering, evaluation, claudecode
---

> **What this article gives you**: How to design LLM quality evaluation around "binary checks + a named verdict" instead of numeric scores. Includes a judge prompt structure you can reuse by swapping in your own evaluation target.

Having an LLM evaluate deliverables is called LLM-as-judge. Once you introduce it, most people run into the same three walls:

- Ask for a 5-point rubric score and the same input oscillates between 3 and 4 across runs
- Gate pass/fail on a total-score threshold and one fatal flaw gets diluted by high scores on everything else — and slips through
- Read the scores back later and nobody can explain why something got a 3.5

This article introduces a design pattern that avoids all three at once. The core fits in one line:

**Collect evidence with binary Yes/No checks, have the judge pick one verdict from named labels as a holistic judgment, and never aggregate anything into a score.**

I've been running this pattern for about four and a half months in a Claude Code skill-quality audit (`/skill-stocktake`) and a knowledge-extraction quality gate (`/learn-eval`). How I built the audit command — the trial and error that led me to throw out numeric rubrics — is covered in [my previous article](https://dev.to/shimo4228/offloading-ais-weak-spots-to-shell-scripts-designing-building-and-publishing-a-skill-audit-2ll8).

This article is the sequel. It generalizes that design into a **reusable LLM-as-judge pattern**, including the episode where I tested my own design while it was in production — and rebuilt it.

## Assumptions

- Audience: anyone who wants to automate quality evaluation of deliverables (documents, code, data) with an LLM
- The examples use Claude Code skill evaluation, but the pattern itself is agnostic to evaluation target, model, and tooling
- Terminology: **verdict** = the final output of an evaluation. It takes the form of picking exactly one from named options such as "Keep / Retire". The JSON examples in this article use a `verdict` field
- Terminology: **holistic judgment** = a single conclusion reached by looking at the whole, without going through per-dimension scoring

## The pattern at a glance — three principles

```text
Evaluation target
  → ① Binary checks: decompose into Yes/No questions
  → No answers = evidence
  → ② Holistic judgment: pick one named verdict
  → ③ No aggregation: scoring and averaging are forbidden
  → Downstream code / humans branch on the verdict
```

| Principle | Do | Don't |
|---|---|---|
| ① Checks are binary | Decompose criteria into questions answerable with Yes/No | "Rate specificity on a 5-point scale" |
| ② The verdict is a named label | Look at the whole and pick one from `Keep / Improve / Retire` etc. | "Total is 12 points, so it passes" |
| ③ No aggregation | Have the No answers **listed as the grounds** for the verdict | Using the Yes ratio (satisfaction rate) as a quality metric |

### ① Make the checks binary Yes/No

Instead of "how specific is this skill, out of 5?", ask "is there a concrete command example you can run immediately after reading? Yes/No."

Binary questions have two properties that numeric scoring lacks:

- **Verifiable**: "Is there a command example?" can be settled black-and-white by looking at the text. "Specificity: 3 points" cannot be verified at all
- **Evidence**: a No answer points directly at *what is missing*. It feeds straight into an improvement list

In the skill audit I run in production, every target goes through these four questions:

```markdown
- [ ] Actionability: are there steps, commands, or worked examples you can run immediately?
- [ ] Scope fit: do the name, trigger, and body agree (not too broad / too narrow)?
- [ ] Uniqueness: does it avoid overlapping with other skills in the same batch?
- [ ] Currency: do the referenced paths, CLI flags, and URLs still exist today?
```

### ② Have the verdict picked from named labels, as a holistic judgment

Holistic judgment is what LLMs are good at. As I wrote in the previous article, LLMs are bad at scoring dimensions independently — they get pulled by the overall impression. So it's more honest to design for that from the start: "pick one, based on the overall impression."

The key is to name the verdict labels so they map **1:1 to the next action**.

| Use case | Verdict options | Corresponding action |
|---|---|---|
| Skill audit | `Keep / Improve / Update / Retire / Merge into [X]` | Keep / hand off to the improvement engine / technical refresh / delete / consolidate (with an explicit target) |
| Knowledge-extraction gate | `Save / Improve then Save / Absorb into [X] / Drop` | Save / fix then save / append to an existing skill / discard |

A **fixed set of options** that downstream processing can branch on directly is more practical than a bare `accept / reject` (in programming terms, an enum — a mechanism that forbids any value outside the defined set. With free-form text you get drift like "Improve" vs. "improve slightly", and code can't branch on it). Designs like `Merge into [X]` that **force a concrete target name** make vague verdicts like "this feels like it overlaps with something" structurally impossible to write.

This separation — "the LLM picks from named options, code executes" — also acts as a firewall against judgment errors. If judging and executing are separate, an LLM's bad call can never corrupt system state directly (I run this as a pattern I call **LLM judge + Code enforce**).

### ③ Never aggregate the binary answers

This is the pattern's biggest fork in the road. Once you have binary checks, you'll be tempted to say "6 of 8 questions are Yes, that's 75%, above the 70% threshold, so it passes." **Don't.**

The reason is simple: **a satisfaction rate dilutes a single fatal No.** If one No says "the referenced file doesn't exist," the skill is broken even if the other seven answers are Yes. Averages and ratios convert that dominant No into a 12.5% deduction.

Do these two things instead:

1. Require the No answers to be **listed as the grounds** for the verdict (hidden Nos breed verdict drift)
2. If there is even one dominant No (a nonexistent reference, an unsupported claim, etc.), tip the verdict to the non-Keep side even if everything else is Yes

The skill-audit definition file states the principle in one sentence:

> Evaluation is **holistic judgment, not a numeric rubric** — binary answers are evidence feeding the verdict, never aggregated into a score (a satisfaction ratio changes no decision and dilutes a single dominant No).

## The verdict pressure-test — attack the verdict before you commit it

Binary checks plus holistic judgment already work, but one more quality device raises the verdict's reliability: **before finalizing a provisional verdict, have the LLM itself generate and answer questions that try to refute it.**

```markdown
Procedure (applied only to non-Keep candidates):
1. Generate 1–3 Yes/No questions that would refute the provisional verdict
   e.g. if the provisional verdict is "Update (a referenced CLI flag is deprecated)"
   → "Doesn't that flag still exist in the current version's --help? Verify empirically"
2. Answer each question with one line of evidence (file read, path check, web search result)
3. Refutation succeeds (e.g. the flag still exists) → move the verdict back toward Keep
4. Defect confirmed (e.g. the flag was indeed removed) → the No items from the binary
   checks become the improvement list as-is
```

Two disciplines govern question design:

- **Atomicity**: each question tests exactly one verifiable claim
- **Refutation-oriented**: frame questions to seek refutation of the provisional verdict, not confirmation of it

One more discipline matters for re-judging after fixes: **re-judge exactly once, with the same question set.** If you rewrite the questions, you can no longer tell whether the fix worked or the bar just moved.

## A copy-paste judge prompt structure

Here is the whole pattern in a form you can reuse by swapping in your own evaluation target.

```markdown
You are a quality evaluator of {kind of evaluation target}. Evaluate using the following steps.

## Step 1: Binary checks (all questions mandatory)
Answer each question with Yes/No plus one line of evidence.
- Q1: {verifiable question, e.g. is there a runnable code example?}
- Q2: {verifiable question}
- Q3: {verifiable question}
- Q4: {verifiable question}

## Step 2: Target-specific refutation questions (only if the provisional verdict leans non-pass)
Pick one provisional verdict, generate 1–3 Yes/No questions that would refute it,
and answer each with one line of evidence.

## Step 3: Verdict
Choose exactly one of the following. Do not output scores or points.
- {verdict_label_1}: {meaning and next action}
- {verdict_label_2}: {meaning and next action}
- {verdict_label_3}: {meaning and next action}

In the grounds for the verdict, list every question answered No.
If there is even one dominant No ({domain-specific fatal condition}),
choose {non-pass verdict label} even if everything else is Yes.

## Output format
Follow the JSON schema below and output **JSON only**
(no explanatory text or Markdown before or after).
```

Receive the output as JSON and downstream code can process it directly.

```json
{
  "verdict": "Improve",
  "evidence": [
    { "question": "Is there a runnable code example?", "answer": "No", "detail": "Steps are bullet points only; not a single command example" },
    { "question": "Do the referenced paths exist?", "answer": "Yes", "detail": "All 3 paths confirmed with ls" }
  ],
  "pressure_test": [
    { "question": "Does the refutation hold that the bullet-point steps alone are reproducible?", "answer": "No", "detail": "The argument spec in step 3 is ambiguous; not reproducible" }
  ],
  "reason": "The Actionability No is dominant. Adding a worked example to step 3 would make this Keep-worthy"
}
```

Since the `verdict` field only takes fixed options, the receiving code just branches with a `switch` statement. The No items in `evidence` can be handed to the next stage (a human or another LLM) as an improvement task list as-is.

The full design pattern, including this template, is published as a Claude Code Agent Skill at [github.com/shimo4228/llm-as-judge](https://github.com/shimo4228/llm-as-judge). Copy `skills/llm-as-judge` into `~/.claude/skills/` and it fires automatically whenever you're designing a judge.

## Same principles, different operation at different scales

Running this pattern at two scales taught me that **the principles are shared, but the application conditions change with scale**.

| | Knowledge-extraction gate (learn-eval) | Skill audit (skill-stocktake) |
|---|---|---|
| Evaluation target | 1 draft extracted from a session | The entire library (73 skills) |
| Refutation question generation | **Unconditional** (3–5 questions every time) | **Non-Keep candidates only** (1–3 questions) |
| Reason | N=1, so the cost is negligible | Generating for all 73 items wastes most of the shots |

With a single evaluation target, go all-in — it costs nothing. At tens of items, reserve the expensive device (refutation questions) for the suspicious candidates only.

## Does single-context evaluation lose accuracy? — testing my own design

Here begins the second half of this article. The skill audit above originally used a design of "**load every skill into one context and evaluate**." The logic: a long-context model can survey everything at once, so cross-skill duplication should also be visible.

Then an audit run under this design returned **Keep for every single item**. Not one defect, not one duplicate pair detected. Is that "the library is healthy" or "the evaluation is spinning idle"? To find out, I re-audited the same library two ways: **splitting it into small batches of about 10 items, each close-read by an independent agent**, and **a probe dedicated solely to duplicate detection** (the experiment design and caveats about the numbers are in the collapsible section at the end of this chapter).

### Results — some dimensions degrade, others don't

| What was tested | Result |
|---|---|
| Per-item defect detection (small-batch close reading) | **12 of 73 items non-Keep** (16%). The single context had missed all of them |
| Duplicate detection (dedicated probe) | True duplicates: **0** (all 17 candidate clusters were adjacent skills with documented role separation) |

Half of the 12 missed items were **mechanically detectable defects**: 404 links, references to deleted files, deprecated CLI flags. The kicker: **two files that no longer existed on disk had been given Keep verdicts.**

Zero duplicates, on the other hand, turned out to be reality, not dilution (attention thinning as the context fills up). The single-context rationale — "you can see duplication because you survey everything at once" — had been fully replaced by a lightweight description scan plus targeted close reading.

### The biggest lesson isn't context width — it's verification ownership

Tracing the mechanism of the misses revealed a cause deeper than context width itself. The audit definition contained a conditional verification instruction: "**if a reference looks stale, check it.**" That "if it looks..." condition is itself a judgment that depends on the LLM's attention. When the context fills up and attention thins, conditional triggers default to "don't check."

The previous article's conclusion was "mechanical work to scripts, quality judgment to AI." This experiment redrew that boundary one level deeper: **inside quality judgment there are deterministic parts hiding, and they belong in code.** "Does this file exist?" is not a judgment — it's `ls`. The deterministic checks that had snuck into the judgment phase should have been moved to the code side as an unconditional, mandatory pre-pass. That is what "verification ownership" in the heading means: moving the execution owner of deterministic checks from the LLM's attention to code.

The revised design (v3.0) assigns each property to the environment that should check it:

```text
Phase 0: Deterministic pre-pass (code-owned, unconditional)
         Reference-existence checks, ledger consistency.
         Anything that doesn't exist never reaches judgment.
Phase 1: Inventory
         (the layer offloaded to scripts in the previous article; unchanged)
Phase 2: Per-item scrutiny (small batches of ~10, parallel)
         Binary checks + verdict pressure-test + holistic judgment
Phase 3: Dedicated duplication probe (1 agent, all items)
         Lightweight description scan → close-read candidate clusters only
```

I reviewed the 12 detections one by one and fixed them the same day. For one of them, testing the proposed fix before applying it showed the command didn't actually work, so I swapped in a different form. Verify not just the verdict but **the fix itself before committing it** — the same pattern surfacing outside the evaluation loop.

:::details Experiment design and notes on the numbers (for the curious)
- **Baseline**: the audit result from the all-in-one-context run. On the ledger it was 84 entries, all Keep. The actual files on disk numbered 73 — the gap was a ledger bug: the same skill double-counted under two different keys, plus entries for files that no longer existed. That the ledger was this dirty had gone unnoticed by everyone at that point. The follow-up experiments target the 73 real files
- **Treatment A (small-batch close reading)**: split the 73 items into 7 batches of 10–11, each close-read by an independent subagent using the same criteria (binary checks → holistic judgment). Reference existence had to be verified with `ls` etc., stated explicitly
- **Treatment B (dedicated duplication probe)**: one agent reads all 73 descriptions, enumerates candidate clusters → close-reads the bodies side by side to decide
- **Bias control**: the agents were not told that the baseline had returned all-Keep
- **An honest note on confounding**: Treatment A's prompt explicitly required "verify reference existence with `ls`", so part of the difference from baseline is attributable to "forced verification" rather than "context width." However, detections that required semantic judgment — description/body mismatches, overly abstract writing, scope drift — cannot be explained by forced verification, and I read those as the effect of attention density: 10 items per batch versus 73
:::

## Why no scores — the boundary the proposing paper drew itself

The "decompose evaluation criteria into binary questions" approach has a research lineage: CheckEval (arXiv:2403.18771, 2024), TICK (arXiv:2410.03608, 2024), and the later BinEval, "Ask, Don't Judge" (arXiv:2606.27226, 2026). My setup had the "binary checks + holistic judgment" skeleton first; I learned of this lineage afterward and folded it into each skill's References. BinEval proposes decomposing into atomic Yes/No questions and wiring failed questions directly into improvement feedback — the dynamic generation of refutation questions and the "No answer = improvement list" wiring are the parts I ported from it after it came out.

What's interesting is BinEval's own limitations section. The paper self-reports two reservations. First: binary decomposition is reliable only up to **concretely checkable criteria**, like "is there a code example?" Subjective quality like "is this well written?" is something humans judge by looking at the whole rather than stacking individual checks — it **cannot be fully decomposed into a bundle of Yes/No questions** (less reliable). Second: "it assumes **the fraction of satisfied questions corresponds roughly linearly to quality**, and **this does not always hold**." In other words, using the satisfaction rate of decomposed questions as a score comes with a caveat from the proposing paper itself.

Flip that limitations report around and it is exactly a **division-of-labor boundary**. Concretely checkable criteria can be decomposed into Yes/No — so let the checks gather evidence. The final value judgment belongs to the subjective "is this good writing?" layer, which reduces neither to a bundle of questions nor to a satisfaction rate — so that layer stays a holistic judgment. The three principles in this article are that self-reported boundary, transcribed directly into a design.

## Summary

- Design LLM-as-judge evaluation around three principles: "binary checks = evidence," "verdict = pick one named label holistically," "no aggregation"
- Make verdict labels a fixed set mapping 1:1 to next actions, and require every No answer to be listed as grounds for the verdict
- A verdict pressure-test before finalizing raises reliability. Re-judge exactly once, with the same question set
- In my experiment, per-item scrutiny diluted as the context filled up (16% missed). Don't put deterministically verifiable checks on the LLM's attention — move them to unconditional, code-owned execution
- The reason not to turn "satisfaction rate" into a score comes from the limitations self-reported by the binary-decomposition paper itself (BinEval): decomposition works up to concrete criteria; the value-judgment layer stays holistic

The previous article's division of labor — "mechanical work to scripts, quality judgment to AI" — got one level deeper this time. **Inside judgment, too, there are parts that belong in code.** When you design an LLM-as-judge, start by asking, before anything reaches the judge: "is this really a judgment, or is it `ls`?"

## Related links

- [llm-as-judge](https://github.com/shimo4228/llm-as-judge) — the design pattern from this article, packaged as an Agent Skill (install and use as-is)
- [Previous article: Offloading AI's Weak Spots to Shell Scripts — Designing, Building, and Publishing a Skill Audit](https://dev.to/shimo4228/offloading-ais-weak-spots-to-shell-scripts-designing-building-and-publishing-a-skill-audit-2ll8)
- [claude-skill-stocktake](https://github.com/shimo4228/claude-skill-stocktake) — the skill-audit command from this article (v3.0 hybrid structure)
- [agent-knowledge-cycle](https://github.com/shimo4228/agent-knowledge-cycle) — where the LLM judge + Code enforce pattern mentioned in this article is defined
- Paper: [CheckEval](https://arxiv.org/abs/2403.18771) (arXiv:2403.18771, 2024) — prior work on checklist-decomposition LLM evaluation
- Paper: [TICK](https://arxiv.org/abs/2410.03608) (arXiv:2410.03608, 2024) — evaluation and generation improvement via generated checklists
- Paper: [BinEval, "Ask, Don't Judge"](https://arxiv.org/abs/2606.27226) (arXiv:2606.27226, 2026) — source of the atomic Yes/No decomposition and "No answer = improvement list" wiring; its limitations section grounds the boundary drawn in this article
- [github.com/shimo4228](https://github.com/shimo4228) — the author's other repositories
