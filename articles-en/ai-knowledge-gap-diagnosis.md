---
title: "I Asked AI to Diagnose My Knowledge Blind Spots — 15 Days of Deadlock Moved in 85 Minutes"
emoji: "🔍"
type: "tech"
topics: ["systemsthinking", "claudecode", "knowledgemanagement", "metacognition"]
published: true
description: "Asked AI to analyze ~3,000 conversation turns and detect concepts I'd independently reinvented. It pointed to systems thinking. Eighty-five minutes of reading Donella Meadows reframed a skill-management problem I'd been stuck on for 15 days — from pruning the pile to questioning why it grows."
tags: systemsthinking, claudecode, knowledgemanagement, metacognition
---

On August 15, 2026, I wrote this in a session with AI:

> The insights system isn't really working — Claude Code and I ended up dropping most of the skills through manual approval anyway.

This was about skill management in an AI agent I'd built (Contemplative Agent). Skill definition files kept growing. I had tools to visualize usage frequency and a process to cull low-use ones. But the management tooling was there and the problem still wasn't moving.

Fifteen days later, on August 30, I wrote this about the same problem:

> I'm reading about stocks and flows now, and it's making me think the problem with Contemplative Agent's skill count isn't the pile itself — it's something upstream in the episode-to-pattern-to-skill pipeline.

The problem definition shifted. "How do I manage the growing pile of skills" became "there's a structural problem upstream in how skills are born."

The trigger for this shift was asking AI to analyze my session history and diagnose knowledge blind spots. The diagnostic criterion that made the biggest difference: **detecting concepts I had independently reinvented**.

This article is about how that diagnosis worked and why the problem looked different after 85 minutes of reading.

## When Better Management Doesn't Move the Problem

Here's the August 15 situation.

I was managing Contemplative Agent's skills with Claude Code. Visualize usage frequency, get author approval, delete low-frequency skills. Repeat. But even after manually dropping most of the skills, I still felt the system "wasn't working" — that was the opening quote.

Trying to improve the management process kept bringing me back to the same spot. Fifteen days later, on August 30, I was still seeing the same problem through the same frame.

When better management doesn't move a problem, the problem might not be management — the framing itself might be wrong. But blind spots in your own framing are, by definition, invisible to you.

## I Fed AI ~3,000 Turns of Session History

On August 30, I asked Codex (OpenAI's coding agent):

> Analyze my sessions, articles, and other materials. Identify knowledge I'm likely missing, and suggest systematic ways to acquire the domain knowledge that would best fill those gaps.

The input: ~3,000 human turns (my inputs from AI conversations), 72 published Zenn articles, and unpublished essays and project documents.

## The Diagnostic Criterion That Worked — Detecting "Concept Reinvention"

The diagnosis plan AI returned included criteria for judging blind spots.

First, quality thresholds to suppress false positives:

- Only flag a domain when two or more distinct types of evidence and three or more independent instances are present.
- Don't treat absence from conversation as evidence of ignorance.

"Never talked about it" and "knows about it but had no reason to discuss it" are indistinguishable. These thresholds exist to prevent reasoning from absence.

On top of those, the plan listed several signals to look for. The one that made the biggest difference:

**Find concepts the author has independently reinvented where established disciplines already have mature vocabulary and methods.**

Detecting "unknown domains" is binary — you know it or you don't. Detecting "reinvented concepts" is different: it points to an existing body of knowledge that already connects to your practice. The moment you start learning, you have contact points. You find a discipline with built-in anchors to problems you're already working on.

Based on this criterion, the diagnosis flagged systems thinking as a strong candidate.

I had been using "feedback loop" as a core concept in AKC (a knowledge management framework) — a separate project from Contemplative Agent. But feedback loops are standard vocabulary in systems thinking. I was using the concept without recognizing the existing body of work behind it.

The diagnosis recommended Donella Meadows' *Thinking in Systems: A Primer* as the systematic entry point.

## What Happened 85 Minutes Later

That same day, I bought the book and started reading. Eighty-five minutes in, I wrote this about Contemplative Agent's skill proliferation:

> I'm reading about stocks and flows now. With Contemplative Agent, I've been framing the problem as "too many skills — how to prune them." But the problem feels like it's upstream — something in the episode → pattern → skill flow is producing the pile in the first place.

Stock and flow is the most basic concept in systems thinking. A stock is what accumulates. A flow is what moves in and out. When a bathtub overflows, whether the problem is the water level (stock) or the faucet-and-drain structure (flow) determines a completely different intervention point.

This concept reframed the problem I'd been stuck on for 15 days.

| | Before (August 15) | After (August 30) |
|---|---|---|
| Problem framing | Management tooling isn't working | Structural problem upstream of where skills are born |
| Candidate interventions | Stock side — select and prune the accumulated skills | Flow side — change the upstream pattern that creates skills |
| Actions | Frequency-based selection and manual deletion | (Framing changed; concrete measures not yet started) |

Concrete measures on the After side don't exist yet. But the problem moved from "how to reduce the pile" to "change the structure of why it piles up," and that shifted the intervention point. The reason I was going in circles for 15 days: I was intervening at the wrong level.

About 50 minutes later, I wrote this about AKC:

> I've been putting feedback loops at the center of AKC — looks like that connects to systems thinking too.

Self-confirmation that the "feedback loop" I'd been using independently mapped onto existing systems thinking vocabulary — exactly what the "concept reinvention" criterion had pointed to. The concept already had a body of knowledge behind it, so the connection clicked the moment I started learning.

## Beyond Stock and Flow

Stock and flow is just the entry point. Meadows' framework has tools that shift how you see problems further. Here are two things waiting beyond the 85-minute reframe.

### Feedback Loops — Reinforcing and Balancing

Feedback loops come in two types. **Reinforcing loops** snowball — more leads to more. **Balancing loops** act like a thermostat — they push back toward a target.

The skill proliferation problem reads as a reinforcing loop: more skills → more management complexity → more skills to manage the complexity → even more management complexity. What I'd been calling "feedback loops" in AKC corresponded to this reinforcing type.

What I was doing on August 15 — "delete low-frequency skills" — is a balancing-loop operation. I was applying balancing-loop operations to a structure driven by a reinforcing loop. That's one reading of why it wasn't working.

### Leverage Points — Where to Push to Move the System

Meadows ranked system interventions by effectiveness across 12 levels. Parameter adjustment (tweaking numbers) is the weakest. Paradigm shift (changing how you see the problem) is the strongest.

"Adjusting the deletion threshold" — what I'd been doing for 15 days — is a parameter operation. "From stock management to flow structure" is a change in structural recognition, several levels up the leverage hierarchy. The diagnosis didn't just fill a knowledge gap. It moved the intervention to a higher leverage level.

### What I Haven't Touched Yet

Meadows' framework goes further: how time delays inside feedback loops cause oscillations, how to draw system boundaries, resilience, and self-organization. In a separate lineage, Peter Senge's *The Fifth Discipline* systematizes recurring structural patterns across different domains (system archetypes).

I've learned one entry-point concept — stock and flow — and haven't touched the rest. But the fact that a single entry-point concept reframed 15 days of stagnation shows how close the diagnosed discipline was to my existing practice.

From here, I'll return to the procedure for reproducing the diagnosis itself.

## Key Points for Reproducing This

Here's what you need to try this yourself.

### Input

You need enough material for AI to analyze. In my case, ~3,000 conversation turns and 72 articles. Pattern detection requires repetition — a few dozen turns won't reach the threshold.

Where session history is stored depends on your tool. Claude Code keeps it under `~/.claude/projects/`, Codex under `~/.codex/sessions/`, both as JSONL. But raw JSONL includes the AI's own outputs and tool results. Filter to human-authored turns only. If you include AI output, the AI's vocabulary gets misattributed as the author's knowledge.

### How to Request the Diagnosis

Hand over the session history and artifacts, and specify these three criteria explicitly:

1. **Set thresholds** — Only flag a domain when two or more distinct types of evidence and three or more independent instances are present.
2. **Don't reason from absence** — "Never mentioned" is not evidence of ignorance.
3. **Look for "concept reinvention"** — Detect concepts I've independently reinvented where established disciplines already have mature vocabulary and methods.

The third criterion matters most. Domains it surfaces have built-in connection points to your existing practice from the moment you start learning. The motivation and speed are different from studying something because you feel you should.

### Limitations of This Article

This is a single case. The 85-minute reframe is an observation that the diagnosed discipline connected to an existing problem — not a causal verification of the diagnosis. The reading itself, ongoing thinking, and other stimuli may have contributed. I can't rule them out.

I built a 12-week study plan based on the diagnosis, but as of writing, I haven't started it. "What happened after learning" is a later story.

What I can say is one observation: I asked AI to read my session history and detect concept reinvention, and a problem I'd been stuck on for 15 days looked different.

## Related links

- [Markdown source on GitHub](https://github.com/shimo4228/zenn-content/blob/main/articles-en/ai-knowledge-gap-diagnosis.md) — All article Markdown files and the full index (docs/PUBLICATIONS.md) live in the same repository
- [Author's GitHub](https://github.com/shimo4228) — DOI-registered research repositories
