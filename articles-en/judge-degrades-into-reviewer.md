---
title: "My KPIs Improved. I Deleted My Homegrown LLM Judge Anyway"
emoji: "⚖️"
type: "tech"
topics: ["claudecode", "llm", "evaluation", "agents"]
published: true
description: "I ran two LLM judges in my writing harness for 11 days. I backtested one against 67 past articles, calibrated it four times, and drove my KPI from 6 findings to 0. Then I deleted 1,151 lines of it. None of the three reasons was accuracy — both judges called themselves judges while behaving like reviewers. Here is how to tell the difference in three questions."
tags: claudecode, llm, evaluation, agents
---

If you have built your own LLM judge, try to recall one thing. **When did that judge's verdict last actually change where a piece of work went?**

For 11 days in August I ran my writing harness with two judges bolted on: one that evaluated the theme, and one that evaluated the finished draft.

I backtested the theme-side judge against 67 past articles and tuned its criteria four times. The KPI — the number of findings I still discovered myself *after* the judge had passed a draft — fell from 6 to 0.

The numbers were getting better. I deleted 1,151 lines of that layer anyway.

The reason was not accuracy. It was that **both of them called themselves judges while, in practice, being reviewers.** This article is about how to tell those apart.

## Scope

- This is for people who have built their own "let an LLM evaluate the work and decide pass / no-pass" machinery
- The concrete case is my article-writing harness (Claude Code + subagents). I have not verified whether the same holds when the thing being judged is code or documentation
- Every number is measured in my own repository, over 2026-07-27 to 2026-08-23 (the runtime, per the last recorded session, was Claude Code 2.1.24x)

## If passing guarantees nothing, it is not a gate

First, what I built.

`theme-eval` ran before writing. It looked at the strength of a theme across 8 dimensions and returned one of three values: `Likely-Write-A / Likely-Write-B / Deepen`. `article-judge` ran on the finished draft. It stacked up binary checks and returned `Publishable / Fix / Rewrite`.

At design time I made one deliberate choice. **I gave `theme-eval` no Drop verdict.**

The reasoning survives in the documentation from back then. Someone writing 2-3 pieces a week does not have a strong theme on hand at all times. Make it a rejection gate and the writing stops.

So I chose "deepen it even if it's weak, and if it doesn't rise, write it anyway knowing the ceiling."

I still think that choice was right. The problem is what came next.

A judge that cannot say Drop always lands on "go ahead and write it," whatever else it returns. And in fact, both articles that went through `theme-eval` ended up at `Likely-Write-A`. **There is not a single record of a verdict changing where an article went.**

What was working was never the verdict. It was the deepening questions attached to `Deepen`, and the conversation with me that those questions started.

An essay of mine on desire went two levels deeper on its central question through exactly that conversation. The substance was the pre-writing deepening dialogue; the verdict was a garnish.

The other one, `article-judge`, was the same. Here is the entire track record — three articles.

| Article | Judge verdict | What happened next |
|---|---|---|
| #1 | Fix on the first pass → revised → Publishable | No further findings in my read-through |
| #2 | Publishable | **My read-through found 3** |
| #3 | Publishable (passed twice) | **A different model's review (codex) caught 2 inconsistencies with the source material** |

Two out of three shipped defects *after* passing.

Missing something outside your declared coverage is normal for a gate. The problem was what it missed. The 3 I found in #2 — an unresolved referent, a false dichotomy, a seam left showing — were **the exact items the judge had declared it would check for.**

A gate earns its keep because, for the checks it declares, passing is a guarantee. If that stops being a guarantee, what comes back is just findings. Which is to say: a reviewer.

And judged as a reviewer, neither of these two had a single strength my existing reviewers lacked.

## The KPIs improved. None of my three reasons was accuracy

This is the part I most want to land.

On the numbers alone, the layer was working.

| Metric | Value |
|---|---|
| Theme-judgment backtest | 67 past articles, judged blind to their recorded rank, then reconciled |
| Top-rank recall | 88% (22/25) |
| Bottom-rank separation | 80% (8/10) |
| Read-through findings (the KPI) | 6 → **0** |
| Criteria calibrations | 4 |

Normally that is where you conclude the thing is on track. On August 21, that is exactly what I thought.

Two days later I tore it out. There were three reasons, and **none of them was about accuracy.**

### Reason 1: the reconciliation cost did not come from the number of evaluators

I had been feeling that "there are more things doing evaluation now and the process has gotten complicated," so my first instinct was to reduce the count. But when I actually counted, I had 4 reviewers and almost no reconciliation work coming from them.

The difference was where things lived.

| | Where the criteria live | Files touched per change |
|---|---|---|
| Reviewers (clarity / fact-check, etc.) | Closed inside **one** agent file | 1 |
| Judges (`theme-eval` / `article-judge`) | Skill + checklist + code + loop section + gate conditions | **5** |

For a reviewer, the criteria are self-contained inside its agent file. So adding more of them does not grow the reconciliation cost linearly. For the judges, the question set was in a separate file, the mechanical checks were in code, the re-judgment retry limit was in the orchestrator's skill, and the publication-blocking conditions were in the gate's skill.

On the morning I dismantled it, I pushed 3 commits doing nothing but internally reconciling this one subsystem. **I was spending a session on the internal consistency of an asset with exactly one consumer.**

The "too many evaluators" feeling was not about count. It was about scatter.

### Reason 2: the question set collided head-on with my own writing conventions

I had built the fixed question set the judge used by distilling it from external writing-craft articles. I thought of it as "genre-neutral craft principles."

When I checked it against my conventions, it collided in 3 places.

- **"Commit to a claim, don't hide behind both-sides framing"** ⇄ my essay conventions call for the interrogative form, "isn't it the case that…". The judge hammers that as hedging
- **"Don't end on a cheap N-step summary"** ⇄ for a practical article, a committed list of steps is the legitimate conclusion
- **"Open on a concrete scene"** ⇄ for a practical article, the first screen is required to hand over "what is this" first

The cause was plain: the question set **had no concept of a channel.** My writing conventions branch on voice depending on whether a piece is going to Zenn or to note. Import single-channel principles wholesale and they will always beat up one of the branches.

Here is the part that stung most. When I introduced the judge, I wrote in the risk section that "voice converges on the judge's preferences (flattening)," and I placed voice regression tests and a different-model review as the countermeasures.

**That risk was not a future hazard to be mitigated. It was already baked into the question set as structure.**

### Reason 3: raising the bar pinned the standard to the past

There was one more side effect, in the process of tightening how strict the judgment was.

In the first backtest, the top rank came up 43% of the time. "If a third of everything is top-rank, this isn't strict at all," I thought, and tightened.

| Iteration | Change | Top-rank rate |
|---|---|---|
| 1st | Reconcile against the recorded ranks | 43% |
| 2nd | Add mandatory conditions; downgrade when in doubt | 27% (18/67) |
| 3rd | Pairwise comparison against my 2 strongest articles as anchors | **6% (4/67)** |

Down to 6%. As strictness goes, that is unimpeachable.

But I removed the 3rd iteration immediately after adopting it. **Because using past articles as the standard pins the ceiling to the past.**

The easiest way to make a judgment stricter is to make something already good into your yardstick. But put the yardstick in the past and the upper bound settles near the past's level too.

At least in my setup, the move that raises strictness and the requirement to keep the standard open forward collided at exactly this point.

Incidentally, when I looked at the articles that outperformed, the picture that emerged was that the judge's sense of "top rank" tracked reader metrics (likes, views) fairly closely, and my own criteria were stricter than that. I aligned the criteria to my side. The measured numbers are designed to sit alongside as a separate axis.

## The verifier was not what was moving. I was

Everything so far has been about where criteria live. There is one more reason, further down. I only noticed it after I finished writing.

The first time I felt I could not build a judge was actually August 6, 17 days before I dismantled this. I was trying to build an eval on a different project, and I said this:

> The verifier gets updated right away and the implementation gets updated right away, so I can't hold a baseline

That "verifier" is what I have been calling a judge up to here.

At that point I had two moving things sitting side by side: the implementation, and its verifier. That the implementation moves was, in this field, a given.

In the same session I said one more thing:

> That's my dislike of benchmarks showing through. I don't keep scores, so I can't compare over time

So half of me already knew this was about me. I just filed it under "preference."

What the next 17 days taught me is that it was not preference, it was structure. **The verifier's contents are me, and I move.**

How I judge whether an article is good changes the more I write.

In fact, over the course of tightening the criteria, I changed my mind to "the top rank should not be a third of everything," and then changed it again to "using past articles as the yardstick pins the ceiling to the past." **The very work of tightening the criteria was moving my judgment about the criteria.**

A judge cannot track that movement. What a judge executes is a question set written by an earlier version of me.

However far my judgment has moved on, the judge is that far out of date. And rewriting the question set moves my judgment forward again.

I had written down the same mechanism back in June, in a different context: "intent has no verifier outside the operator, and it moves as the operator's judgment sharpens," and "any automated intent-check would have to freeze intent into a stated criterion; a frozen criterion is a specification, and checking against a specification is correctness work" — so "the automatable part of intent alignment reduces, piece by piece, to correctness work" (*[Harness Alignment and Harness Drift](https://doi.org/10.5281/zenodo.20578272)*, 2026-06).

I should confess, though, that there is no record of me consulting that text when I built the judge. It appears nowhere in the design decisions. I noticed the resemblance after I had torn it out.

**A mechanism I had articulated myself did not reach the version of me doing a different piece of work.** And because the KPI was improving, it was that much harder to notice.

"Correctness" can be automated, because the verifier lives outside you. Whether the tests pass is decided independently of my mood.

"Intent" has no verifier outside. I am the judge, and I move.

Only the former can be loaded onto a judge. What I was trying to load was the latter.

## The one that survived did so because nobody else was watching that layer

Here is the shape after the dismantling.

```
Before writing   theme-reviewer (agent)  ← no verdict. Findings and deepening questions only
Finished draft   4 reviewers + the author's read-through
Before posting   title-eval (skill)      ← the one judge I kept at this point
```

Counting the title judge I had added on August 13, there were three. That became one. The one I kept looks at titles.

The deciding criterion was not "does this need strictness." It was **is there anybody else already watching this layer.**

The body already has 4 reviewers running on it, and I read it through at the end. Adding a judge just adds one more mouth returning findings.

Titles, on the other hand, had nobody. So I kept it.

But that is a weak reason. Whether a title is good is not a question settled by evidence either, so this judge can degrade the same way. The mechanism from the previous section applies to it unchanged.

**"Nobody else is here" is not a guarantee that a judge works properly. It is an argument by elimination — that deleting it would leave nothing behind.** The next time my read-through findings go up, this is the first suspect.

:::message
**Addendum (the night of the day I wrote this)**: I deleted that one too.

The trigger was running this very draft through the title judge. What came back was a recommendation of `Adopt / Refine / Keep current`, and the final choice was, as always, mine. **Let a layer whose resolution lives inside you call itself a judge, and you stay in a state where you think you are measuring the judge's performance.** The same shape I described in the body for the theme judge.

I replaced it with `title-reviewer`, which returns findings only, and kept the adopt-or-not with me. Judges: zero.

I wrote the paragraph above as a forecast. It did not get a single day of grace.
:::

As for `theme-eval`, I replaced it with an agent. The dimensions carried over unchanged. What I dropped was the verdict and the rank.

```diff
- theme-eval (skill)
-   verdict = Likely-Write-A / Likely-Write-B / Deepen
-   treats the theme rank as a ceiling on article quality
+ theme-reviewer (agent)
+   returns findings and deepening questions only
+   deepen it / write it knowing the ceiling / drop it — the author decides
```

The dialogue was what was working, so I kept just the dialogue.

## Diagnose your own judge in three questions

If you are torn between keeping and killing a judge you built, work through these three in order. **This is not a definition of "does it qualify as a judge" — it is a practical check on whether it is worth keeping.** I articulated it after the fact, and each one takes minutes to answer.

| # | Question | Yes (working as a judge) | No (degraded into a reviewer) |
|---|---|---|---|
| 1 | Is the judge **designed to be able to reject** | It can | It can't → passing becomes the default path, and the verdict is decoration |
| 2 | Is there an actual record of a verdict **changing where the work went** | There is | Zero → what's working is the accompanying findings, not the verdict |
| 3 | Is **somebody else already watching** that layer | Nobody → you have grounds to keep it | Somebody is → adding the same dimensions as a reviewer is cheaper |

If all three land on the No side, I think it is worth considering dropping the "judge" name and turning it back into a reviewer. Drop the verdict, keep only the findings, and you can fold the criteria back into one file. You don't have to throw the dimensions away.

Then measure the maintenance side too.

```bash
# How many files are this judge's criteria scattered across right now?
# The count grows when the question set, mechanical checks, loop control,
# and gate conditions each live in a different file
grep -rl "article-judge" . --include="*.md" --include="*.py" | wc -l
#=> 5

grep -rl "zenn-clarity-reviewer" . --include="*.md" --include="*.py" | wc -l
#=> 1
```

Swap `article-judge` for your own judge's name and `zenn-clarity-reviewer` for a reviewer you want to compare against. **That 5-to-1 is the measured value of the "scatter" from Reason 1.**

It only counts name strings, so it misses code that references the thing solely through imports. Treat it as a lower-bound estimate.

:::details I did not stop judging everything
The publication-blocking conditions are still there. Two of them: a specific reviewer must report 0 CRITICALs, and the first-contact-reader clarity review must PASS.

What I cut was only the "have an LLM render an overall verdict and use that verdict as the gate" layer. Individual blocking conditions based on reviewer findings stayed as they were.
:::

:::details On the initial accuracy of the mechanical checks
I threw out the deterministic mechanical checks (banned words, paragraph density, syntactic pattern detection) at the same time. 521 lines of code and 277 lines of tests.

On its first run, the rule-of-three detector hit 20 times with 0 true positives. It was a comma-based heuristic; I later redesigned it as structural detection. On the other items, all 8 hits were intentional fragments that were within convention.

The judge rejected them on sight, so no real harm was done. But the implementation cost of the premise that "bolting on a deterministic layer plugs the LLM's leniency" was all sitting right here.
:::

## When this doesn't apply

To be honest about it: this is one repository over 27 days.

What I was judging were questions like "is this theme worth writing" and "is this draft ready to publish" — **questions with no single determinate answer.**

Let me get the causality right here. Dropping Drop was not a necessary consequence of the question's nature; it was my design decision to keep the writing from stalling. You can absolutely set rejection criteria as an operating policy for subjective questions too.

What was doing the work is what comes after. Because the answer is not determinate, even with rejection criteria in place the substance comes down to my taste.

And my taste moves. So the judgment can't be pinned down, and what remains is findings.

Questions that do have determinate answers — do the tests pass, do the types check, does each reference correspond one-to-one with the body — are a different story. There a judge functions in the proper sense of the word. I have kept the check that reconciles citations against references.

The line I'd draw is whether the question **can be settled by evidence**. If it can't, my conclusion this time is that placing a judge there only defers the human judgment.

One more thing: this conclusion rides on an operating practice where the author always does a final read-through.

If I start skipping the read-through, the grounds for bringing automated judgment back come alive again. Same if the publishing pace goes past 5 pieces a week and human read-through becomes the bottleneck.

## Takeaways

Don't decide whether to kill a judge based on accuracy.

In my case the KPIs were improving. It passed the backtest, and it had been through four rounds of calibration. If I had judged on the numbers, this layer would still be there.

What I should have been looking at was one thing: is there a record of a verdict actually changing something. If it's zero, what's working is not the verdict.

To be fair, adding more eyes is not a bad thing in itself. In my case, a different model's review found 2 defects in a draft that had passed a judge twice.

**The problem was adding it under the name "judge."** That scatters the criteria across 5 files. Had I added the same dimensions as a reviewer, one file would have done it.

The mechanism underneath is this. What fits into an automated check is only "correctness" — the kind that has a verifier outside you.

Try to load "is this good enough" onto it, and since the only verifier is yourself, the judge becomes a frozen copy of an earlier you. And the act of adjusting the criteria itself moves your judgment about the criteria forward. It's a structure that can't catch up.

"The metrics are improving" and "this machinery is worth maintaining" were different questions. The judge was only measuring the first one.

## Related links

- [LLM-as-Judge Shouldn't Aggregate Scores: Binary Checks as Evidence, One Holistic Verdict](https://dev.to/shimo4228/llm-as-judge-shouldnt-aggregate-scores-binary-checks-as-evidence-one-holistic-verdict-822) — the piece where I designed the very verdict format I threw out here
- [Harness Alignment and Harness Drift: Why Intent, Unlike Correctness, Resists Automation](https://doi.org/10.5281/zenodo.20578272) — my own paper quoted in the body (2026-06, CC BY 4.0)
- [github.com/shimo4228](https://github.com/shimo4228) — the repositories, including the writing harness
