---
title: "Can Six-Month-Old AI Code Survive Today's Review? A 25-Bug Triage"
emoji: "🕰️"
type: "tech"
topics: ["claudecode", "codex", "codereview", "python", "testing"]
published: true
description: "I had two current-generation AI lineages (Claude Fable 5 + GPT-5.6-Sol via Codex CLI) audit a CLI tool Claude wrote six months ago. 31 verified findings, zero false positives, ~25 unique bugs — including features that had never worked once. What the audit says about AI code 'aging', mock blind spots, and how much harness scaffolding you can dissolve."
tags: claudecode, codex, codereview, testing
---

Six months ago, I had Claude write a CLI tool. All 694 tests were green; mypy and ruff were clean.

Back then I even wrote an article called "[Never trust LLM output](https://dev.to/shimo4228/never-trust-llm-output-6-defenses-from-building-a-pdf-to-anki-cli-43mo)", listing six defenses.

The other day, I had two lineages of current-generation AI review that proud piece of work end to end.

Every finding I put through verification (31 in total, counting duplicates) turned out to be **a real bug. About 25 after deduplication, zero false positives.**

But the subject of this article is not "what bugs were in there."

What I wanted to know was: **by today's standards, what level was the code written by the AI generation of six months ago — and the harness that propped it up?**

Here is the report card, up front:

- **Skeleton (design): still holds.** Only 2 findings around Vision required design changes, and the fixes fit in a patch release
- **Details that touch the outside world: below shipping grade.** Reversible-card submission to Anki and extraction of large images had never worked correctly from the day they were implemented
- **Aging: no confirmed case.** Not one confirmed instance of "the world moved after the code was written and broke it" — every breakage I could confirm was "broken from day one"

The rest of the article backs these three lines with numbers.

## The setup: two generations, six months apart, head to head

The test subject is [pdf2anki](https://github.com/shimo4228/pdf2anki), a Python CLI that auto-generates Anki flashcards from PDFs, implemented over 10 days in February 2026 (the record from that time is in [another article](https://dev.to/shimo4228/a-beginners-first-10-days-of-real-development-with-ecc-23k4)).

Between the side that wrote it and the side that audited it lies six months of generational difference — in the models, and in the harness (the full set of skills, rules, and hooks loaded into Claude Code).

| | Writer (2026-02) | Auditor (2026-08) |
|---|---|---|
| Model | Claude Opus 4.6 (partly Sonnet 4.5) — per commit Co-Authored-By | Claude Fable 5 + GPT-5.6-Sol (via Codex CLI) |
| Harness | Early ECC adoption. The period of stacking thick scaffolding from community skill collections | After scaffold dissolution. A thin setup with skills and rules heavily cut |
| Quality assurance | TDD + that generation's code review | The 2 commands in this article |
| Code state | 694 tests passed, mypy/ruff clean | Same (no feature work since the Feb implementation) |

ECC (Everything Claude Code) is a community-built collection of Claude Code extensions. Its philosophy was to lift the weaknesses of then-current models with bundles of skills and rules (which this article calls "scaffolding"); my harness started there and, after [swelling and a stocktake](https://dev.to/shimo4228/15-days-of-skill-sprawl-in-claude-code-lessons-from-3-audits-27em), headed toward dissolution.

:::message
All measurements below are as of 2026-08-13.

Models, prices, and tool behavior keep changing — if you reproduce this, substitute whatever is current at that time.
:::

## What I did: run two review lineages in parallel

I used only 2 commands. Both are read-only; neither modifies the code.

The first is Claude Code's built-in `/code-review`. Point it at the whole directory and set effort to high so it sees everything.

```text
/code-review src/pdf2anki high
```

The second is [codex-review](https://github.com/shimo4228/codex-review), a skill that calls the OpenAI Codex CLI as a reviewer. It runs in prompt-driven mode, launched with an explicit focus:

```bash
bash ~/.claude/skills/codex-review/codex-review.sh "Review the entire codebase under src/pdf2anki/ (not just the diff). Focus on: correctness bugs, error-handling gaps, API misuse (Anthropic SDK, PyMuPDF, Gradio, Textual), security issues, cost-tracking accuracy in cost.py, cache integrity in cache.py, and concurrency/state bugs. Report concrete findings with file:line references. Ignore style nits."
```

The reason for stacking a model from a different lineage is that models from the same lineage share the same blind spots. I wrote up this design intent in [the previous article](https://dev.to/shimo4228/i-built-a-skill-for-easy-codex-reviews-from-claude-code-4h89).

Here is the scale of the audit, in numbers:

| Item | Measured |
|---|---|
| Codex (GPT-5.6-Sol) findings | 15 (P1 = top priority ×6, P2 = runner-up ×9). All confirmed real by reading the code |
| Claude (Fable 5) detection flow | 8 perspectives → 44 candidates → 32 after dedup → 16 correctness candidates individually verified → 16 CONFIRMED / 0 REFUTED (several reproduced by actual execution in a venv) |
| Combined (after dedup) | ~25. 23 of them fixed and released as [v0.3.1](https://github.com/shimo4228/pdf2anki/releases/tag/v0.3.1) (39 files, +739/−361) |

## Verdict 1: fatal or trivial?

Twenty-five bugs sounds catastrophic, but they are a mixed bag. Sorted by severity:

| Severity | Count | Contents |
|---|---|---|
| **Broken features** (fail when used) | 4 | Reversible-card submission to Anki (fails every time) / Vision extraction of large images (total loss) / import inconsistency in TSVs mixing card types / bulk Vision submission of very long PDFs |
| **Silent leaks** (money and data) | ~13 | Budget check bypassed in batch runs / costs overstated 3× / prompt-cache billing not counted / one bad response losing every card in the file / configured model selection ignored, etc. |
| **Robustness / UX** | ~8 | TUI display skips / unhelpful crashes on error / retries applied twice, etc. |

Two things follow from this distribution.

First, **almost none of these bugs crash loudly**. Most of them either fail silently or silently record the wrong amount of money.

That is why demos ran to completion, tests stayed green, and nobody noticed for half a year.

Second, the top two broken features (reversible-card submission and large-image extraction) had **never worked correctly from the day they were implemented**. They sent a note type name that does not exist and called an API in a way that does not exist — this can be deduced without any guesswork.

So the level of the six-month-old code is not "works, but rough." It is: **"shipped in a state where part of the main functionality was dead, and neither the tests nor the author could notice."**

On the other side, here is the evidence for the skeleton. Of the 25 findings, only 2 — around bulk Vision submission — required design changes (deferred this time); the remaining 23 closed with local fixes.

The entire fix fitting into a 39-file, +739/−361 patch release is what it looks like when the skeleton holds up even under current-generation eyes.

:::details The representative bugs (with code — only if you're curious)
**① A nonexistent Anki note type name** (broken feature)

```python
# src/pdf2anki/anki_connect.py:95-102 before the fix
# Anki's standard name is "Basic (and reversed card)". This name does not exist
model_name = "Basic (and target: reversed card)"
```

The tests were green because the tests themselves asserted the same wrong string.

```python
# tests/test_anki_connect.py:200 before the fix
assert payload["params"]["note"]["modelName"] == "Basic (and target: reversed card)"
```

**② A nonexistent PyMuPDF API call** (broken feature)

```python
# Reproduced during verification (pymupdf 1.26.7). Equivalent to src/pdf2anki/image.py:156 before the fix
import pymupdf
src = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 100, 80))
scaled = pymupdf.Pixmap(src, 50, 40, None)          # the correct form works
bad = pymupdf.Pixmap(src, pymupdf.Matrix(0.5, 0.5))  # TypeError
```

This TypeError was swallowed by a broad `except Exception: continue` and lurked as "only images above a certain size silently disappear." The verification agent reproduced extraction returning 0 images on a PDF containing a 2000×2000 image.

**③ A price table with the previous generation's prices written in** (silent leak)

```diff
# src/pdf2anki/cost.py:17-21 — per-model prices ($/MTok, input/output)
- "claude-haiku-4-5":  (0.80, 4.00)   # actual is $1 / $5 (20% under)
- "claude-opus-4-6":   (15.00, 75.00) # actual is $5 / $25 (3x over)
+ "claude-haiku-4-5":  (1.00, 5.00)
+ "claude-opus-4-6":   (5.00, 25.00)
```
:::

## Verdict 2: why did the tests stay green for half a year?

The 25 broken places shared 2 common mechanisms. The mechanisms are worth more than the individual bugs.

**Mechanism 1: the tests go green together with the assumptions.**

Tests replace the real external things (Anki, PyMuPDF, the API) with fakes (mocks). Nearly all of these bugs lived outside that replacement boundary.

When the same AI writes the implementation and the tests in the same session, its assumptions get copied to both sides. The tests can only verify "does the implementation match my assumptions" — never "do my assumptions match the world."

Testing as a practice is not powerless. The fixes added a regression test that pushes a large image through the real PyMuPDF, so this class of bug will be caught by tests from now on.

What is powerless is a mock written with the same assumptions as the implementation.

**Mechanism 2: the writer's (the AI's) knowledge is already stale at the time of writing.**

The price table in the code said $15/$75 for Opus 4.6 and $0.80/$4.00 for Haiku 4.5 (actual: $5/$25 and $1/$5, respectively). These wrong numbers exactly match the prices of the previous generation — Opus 4/4.1 and Claude 3.5 Haiku.

[The Opus 4.6 launch announcement](https://www.anthropic.com/news/claude-opus-4-6) (2026-02-05) says "Pricing remains the same at $5/$25 per million tokens", and the implementation was on 02-08.

In other words, the model **wrote the previous generation's going rate, memorized during training, straight into the code as the new model's price.**

What's more, a research doc inside the repo, written the day after implementation, had the correct prices on record. The right answer was sitting right there — and the code got the memory instead.

Full disclosure: the first draft of this article also explained this as "a price cut after the code was written broke it." Until fact-checking refuted it, I believed that plausible memory myself.

Staleness sneaks in whether the writer is an AI or a human.

Both of these mechanisms produce "broken from day one." And every breakage I could confirm was one of the two; confirmed cases of "the world moved after the code was written and broke it" came to zero this time.

**The six-month-old code had not decayed with age. It was broken from the start, and simply ran unnoticed.**

The countermeasures map onto the mechanisms. Against replicated assumptions: cross-checking against the real thing, independent of the implementation (a different-lineage review, or verification against the real dependency). Against staleness: re-verification after writing, not a single check at write time.

The 2 commands in this article were a cheap way to run both at once.

## What the audit side revealed: the two models looked at different places

The overlap between the two models' findings — counting same-file, same-substance findings as one theme — was 4 themes (5–6 by finding count). **Only about 20% overlap by count.**

| Category | Count | Tendency |
|---|---|---|
| Independently agreed | 4 themes | Budget bypass, cache-key flaw, note type name, ignored model selection |
| Codex only | ~10 | **Strong on external contracts**: API pricing, the prompt-cache billing scheme, Anki's TSV import spec |
| Claude only | ~10 | **Strong on runtime failure paths**: nonexistent API calls, exception propagation, data loss on partial failure |

Flip that around: **either one alone would have found only around 60% of the ~25.**

The 4 independently-agreed themes worked as a priority signal. When two models from different lineages point at the same spot, that spot is almost certainly real.

In practice, I fixed in this order: both-agreed + billing → total-data-loss → UX.

## How much of the scaffolding could be dissolved?

The other thing I wanted to measure in this audit is the **harness row** of the setup table.

Six months ago, I stacked thick scaffolding (bundles of instructions — skills, rules, procedure docs) to supplement the model's judgment. These days I keep dissolving it.

| Period | Harness state |
|---|---|
| 2026-02 (implementation) | Early ECC adoption. Thick scaffolding to lift the then-current model |
| 2026-03 | ECC itself had swollen to 116 skills. Disabled the plugin; cut my imported 33 skills down to 16 |
| 2026-07 | Cut roughly 8–9k tokens of always-on rules. The judgment: "instructions that compensated for an old generation's weakness are shackles on the new one" |

Can a thin-harness, current-generation set properly inspect the products of the thick-harness era?

The result: all 31 findings put through verification (15+16) were real, zero false positives. That precision came without any author-written procedure docs.

Saying the procedures are gone would be inaccurate, though. `/code-review` itself has a multi-stage procedure built in — "explore from 8 perspectives → a verification agent tries to refute." **The procedure moved from the author's bolt-on into the tool's built-ins.**

Meanwhile, 2 mechanisms in a layer separate from instruction scaffolding were **still earning their keep**.

The first is machine gates. The fix commit was bounced 3 times by pre-commit hooks (security scan → formatter → secret detection), and passed all 3 through real fixes.

The layer that machine-checks LLM output is still doing its job in the current generation.

The second is human intervention points. The review agent sat stalled, waiting on verification, for about 40 minutes — and only ran to completion after I sent a resume instruction.

The "press the button when it stalls" human is still required.

**The scaffolding that taught judgment could be peeled away. The machinery that inspects, and the intervention point a human presses when things stall, remained.** That is where the dissolution stands today.

:::details Operational tips (fine print for reproducing this)
- **Review agent stalls**: a background review being quiet does not mean "task complete." It may simply be stalled. This time, after ~40 minutes of no activity, one message — "collect the verification results and write the final report" — got it to finish in ~2 minutes
- **Always check price/spec fixes against current primary sources**: fixing a price table because "the AI said so" just plants one more stale fact
- **Fix "both-agreed + billing" first**: findings two models reached independently carry the lowest false-positive risk, and billing bugs cost real money while they sit
- **Cost**: the Claude-side review subagents consumed about 200k tokens in total (95,229 + 106,860). A full-codebase effort-high review is not cheap — running it at milestones is the realistic cadence
:::

## Wrap-up: how to read the report card

The level of the code written by the six-months-ago generation set (Opus 4.6 + a thick harness) was this:

- **Skeleton: pass.** Only 2 findings around Vision needed design changes; the fixes fit in a patch release
- **Details that touch the outside world: fail.** 4 broken features, ~13 silent leaks. Some features had never once worked
- **Aging: no confirmed case.** Every confirmed breakage was "from day one." It simply went unseen for half a year

And **the green tests taught us nothing about this gap**. 694 green tests coexisted with "part of the main functionality is dead" for half a year.

What worked as the measuring instrument was two reviews from different lineages. Either one alone saw only ~60%, so being two lineages is the point.

The harness answer also fits in one line: the scaffolding that taught judgment could be peeled away; the machinery that inspects and the intervention point a human presses remained.

If you have code an AI wrote months ago, still running with green tests, the same measurement is 2 commands away.

And six months from now, the code today's Fable 5 writes will rotate into the audited seat before the next generation. What grade will it get? Keeping it in a shape where that can be measured is, I think, the preparation available to us now.

## Sources

- [Anthropic, "Introducing Claude Opus 4.6"](https://www.anthropic.com/news/claude-opus-4-6) (primary source for the $5/$25 launch pricing)
- [Claude Platform Docs, "Pricing"](https://platform.claude.com/docs/en/about-claude/pricing) (current prices as of 2026-08-13)
- [Anki Manual, "Card Generation"](https://docs.ankiweb.net/templates/generation.html) (standard note type names)
- [PyMuPDF, "Pixmap"](https://pymupdf.readthedocs.io/en/latest/pixmap.html) (Pixmap constructor spec)

## Related links

- [pdf2anki v0.3.1](https://github.com/shimo4228/pdf2anki/releases/tag/v0.3.1): the release containing these fixes ([fix commit](https://github.com/shimo4228/pdf2anki/commit/d9ddc44) / [before/after diff](https://github.com/shimo4228/pdf2anki/compare/v0.3.0...v0.3.1))
- [codex-review](https://github.com/shimo4228/codex-review): the Claude Code skill that calls the Codex CLI as a cross-model reviewer
- [I built a skill for easy Codex reviews from Claude Code](https://dev.to/shimo4228/i-built-a-skill-for-easy-codex-reviews-from-claude-code-4h89): the previous article, with the design intent
- ECC journey series: [part 1 (the 10-day implementation)](https://dev.to/shimo4228/a-beginners-first-10-days-of-real-development-with-ecc-23k4) / [part 2 (the 6 defenses)](https://dev.to/shimo4228/never-trust-llm-output-6-defenses-from-building-a-pdf-to-anki-cli-43mo) / [part 3 (skill sprawl and stocktakes)](https://dev.to/shimo4228/15-days-of-skill-sprawl-in-claude-code-lessons-from-3-audits-27em)
- [github.com/shimo4228](https://github.com/shimo4228): my other tools and repositories
