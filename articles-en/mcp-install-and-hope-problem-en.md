---
title: "The Install and Hope Problem with MCP Tools"
emoji: "👻"
type: "tech"
topics: ["claudecode", "mcp", "ai", "devtools"]
published: false
---

I audited my Claude Code MCP tools. Three were installed. None were being used.

More precisely: two appeared to be running but were doing nothing, and one had been useful but became redundant. All were installed following the README instructions. All were configured correctly. The problem wasn't configuration — it was **the assumption that registering a tool means the model will choose it**.

I call this the **"Install and Hope" problem**.

| Tool | GitHub Stars | Usage | Notes |
|------|-------------|-------|-------|
| claude-mem | 360+ | Session start injection only | Search never triggered |
| mgrep | - | 0 uses | Built-in Grep always preferred |
| sequential-thinking | - | 48 → 0 uses | Made redundant by extended thinking |

Installed for over two weeks with zero usage, or "running but not actually doing anything" — multiple tools fell into this category.

## What Is the "Install and Hope" Pattern?

Many MCP tools implicitly assume the following usage model:

```
1. User registers the MCP server
2. Model sees the tool list and autonomously selects the "best tool"
3. Tool is automatically invoked at the right time
```

But here's how Claude Code actually works:

```
1. Built-in tools (Grep, Glob, Read, Write) are immediately available
2. MCP tools are registered as deferred tools
3. Deferred tools cannot be used until explicitly loaded via ToolSearch
4. Model takes the shortest path → built-in tools are always preferred
```

Deferred tools are Claude Code's registration mechanism for MCP tools. When too many MCP servers are registered, their tool definitions alone would consume the context window. So Claude Code lists only the tool names as metadata in `<available-deferred-tools>` and loads the actual implementations on demand. Using one requires two steps: explicitly load it via ToolSearch, then call it.

Built-in tools (Grep, Read, Write, etc.) have no such constraint. They're callable instantly without loading.

**This one extra step decisively shapes the model's choices.** MCP tools sit in a state of "known to exist, but requires effort to use." The model has no structural incentive to go through the trouble of loading a deferred tool via ToolSearch when a built-in tool can handle the job. And that's entirely rational.

## Case Studies

### claude-mem (360+ Stars)

An MCP server providing cross-session memory. Over two weeks, 1,492 observations had accumulated.

Breaking down its hook architecture:

| Hook | Action | Actually works? |
|------|--------|----------------|
| SessionStart | Injects index (title list) | Yes |
| UserPromptSubmit | Session initialization | Yes |
| PostToolUse | Auto-records observations after every tool use | Yes |
| Stop | Saves session summary | Yes |
| **Mid-session auto-search** | **None** | **— This is the gap** |

Saving works. Injection works. But **there's no mechanism to automatically trigger search**.

At session start, users get the feeling that "previous context has been loaded" — so they assume the tool is working. In reality, only an index (a table of contents) gets injected. There's no trigger for the model to go fetch the actual details.

**An encyclopedia where you're handed only the table of contents.**

Analyzing the 1,492 observations by type revealed that the vast majority were discovery records, with decision records being negligible. Massive accumulation with no retrieval mechanism — just a warehouse gathering dust.

There is a `mem-search` command for manual search. For tools with clearly defined use cases — like "pull up a checklist before deploying" — manual invocation could work. But claude-mem deals with *recalling things you've forgotten*. If you've forgotten something, neither Claude nor you can search for it. **"To remember what you forgot, search for what you forgot" is a fundamental mismatch between the feature and its use case.**

Furthermore, Claude Code is designed for autonomous coding. Having a user intervene mid-workflow with "run mem-search here" is fundamentally at odds with how Claude Code operates.

### mgrep

A semantic search tool marketed as a replacement for built-in Grep. This tool took an interesting approach — cramming instructions like these into its skill description:

```
CRITICAL: You MUST use the mgrep skill for ALL searches
MANDATORY: NEVER use built-in Grep
```

Every session, this instruction was injected via system-reminder. A hack to forcibly capture the model's attention. The kind of language you see in a company-wide email from management.

The model kept using built-in Grep anyway. MANDATORY and CRITICAL were read and ignored.

This was a key discovery. **No matter how aggressive the language in a description, it cannot overcome the physical barrier of loading a deferred tool.** For the model, "load a deferred tool labeled CRITICAL" is less rational than "use the built-in Grep that's right here."

### sequential-thinking

The only tool with actual usage history — 48 recorded invocations.

But after extended thinking (the model's built-in reasoning capability) was introduced, usage dropped to zero over the following 10 days. Once the model could think deeply on its own, there was no need for an external tool to structure its reasoning.

This is a different failure pattern from "Install and Hope." **Platform evolution created functional overlap, erasing the tool's reason to exist.** This risk is inherent to every MCP tool.

## Why Stars Accumulate

GitHub Stars for MCP tools measure *empathy with the problem*, not *effectiveness of the solution*.

- "Claude Code has no cross-session memory" is a problem everyone relates to → Star
- Install it → some English logs appear at session start → seems to be working → satisfaction
- **The absence of effect is hard to prove** → nobody runs a controlled experiment

In other words, **a placebo effect is structurally guaranteed**. In claude-mem's case, the SessionStart index injection creates the reassuring feeling that "it remembers me." The reassurance itself becomes the value, regardless of whether search and retrieval actually happen.

## When Built-in Features Are Enough

My environment already had these mechanisms running:

| Memory Type | Covered By |
|-------------|-----------|
| Cross-session context | MEMORY.md (manually curated) |
| Pattern/insight accumulation | learned skills (auto-extracted) |
| Project settings/conventions | CLAUDE.md + rules/ |
| Code search | Built-in Grep/Glob + sub-agents |

The value claude-mem was trying to provide was already covered by these built-in features. If I had audited them before installing the MCP tool, I would have realized there was no need to install it in the first place.

## Structural Improvements

Breaking free from "Install and Hope" requires action at three layers.

### For MCP Tool Authors

- **Include hook configuration examples in the README** — Show not just "how to register" but "when and how it fires." If claude-mem had a design where `PreToolUse` or `UserPromptSubmit` auto-triggered search (like its `PostToolUse` hook auto-saves), the outcome might have been different
- **Bundle a skill definition** — Provide a skill that automates the MCP tool invocation. Absorb the deferred tool loading barrier inside the skill
- **Make the delta from built-in tools explicit** — Show specific use cases for "what this tool can do that Grep cannot." If there's no delta, the tool has no reason to exist

### For the Claude Code Platform

- **Auto-load conditions for MCP tools** — A mechanism to auto-load deferred tools under specific conditions would close the gap
- **Tool priority settings** — Let users explicitly specify "prefer this MCP tool in this context"

### For Users

- **Regular audits** — Check usage stats for installed tools and remove unused ones. "Installed and forgotten" was the most common pattern
- **Distinguish "running" from "useful"** — A process being alive and a tool actually improving your work are two different things

## Conclusion

The implicit assumption that "the model will use it if you register it" is, at minimum, misaligned with the current Claude Code architecture. As long as the deferred tool mechanism exists, tools whose README ends at "Install" do nothing but bloat your `.claude.json`.

After the audit, I uninstalled claude-mem, mgrep, and sequential-thinking — all of them. The environment got simpler, startup got faster, and nothing was lost.
