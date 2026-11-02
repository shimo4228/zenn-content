---
title: "Auditing My Claude Code Harness: 192 Items, One Report, Two Decisions"
emoji: "🧹"
type: "tech"
topics: ["claudecode", "agentskills", "harness", "claude"]
published: true
description: "I merged seven harness audit tools I had built one by one into a single Claude Code plugin, harness-stocktake. The parts judge; I approve and apply once. On my own harness, 192 items and 74 non-Keep verdicts came down to two decisions. It runs after /doctor, not instead of it."
tags: claudecode, agentskills, harness, claude
---

A skill I wrote a while ago calls a script that no longer exists. A rule and a skill say the same thing in different words. CLAUDE.md lists a command I deleted. Left alone, a Claude Code harness (skills, rules, agents, hooks, CLAUDE.md) goes stale like this. Every one of these was correct when it was written.

I see the harness as the place where the owner's thinking comes out through the agent. So I think an untidy harness is close to an untidy mind.

This post is the record of publishing harness-stocktake, a tool that runs that cleanup in one pass. It is not a new idea. Over the past six months or so I polished the audit parts one at a time, and then noticed they could be merged.

## I polished the parts one at a time

The first part was `skill-stocktake`, an audit for skills. I built it in February 2026, [wrote about it](https://dev.to/shimo4228/offloading-ais-weak-spots-to-shell-scripts-designing-building-and-publishing-a-skill-audit-2ll8), and sent a PR to the community skill collection [ECC (Everything Claude Code)](https://github.com/affaan-m/everything-claude-code), and it was merged. Later, `rules-distill`, which distills rules out of skills, was merged into ECC as well. Locally I kept adding, until there were seven parts: `skill-stocktake` for skills, `rules-stocktake` for rules, `rules-distill` for finding rule candidates, `agent-stocktake` for agents, `hook-stocktake` for hooks, `context-sync` for bringing descriptions such as CLAUDE.md and README back in line with what actually exists, and `repo-asset-stocktake` for repo settings and scripts.

Each one got better. The harness as a whole did not get clean. The parts ran separately, and each asked me to decide one item at a time. On October 31, 2026, I wrote:

> skill-stocktake asks me to decide each item one by one, so it's hard to approve in bulk

Asking one item at a time was a design choice: it kept me from bulk-approving without looking at the contents. I had copied that design into all seven parts, so the number of decisions grew with the number of parts and the number of items.

## The parts judge; approving and applying happen in one place

The merge was a change in how the work is divided. The seven parts handle everything up to the verdict. A verdict is one of Keep, Improve (make the content better), Update (bring stale references in line with what exists), Merge (combine), or Retire. Approving and applying are handed to a single procedure in harness-stocktake.

1. The seven parts judge in parallel, and the results are collected into one report. Each item gets one line: verdict, target file, reason, and the concrete change
2. I read the report, rewrite only the lines I want changed, and approve once
3. The approved changes are applied to a working branch, and a completion report comes out
4. I look at the completion report and merge into main

Asking one item at a time existed to prevent approving without reading. With a single approval, what prevents that is not the count but how the report is written. Each line carries enough reason to decide without opening the file, and the lines with the biggest impact (Retire) come first. Here is one line from a report, shortened. It comes from the sample harness in the plugin's repo, which anyone can open and check:

| Verdict | Target | Reason |
|---|---|---|
| Retire (alternative: Improve) | `.claude/hooks/check-secrets.sh` | `settings.json`'s PostToolUse calls this script on every Bash call, but the file is not in the repo. Every call ends in a hook error, and no secret check actually runs |

Putting everything on one sheet also made conflicts across parts visible: retiring one skill breaks a reference from some rule, for example.

The same day, I ran the first pass on my own harness. The seven parts produced 192 items, 74 of them non-Keep. I made two decisions: approving the report, and merging after reading the completion report. When I say "cleaned up" in this post, I mean up to the point where the approved changes were applied and landed in main. I have run it only this once.

## I ran it on 20 public harnesses

With only my own harness, I might just be looking at my own habits of making a mess. So I cloned 20 public harnesses locally and ran it in read-only mode (`--dry-run`). The selection: one GitHub code search (`filename:SKILL.md path:.claude/skills`) returned 662 repos; I shuffled them with a fixed seed and took the first 20 that were not forks, had been updated within 90 days, and had at least five skills. I did not contact the owners, and I'm not naming the repos.

In each of three areas, 19 of the 20 got at least one non-Keep verdict: docs (CLAUDE.md, README, and ADRs, the records of design decisions), skills, and repo settings and scripts. For rules, it was 2 of the 20.

Non-Keep includes not only Retire and Merge but also Improve and Update proposals. The judge was also Claude, not the owners. So these numbers count candidates for fixes; they do not confirm defects that need fixing. The 20 came from a single search and do not represent Claude Code harnesses as a whole. And what I ran was a pre-release version.

## Run it after `/doctor`

Claude Code ships with `/doctor`, which lists unused plugins, unused skills, and slow hooks; `/doctor prompt-audit`, which lists stale or contradictory instructions; and `/skill-doctor`, which measures each skill's resident cost. harness-stocktake looks at content across files: a rule that contradicts a skill, a hook whose script is gone, an ADR that no longer matches the code, two agents that do the same job.

When I ran both on my harness and compared, each caught things the other did not. They also disagreed in places. One example: for a skill I hadn't used in 10 days, `/doctor` recommended turning it off, while harness-stocktake read its content and judged Keep. Looking at how often something is used and looking at what it says give different answers. So I'm releasing it not as a replacement for `/doctor`, but as a tool to run after `/doctor`.

## Try it

```bash
claude plugin install harness-stocktake --marketplace shimo4228/harness-stocktake
```

Open Claude Code and type `/harness-stocktake:harness-stocktake --dry-run`. It reads `~/.claude` and writes one Markdown report. It changes no files. To look at a repo's `.claude/`, add `--project <path to the repo>`. To run it monthly on a repo, there is also a [GitHub Action](https://github.com/marketplace/actions/harness-stocktake).

## What I decided, and what I didn't

I bundled the seven parts into one plugin, and also released a GitHub Action for keeping it running on a repo. I ran the public harnesses locally, did not contact the owners, and published only the aggregates. There is no mechanism that sends usage data (telemetry).

I split the procedure for growing an agent's knowledge into six phases and call it AKC (Agent Knowledge Cycle). harness-stocktake runs one of them: Curate, the phase that finds duplicates, stale items, and items that never fire.

Some things I haven't settled. I compared against `/doctor` only on my own harness, not on the 20 public ones. Checking whether the verdicts match what is actually in the repo was also done by Claude-family models, not by the owners. Harnesses distributed as plugins are not among the 20. And I haven't yet measured whether the agent behaves better after the fixes.

I think keeping a harness clean is close to keeping your own thinking in order. What I changed is how that tidying gets done: from one decision per item to one report and two decisions.

## Related links

- [harness-stocktake (GitHub)](https://github.com/shimo4228/harness-stocktake) — the plugin itself, with the sample harness and the report it produced
- [harness-stocktake-action (GitHub Marketplace)](https://github.com/marketplace/actions/harness-stocktake) — a GitHub Action for running it monthly on a repo
- [Offloading AI's Weak Spots to Shell Scripts — Designing, Building, and Publishing a Skill Audit Command](https://dev.to/shimo4228/offloading-ais-weak-spots-to-shell-scripts-designing-building-and-publishing-a-skill-audit-2ll8) — the record of the first part, skill-stocktake
- [I Found the Shortest Route to Ship My Claude Code Skills to 57,000 Developers](https://dev.to/shimo4228/i-found-the-shortest-route-to-ship-my-claude-code-skills-to-57000-developers-4g43) — the record of sending the PR to ECC
- [Agent Knowledge Cycle (DOI)](https://doi.org/10.5281/zenodo.19200726) — the six phases, including Curate
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles-en/harness-stocktake-after-doctor.md) — every article's Markdown and the index (docs/PUBLICATIONS.md) live in the same repository
- [The author's GitHub](https://github.com/shimo4228) — research repositories with DOIs

---

**How this was written:** Claude (Claude Code) wrote the prose and translated it into English. It worked from the records of my harness audit, the aggregates from running it locally on 20 public harnesses, my earlier articles, and conversations with me. I decided to treat the harness as an outlet for thinking, the storyline of merging parts I had polished, and to limit the numbers in the text to 192 items and two decisions. I read the full Japanese original before publishing, and I am responsible for the content of both versions.
