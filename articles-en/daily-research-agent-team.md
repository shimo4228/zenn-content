---
title: "I Tried an Opus Orchestrator and Killed It — The ROI of Multi-Agent Systems"
emoji: "🤖"
type: "tech"
topics: ["claude", "ai", "claudecode", "automation"]
published: false
---

## Introduction

In [the previous article](https://zenn.dev/shimo4228/articles/daily-research-automation), I introduced the AI research pipeline that runs automatically every morning at 5 AM. Sonnet alone, 7 minutes, within the Max plan flat rate — effectively zero cost. It worked well enough.

But then the itch kicked in: "Could this be better?" Some days the topic selection felt shallow. Research depth was inconsistent. What I really wanted was an **agent team**. Opus as the orchestrator, with researchers and writers running as sub-agents in parallel. Multiple agents with distinct roles collaborating on a single deliverable — a real multi-agent system.

Here's the punchline: quality did improve. But it wasn't worth the 9x time and 2x cost. **Inter-agent communication consumed far more tokens than expected.** The next day, I disbanded the team and switched to a sequential agent relay.

---

## It Started with a Podcast

I was listening to a Japanese AI podcast where people were pushing automated AI research to extremes:

- Playwright + headless Chrome driving Gemini Deep Research **200 times per day**
- Manus wide research with **100 parallel agents**, Claude Agent Team distributing work across sub-agents

The scale was in a different league. My pipeline was a single Sonnet doing topic selection, research, and writing in sequence. Wouldn't parallelization improve both quality and speed?

A Google Research paper on multi-agent systems gave me further confidence. It showed that a centralized orchestrator architecture significantly reduces error amplification compared to independent parallel agents, and that a Plan-and-Execute pattern (smart model plans, cheap model executes) can dramatically cut costs.

The theory was clean. Opus decides "what to research," Sonnet does "the actual research and writing." I decided to build it.

---

## The Design — and Its Unintended Configuration

### Architecture

```text
Opus Orchestrator (--model opus)
├── Load config.toml / past_topics.json
├── WebSearch for trend discovery
├── Topic selection (tech + personal)
├── Task: researcher (tech)     ──→ [intended: Sonnet / actual: Haiku]
├── Task: researcher (personal) ──→ [same]
├── Task: writer (tech)         ──→ [same]
├── Task: writer (personal)     ──→ [same]
├── Report validation
└── Update past_topics.json
```

### I Thought It Was Sonnet — It Was Haiku

When I ran it and checked the cost breakdown, I couldn't believe the numbers. The sub-agent costs were suspiciously low.

`--model opus` only applies to the main agent — **it doesn't propagate to sub-agents spawned by the Task tool.** Claude Code's Task tool falls back to Haiku when no model is explicitly specified.

In other words, this is what was actually running:

```text
Intended: Opus (orchestrator) → Sonnet (research & writing)
Actual:   Opus (orchestrator) → Haiku (research & writing)
```

Opus meticulously selects topics and crafts detailed instructions. The one receiving those instructions? The lightest model available. It was like a CEO writing a thorough project brief and handing it to an intern.

I considered starting over. But even if I switched to Sonnet, I still wouldn't know whether Opus orchestration itself was adding enough value. If quality was already acceptable with Haiku, maybe the orchestrator itself was unnecessary. I decided to evaluate the current setup first and let the data decide.

---

## Blind Evaluation with LLM-as-Judge

"The team version seems better" is a dangerous subjective judgment. You're unconsciously lenient toward your own work.

So I had an LLM score all 12 reports from two days (4 Sonnet + 8 Team) in a blind evaluation. The generation method was hidden, and each report was scored across 7 dimensions (topic selection, research depth, specificity, source quality, prose quality, structure, and topic relevance) on a 10-point scale, totaling 70 points.

The goal of quantification was to move beyond "feels better" or "feels worse" and **isolate which dimensions showed real differences and which didn't**.

### Result: Only Topic Selection Was Dramatically Different

Aggregated scores across all 12 reports:

| Metric | Sonnet (n=4) | Team (n=8) | Delta |
|--------|-------------|-----------|-------|
| Average total | 53.0/70 | 57.1/70 | +4.1 (+8%) |
| Topic selection | 6.5/10 | 8.3/10 | +1.8 (+28%) |
| Ranking | All 4 at the bottom | Dominated the top | — |

In the blind evaluation, all 4 Sonnet reports ranked last in their respective tracks. The team versions swept the top spots. The gap was clear.

But **the breakdown tells a different story.**

Topic selection was +28%. That's significant. Opus tended to pick themes like "the quiet shift in memory infrastructure" or "meditation meets molecular reprogramming" — niche but deeply explorable. Topic selection is a task that requires comparing multiple candidates across multiple axes and choosing the highest-value combination. It's exactly where Opus's reasoning depth pays off.

Sonnet, by contrast, gravitated toward surface-level topics like "Chrome DevTools MCP" — eye-catching but shallow.

Research depth and prose quality were **roughly equivalent.** Despite Haiku doing the actual research. This partly reflects the high quality of Opus's instructions — but it simultaneously means that "deep reasoning from an orchestrator isn't necessary for research and writing." For tasks that simply execute instructions, model reasoning depth didn't make a difference.

---

## Inter-Agent Communication Was Too Token-Hungry

The quality gap was clear. The question was: how much did it cost?

| Metric | Sonnet solo | Team (Opus + Haiku) |
|--------|------------|---------------------|
| Duration | 7 min | 62 min (9x) |
| Cost | $1.78 | $3.53 (2x) |
| Output tokens | 13,906 | 42,803 (3x) |
| Monthly cost (daily) | ~$54 | ~$106 |

Note: the Sonnet solo cost dropped from $2.15 in the previous article to $1.78 after prompt optimization and turn count tuning.

The poor ROI wasn't just because "Opus is expensive." **Structural overhead inherent to agent teams** was compounding.

In an agent team, the orchestrator sends instructions to sub-agents, receives results, and incorporates them into the next instruction. All of this "inter-agent communication" is consumed as tokens:

- The **instruction prompts** Opus sends to sub-agents (topic context, research direction, expected format)
- The **full output** from each sub-agent accumulating in Opus's context window — output from all 4 Tasks flowing in, inflating the context continuously
- Token consumption when Opus **reads results and makes the next decision**

Output tokens ballooning to 3x (13,906 to 42,803) wasn't because research got 3x deeper. **The delegation and reporting overhead between agents** was eating the tokens.

Opus's cost ($3.31) was 94% of the total. The Haiku researchers cost just $0.21. **Nearly all the cost went to Opus's orchestration and context accumulation**, yet quality improvement outside topic selection was only +6-8%.

9x the time and 2x the cost for +8%. An additional $52/month. This investment doesn't pencil out.

On top of that, each Task required a startup-and-response round trip — four times, executed sequentially, not in parallel. And Opus generates tokens slower than Sonnet. The orchestrator itself was the bottleneck.

The cost reduction that the Google Research paper envisioned for Plan-and-Execute assumes the execution fleet is sufficiently cheap and can run in parallel. Claude Code's Task tool doesn't allow model specification for sub-agents (Haiku fallback), and doesn't support parallel execution. The gap between theory and reality showed up directly in the numbers.

---

## The Decision: Disband the Team, Switch to Sequential Relay

Switching to Sonnet sub-agents might have improved quality further. But the cost structure problem doesn't go away by changing models. As long as the **orchestrator accumulates all sub-agent results in its context**, token consumption won't decrease.

The conclusion from the data was clear:

> **Opus's value is concentrated in topic selection. As a full orchestrator, the ROI is poor. Use it only where its strengths match the task.**

I abandoned the agent team (orchestrator managing multiple sub-agents) and switched to a **sequential agent relay** (two-pass approach):

```text
Pass 1: Opus handles topic selection only (~3 min)
  ↓ Theme JSON passed via file
Pass 2: Sonnet handles research + writing in one shot (~8 min)
```

The critical difference from the agent team: **the two agents don't share a context window.** Pass 1's output is written as a JSON file, and Pass 2 reads it independently. Inter-agent communication token cost drops to zero.

Keep only the portion of Opus's cost used for topic selection; eliminate all orchestration overhead. In theory, this should deliver the team version's topic selection quality (+28%) at close to Sonnet solo's cost and speed.

<!-- textlint-disable no-dead-link -->
The implementation of this two-pass approach — and the new problems I hit along the way — is covered in [the next article](https://zenn.dev/shimo4228/articles/daily-research-postmortem).
<!-- textlint-enable no-dead-link -->

---

## Two Takeaways from the Experiment

### 1. Expensive Models: Don't Use Them for Everything — Use Them Where They Shine

Making Opus the orchestrator for the entire pipeline spreads its reasoning power thin. For tasks like topic selection — "compare multiple candidates across multiple axes and make a judgment" — the difference is overwhelming. For tasks like research and writing — "execute instructions as given" — the difference is negligible.

Model allocation shouldn't be "the expensive one is probably better." **Deploy each model only where the task characteristics match its strengths.**

### 2. Always Verify Which Model Sub-Agents Actually Run

The fact that `--model opus` doesn't propagate to sub-agents wasn't discoverable by reading documentation alone. I only noticed it by checking the cost breakdown.

If you're building multi-agent architectures, **add a step at the very beginning to verify via logs which model each agent is actually using.**

---

## Source Code

The complete source code for the system described in this article is available on GitHub.

https://github.com/shimo4228/daily-research
