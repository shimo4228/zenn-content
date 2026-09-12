---
title: "Why an 11-Second Burst Never Showed Up in the Log That Gets Read Every Week"
emoji: "🔭"
type: "tech"
topics: ["claudecode", "aiagents", "observability", "logging"]
published: true
description: "I gave every log my agent writes a weekly reader, then found by hand a 13-hit burst in 11 seconds that the reader could not show: 30 random rows out of 4,035 carry 0.1 of it. One row per session and three time axes made the burst surface on its own, and the same choice hid a fault present in every session. Three rules for your own log reader."
tags: claudecode, aiagents, observability, logging
---

On the morning of September 12, 2026, I gave every log my agent writes a weekly reader.

That afternoon, counting the same logs by hand for a different article, I found `GET /home` hit 13 times in the 11 seconds before a session ended. All HTTP 200. The agent was in a loop with nothing left to do, fetching `/home` once a second.

The reader I set up that morning cannot show this. Not bad luck; arithmetic. Draw 30 random rows from the week's 4,035 API log rows, and the expected number of those 13 rows that make it into the sample is 0.1.

Giving a log a reader and shaping it so a fault shows up turned out to be two different jobs. This article is about what became visible once I replaced the way the logs get shown with a form that shows the fault, and what that same replacement made invisible.

## Setup: what is being scored, and what is being logged

The subject is Contemplative Agent, an autonomous AI agent (Python) I am developing. It runs on Moltbook, a social network where agents talk to each other.

How it works is simple. Within a 60-minute session, it scores feed posts for relevance with an LLM, and upvotes or comments on the ones above a threshold. Upvotes and comments had a duplicate check ("never twice on the same post"); scoring did not.

The agent writes its own activity to JSONL logs, one event per line, in 15 files; the API log (one call per line) and the LLM-call log (one call per line) are two of them. Every week, an unattended Claude Code session (the weekly chain, from here on) reads them and writes an observation document.

## Morning: a reader, a sample with no question, and still no burst

What I built that morning was a registry (`REGISTRY`) holding one "weekly question" per log, and a script that reads it and emits a count table and a value distribution for each log. The first stage of the weekly chain reads that output. This was me applying the rule from the previous article: when you build a new instrument, write down who reads it and when.

The part I cared about most was one no-question stage, where nothing is decided in advance. Every existing check in the weekly chain counts a fault shape someone has already imagined. To catch a fault nobody imagined, I figured you need a stage that reads near-raw data with no question attached, so I had it draw 30 random rows from each log and read them.

The sample drops the body field. That field holds post text written by other agents, and feeding it to an unattended LLM session is an entry point for prompt injection.

From here on I call this kind of processing, deciding what part of a log is shown and how, a **projection**.

Even after all of that is read, the 13-row burst does not show. This stage takes up most of what gets read: of the 130,547 bytes and 443 lines the output had for the same week (September 5 to 11, 28 sessions), 96% is sample.

There are two reasons it does not show, and neither is fixable by tuning.

- The count table does not distinguish 13 rows in 11 seconds from 13 rows spread over an hour. The fault's shape is in time, and a count has no time in it
- The sample shows the distribution of rows but erases the **gaps** between them. 13 ÷ 4,035 × 30 ≈ 0.1 rows. Change the seed as many times as you like; it stays invisible

What was missing was a **time axis in the projection**. There was a reader, and there was a no-question stage. A fault shaped like time still does not show in a projection that has no time in it.

## Afternoon: no column that catches a known bug

The cause of the burst was quick to find. A boundary condition in the wait logic: when the remaining time was shorter than the intended wait, the sleep was skipped and the loop spun for the rest of the session (proposal record RFC-0036, fixed the same day).

Before fixing the bug, I decided how to fix the reader. Partway through, I typed this to the agent:

> One thing about scope: in this session I am not thinking about symptomatic fixes that squash a known bug. I want to build something that picks up the anomalies that come next.

Add a column that counts `/home` hits and this burst shows up. But that projection will not show the next unknown fault. Put in a single column or threshold carrying the name `/home`, or keyed to the scoring function, and the projection catches only the faults you already know.

So everything I built into the reader was a shape that carries no known name.

- The unit is the **session**, not the row: one session, one row
- For each category (endpoint for API, caller for LLM), three time-axis columns: count, hits in the busiest minute, minimum gap
- Outliers are decided not by a threshold but by distance from the other 27 sessions in the same week (median and MAD, the median absolute deviation, with a modified z-score of 3.5 or above)

Columns are not declared; they are derived from the data. The columns are the union of this week's categories and the past four weeks', so when a new endpoint appears next week, it gets measured from that week without anyone editing the registry.

Bursts are the one exception; I fold them the way syslog does with `last message repeated N times`: three or more consecutive events in the same category within 2 seconds collapse into one line.

## Something I was not looking for came out on its own

Run the replaced projection over the same week, and the burst I had found by hand comes out with nobody looking for it. It is third in the within-week outliers table. Columns are named `log:category`, so `api-audit:GET /feed` is the API log's `/feed` endpoint.

```text
### Within-week outliers (median / MAD over sessions, |modified z| ≥ 3.5)
|      z | column                            | session   |   value |   median |   MAD |
| 1294.3 | comment-outcomes:reply            | db8ed4e2  |    1919 |        0 |   0   |
|  116.7 | comment-outcomes:reply /1m        | e4a99b6b  |     173 |        0 |   0   |
|  -19.6 | api-audit:GET /feed gap s (log z) | a6eac8ae  |       0 |      148 |  25.5 |
```

It surfaced because "the minimum gap for `GET /feed` is 0 seconds, far from the other sessions' median of 148 seconds." The name `/home` appears nowhere. Once the columns carry a time axis, a burst comes out as a time-axis outlier, nothing more.

The section that lists the minutes around each outlier in time order also showed something I had missed when counting by hand. The second line: `/feed` was being hit 12 times too, alternating with `/home`.

```text
15:59:09 api-audit:GET /home ×13 in 11s
15:59:10 api-audit:GET /feed ×12 in 10s
```

The top two entries were a separate matter. One session wrote 1,265 comment-outcome rows in a single second, cause not yet identified (my guess is a bulk import of past data). This time, the no-question stage I placed that morning did pick up something I had not seen, and it was not the burst.

The amount that gets read went down: from 130,547 bytes to 24,463 bytes, 311 lines. Two runs with the same arguments are byte-identical, and zero fields derive from the body field.

## The same replacement hides a fault that happens every time

This is the part I most wanted to write.

The agent had one more known bug. It did not remember scoring results, so as long as a post stayed in the feed, it re-scored the same post every cycle (RFC-0032).

Scoring has been an LLM call since the first commit on March 8, 2026, and the LLM call log shipped on June 10. The evidence had been on disk since June. The bug was found in a code review on September 12.

In the new projection's session ledger (the one-session-one-row table), this fault shows up as a number: a median of 44.5 scoring calls per session.

But it does not show up as an outlier. All 28 sessions do the same thing, so no session is far from the others. **The moment "different from the other sessions" becomes the definition of a fault, a fault that has happened every time since day one falls outside the definition.**

This is not an oversight; it is the structure of the replacement. The very judgment that made the burst visible, distance from the other sessions in the same week, is what hides the chronic fault. The fault that became visible because I added a time axis and the fault that vanished because I switched to differences are two faces of one decision.

So I wrote the hidden shape into the projection's own output. It appears in the header, the one place that gets read every time:

> A session is compared with the other sessions of this window, so a fault present in every session since it began departs from nothing: that shape belongs to Redundancy and to the reader of the ledger's absolute values (ADR-0110).

ADR-0110 is the Architecture Decision Record for this replacement, one decision per file.

Two things cover the chronic shape. One is the Redundancy section of the output, which counts violations of a written invariant: the same caller with the same normalized prompt does not repeat within a session. The other is the LLM that reads the session ledger's absolute values; whether 44.5 scoring calls per session is too many is for that reader to judge, not a difference to compute.

To be honest, the Redundancy section does not work for this week yet. The normalized prompt digest exists only in rows from September 12 onward, so this week reports 0 repeats. The projection starts covering the chronic shape next week, and the effect of the fix becomes readable in the weekly readings of September 18 and 25.

## Where this decision does not hold

Before you port any of this, the conditions under which it does not hold.

**More shapes shown means the reader grew.** The script went from 616 lines to 1,079 (3 modules), and pandas entered the dev dependencies. What shrank was the output that gets read, not the code I wrote, and the trap from the previous article, where more lines were built for retirement than were removed, can happen here too.

**The calibration values are empirical, added one at a time as simpler shapes failed on real data.** Minimum gap only for categories with 4 or more events; gaps and totals under `log1p`; columns with MAD 0 get a scale floor of one unit of that column. All three were added after a simpler shape failed on real data, and there is no guarantee the same values are right in your environment.

**The price of the floor: a constant column needs a 5.2-unit departure (3.5 × 1.4826, the MAD-to-sigma constant).** If every session calls a category 3 times and one session calls it 0 times, that does not appear as an outlier; it stays as a zero in the session ledger. That is another shape the "shape shown" hides.

**The population is 28, and the unit is fixed-length sessions.** With only a handful of sessions per week, neither median nor MAD means anything, and for a set of services whose request counts differ by orders of magnitude, the right unit will be a different one.

**The chronic side is unverified.** That acute faults show was confirmed on real data from the week before the fix. For chronic faults, I only wrote at design time that they do not show in differences; whether the invariant and the reader pick them up has not been read even once.

## If you want to port this to your own setup

If you have logs read periodically by an LLM or a human, decide three things before building the projection.

**1. Make the unit of a row a unit of work, not a log line.** One row per session, request, or job, and, per category, a count, the busiest minute, and the minimum gap. A random sample of rows shows the distribution but erases gaps and density; a fault shaped like time shows only in the minimum gap or the busiest minute.

**2. The moment you decide the shape shown, write one line about the shape it hides into the output itself.** If you show differences from the other rows in the same window, a fault present in every row will not show. Write it in the header that gets read every time, before the reader has to guess.

**3. Catch the chronic shape with an invariant, not a difference.** Count an invariant you can write down, such as "the same input does not get the same processing twice within a session." A difference only sees change, and something that has been that way from the start is not a change.

Last, the thing I overlooked longest.

The evidence of re-scoring was on disk every day from June 10. The reader arrived on the morning of September 12, and even had that reader been running, it was not shaped to show this fault. Giving a log a reader and shaping it so a fault shows up are two different jobs.

**Building a projection means deciding the shape it shows and the shape it hides at the same time.** Unless you write the hidden shape into the output, the next reader keeps reading without knowing what it is not seeing.

## Supplement: on writing "no registry" in the previous article

In [the previous article](https://dev.to/shimo4228/my-dead-code-scan-returned-zero-then-i-deleted-2063-lines-detectors-measure-references-not-4o4e) I wrote that I would not build a registry of instruments. Two weeks later I built something named `REGISTRY`, so here is what is the same and what is different.

What the previous article rejected was a list managing consumers per instrument. If you cannot answer, about that list itself, who reads it, how many readings close the decision, and when it gets retired, you have only added one more layer of the same problem.

This `REGISTRY` is a set of rows holding each log's weekly question as data. The reader is the weekly unattended session, the editor is me looking at the non-OK rows in the weekly human review, and the removal condition is the retirement of the weekly chain itself; all three are written in the design decision record. The principle was never "build no registry" but "build no instrument whose consumer you cannot name," and the previous article's wording was narrower than the principle.

## Sources and references

- [Google SRE Book, ch.6 Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) — the principle that rules which never fire should be removed. The reason this article's projection has no thresholds
- [Fast and flexible observability with canonical log lines (Stripe)](https://stripe.com/blog/canonical-log-lines) — one request, one line. This article turns that into one session, one line
- [The RED Method (Grafana Labs)](https://grafana.com/blog/the-red-method-how-to-instrument-your-services/) — the idea of giving every category the same axes
- Boris Iglewicz and David Hoaglin, *How to Detect and Handle Outliers* (ASQC, 1993) — the modified z-score and the 3.5 threshold. This article does not adopt their alternative scale for MAD 0; it uses one unit of the column as the floor instead
- [Log Sampling: Techniques, Challenges & Best Practices (groundcover)](https://www.groundcover.com/learn/logging/log-sampling) — the general explanation of how sampling drops rare, short-lived events

## Related links

- [I Cut My AI Review Chain From 6 Stages to 1: Breaking the Loop That Never Hits Zero Findings](https://dev.to/shimo4228/i-cut-my-ai-review-chain-from-6-stages-to-1-breaking-the-loop-that-never-hits-zero-findings-1moi) — three articles back: how I cut the reviews
- [After Cutting My AI Reviews, I Put a Complexity Ceiling in Ruff](https://dev.to/shimo4228/after-cutting-my-ai-reviews-i-put-a-complexity-ceiling-in-ruff-1hho) — two back: output decided by a rule does not grow when you add to it
- [My Dead-Code Scan Returned Zero, Then I Deleted 2,063 Lines: Detectors Measure References, Not Consumption](https://dev.to/shimo4228/my-dead-code-scan-returned-zero-then-i-deleted-2063-lines-detectors-measure-references-not-4o4e) — the previous article: the three items of the consumption plan, and where "no registry" came from
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles-en/log-projection-blind-by-construction.md) — the Markdown for every article, plus the index (docs/PUBLICATIONS.md), lives in the same repository
- [My GitHub](https://github.com/shimo4228) — my research repositories, with DOIs
- [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) — the subject measured in this article. The morning design is ADR-0107, the afternoon replacement is ADR-0110, and the two faults are RFC-0036 and RFC-0032
