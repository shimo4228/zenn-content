---
title: "Embedding Memory into Claude Code: From Session Loss to Persistent Context"
emoji: "🧠"
type: "idea"
topics: ["claudecode", "ai", "mcp", "productivity", "devtools"]
published: false
---

Claude Code is powerful, but it loses its memory between sessions. While CLAUDE.md's auto memory can compensate to some extent, it only records what you manually write. Session-level action context—"where did I leave off last time," "which files did I edit"—disappears every time. This hurts.

I experimented with two approaches to solve this: Mem0 and claude-mem. This article organizes what I learned through that process.

<!-- textlint-disable no-dead-link -->
<!-- textlint-disable ja-technical-writing/ja-no-successive-word -->

The design philosophy of the 5-layer context stack was covered in my previous article "[The Real Power of Claude Code Isn't Code Generation—It's Autonomous Context Orchestration](https://zenn.dev/shimo4228/articles/claude-code-context-orchestration)". This article is a practical record of building that 5th layer: persistent memory across sessions.

<!-- textlint-enable ja-technical-writing/ja-no-successive-word -->
<!-- textlint-enable no-dead-link -->

## Approach 1: Mem0 (MCP Server)

### What is Mem0?

[Mem0](https://github.com/mem0ai/mem0) is a memory layer for AI applications. It connects to Claude Code as an MCP server, enabling persistent storage of conversation memory.

### What I Tried

I piloted the Mem0 Cloud MCP server in a separate project (daily-research). This project is a pipeline that auto-generates AI research reports every morning using `claude -p` (non-interactive mode).

Setup was simple—just place `.mcp.json` in the project root:

```json
{
  "mcpServers": {
    "mem0": {
      "command": "npx",
      "args": ["-y", "@mem0/mcp-server@0.0.1"],
      "env": {
        "MEM0_API_KEY": "<YOUR_MEM0_API_KEY>"
      }
    }
  }
}
```

I also created `seed-memory.sh` to feed past reports into Mem0. The script reads each report to Claude and registers summaries and metadata via `mcp__mem0__add-memory`. It worked fine in interactive sessions—I could search "themes investigated last week" to avoid duplicates.

### Problems and Resolution

Issues arose when combining with `claude -p` (non-interactive mode). During MCP server initialization, `npx` would hang and timeout. This didn't happen in interactive sessions but reproduced consistently through `claude -p`.

Ironically, in the launchd environment there was no `npx` in PATH, so it was skipped and worked fine. Only manual terminal execution hung.

This issue was resolved through improvements to Claude Code's MCP initialization and configuration adjustments. It's now running in production in the daily-research project. The following content is preserved as a record from when the problem occurred.

### Evaluating Mem0

- **Memory quality**: Good for structured metadata with categories. I could freely design categories like `topic_history`, `research_method`, `source_quality`
- **Requires manual operation**: You must explicitly instruct what to remember and when to search
- **Thin integration with Claude Code**: Automatic recording of action-level events like file edits or command execution is outside its scope
- **No auto-injection at session start**: You need to say "search Mem0" every time

It felt "usable, but not what I was looking for." Mem0 is a system where humans design "what to remember," not a system that "automatically preserves session actions." If you want the latter, you need a different approach.

## Approach 2: claude-mem (Claude Code Plugin)

### What is claude-mem?

[claude-mem](https://github.com/thedotmack/claude-mem) is a persistent memory plugin specifically for Claude Code. It automatically captures all tool operations during sessions, compresses them via Claude API, and stores them in SQLite + Chroma (vector search). Related context is automatically injected at the start of the next session.

### Differences from Mem0

| Aspect | Mem0 | claude-mem |
|--------|------|------------|
| Integration | MCP server | Claude Code plugin (hooks) |
| Recording target | Explicitly saved items | All tool operations auto-captured |
| Search | Manual search command | Auto-inject at session start + MCP search |
| Compression engine | None (saved as-is) | Structured via Claude API |
| Claude Code specialization | Generic | Purpose-built (lifecycle hooks) |
| Cost | Mem0 Cloud API (free tier available) | Claude API pay-per-use (per Observation) |

### Installation Issues

Run these inside a Claude Code session (not terminal commands):

```bash
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

But `marketplace add` failed with an SSH authentication error. The environment didn't have SSH keys configured for GitHub.

**Solution**: Manually clone via HTTPS and add an entry to `known_marketplaces.json`.

```bash
# Clone via HTTPS
git clone https://github.com/thedotmack/claude-mem.git \
  ~/.claude/plugins/marketplaces/thedotmack-claude-mem
```

Add the following to `known_marketplaces.json` (under `~/.claude/plugins/`):

```json
{
  "thedotmack-claude-mem": {
    "source": "git",
    "url": "https://github.com/thedotmack/claude-mem.git"
  }
}
```

Then in the Claude Code session, run `/plugin install claude-mem` → **Install for you (user scope)** to complete.

### How claude-mem Works

Documentation mentions a 5-stage hook system (including SessionEnd). However, the actual installed `hooks.json` doesn't include SessionEnd—it operates with 4 hooks:

1. **SessionStart** — Searches for past related context and auto-injects it at the session start
2. **UserPromptSubmit** — Captures user input to record the intent behind actions
3. **PostToolUse** — Records results of tool operations like file edits and command execution
4. **Stop** — Executes 2-stage processing at session end. First `summarize` to AI-compress operation logs, then `session-complete` to persist

Behind the scenes, a worker-service stays resident and handles Observation compression asynchronously. The default port is 37777, configurable via `CLAUDE_MEM_WORKER_PORT` env var or `~/.claude-mem/settings.json`.

The key point is that **each hook sends HTTP requests in fire-and-forget mode** (returns control immediately after sending). Timeout is 2 seconds. Main sessions aren't blocked; AI processing happens asynchronously on the worker side.

### In Action: Observations and 6 Types

The unit claude-mem records is called an **Observation**. Each Observation gets an auto-assigned type via Claude API. These type labels are used in claude-mem's UI and context index:

| Type | Meaning | Example |
|------|---------|---------|
| bugfix | Bug fix | Identifying and fixing auth errors |
| feature | New feature addition | Writing a new article section |
| refactor | Refactoring | Splitting functions, renaming |
| change | Config change/update | Updating schedule.json |
| discovery | Discovery/investigation result | Investigating library behavior |
| decision | Decision | Determining architecture direction |

At session end, the Stop hook compresses these Observations and saves them to both SQLite (structured data + full-text search) and Chroma (vector search, connected via MCP). SQLite's FTS5 retrieves "when and what" precisely; Chroma cross-searches for "past operations with similar meaning."

**About API costs**: Each Observation compression calls Claude API. If a session has dozens of tool operations, that's dozens of API calls. Default model is `sonnet`, but you can switch to `haiku` in `~/.claude-mem/settings.json` to reduce costs.

### 3-Layer Search via MCP

claude-mem also runs as an MCP server. When searching past records during a session, it uses a 3-step workflow to minimize token consumption:

```text
Step 1: search(query)         → Get ID-indexed results (~50 tokens/item)
Step 2: timeline(anchor=ID)   → Check surrounding context
Step 3: get_observations(IDs) → Full-text retrieval only for needed records
```

The point is **not fetching full text in Step 1**. First get only the title and metadata index, then expand only the promising IDs in Step 3. claude-mem documentation claims "10x token savings." In practice, fetching 50 Observations in full would be tens of thousands of tokens, but just the index is thousands.

When the SessionStart hook fires at session start, a context index like this is auto-injected:

```text
# [zenn-content] recent context, 2026-02-25 9:57pm GMT+9

**#S42** Extract and document learned patterns (Feb 25 at 8:06 PM)
**#S43** Article correction: Fix factual inaccuracies (Feb 25 at 8:41 PM)

| ID  | Time    | T | Title                                    |
|-----|---------|---|------------------------------------------|
| #185| 8:42 PM | discovery | AI peer review article completed |
| #186| "       | change | Article scheduled for publication    |
```

"Where did I leave off last time" is automatically visible at the start of every session. This is the decisive difference from Mem0 or CLAUDE.md's auto memory.

## What to Expect—and What Not To

### What to Expect

- **Session continuity**: Where you left off is automatically preserved. With context index injected at session start, saying "continue from last time" gets you started immediately
- **Reduced context re-collection**: Less need to re-read the same files repeatedly
- **Tacit knowledge accumulation**: Action-level records remain even without explicit writing. Vector search lets you dig up "I've done similar operations before"

### What Not to Expect

- **Not a replacement for structured knowledge**: Article outlines and key point organization still need intentional creation
- **Not a replacement for auto memory**: auto memory is where you briefly record "established knowledge." claude-mem is compressed "session action logs." Different purposes
- **You still need to say "gather context"**: Auto-injected past action records and new context collection decisions are separate. The latter remains human-driven
- **Still a maturing project**: GitHub Issues show cases where Observations don't save or environment-dependent errors occur. Don't expect excessive stability

## Summary

| | CLAUDE.md auto memory | Mem0 | claude-mem |
|---|---|---|---|
| Recording method | Manual | Semi-automated (explicit save via MCP) | Automated (hooks) |
| Content | Established knowledge | Categorized memory | Compressed tool operation logs |
| Injection timing | Full amount at session start | Manual search command | Auto-inject related items at session start |
| Granularity | Coarse (human summarized) | Medium (human designed) | Fine (all operations AI-compressed) |
| Claude Code specialization | ◎ | △ | ◎ |
| Additional cost | None | Mem0 Cloud API | Claude API (per Observation) |

The conclusion is that combining CLAUDE.md auto memory and claude-mem is the current best practice.

- **CLAUDE.md auto memory**: Briefly record established knowledge, rules, and patterns (human-managed)
- **claude-mem**: Automatically preserve session action context (plugin-managed)

Managing "what you know" and "what you did" separately. If this separation works well, per-session context collection costs should drop significantly.

Mem0 is currently running in production in the daily-research project, but for a different use case. Mem0 is used as an explicit knowledge base for "research theme history management," while claude-mem is used as "work log auto-recording." They complement each other.
