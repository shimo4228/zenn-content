---
title: "Banned from Wikidata Overnight — I Believed Every Edit Was Compliant, but All 109 Items Were Deleted as Promotion"
emoji: "🚫"
type: "tech"
topics: ["wikidata", "postmortem", "geo", "claudecode"]
published: true
description: "A postmortem of losing 109 Wikidata items and an account in one night. Every individual edit was believed to be policy-compliant — sourced, constraint-checked — but moderation judges the account-level pattern, not each edit. What I did the same day (withdrawal, purging dead references, a plain apology), and how I converted the failure into design records and agent rules."
tags: wikidata, postmortem, geo, claudecode
---

On the morning of July 16, 2026, I noticed a notification from Wikidata. When I opened it, my account was indefinitely blocked. The reason field said "Promotion-only account." My first reaction was: "Wait — I didn't do anything wrong."

I pulled the deletion log. Between 01:58:29 and 02:00:51 — **about two and a half minutes — all 109 items I had created were mass-deleted.** Six weeks of building, gone overnight.

"Subjects listed on Wikipedia or Wikidata get cited by AI. So register your own work as entities." — If you follow discussions of LLM-era discoverability (so-called GEO: Generative Engine Optimization), you have probably seen this idea somewhere. I acted on it, and this is how it ended.

The puzzling part is that **I believed every individual edit was policy-compliant.** I knew you must not write your own Wikipedia article. But Wikidata's policy is different: editing items about yourself (an item is Wikidata's unit of registration — a person, a work, a concept each gets one) is generally tolerated as long as you meet the sourcing requirements. The guideline [Wikidata:Autobiography](https://www.wikidata.org/wiki/Wikidata:Autobiography) says so explicitly.

Under that understanding, I attached references to every statement and passed Wikidata's constraint checks. My talk page — the public per-user contact page where policy warnings land first — never received a single warning. The block notice names no individual edit as a violation either.

And yet I lost everything. Why?

This article does three things.

1. **Why the total loss happened** — I explain the structure in which the judgment is rendered per account, not per edit
2. **The incident response I closed out the same day** — the withdrawal decision, purging references, and designing the apology, exactly as I did them
3. **How to convert failure into norms** — the procedure I used to turn this incident into a design decision record (ADR) and into rules my agent loads on every session

## What I was building, and what happened

Some context first: why was I registering DOIs and the like as an individual? I have no ambition to become an academic or a researcher.

Writing implementations with AI coding tools, I came to feel that the cost of implementation is steadily evaporating, and that any code I write will be obsolete soon.

Then at least I wanted to keep a dated record of judgment — "at this point in time, this is what I was thinking." So I started consolidating my thinking into public repositories (the "research repos" below) and papers, attaching DOIs (persistent identifiers for papers and software; services like Zenodo let you mint them yourself), making it all citable with dates.

The Wikidata investment was an extension of this.

But a record that never gets discovered might as well not exist. And what decides whether something gets read today is generative AI, more than search engines.

Readers ask an AI; works the AI cites get found, and works it does not cite might as well not exist. So I also invested in the groundwork for being discovered by AI (GEO).

What encouraged me was GEO measurement data. Multiple studies of generative-AI citation sources report that Wikipedia consistently ranks near the top of ChatGPT's cited domains (second tier, just behind Reddit) — see [Semrush](https://www.semrush.com/blog/most-cited-domains-ai/) and [Ahrefs](https://ahrefs.com/blog/most-cited-domains-in-chatgpt/), among others.

I have not found any measurement isolating the effect of Wikidata itself, as far as I searched.

Still, I reasoned: "Wikidata is what supplies the machine-readable entity data behind Wikipedia. If I register my author, repositories, and papers as items, cross-linked with identifiers like DOIs, an AI should be able to establish that this author and these works exist and connect this way." — That was my read, and I invested in this layer.

Looking back, the boundary between measurement and hope was already blurred at this point.

Here is what I built: an author item, repository items, paper items, and bibliographic items for the external works my papers cite — all connected with citation-relation properties.

The edits were executed by an AI agent (Claude Code) in a semi-automated setup, with me approving before any batch of writes. Every edit carried references. Over six weeks it grew to 109 items.

| When | What |
|---|---|
| 06-07 | Created author item + 3 papers + 7 repositories |
| 06-12 | Added 27 bibliographic items for cited works + citation edges |
| 06-13 to 26 | Added external identifiers, more paper items |
| Late night 07-15 to 16 | Created 19 new bibliographic items + bulk-synced citation edges from 14 to 33 |
| 07-16 01:58–02:01 UTC | **All 109 items mass-deleted + account blocked indefinitely** |

The block reason: "Promotion-only account: Promoting Tatsuya Shimomoto." The deletion log reason: "Spam / advertising: Mass deletion." Anyone can still verify this judgment through Wikidata's public API. (Throughout this article, every count and timestamp is a value you can confirm via the public API; wherever no log survives, I flag it explicitly as the author's recollection.)

```bash
# Count deletions related to the account in the 2026-07-16 mass-deletion log
curl -s "https://www.wikidata.org/w/api.php?action=query&list=logevents&letype=delete&leuser=The%20Squirrel%20Conspiracy&lelimit=500&format=json" \
  -A "audit/1.0" | python3 -c "
import json,sys
evs = json.load(sys.stdin)['query']['logevents']
mine = [e for e in evs if 'Shimo4228' in e.get('comment','')]
print(len(mine))  # -> 109
"
```

Note that the Wikidata API rejects requests without a User-Agent with a 403, so the `-A` flag is required.

:::details The block reason text is also retrievable verbatim via the API
```bash
# Fetch target, timestamp, and reason of the currently active block
curl -s "https://www.wikidata.org/w/api.php?action=query&list=blocks&bkusers=Shimo4228&bkprop=user%7Cby%7Ctimestamp%7Creason&format=json" \
  -A "audit/1.0" | python3 -m json.tool
```
:::

## The cause: judgment is per account, not per edit

Mechanical validation (presence of references, constraint checks, schema validity) measures **the technical validity of each individual edit**. What Wikidata's human administrators look at is **the pattern drawn by the account's entire contribution history**.

My 109 items — author, the author's works, the author's papers, the works the author's papers cite — varied in kind, but they all traced **a web pointing at one single person**. Any administrator opening this history for the first time sees "promotion-only," regardless of how careful each individual edit was.

Indeed, the block notice contains not one citation of an individual violating edit. The granularity of the judgment is simply different.

An immediate indefinite block with no warning is not unusual, either. Wikidata's [blocking policy](https://www.wikidata.org/wiki/Wikidata:Blocking_policy) states explicitly that a warning is not required before a block, and blocking accounts judged promotional or spam indefinitely without warning is routine operation across Wikimedia projects (Wikipedia's policy likewise provides that promotion-only accounts may be blocked "without warning, usually indefinitely").

Warnings and dialogue are afforded to those inside the "good-faith user" category. My account was classified outside that category — that is what this judgment means.

One more factor, I believe, determined the timing of detection: speed. About ten hours before the block, late at night, I was running the creation of 19 bibliographic items plus a bulk sync of citation edges. During the run, the agent kept reporting that "some items fail to post." (No log of this survives, so this part is the author's recollection.)

My read was "probably a transient server error on Wikidata's side," so I waited a while and resumed posting. The posts went through, and I even thought, "good, the server has recovered." The next morning: the block.

I cannot see what the moderation side actually detected, so I cannot prove the causal link between speed and detection. But as a lesson, I should have leaned toward assuming it. A non-bot account pinned against the throttle ceiling is the most conspicuous thing on the new-item feed and edit-rate patrols.

Repeated rate-limit errors are not "an outage that resolves if you wait." They are an **alarm**: "this speed and volume is anomalous for this account type." I should have stopped on the spot and reassessed. The errors clearing and the posts going through was not "recovery." I had merely resumed the single most conspicuous behavior on the patrol surface.

In hindsight, there was also a hole in how I approved. I had authorized the creation of 19 items through one single decision — "OK to run the bulk sync?" A judgment I might have paused on item by item had been diluted to one nineteenth by batching.

## Where the misunderstanding came from: "Wikidata allows self-registration"

So where did the understanding I opened with — "Wikipedia forbids it, but Wikidata tolerates it" — come from, and where did it turn into an error? I traced four sources.

1. **Wikidata's policy really is looser than Wikipedia's.** As we saw at the start, the guideline generally tolerates editing your own item, and that understanding itself is not wrong. Moreover, initiatives like WikiCite, which aggregates scholarly bibliographic data in Wikidata, have a culture of researchers curating publication data themselves. The error was the leap from "individual edits are tolerated" to "therefore any amount accumulated across the account is safe"
2. **Survivorship bias.** Deleted self-registrations are unobservable. All you ever see are the cases that survived
3. **Measuring the wrong axis.** My validation loop measured only technical compliance — references, constraints, schema — and kept returning PASS. It never measured the axis of "what does this look like to an administrator"
4. **Misreading notability.** A DOI is an identifier I can mint through my own actions, but I had misconstrued it as usable evidence of notability (the standard for whether something merits an item)

And here is the fact that stings the most: **I half knew.** Self-citation on Wikipedia was something I had already considered in advance and rejected as a conflict-of-interest violation. Even so, I redrew the boundary — "the prose encyclopedia is off-limits, but structured data is different" — and went ahead. Draw the boundary in the wrong place, and half-knowing still ends in an incident.

## Same-day response: withdraw, purge references, apologize

Once I finished confirming the facts (pulling the deletion log above), the first fork was: appeal the block, or withdraw?

| Option | Decision | Reason |
|---|---|---|
| Appeal the block | **Rejected** | Even if it succeeded, this layer would remain revocable at the operators' discretion at any time. What was rejected was not the quality of my execution but the premise itself: manufacturing your own authority data |
| Withdraw + document the lessons | **Adopted** | Remove all references to the revoked layer, extract design principles from the failure, and build a structure that never chooses this path again |

The first task in withdrawal was **purging dead references**. My research repos embedded `sameAs` links to Wikidata item IDs (QIDs) in their machine-readable metadata (JSON-LD knowledge graphs and the like) — and every one of those targets was now a 404.

Leaving identity links pointing at 404s is misinformation aimed at crawlers, and — ironically — an imitation of a classic spam pattern. I removed every QID reference from 9 repositories plus the distribution mirrors within the same day.

Careless removal breaks other things. I used a script with a two-gate check: "still valid as JSON" and "the only change is the removal."

```python
# The gist of purge_wikidata.py (a one-off script for that day, never committed):
# after dropping the target lines, pass two gates before writing
text = "".join(out_lines)
after = json.loads(text)          # gate 1: still valid JSON?
assert after == strip_wd(before)  # gate 2: is the only semantic change the removal?
```

:::details Two things that actually bit me during the bulk removal
- **Hardcoded values inside generator scripts**: I deleted QIDs from the data files, but a page-generation script had QIDs written directly into it, so regeneration resurrected them. When removing something from generated output, suspect the generator
- **Missed restatements of counts**: statements like "there are 20 ADRs" inside the repos — human review missed 6 files. What caught them was an existing verification script that scans every numeric claim in every file against the file contents as ground truth. It was a case where mechanical scanning beats human thoroughness
:::

Finally, the apology. I made one design decision here: **post to the talk page a pure apology containing no request for an unblock.** The moment you attach an unblock request, the apology reads as a negotiating tool.

By the time I posted it, I had already deleted the automation skill for Wikidata writes and the API credentials (the companion repository that published those procedures was deleted the same day as well; the research repos themselves remain — what I removed was the means of writing). I could demonstrate "never again" through the state of things, not words.

I consider the administrator's judgment fair. What this incident actually left the community was the administrative labor of reviewing and mass-deleting 109 items.

:::details Even while blocked, you can write to your own talk page
Even under a site-wide editing block, if the block's parameters do not forbid editing your own talk page, you can post to it via the login API (logged-out attempts were rejected by the automatic IP block). I made the post with a one-off script using an existing BotPassword, and deleted the credentials after running it.
:::

## Prevention: the record goes into an ADR, the behavior into rules

In parallel with the incident response, I fixed this failure in place at two layers — so it would not end as "let's be careful next time." **A record of the judgment (ADR)** and **rules that change day-to-day behavior**.

First, the record layer. An ADR (Architecture Decision Record) is a document format that records a design decision together with its context and the alternatives that were rejected. What it preserves is the reasoning — "why we withdrew, why we will never do this again" — so future sessions do not relitigate the same argument. I wrote one ADR, "entity grounding is done self-sovereign," with four core points:

1. **Design any layer governed by a third party under the assumption it can be revoked** — does the strategy survive if that layer vanishes entirely? Never place load-bearing references on a revocable layer
2. **Use only mentions that others created of their own volition; never choose the path of creating them yourself** — commissioning someone else to create them is equally out
3. **When revoked, remove dead references promptly — but never rewrite dated historical records** — present-tense claims and historical records have different roles
4. **No circumvention** — alternate accounts, logged-out editing, or proxying through third parties only converts a disagreement with governance into a permanent adversarial relationship

I also set a principle about the order of response. A "do not climb" sign does not stop someone who is climbing. What stops them is the absence of any means to climb.

So that day's response ran in this order: **deleting the means (skill, credentials, repository) → mechanism (writing the lessons into rules) → words (the apology)**. The strength of a prohibition ranks: absence > mechanism > signage.

However, **what actually works as prevention is not the ADR.** Records are not guaranteed to be reread. What changes behavior is the **instruction files** of the executing agent, Claude Code. The agent automatically loads its rule files at the start of every session before doing anything, so a lesson written there never needs to be "remembered." This time I wrote it into three places:

| Where | What |
|---|---|
| Rules shared across all projects (`~/.claude/rules` — auto-loaded every session) | "Repeated rate-limit errors are an alarm. Stop the bulk write and report to the human." "Never pass N writes through one approval. Approvals must state count and scope" |
| Learned notes (`~/.claude/skills/learned` — consulted during bulk external-write work) | Before executing, ask: "if an administrator seeing this account for the first time opened its history, what would it look like?" (a platform-agnostic self-check) |
| The project's own instruction file (loaded when working in that repository) | Total ban on self-registration paths (variants — alternate accounts, anonymity, proxies — are equally guilty) |

With this, "stop and report when errors repeat" no longer depends on whether I or the agent happens to remember it on some future late night. The lesson lives in the agent's boot sequence, not in human memory.

I decided against enforcement via hooks, by the way. "Bulk writes to external platforms" cannot be detected deterministically, and the cost of false positives halting work outweighs the benefit. Enforce mechanically only where detection is mechanical; keep everything requiring judgment as rules and questions. That dividing line is itself part of the prevention design.

## Conclusion: separate the effect from the pathway

The lesson of this incident is not "Wikidata is useless." **The effect and the pathway are different things.**

- **The effect**: multiple measurements support that being mentioned in authoritative sources like Wikipedia helps AI citation. The hope for Wikidata sits on that same line (though the honest summary of what I found is that direct measurements of Wikidata alone are thin)
- **The pathway**: the pathway of **creating those mentions yourself** can suffer total loss through account-level governance judgment even when every individual edit is permitted. In my case, it did. So I switched to relying only on **earned** mentions — ones that others created of their own volition

GEO literature talks about the effect; almost none of it teaches the distinction between pathways. My 109 items were the tuition for that distinction.

Looking back, my error was not one of effort but of **classification**. Among the places that hold identifiers and proof of existence, there are places where self-registration is legitimate (self-service identifiers like DOI minting, machine-readable metadata in your own repositories) and places where you must wait to be written about by others.

Wikidata — even though each individual edit is tolerated — turned out to be the latter, just like Wikipedia, as a place for registering an entire web centered on yourself. I had classified it as the former, and that was the six-week, 109-item error.

There is one more lesson specific to the era of AI agents. **An agent, with no malice at all, effortlessly reaches the speed and volume that platforms treat as hostile.**

Individual edits are careful precisely because an agent does them — referenced, constraint-check PASS. With that per-edit compliance intact, the account grew into a 109-item "web pointing at one person" over six weeks, and on the final night it was writing at a speed pinned against the rate limit.

The only human decisions made that night were approving "OK to run the bulk sync?" and choosing to resume after the errors. Nowhere in this incident is there a human who willfully broke the rules.

So what I want you to take away is not "a procedure for safely bulk-writing to external platforms." The conclusion is: **don't**.

Beyond that, if you operate agents that write to external services, put these five questions in your agent's rule files — so the work of good faith can stop before it grows into a web of promotion:

- [ ] If this account's history plus today's writes are viewed together, what do they look like to an administrator seeing them for the first time?
- [ ] Are the write targets skewed toward yourself, your works, and references to you?
- [ ] Did the approval state the count and scope explicitly (or did one decision dilute N items)?
- [ ] Is there a predefined stop condition for when rate-limit errors start appearing?
- [ ] Have you enumerated what breaks if this entire layer gets revoked?

And the final question is this: **the place you are about to write to — which side is it on?** When in doubt, imagine what that platform's administrator would see upon opening your account history.

My footing now rests on layers under my own control. Whether anything gets built on top of that is for others to decide.

## Related links

- [ADR-0021: Self-Sovereign Entity Grounding](https://github.com/shimo4228/authorship-strategy/blob/main/docs/adr/0021-self-sovereign-entity-grounding.md) — the actual design decision record extracted from this failure
- [The apology post (User talk:Shimo4228)](https://www.wikidata.org/wiki/User_talk:Shimo4228)
- [GEO: Generative Engine Optimization (Aggarwal et al., KDD 2024)](https://arxiv.org/abs/2311.09735)
- [Wikidata:Autobiography](https://www.wikidata.org/wiki/Wikidata:Autobiography) / [Wikidata:Notability](https://www.wikidata.org/wiki/Wikidata:Notability)
- [Author's GitHub](https://github.com/shimo4228) — index of the research repositories
