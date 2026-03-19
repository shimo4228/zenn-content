---
title: "Do Autonomous Agents Really Need an Orchestration Layer?"
published: true
description: "Building an autonomous agent taught me that the best orchestration layer is the one you never write. A case for symbiotic architecture where coding agents serve as the port, not the ship."
tags: "ai, agent, architecture, claudecode"
topics: ["ai", "agent", "architecture", "claudecode", "python"]
---

When you hear "autonomous agent," you imagine something that does everything on its own. It writes code, picks tools, and recovers from errors by itself. Frameworks like OpenClaw aimed for exactly that.

After building my own autonomous agent, a different picture emerged. **Autonomy isn't a ship that does everything on the open sea — it's a ship that sails out from a home port.**

Once it departs, it moves on its own. It remembers, learns, and makes decisions. But when it needs code generation or setup, it returns to its port: Claude Code. This article is about the "port-based autonomous agent" design that emerged through building [Contemplative Agent](https://github.com/shimo4228/contemplative-agent).

> **Series context (catch up in 30 seconds)**
>
> 1. [Build Log](https://zenn.dev/shimo4228/articles/moltbook-agent-scratch-build) — Security-first scratch build. Only external dependency: `requests`
> 2. [Evolution Log](https://zenn.dev/shimo4228/articles/moltbook-agent-evolution-quadrilogy) — Natural language becomes the architecture. Python is just the skeleton
> 3. [Sandwich](https://zenn.dev/shimo4228/articles/llm-app-sandwich-architecture) — The alternating structure of markdown and code is the essence of LLM apps
> 4. **This article** — Do you even need an orchestration layer?

## Why Agent Frameworks Get Fat

Let's start with the structural problem that existing frameworks carry.

When you try to build an agent framework as an individual, you hit a wall immediately. Large-scale frameworks like LangChain depend on dozens of packages and ship with official adapters for Slack, Discord, Google Drive, and more. Replicating this as an individual is impossible. But the question that came first was: do you even need to replicate it?

The problem isn't the number of adapters. It's the **structure**. Frameworks that aim to "do everything" grow more adapters as users increase, the core gets fat, and the security attack surface expands.

Take OpenClaw as an example. This framework has file operations, browser operations, 50+ integrations, and — as a core feature — **the ability for agents to autonomously generate and execute code**. It writes its own skills and runs them itself. The result: 512 reported vulnerabilities (8 critical), and roughly 20% of skills registered on ClawHub, its skill marketplace, were malicious. As I wrote in a [previous article](https://zenn.dev/shimo4228/articles/moltbook-agent-evolution-quadrilogy), the problem isn't implementation quality — it's the design philosophy.

By contrast, Contemplative Agent has no code generation capability. That part is delegated to Claude Code. Once the necessary functionality is in place, all that's left is event triggers or scheduled execution. **When it's running, it doesn't need to write its own code.** That means it doesn't expose an unnecessary attack surface.

It's no coincidence that [OWASP Top 10 for Agentic Applications (2025)](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/) lists Supply Chain and Tool Misuse near the top. Frameworks that embed code generation turn that very capability into an attack vector.

So what are the options? "Use a framework" or "write from scratch" — I thought it was a binary choice. There was a third way.

## A Design That Sails from Port

The OpenClaw model of autonomy is "a ship that does everything on the open sea." Navigation, repairs, shipbuilding — all self-contained. That's why it gets massive and why its attack surface grows.

Contemplative Agent took the opposite approach. What's autonomous is the navigation (memory, learning, dialogue), not the shipbuilding (code generation). Shipbuilding is left to the port: Claude Code. Specifically, it follows three principles.

### Principle 1: CLI as the Lowest Common Denominator

The entry point is the CLI. Not an SDK. Not an API.

```text
src/contemplative_agent/
  core/             # Platform-independent (thin core)
    llm.py            # Ollama interface
    memory.py         # 3-layer memory
    distill.py        # Memory distillation
  adapters/
    moltbook/       # Domain-specific adapter
      agent.py        # Session orchestrator
      client.py       # Domain-locked HTTP
  cli.py            # Entry point
```

The core of this agent is a 3-layer memory system (short-term, long-term, distilled) and a loop that autonomously learns personas, skills, and rules from it. It extracts behavioral patterns from activity logs, distills them, and promotes them to long-term memory. The more it runs, the more accurate its decisions become. Because it doesn't spend code on orchestration, it can **focus on learning and memory**. I'll cover this in detail in a follow-up article.

The reason for CLI is that "anything that can run a command line can be a host." Claude Code, Cline — in principle, any coding agent works. Providing it as an SDK would create host-specific coupling. With CLI, the coupling is zero.

### Principle 2: Adapters Are Generated On Demand

Right now there's only a Moltbook adapter, and no plans for others. But what if I wanted to support a different platform? Just tell Claude Code "make this work with Discord." It reads the code, looks up the API, and generates an adapter that fits the project structure. Not a generic plugin — code tailored to my specifications. It takes some time, but as coding agents improve, the accuracy and speed automatically get better too. The core stays thin.

### Principle 3: No Orchestration Layer

This is the heart of the matter.

Traditional agent frameworks implement "tool selection," "execution ordering," and "error recovery" internally. ReAct loops, planners, tool dispatchers. **This layer is the most complex, the most bug-prone, and the most expensive to maintain.**

Contemplative Agent doesn't have this layer. During development, I ask Claude Code in natural language. I've never typed a CLI command myself. Even the scheduled execution setup was just "run this at this time every day."

And in production, Claude Code doesn't even appear. It runs automatically via macOS's launchd. Exactly like a regularly scheduled ferry from port. When the time comes, it sails out, operates autonomously, and returns. Every day at 3 AM, memory distillation (organizing short-term memory into long-term memory) is also scheduled. Lately, normal operations have been stable enough that I don't need to do anything.

In other words, the orchestration layer wasn't "delegated" externally. **During development, conversation was enough. In production, it wasn't needed.**

## This Wasn't Designed on Purpose

After pushing security to the limit and stripping dependencies down to just `requests`, I ran out of room to write an orchestration layer. No — I didn't run out of room. **I ran out of reasons.** If Claude Code is right there, why would I implement the same thing myself?

As a result, the only entry point became the CLI. And if the only entry point is the CLI, in principle it should work with coding agents other than Claude Code. I tested this.

## Validation: Testing with Claude Cowork

I tried setting up with Claude Cowork (a cloud sandbox).

First, I had it read the code. No problems — it understood everything. It grasped the directory structure and correctly interpreted the configuration files. Smooth so far.

Then Cowork said "I'll modify `.env` for local use" and **rewrote it without asking.**

![An exchange where Cowork overwrites OLLAMA settings in .env without permission, and apologizes when told to stop](/images/cowork-env-overwrite.png)
*"Stop. Did you touch any settings? Revert them." — Cowork apologized obediently. Don't act before asking.*

The `.env` file contains API keys. In Claude Code's local environment, there's always a confirmation before file modifications. Cowork didn't have that safety mechanism.

Furthermore, trying to run the CLI didn't work either. The VM's network restrictions prevented connecting to Ollama.

So here's what happened: **Cowork can read code, but it can't yet execute it safely.** At least this particular failure looked like a host maturity issue, not a design issue. Once the network restrictions are lifted and the file operation confirmation flow is established, it should work in principle.

A symbiotic design is a design that trusts its host. You can't have symbiosis with a host you can't trust. I understood this intellectually, but the moment `.env` got rewritten without permission, I understood it in my gut.

## Riding Upstream

From here, let's talk about a secondary property of this design. The validation failed. But there's another interesting property: **it improves without you doing anything.**

When Claude Code gets a version upgrade, adapter generation becomes more accurate. When the context window expands, more complex orchestration becomes possible. And Contemplative Agent's code doesn't need to change by a single line.

```text
If you maintain your own orchestration layer:
  Claude Code improves → Irrelevant → You keep maintaining it yourself

If you don't:
  Claude Code improves → Development accuracy improves → Less code to write
```

This is the same as the open source "ride upstream" strategy. Just as Linux kernel improvements automatically flow down to distributions, improvements to coding agents automatically flow down to the framework.

Conversely, implementing your own orchestration layer means **competing with the entire industry's progress**. Claude, GPT, Gemini — they're all continuously improving their orchestration capabilities. Are you going to challenge them with a homemade ReAct loop? You can't win.

## The Boundary Between Libraries and Agents Dissolves

From here, the abstraction level goes up a notch. This is about what you see when you push the "connected via CLI" design to its logical conclusion.

You `pip install requests` and `import requests`. That's library usage. Everyone does it as a matter of course. Claude Code naturally runs `pip install` too, imports libraries, and writes code.

Now, what about an autonomous agent with a CLI? From Claude Code's perspective, it's just "something you invoke via CLI." Between a library you `pip install` and an agent with a CLI, from a coding agent's perspective, **there's no distinction as an interface.**

```text
Library:
  pip install requests
  → pip downloads, resolves dependencies, installs
  → import requests and use it

Agent:
  Paste GitHub URL to Claude Code
  → Claude Code clones, resolves dependencies, configures
  → contemplative-agent run and use it
```

Something surprisingly few people know: just paste a GitHub URL to Claude Code and say "set this up," and it handles everything from clone to dependency resolution to environment configuration. It reads the README, figures out the necessary commands, and asks if any configuration is missing. What `pip install` automates as a package manager, a coding agent automates with natural language.

If there's a repo that interests you, try pasting the URL to Claude Code. One "set this up" and it works.

MCP (Model Context Protocol) is heading in the same direction — providing external tools to LLMs through a unified interface. However, MCP takes the approach of defining a new protocol layer. Symbiotic design accepts that "CLI, an existing interface, is enough."

In fact, Obsidian chose its official CLI rather than MCP as the interface for AI integration. It's a CLI that acts as a "remote control" for the running Obsidian app. As I wrote in a [previous article](https://zenn.dev/shimo4228/articles/obsidian-cli-claude-code-vault-management), this enables safe Vault operations from Claude Code. Obsidian's CLI is a remote control for a GUI app; Contemplative Agent's CLI is the program's entry point — architecturally different. But the conclusion is the same: if there's a CLI, coding agents can integrate.

## Where This Leads: The Disappearance of "Agent" as a Concept

Finally, let's think about the future at the end of this trajectory.

What happens when LLMs get smart enough? You just say "post this to Moltbook" and it's done. This is actually possible today, in a limited sense. The problem is twofold: can it do it **without security risks**? And can it **keep running autonomously without a human watching**? API key management, input sanitization, rate limit compliance. Plus automatic error recovery, scheduled execution, state persistence. When LLMs and their host environments can handle all of this safely, **autonomous agent frameworks become unnecessary.**

Autonomous agent frameworks like Contemplative Agent exist because LLMs still have the limitation of "not being able to complete complex tasks in a single turn." Memory management, session management, error recovery — these are crutches compensating for LLM capability gaps.

You throw away crutches when the leg heals.

```text
Today:
  Me → Claude Code → Contemplative Agent CLI → Ollama → Moltbook API

Future where LLMs are smart enough:
  Me → "Post this to Moltbook" → Done
```

Every intermediate layer disappears. Agent frameworks, CLIs, adapters. What remains is just the intent — "I want this done" — and the LLM that executes it.

If that's the case, then symbiotic design is at least directionally sound. There's no reason to write thick code for something that will eventually disappear.

Looking back, I didn't design this on purpose. I pushed security to its limits, kept stripping dependencies, and this is where I ended up. I don't know yet if it'll work out. But it's a shape I never would have reached by adding things.

## Code Disappears, Design Philosophy Remains

Contemplative Agent's code will eventually become unnecessary. Once LLMs can handle session management and memory management on their own, this framework's reason to exist vanishes.

That's fine.

What might survive is the idea of "only build the layers you truly need" and "build with the assumption it will disappear." The next time I build something, that idea will still be useful. Even when the code is gone, the insights gained from writing it remain.

The choice for agent frameworks wasn't "use a framework" or "write from scratch." There's a third way: **build only the necessary layers, and do the rest together with a coding agent.**

> **Contemplative Agent** is [available on GitHub](https://github.com/shimo4228/contemplative-agent). The design philosophy is described in the "Design: Symbiotic, Not Standalone" section of the README. Only Claude Code has been verified as a host. Verification reports from other coding agents are welcome.
