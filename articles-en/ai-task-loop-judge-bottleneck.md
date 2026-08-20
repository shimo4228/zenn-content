---
title: "I Handed 41 Tasks to an AI Loop. The Bottleneck Was Judgment, Not Code"
emoji: "🔁"
type: "tech"
topics: ["claudecode", "aiagents", "automation", "agenticcoding"]
published: true
description: "One week of running a judge/build/human AI task loop over 41 stale tasks: 10 closed without writing code, one unattended cycle, and exactly one decision that reached a human. Field notes, n=1."
tags: claudecode, aiagents, automation, agenticcoding
---

Is there a region at the bottom of your task ledger you haven't scrolled to in weeks?

Mine held 41 tasks across two repositories. I use AI agents every day, and yet the ledger never shrank.

One morning I ran my homegrown "list the tasks that are ready to start" command. The answer was empty.

```bash
python3 ~/.claude/scripts/claims.py ready
# (no output)
```

Forty-one tasks, and zero of them ready to hand to an implementation session. Implementation capacity was sitting idle. The bottleneck was judgment.

This article is a field report from one week of processing those 41 tasks with an AI loop split into three roles: judge, build, and human. By the end, you should be able to tell where your own ledger is actually stuck — and what to design first if you want to run an unattended loop.

:::message
This is a record of two repositories, one week, one person (n=1). Every number comes from logs and commits; generalize only within that range.
:::

## Tasks start rotting the moment you write them

The day before I built the loop, I hand-dispatched 7 tasks to implementation sessions as a trial.

Two of the 7 had premises that had already collapsed by the time work started. A spec they depended on had changed, or the problem itself had been dissolved by some other change.

A ledger's "someday" entries assume the world as it was at write time. A task that sat for a few weeks needs a re-judgment — "is this still worth doing?" — before anyone implements it.

In other words, processing a ledger has a judgment layer that comes before implementation. If your automation design skips it, the AI will stack correct code on top of rotten premises.

## What I built: a role split, and plumbing

I did two things. First I split task processing into three roles; then I laid the plumbing to run them unattended.

The role split:

| Role | Who | Concretely |
|---|---|---|
| Judge | A resident session on a stronger model (one tier above the build side). One per repository | Re-judges every task in the ledger and dispatches only the ones still alive |
| Build | A fresh session spawned per task | Implements exactly one task on a git worktree. Never touches main |
| Human | Me | Final approval on merge, drop, and filing only. The last switch |

No pull requests. Build sessions just stack commits on a task branch.

Acceptance is done by the judge session — `git diff --stat` plus re-running the tests — and once the human approves, it fast-forward merges. The list of unmerged branches doubles as the acceptance queue.

```bash
git branch --no-merged main   # unmerged = acceptance queue (the PR substitute)
git merge --ff-only task/<name>   # only after the human says "merge"
```

For a one-person operation, PR review UIs and merge buttons were overkill. Branches plus ff-only merges are enough to build the structure where a human checks last.

## Measured: 10 tasks closed before any code was written

Here is the balance sheet from the first full day with all three roles running (separate from the 7-task trial the day before; operation at this point was still manual — unattended mode comes later).

- Open tasks went from 41 to 22 across the two repositories (13 → 5 and 28 → 17)
- 27 tasks closed, 13 merges (the two are not 1-to-1 — some merges were docs-only, some tasks closed with no merge at all)
- 6 new tasks were filed during the cycle (each filing approved by the human on the spot)

For the arithmetic-minded: 2 of the 27 closed tasks belonged to an adjacent repository, fixed in passing, so they sit outside the 41. That gives 41 − 25 + 6 = 22, and the books balance.

What stands out in the 27 is the share closed without writing code.

The judgment pass alone — before anything was dispatched to implementation — closed 6 tasks through decisions and withdrawals. Read-only investigation sessions closed 4 more.

The judgment pass also repaired the ledger in ways other than closing. Three tasks sat marked blocked even though their dependency had completed weeks earlier; one had a resume condition that structurally could never fire.

All of them moved forward with nothing but a state correction.

A ledger shrinks through judgment before it shrinks through implementation. If your tasks look piled up, the first suspect may not be a shortage of implementation capacity — it may be that this re-judgment is nobody's job.

To be clear, the build side worked too: 14 implementation sessions (pilot included) ran in one day under a parallelism cap of 3, producing the 13 merges.

What was missing was not implementation muscle but the layer that judges tasks into a dispatchable shape. That is how to read these numbers.

## Write the briefing as a hypothesis

The briefing document I hand to each build session (I call it a kickoff packet) failed me twice.

**First: every packet I wrote on day one was wrong somewhere.** A premise that was only half true, or a prescribed fix that wouldn't actually close the hole.

The countermeasure was to put "Phase 0: re-verify the premises. If falsified, stop and report instead of implementing" at the top of every packet. I stopped writing packets as orders and started writing them as hypotheses.

The same sessions then began producing correct results from incorrect instructions. And having them report the falsifications they found feeds material back to the judge.

**Second: when I enumerated the review steps in a packet, an omission was read as permission to skip.** One build session did skip the simplification review — the one step I hadn't listed.

The fix: stop enumerating steps, reference the conventions instead, and state explicitly that "anything not written in this packet defaults to the conventions."

The specifics you write into a delegation document get read as exemptions for the ones you didn't. At least this build session interpreted the list that way.

## Unattended loops die quietly

Everything so far was manual operation. Next came unattended mode — and my first design failed.

Claude Code can schedule recurring runs inside a session, and that is what I reached for first. But an in-session timer shares its fate with the session.

A restart, a tool update, the session's own lifespan — any of them stops it, and nothing on the outside can detect that it stopped.

A loop that fails loudly is manageable. A loop nobody notices has stopped is the dangerous one. So I settled on this design principle:

**Timers live outside the session. Judgment lives inside. And the human's answers arrive only inside the session too.**

Concretely, macOS launchd (the OS-native cron equivalent) fires a small shell script every few days.

This script (I call it the tick) never reads the ledger. Its entire job:

```bash
# tick's job: find a live judge session; if none, spawn one; then request one cycle
# (the real thing is ~/.claude/scripts/triage-tick.sh; excerpted to the essentials)
if ! find_live_triage_session; then
  spawn_session && rename_to_fixed_name
fi
# digest = the report the judge session sends the human at the end of a cycle
# (the Slack notification in the next section)
send_prompt "Unattended triage cycle. Go as far as the digest.
Do not merge, publish, or touch rules / hooks / security gates.
File nothing and drop nothing on your own."
```

The intelligence stays in the session; the tick only checks for a pulse and wakes it up. Keeping the plumbing dumb is a deliberate choice — fewer parts that can break. (Durability itself is what the upcoming scheduled runs will test.)

### The liveness signal: no report is itself the alarm

An unattended cycle sends two kinds of Slack messages: one notification per item that needs a human decision, and a single liveness line that is always sent at the end of the cycle.

> .claude triage cycle done: 1 decision pending (…)

If the scheduled time passes and that line doesn't arrive, something in the loop is dead.

Converting silence into an anomaly signal — that turned out to be the real substance of going unattended.

Slack, however, is one-way here. Treating replies as human answers would open impersonation and misreading paths, so answers like "merge" are accepted only at the judge session's own screen.

In fact, on day one the judge session nearly misread a suggestion Claude Code had auto-inserted into its input box as a human instruction. Deciding which single channel carries the human's words is worth settling before you go unattended.

## The biggest hole the loop found was outside the ledger

The first cycle produced a discovery I hadn't planned for.

My environment has machine gates that run on every commit (secret scanning and the like). The gate keeps a human-approved list of scripts allowed to run unattended — and that list had gone stale 2.5 weeks earlier. **The gate had been quietly dormant.**

Nobody had noticed.

A gate that fails red at least gets noticed. A quietly dormant gate keeps waving things through while pretending to be green.

Only after building the unattended loop did I see that "is the loop alive" and "are the verification devices the loop relies on alive" are the same problem.

Addy Osmani, in [Loop Engineering](https://addyo.substack.com/p/loop-engineering) (June 2026), points at the leniency of letting the model that wrote the code grade itself, and at human verification throughput as the ceiling on parallelism. This week traced both points on the ground.

I would add one thing: the verification devices themselves belonged on the watch list. Osmani's "done is a claim, not a proof" applies to gates too.

## What I still don't know

Honestly: this system has only been verified up to the entrance.

- Each repository has run exactly one unattended cycle (manually triggered). A natural launchd firing at the scheduled time has not yet been observed as of this writing
- The first unattended cycle's content was: all 4 blocked tasks re-checked, none had fired, 0 dispatched to implementation, 1 item waiting on a human. Unglamorous — but correctly doing nothing, and correctly reporting it, in a week with nothing to dispatch was itself a checklist item
- While Slack is down, the liveness signal goes silent with it. The single point of failure in the alarm channel is unsolved

## In one week, exactly one decision reached the human

As of this writing, open tasks stand at 22 across the same two repositories (2 ready, 1 awaiting a decision, 19 waiting on conditions). That is the result of 25 closed and 6 newly filed over the week.

And the first unattended cycle delivered exactly one decision request to the human.

Before automating, my job was to stare at tasks, remember them, start one, and get interrupted by another. Now my job is to answer the one message that arrives.

Implementation can be delegated. Most judgment can be delegated too.

What remains at the end are short words: "may I merge this?" and "can we stop doing this one?"

Your 41 tasks are probably not waiting on implementation either, for the most part. Open just one — the oldest blocked task — and check whether its dependency is still alive.

Build the loop later if you like; the size of the discovery won't change.

## Porting this to your environment (for your coding agent)

This system depends on my local environment (macOS, launchd, homegrown session tooling), so copying the steps won't transplant it. If you want to try it, paste the following into your coding agent as-is, and have it do read-only investigation and planning first.

```text
Draft a plan to apply this article's design to my environment. Do not implement yet.

Preliminary investigation (read-only):
1. Survey my current task tracking (files, tools, task count, last updated)
2. Identify the OS-native mechanism available for unattended scheduled runs
   (launchd / systemd timer / Task Scheduler, etc.)
3. Check whether a notification channel (Slack or similar) is available for sending

The plan must include:
- A structure that separates judgment (task re-triage) and implementation
  into different sessions/processes
- Wiring that places the timer outside any interactive session
- A one-line liveness signal at the end of each cycle, and a way to detect its absence
- The boundary of what the unattended side must NOT do
  (no merging, no publishing, no config changes)

Present the plan and get my approval before proceeding to implementation.
```

## Related links

- [Addy Osmani, "Loop Engineering"](https://addyo.substack.com/p/loop-engineering) (prior art on separating the writer role from the verifier role, and on human verification bandwidth as the ceiling on parallelism)
- [My GitHub](https://github.com/shimo4228) (public repositories for the harness pieces mentioned in this article)
