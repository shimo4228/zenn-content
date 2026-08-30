---
title: "My Dead-Code Scan Returned Zero, Then I Deleted 2,063 Lines: Detectors Measure References, Not Consumption"
emoji: "🧭"
type: "tech"
topics: ["claudecode", "aiagents", "staticanalysis", "technicaldebt"]
published: false
description: "Restore the revision just before the delete, run the weekly dead-code scan, and it returns count 0. One minute later, four files — 2,063 lines — are gone with the commit message zero consumers. Both calls are correct: a detector measures whether a path reaches a symbol, not whether anyone reads what it prints. The fix is not a better detector. It is three questions asked when the instrument is built — who reads it, how many readings close the decision, and when it comes down."
tags: claudecode, aiagents, staticanalysis, technicaldebt
---

Restore the state just before a certain commit, run the weekly dead-code scan that repository has been running all along, and this is what comes back.

```json
{
  "tool": "vulture",
  "report_prefixes": ["src/", "scripts/"],
  "count": 0,
  "candidates": [],
  "parsed_total": 149,
  "unparsed_lines": 0,
  "stderr_lines": 0
}
```

Zero candidates. Looks healthy.

One minute later, the next commit deleted four files — 2,063 lines in total. Counting the documentation updates on the record-keeping side, the whole commit removed 2,065 lines.

The reason for the delete is in the commit message. **zero consumers** — because there were none.

The detector answered zero. The human deleted 2,065 lines. Both calls were correct.

This article is about why both can be correct, and what I changed once I understood that.

## I drained the ceiling the day before. The next day, the code was still growing

The subject is Contemplative Agent, the autonomous AI agent I develop, in Python.

On August 28, 2026, I added a function complexity ceiling to this repository (Ruff's `C901`, `max-complexity = 15`) and drained all 13 violations the same day. I wrote up how that went in [the previous article](https://dev.to/shimo4228/after-cutting-my-ai-reviews-i-put-a-complexity-ceiling-in-ruff-1hho).

At 15:20 the next day, the 29th, I typed this to the agent.

> Lately the codebase has put on a lot of lines from the chain of multiple reviews. I have a feeling this project fundamentally should not need that many lines, but it has ballooned. I want it to be a simple product that carries only the code it genuinely needs — how do I get there from here?

I had put the ceiling in and drained it just the day before. It still did not feel like anything had shrunk.

Partway through the conversation, I asked this myself.

> Didn't we have Vulture in there? Is this the kind of thing it can't detect?

Vulture was in there. It even ran automatically every week. And still nothing had shrunk.

## What the previous article handed to the machine

In the previous article I put out a table that sorted checks into three categories.

| Category | Input to the decision | Destination |
|---|---|---|
| Deterministic | Structure, formatting, existence, matching (complexity, circular imports, **dead code**, naming conventions) | The machine |
| Semantic | Intent, validity, two-sidedness | Left to the LLM |
| Mixed | The machine counts, the LLM interprets | The machine produces the value, the LLM reads it |

I put dead code under "deterministic." It is decided by structure, so it goes to the machine.

The 2,063 lines that disappeared the next day caught on none of those rows.

## I re-ran three checks on the revision just before the delete

Saying it in words is weak, so I restored the pre-delete state and measured. I cut the commit before the delete (`a06c6be^`) into a worktree and ran three things.

```bash
CA=~/MyAI_Lab/contemplative-agent
git -C $CA worktree add --detach /tmp/ca-pre a06c6be^

# 1. The repository's own weekly dead-code scan
cd /tmp/ca-pre && uv run --with vulture==2.16 python scripts/dead_code_scan.py

# 2. From Vulture's raw output, pick only the lines about the four files about to be deleted
cd /tmp/ca-pre && uvx vulture@2.16 | grep -E 'coselection|sampling_probe|offwindow'

# 3. Lint, including the complexity ceiling
cd /tmp/ca-pre && uvx ruff@0.16.0 check \
  scripts/coselection_families.py tests/test_coselection_families.py tests/sampling_probe.py
```

Here are the results.

| Check | Output for the four files (2,063 lines) about to be deleted |
|---|---|
| The weekly dead-code scan | `"count": 0` (zero candidates, 149 parsed in total) |
| Vulture's raw output | Exactly one line: `tests/sampling_probe.py:83: unused variable 'prompt_eval_count' (60% confidence)` |
| Ruff (with `C901`) | `All checks passed!` |

About the 912-line script and its 726 lines of tests, none of the three said anything. The one hit that did come out was an unused local variable inside a different file that was also about to be deleted — and at 60% confidence.

One minute later, those four files were gone.

```text
$ git show --stat a06c6be
 scripts/coselection_families.py    | 912 --------------------
 scripts/offwindow-run.sh           | 129 -------
 tests/sampling_probe.py            | 296 ---------------
 tests/test_coselection_families.py | 726 ------------------
 (the remaining 6 files are documentation updates on the record-keeping side; omitted)
 10 files changed, 22 insertions(+), 2065 deletions(-)
```

## Draining the ceiling added lines

There is one more thing I only learned by measuring.

I said above that the day before, I had "drained all 13 complexity ceiling violations." Here is that commit's Python delta.

```text
$ git show --numstat --format= 009baee -- '*.py' | awk '{a+=$1; d+=$2} END {print "+"a, "-"d, "net", a-d}'
+1901 -1086 net 815
```

**Draining it added 815 lines.**

On reflection this was obvious. "Keep one function's branch count at 15 or below" can be satisfied by splitting one function into several helpers. Complexity per function goes down, but total line count goes up. With more function definitions in the file, it tends to go up rather than down.

The complexity ceiling was optimizing a different quantity from the one I wanted to reduce. It was not that it had no effect — **its effect landed somewhere else**.

At this point I had doubted two checks. The complexity ceiling pointed somewhere else, and dead-code detection pointed at nothing at all. The first is a question about the threshold value; the second is not. I needed to look at what the detector itself measures.

## The detector measures references, not consumption

This is the mechanism.

Vulture matches name definitions against uses, and also picks up code after a `return`, or code under a condition that cannot hold, as unreachable. So what it measures is **whether there is a path that reaches the code**.

- If a function is called, it is "used"
- If there is a CLI entry point, it is "used"

The condition for what I wanted to delete, meanwhile, was **whether the readings have a consumer**. Does anyone read the numbers this script prints and decide something with them?

Those two are different things. And the second appears in no symbol. The fact that "no human has read the output" is written nowhere in the code.

I did not need to retract the classification table from the previous article. Inside Vulture's definition of "dead code," that is still the machine's job. What was off was that **the thing I wanted to fold away sat outside that definition**. The classification was not wrong; the item name I was classifying was coarse.

There is one more structure at work here: the more tests you write, the more easily things fall outside detection. This repository's own weekly scan declares it in a docstring (excerpt).

```python
"""Weekly dead-code intake — the fifth deterministic intake.

Scan-wide, report-narrow: vulture's scan paths (pyproject [tool.vulture])
include tests/ and evals/ so that code used only by tests resolves as used,
but candidates are reported for src/ and scripts/ only.
"""
```

To make code that is only called from tests resolve as "used," the scan paths include tests. This is not a mistake. Leave them out and every test-only helper turns up as a candidate, which makes the whole thing unusable.

The side effect, though, is that **a symbol a test references resolves as "used" even when that reference is the only one in the repository**. The 726 lines of tests called the 912-line script's internal functions exhaustively, so barely any symbol was left with room to become a candidate.

What I am calling an **instrument** here is code written **to be read**, not to be run. Readings, distributions, calibration scales, audit surfaces. Acting on the world is not the point, so nothing breaks when the consumer disappears. And because nothing breaks, nobody notices.

## The only thing keeping 912 lines alive was its own test, deleted in the same commit

Here is the breakdown of the four deleted files, with the grounds for each delete. Each one has a dated reason left in a separate record. What I am calling an ADR (Architecture Decision Record) here is text that keeps a design decision and its reason, one file per decision.

| What was deleted | Why its consumer disappeared | Where it is recorded |
|---|---|---|
| `coselection_families.py`, 912 lines + 726 lines of tests | The proposal that was the sole destination for its readings was withdrawn on 2026-08-26 (`withdrawn`) | A note in ADR-0097 |
| `tests/sampling_probe.py`, 296 lines | Done with once the corresponding ADR was written. No consumer after that | A note in ADR-0047 |
| `scripts/offwindow-run.sh`, 129 lines | Nothing in the repository referenced it | grep on the revision just before the delete |

The first row is the clearest example in this article. Search the pre-delete state for anything that actually imports the 912-line script and you get this.

```bash
# reuse the worktree cut out earlier
$ cd /tmp/ca-pre && grep -rn 'coselection' --include='*.py' --include='*.sh' -l .
tests/test_coselection_families.py
tests/test_stats.py
scripts/_stats.py
scripts/coselection_families.py
```

Of those four hits, only one is an actual code reference. The `test_stats.py` and `_stats.py` hits are mentions inside docstrings, and the dependency runs the other way (`coselection_families.py` is the one importing helpers from `_stats.py`).

```python
# tests/test_coselection_families.py:25
import coselection_families as cf
```

**The only import keeping the 912-line script alive was the 726 lines of tests that were deleted in the same commit.** The test calls the script, and the script is called by nobody else. On a reference graph this shape is perfectly healthy. It stays healthy even when nobody outside uses it.

The third row, `offwindow-run.sh`, is simpler still: nothing but the file itself referenced it. A 129-line orphan. The detector still says nothing about it — **Vulture parses Python syntax trees only, and shell scripts were never in scope to begin with**.

One more thing: `coselection_families.py` had a distinctive history. This instrument's output was read **exactly once**, and that number is frozen in a note on an ADR. Read once, purpose served, and then nobody read it again. The code stayed anyway.

For all three, the record says: the restore point is the delete commit, and if any of them is needed again, recover it from git history rather than rewriting it. The delete is not irreversible.

## Standing one up was mandatory. Taking it down was optional

I measured why this happens on the repository's record-keeping side.

This project has a design decision that says "measure before you intervene." Produce a reading before you change anything. I still think it is a good rule. But **the obligation was only on the side that stands things up, and there was none on the side that folds them away**.

ADRs are allowed to carry a section for expiry conditions (`## Review-when`). I counted at the revision just before the delete.

```bash
$ cd /tmp/ca-pre
$ ls docs/adr/*.md | grep -v ja.md | grep -v README | wc -l
     101
$ grep -l '^## Review-when' docs/adr/*.md | grep -v ja.md
docs/adr/0069-gemma-production-model-and-think-on-value-layer-pipelines.md
docs/adr/0097-consolidator-dissolution-and-skill-store-exit.md
docs/adr/0098-weekly-single-session-and-triage-delegation.md
docs/adr/0099-weekly-report-instrument-redesign.md
docs/adr/0100-retire-chaos-tdd-by-default-mandate.md
docs/adr/0101-instrument-dissolution-mandate.md
```

6 out of 101. But the last two, 0100 and 0101, are ones I wrote that same day. Count before those and it is **4 out of 99** — 95 of them said nothing about when they stop being in force.

It is not that removal was never written about at all. Some individual ADRs said in their body that this instrument comes down once it has served its purpose. The problem is that this was **scattered through prose that no gate reads**. Not unwritten. Unread.

Once that is the case, inventory grows easily no matter how good the local decisions are. It does shrink sometimes — the 2,063 lines in this article are exactly that. But it only shrinks when somebody decides one day to go and count. Every item is individually justified, and only the total is nobody's decision.

## Write three things when you stand one up

The fix was to give up on after-the-fact detection and move the check to a gate at creation time.

When you stand up a new instrument, write these three things into the record of that design decision. Anything that cannot be written is not accepted.

- **(a) Who reads it, and when** — a named consumer, plus a frequency or a triggering event. "When it's needed" is not allowed
- **(b) How many readings decide what** — the decision the readings feed, and the number of readings that closes it
- **(c) The removal condition at expiry** — what counts as done, and when it comes down

Explicitly banning "when it's needed" in (a) is where the work happens. The instruments I wrote in the past mostly got through on exactly that.

I put one exception in (b). Exploratory instruments — the ones you stand up precisely because you cannot choose the intervention until the readings exist — may write a **dated review point** instead of a count. The reader and the date still have to be named. Only the count is waived.

**Not being able to answer the three is itself the signal that the instrument has no consumer.** That is the failure shape I wanted to catch.

Below, I call these three the **consumption plan**.

I fixed where it goes, too. The consumption plan goes inside the `## Review-when` section of the ADR that produced the instrument, under a `### Consumption plan` subheading. One place per instrument, right next to the decision that produced it.

## Building no machinery was the condition

This is the part that runs continuous with the previous article and the one before it.

When I thought about a fix, the first things that came to mind were writing a lint that checks for the presence of a consumption plan, and building a registry of instruments. I dropped both.

Here is what I decided instead. **No new code, no scheduler, no lint gate, no registry file.** The obligation is met by adding three sentences to a document I already write, and what enforces it is the same human gate that accepts that record.

I made the shape of a rejection produce no new artifact either. There is no rejection ledger. A rejection is recorded as **the proposal sitting unaccepted, with a one-line reason**.

There is a reason I did not build a registry, and it is the subject of this article itself. **A registry is itself an instrument you then have to maintain.** If you cannot answer, about the registry, who reads it, how many readings close the decision, and when it comes down, you have only added the same problem one layer up.

## How many lines went away

At the end of the session, I asked this.

> So before and after, how much did the line count actually go down?

Here are the re-measured numbers, comparing the commit just before I started deciding against the next day.

| Metric | Before | After | Delta |
|---|---|---|---|
| Total Python lines | 94,882 | 92,723 | −2,159 |
| `.py` file count | 234 | 231 | −3 |
| `scripts/` (.py + .sh) | 9,544 | 8,503 | −1,041 |
| `tests/` | 52,170 | 51,021 | −1,149 |
| `src/` | 29,965 | 29,867 | −98 |

The measurement expands each of the two commits and counts it (this is not the sum of the per-commit diffs).

```bash
CA=~/MyAI_Lab/contemplative-agent
loc() { T=$(mktemp -d); git -C "$CA" archive "$1" | tar -x -C "$T"; \
        find "$T" -name '*.py' -exec cat {} + | wc -l; rm -rf "$T"; }
loc 64393cf   # 94882 (just before I started deciding)
loc 6ce54d9   # 92723 (the next morning)
```

Notice that most of the reduction sits in `tests/` and `scripts/`. What I was able to cut was not the product itself (`src/` is −98 lines) but **the side built to be read**.

## Where this decision does not hold

Let me put the weak points first.

**I cannot say this is undetectable in principle.** What I measured here is the blind spot of a detector that measures references. If you have runtime tracing, or usage logs that record that an output was actually read, the absence of consumers may well be measurable. I did not have that, and standing up a new instrument for the purpose would defeat the point. If you do have it, another road is open to you.

**The fix is at the "wrote it" stage, not the "did it" stage.** I decided on the consumption plan obligation on August 29, 2026, and a retroactive stocktake of the existing instruments has not been through even one pass yet. I can talk about effect after at least one lap.

**This fix may fall into the same trap itself.** There is a real example. The prior design decision that produced the instrument I deleted this time added 6,355 lines of `.py` to stand up the readings, and the conclusion those readings led to deleted 5,672.

```text
(.py only, net delta per commit)
Stand-up:   186dee6 +2,816 / 8757683 +2,008 / c9a1df4 +1,531  → +6,355
Retirement: 47616da +841 −6,513                               → −5,672
```

**The line count built to justify the retirement was larger than the line count the retirement removed.** There is still no guarantee that the same thing will not happen to the "consumption plan" section itself. That is why I leaned toward a shape with no machinery in it.

**I am not claiming that instruments dominate the total.** Over the window from May 2026 to the end of August, tracked Python went from 29,079 lines to 93,620, a gain of +64,541 lines. I have not measured what share of that instruments account for. The 2,063 lines here are one slice I could identify, not a demonstration that they are the main driver of the growth.

## If you want to port this to your own setup

You can run the same judgment without an ADR or RFC acceptance gate. What you need is not the record format but the questions.

**1. List the code you wrote "to be read" rather than "to be run."** Metrics, distribution rollups, audit scripts, one-shot measurement harnesses, dashboard exporters. Anything whose execution does not change product behavior.

**2. One at a time, try to name the reader.** "Someone, when it's needed" is not a name. The moment you cannot name one, that is the zero-consumer signal.

**3. For the ones you can name, write two more things.** How many readings close the decision. When it comes down once it has closed. For exploratory ones, a review date instead of a count is fine.

**4. Write it next to the decision that produced the instrument.** If you do not have ADRs, a docstring at the top of the file will do, or one line in the commit message that added the instrument. What matters is that it lands in the eyes of the next person who touches that file. Collect it all into a separate document and that document becomes an instrument with no reader.

**5. Ask at creation time.** Stocktaking what already exists is heavy work. The creation-time side, in my setup, came down to adding three items to a document I already write. Where agreeing on who the reader is takes negotiation, that is where the cost lands. A stocktake reduces inventory; a gate at creation time stops the increment. Without stopping the increment, the stocktake returns to the same volume every time.

One last thing, which is also in this article.

The moment the 912-line instrument's consumer disappeared can be pinpointed. It is August 26, 2026, when the proposal that was the sole destination for its readings was withdrawn. The reason for the withdrawal was not a flaw in the proposal but a judgment that redoing the upstream design came first. I think that was a good call.

The problem is that **nothing happened on the code side**. The proposal's state became `withdrawn`, and the 912 lines stayed exactly where they were. There was no mechanism connecting the two. The only thing that connected them was one human recounting three days later, on a different errand.

Ledger state transitions and the life or death of code do not track each other if you leave them alone. That is why you need (c), the removal condition. **Unless you write "when the destination for these readings disappears, this instrument comes down too" right next to the thing that will disappear, nobody can notice that it disappeared.** Whether there is a consumer is not written inside that file.

## Sources and references

- [The Telemetry Debt Crisis: Why Cloud-Native Teams are Optimizing the Wrong Metric](https://cloudnativenow.com/contributed-content/the-telemetry-debt-crisis-why-cloud-native-teams-are-optimizing-the-wrong-metric/) — the nearest discussion in the observability field. Its prescription — ask who will use a signal at the point you create it, rather than reaching for a detection tool — is close to identical in shape to (a)(b)(c) here (retrieved 2026-08-30). What this article adds is that the subject is code inside a repository rather than telemetry, and that it is a measurement of one and the same case — the code a detector returned zero on was deleted a minute later — rather than an argument
- [Telemetry accumulates like technical debt](https://michaelscodingspot.com/telemetry-technical-debt/) — a description of how instrumentation piles up as debt (retrieved 2026-08-30)
- [Vulture](https://github.com/jendrikseipp/vulture) — the dead-code detector used in this article (2.16)
- [Ruff `C901` (mccabe)](https://docs.astral.sh/ruff/rules/complex-structure/) — the complexity ceiling rule

## Related links

- [After Cutting My AI Reviews, I Put a Complexity Ceiling in Ruff](https://dev.to/shimo4228/after-cutting-my-ai-reviews-i-put-a-complexity-ceiling-in-ruff-1hho) — the previous article: installing the complexity ceiling, and what it measured
- [I Cut My AI Review Chain From 6 Stages to 1: Breaking the Loop That Never Hits Zero Findings](https://dev.to/shimo4228/i-cut-my-ai-review-chain-from-6-stages-to-1-breaking-the-loop-that-never-hits-zero-findings-1moi) — the one before that: how I cut the reviews back
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles/instrument-consumption-plan.md) — the Markdown for every article, plus the index (docs/PUBLICATIONS.md), lives in the same repository
- [My GitHub](https://github.com/shimo4228) — my research repositories, with DOIs
- [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) — the subject measured in this article. The design decisions live in `docs/adr/`, and the consumption plan obligation is ADR-0101
