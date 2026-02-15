---
title: "Zero Python Code: How I Built a Daily AI Research Report System"
emoji: "🔬"
type: "tech"
topics: ["claude", "ai", "claudecode", "automation"]
published: true
---

## Introduction

Every morning at 5 AM, my Mac wakes up on its own. Claude Code crawls the web, generates two deep research reports, and saves them to my Obsidian vault. By the time I'm making coffee, I can read them on my iPhone.

I built this with zero lines of Python. Just one shell script and two prompt files.

The key ingredient is Claude Code's non-interactive mode (`claude -p`). Since it runs within the Max plan's flat rate, the additional cost is zero. The display shows $2.15 per run, but my wallet stays untouched.

This article covers the design and implementation. But more importantly, I want to talk about **the planning process that led to it** — because that's where the real lesson is.

---

## Spending Time on Planning Was the Fastest Path

### Three Sessions to Decide What NOT to Build

This project didn't come from a single session. I went through three separate sessions of planning and research before writing any code.

After implementing several projects with Claude Code, I had one conviction:

> **You should spend the most time on initial planning.**

Implementation is fast with Claude Code. Writing code is no longer the bottleneck. The bottleneck is deciding "what to build" and "what not to build." If you start implementing with ambiguous requirements, you'll hit mid-course corrections, rewrites, and end up slower overall.

So this time, I didn't write a single line until I had a plan I was satisfied with.

### Session 1: Lay Out All Options and Eliminate

The first session was about technology selection for the research engine.

| Option | Quality | Cost | Complexity | Verdict |
|--------|---------|------|------------|---------|
| OpenAI Deep Research API | High | $1.3–$3.4/run ($78–$204/mo) | Medium | Too expensive |
| GPT Researcher (OSS) | Medium | Same API costs | High | Same issue |
| Gemini CLI + Claude Code | High | Zero | Medium (2 auth sources, Python needed) | Overkill |
| **Claude Code standalone** | **Medium** | **Zero** | **Low** | **Adopted** |

OpenAI's Deep Research is high quality, but at nearly $200/month it doesn't suit daily automated execution. The Gemini CLI combination was also considered, but it would split auth management across two services and require Python glue code.

**Start with the minimal setup, then expand if quality is lacking.** This turned out to be the right call.

### Session 2: Realizing Prompt Design Decides Everything

In the second session, I noticed something important:

> Topic selection and prompt quality determine the entire system's value.

Simply picking the highest-scoring articles from Hacker News or GitHub Trending would just mass-produce superficial reports. To get hints about "what I should build next," the topic selection needed intentionality.

I designed three scoring criteria:

- **Whisper trend factor**: Is this a change most people haven't noticed yet?
- **Signs of movement**: Not static knowledge, but an actively evolving area?
- **Buildability**: Could I build something with my skills (Python/Swift/TypeScript)?

I'd heard an AI researcher on a podcast say: "Information gathering and generation can be automated, but human comprehension is the bottleneck." That's exactly why I needed a system that **controls quality, not quantity**.

### Session 3: Detailed Spec Done, Implementation Was Instant

In the third session, I created a detailed specification for Plan A (Claude Code standalone):

- File structure and responsibilities
- CLI flag selection rationale (why `--append-system-prompt-file` and not `--system-prompt-file`)
- The 8-step research protocol
- Topic scoring weight distribution
- Environment sanitization procedures

Once this spec was complete, everything was crystal clear.

In the implementation session, a single instruction — "implement plan-a-implementation.md" — generated all 8 files at once. Including CLI flag verification, auth checks, and full execution testing, there were zero notable errors.

**Three rounds of planning made implementation instant.** It sounds paradoxical, but this has been my consistent experience across multiple Claude Code projects.

---

## The Finished System

### Project Structure

```text
daily-research/
├── config.toml                          # Topic sources & scoring criteria
├── past_topics.json                     # Topic history (dedup)
├── prompts/
│   ├── research-protocol.md             # Research protocol (core)
│   └── task-prompt.md                   # Execution instructions (7 lines)
├── templates/
│   └── report-template.md               # Report format definition
├── scripts/
│   ├── daily-research.sh                # Wrapper called by launchd
│   └── check-auth.sh                    # OAuth auth check
├── com.shimomoto.daily-research.plist   # launchd config (daily 5:00 AM)
└── logs/                                # Execution logs
```

No Python files. Shell scripts are the infrastructure; prompts are the application logic.

### Execution Flow

```text
launchd (5:00 AM)
    ↓
daily-research.sh (environment sanitization + auth check)
    ↓
claude -p "$(cat prompts/task-prompt.md)" \
  --append-system-prompt-file prompts/research-protocol.md \
  --allowedTools "WebSearch,WebFetch,Read,Write,Glob,Grep" \
  --dangerously-skip-permissions \
  --max-turns 40 --model sonnet \
  --output-format json --no-session-persistence
    ↓
Claude Code autonomously follows research-protocol.md:
  [1] Load config.toml + past_topics.json
  [2] WebSearch across topic sources → scoring → select 2 topics
  [3] Self-generate 5 "key questions" per topic
  [4] Multi-stage research (WebSearch × 20 + WebFetch)
  [5] Generate 2 reports → save to Obsidian vault
  [6] Update past_topics.json
    ↓
macOS notification on completion
```

---

## The Core Decision: `--append-system-prompt-file`

The most critical CLI flag choice was between `--append-system-prompt-file` and `--system-prompt-file`.

| Flag | Behavior | Risk |
|------|----------|------|
| `--system-prompt-file` | **Replaces** the default system prompt entirely | May lose Claude Code's tool usage capabilities |
| `--append-system-prompt-file` | **Appends** to the default | Preserves Claude Code's judgment while injecting protocol |

Full replacement risks losing Claude Code's built-in knowledge of how to use WebSearch, Write, and other tools. Appending preserves those default capabilities while layering on the research protocol.

This is the "prompts as code" design philosophy. Claude Code already has web search, file I/O, and pattern matching capabilities. Instead of writing Python orchestration code, you just control the decision logic through prompts.

---

## Environment Sanitization: A Billing Pitfall

The processing at the top of `daily-research.sh` is quietly critical:

```bash
# Remove API key to prevent per-usage billing
unset ANTHROPIC_API_KEY

# launchd starts with minimal PATH. Load user environment.
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
[ -f "$HOME/.zshrc" ] && source "$HOME/.zshrc" 2>/dev/null || true
```

If the `ANTHROPIC_API_KEY` environment variable exists, Claude Code switches from Max plan OAuth auth to per-usage API key billing. Many developers have API keys set in their environment. Forget the `unset`, and that $2.15 per run actually gets charged.

Also, launchd starts with minimal environment variables, so the `claude` command won't be in PATH. Loading the shell environment is essential.

---

## Topic Selection Scoring Design

Scoring criteria are defined in config.toml, and Claude autonomously evaluates candidates.

**Tech Trends:**

| Criterion | Weight | Intent |
|-----------|--------|--------|
| Novelty | 30% | No similar topics in past_topics.json |
| Signs of movement | 25% | Actively evolving, not static knowledge |
| Buildability | 25% | Could I build something with my skills? |
| Whisper trend factor | 20% | Changes most people haven't noticed yet |

**Personal Interests:**

In addition to the above, a "tech × personal interest intersection" bonus (20%) is added. Topics at the crossroads of technology and personal hobby domains get priority.

Humans only design the criteria. Scoring and selection are handled autonomously by Claude.

---

## Results

Here are the results from the first full execution test:

| Metric | Result |
|--------|--------|
| Duration | ~10 minutes (588 seconds) |
| Turns | 51 |
| WebSearch calls | 20 |
| Displayed cost | $2.15 |
| Actual cost (within Max plan) | **$0** |

Two reports were generated:

**Tech Trend: "OpenAI Frontier — A New Era of Enterprise AI Agent Management"**
Captured breaking news from February 5, 2026. 10 sources cited. Analyzed the inflection point where AI agents shift from "building" to "management and integration," proposing 3 development ideas including a multi-agent integration dashboard.

**Personal Interest:** A deep research report in a non-tech domain I follow personally. 12 sources cited. Getting the same quality of report in hobby domains was a pleasant surprise.

Each report includes a "Development Ideas" section evaluating technical feasibility, estimated demand, and skill fit. Hints for "what to build next" arrive every morning.

---

## When the Agent Exceeds the Plan

One interesting phenomenon occurred with the past_topics.json (topic history) schema.

**Schema defined in the plan:**

```json
{
  "date": "2026-02-14",
  "track": "tech",
  "topic": "Rapid Growth of MCP Server Ecosystem",
  "tags": ["AI", "MCP", "DevTools"],
  "filename": "2026-02-14_tech_mcp-server-ecosystem.md"
}
```

**Schema Claude actually generated:**

```json
{
  "date": "2026-02-14",
  "track": "tech",
  "title": "OpenAI Frontier - A New Era of Enterprise AI Agent Management",
  "slug": "openai-frontier-enterprise-ai-agent-management",
  "keywords": ["OpenAI", "Frontier", "AI Agents", "Enterprise"],
  "summary": "OpenAI announced on February 5..."
}
```

`topic` → `title`, `tags` → `keywords`, `filename` → `slug`, and `summary` was added. Claude interpreted the protocol and autonomously chose a "better" schema.

The detailed spec focused on "what to achieve" without over-constraining "how to implement it." That's likely why this happened. Spec granularity design is something I've learned across multiple projects.

---

## Operational Challenge: OAuth Token Lifespan

The sole operational issue is that Claude Code's OAuth token expires after about 4 days.

As a workaround, `check-auth.sh` pre-checks auth status and sends a macOS notification if it's expired. Launching `claude` from the terminal about twice a week to refresh the token keeps things running smoothly.

It's not fully unattended, but the "read reports over morning coffee" experience works well enough.

---

## Max Plan Economics

| Metric | Value |
|--------|-------|
| Displayed cost | $2.15/run |
| Actual cost (within Max plan) | $0 |
| 30 days/month, no extra charges | Yes |
| 5-hour rolling window | Completes at 5 AM → resets by late morning |

If execution completes at 5:00 AM, the 5-hour window resets by late morning. Daytime interactive usage is completely unaffected.

---

## Summary: Three Design Principles

1. **Spend the most time on planning.** Implementation is fast with Claude Code. The bottleneck is deciding what to build. Three sessions of iterating on research and planning, then creating a detailed spec, meant implementation went through on the first try.
2. **Prompts are code.** Instead of writing Python orchestration, delegate decision logic to prompts. Use `--append-system-prompt-file` to inject a protocol without killing default capabilities.
3. **Start minimal, expand later.** Plan A (Claude Code standalone) delivered sufficient quality. If search quality falls short, there's room to upgrade with Gemini CLI.

If you have a Max plan and haven't tried `claude -p`, give it a shot. Zero Python code can accomplish more than you'd expect.
