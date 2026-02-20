---
title: "What I Learned from Breaking My AI Pipeline for Two Days Straight"
emoji: "🔥"
type: "tech"
topics: ["claude", "ai", "claudecode", "debugging"]
published: false
---

In [my previous article](https://zenn.dev/shimo4228/articles/daily-research-automation), I introduced a daily AI research pipeline that runs automatically at 5 AM every morning. Sonnet handles everything end-to-end — topic selection, web research, report generation. Zero lines of Python. Zero additional cost within the Max plan.

It was running smoothly. **Until I decided to add new features.**

This article is a two-day incident and recovery log. It is a debugging story on the surface, but what I really want to write about is something else: **AI coding assistants have their own debugging cognitive biases**, and the story of how **human-AI debugging collaboration** actually played out.

---

## I Added Mem0 and 2-Pass Mode at the Same Time

<!-- textlint-disable no-dead-link -->
In [the previous article](https://zenn.dev/shimo4228/articles/daily-research-agent-team), I evaluated an agent team approach (Opus as orchestrator + sub-agents for parallel research) and reached a key conclusion: **Opus's real value is concentrated in topic selection.** As a full orchestrator, the cost-effectiveness is poor. Better to extract just the part it excels at.
<!-- textlint-enable no-dead-link -->

The next day, I implemented two features simultaneously.

**1. Mem0 MCP Integration**

[Mem0](https://mem0.ai/) is a persistent memory service for AI applications. Claude Code can connect external tools via MCP (Model Context Protocol). You define server configurations in `.mcp.json`, and they automatically connect when `claude` starts.

The goal was to **carry context across daily research sessions**. "We went deep on this topic last week, so let's continue from there today." "We've picked this domain three times in a row, so let's deprioritize it." That kind of judgment — not as a flat list in `past_topics.json`, but as semantic-level memory.

**2. Opus 2-Pass Topic Selection**

A division-of-labor approach where Opus handles only topic selection and Sonnet executes the research. This was a direct translation of the finding from the agent team evaluation: "Opus is only strong at topic selection."

Both were individually rational extensions. The problem was doing them **at the same time**.

### Five Failures and Nine Commits Reverted

Implemented the 2-pass mode. Ran it manually. Hung. Fixed it. Ran again. Hung again. Added MCP fallback code. Dropped by SSH disconnect. Ran in the same terminal. `claude -p` got suspended.

By the third attempt, I had lost track of what I was even debugging.

When `claude -p` hung, multiple candidate causes existed simultaneously:

- Was the Mem0 MCP server timing out during initialization?
- Was Opus just slow to respond?
- Was it a terminal TTY conflict?

If I had added one feature at a time, the first failure would have pinpointed the cause. With two features intertwined, each fix generated the next problem, and issues cascaded. **Speed of implementation and speed of verification are different things** — that hit home hard.

### The Root Cause of Mem0, and Giving Up on It

After reverting nine commits and isolating the variables, the main culprit was Mem0 MCP.

`claude -p` (non-interactive mode) was reading `.mcp.json`, trying to start the Mem0 MCP server via npx, and hanging for 15 minutes with zero output. The tricky part was that **it worked perfectly in interactive sessions**. I had done my pre-testing in interactive sessions, so I never caught it.

Even more ironic was the production environment behavior (the 5:00 AM launchd execution). In the launchd environment, PATH is minimal and npx isn't found. MCP initialization fails immediately. As a result, **Sonnet runs normally without MCP and generates reports just fine.** "Works in production but fails in manual testing" — the classic pattern, inverted.

| Test Environment | Production Environment | Difference |
|-----------------|----------------------|------------|
| Interactive session | `claude -p` (non-interactive) | MCP initialization behaves differently |
| Local terminal | launchd | Different PATH, conflicts with auto-update |
| Direct terminal execution | Execution from within Claude Code session | Shares TTY, `claude -p` gets suspended |

"It worked in the interactive session, so it should work with `claude -p`" — that assumption broke three times.

I removed Mem0 entirely along with `.mcp.json` and reimplemented just the 2-pass mode in a lightweight form. I plan to reintroduce Mem0 once operations stabilize.

---

## The Next Morning, It Broke in a Different Way

### 5:00 AM, Dead on Arrival

I finished the lightweight reimplementation of the 2-pass mode and waited for the next morning's automated run. When I woke up and opened the logs, I didn't understand what I was seeing for a moment.

```text
gtimeout: failed to run command 'claude': No such file or directory
```

Exit 127. Pass 1 failed instantly, there was no fallback, and the script exited as-is.

### The Cause: A Race Condition with Auto-Update

The `claude` command is actually a symlink chain:

```text
/opt/homebrew/bin/claude  (symlink)
  → ../lib/node_modules/@anthropic-ai/claude-code/cli.js  (#!/usr/bin/env node)
    → /opt/homebrew/bin/node
```

`gtimeout` internally calls `execvp("claude", ...)`. While the OS was traversing the symlink chain, a link in the middle was temporarily missing.

There was evidence. The timestamps on `cli.js` and the symlink were `06:37:47` — after the script's execution at `05:00:01`. Claude Code's auto-update was running in the background, and `cli.js` had disappeared during the npm package swap.

A `claude --version` call earlier in the same script had succeeded. That command, executed directly by the shell, completed before the update started.

### Aggravating Factor: I Had Removed the Fallback Myself

During the previous day's refactoring, I had committed a change to "centralize topic selection responsibility to Opus." In that commit, the Sonnet fallback had been removed. Pass 1 failure meant an immediate `exit` with no recovery path.

"Tidying up" a feature can reduce availability. That was the moment when clean code became fragile code.

---

## AI Has Debugging Cognitive Biases

When I had Claude Code investigate the Day 2 failure, the approach it came back with felt off.

1. A broad data analysis incorporating Day 1 logs (the Mem0 + 2-pass stall)
2. Proposed modifications to **code it had recently touched** — WebSearch throttling, prompt optimization
3. Building up indirect hypotheses about API latency, prompt caching, etc.

**"The cause must be in code I recently touched"** — this is a well-known cognitive bias in human developers. AI exhibited the same tendency. Recent work context was so dominant that problem isolation suffered.

### Three Points Where Human Intervention Made the Difference

I gave three specific corrections.

**"Yesterday's logs are a different cause. The only reliable data is today's success log."**

Day 1's failure was MCP hangs and terminal conflicts. Day 2's failure was `gtimeout` ENOENT. Completely different problems, yet Claude Code was trying to analyze both sets of logs together. **Filtering out noise** is something humans do faster.

**"The second run was before the fix. WebSearch worked fine before the throttle was added."**

Claude Code was proposing WebSearch rate limiting, but the second manual run (the one that succeeded) had executed before that fix was applied. So WebSearch call count wasn't the issue. This was a judgment call to **block an unnecessary fix**.

**"Remove the rate limit. Opus can autonomously decide when to stop searching."**

In fact, the artificial WebSearch limit was unnecessarily constraining Opus's judgment. Removing an overprotective guardrail is a decision AI struggles to make about itself.

All three were about focusing on the facts at the time of failure and eliminating unrelated variables.

### A Division of Labor for Debugging Emerged

From this experience, a clear role division between AI and humans in debugging became visible.

| | What AI excels at | What humans excel at |
|---|---|---|
| Data processing | Reading all logs, detecting patterns | Judging "which data is relevant" |
| Hypothesis generation | Listing possibilities broadly | Narrowing focus: "look only here" |
| Fix implementation | Rewriting code, creating tests | Saying "that fix is unnecessary" |
| Context | Gets pulled toward recent work | Returning to facts at the time of failure |

When AI tries to analyze broadly, humans narrow the focus. When AI gets pulled by recent context, humans say "here are the facts."

**AI is not an omniscient debugger. It becomes efficient only when paired with human focus.** Humans correct AI's blind spots — whether you're conscious of this division of labor makes a significant difference in efficiency.

---

## Fixed It, and It Worked

The final fix consisted of four changes.

1. **Path resolution for the `claude` command** — Resolve the real path with `realpath` at script startup and cache it, reducing impact from symlink changes during execution
2. **Restore Sonnet fallback** — When Opus fails, Sonnet handles both topic selection and research in a single pass
3. **Remove `gtimeout`** — `gtimeout` runs commands in a separate process group, causing `claude -p` to receive SIGTTOU and stop. Timeout control now uses `--max-turns` only
4. **Add mock E2E tests** — Automated tests for the happy path and two fallback patterns (28 tests, all passing)

After the fix, the manual run of the 2-pass mode completed successfully for the first time.

| Metric | Result |
|--------|--------|
| Pass 1 (Opus topic selection) | 2 min 38 sec |
| Pass 2 (Sonnet research) | 8 min 27 sec |
| Cost | $1.76 |
| Reports | 2 generated |

In the previous article, Sonnet standalone cost $2.15/run. Through prompt optimization and turn count tuning, it dropped to $1.76. Essentially the same cost, now with Opus topic selection included. Since then, the daily morning report generation has been running stably.

---

## Source Code

The complete source code for this system is available on GitHub.

https://github.com/shimo4228/daily-research
