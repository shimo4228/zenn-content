---
title: "Building a Claude Code × Kimi K2.5 Hybrid Environment: Opus Designs, K2.5 Implements"
emoji: "🤝"
type: "idea"
topics: ["claudecode", "kimi", "ai", "agents", "devtools"]
published: true
---

Claude Code (Opus 4.6) is the flagship model in the Claude family, excelling at complex design decisions. However, its per-token pricing can be a concern. Using Opus for routine implementation tasks feels wasteful.

That's where Moonshot AI's **Kimi K2.5** comes in.

## Why Kimi K2.5?

Kimi K2.5 is a 1-trillion parameter MoE model released in January 2026. It operates as a CLI-based coding agent called "Kimi Code," autonomously handling file edits, command execution, and testing in the terminal—just like Claude Code.

Its standalone performance alone deserves attention.

| Benchmark | Kimi K2.5 | Claude Opus 4.5 | GPT-5.2 |
|---|---|---|---|
| SWE-Bench Verified | 76.8% | 80.9% | 80.0% |
| AIME 2025 | **96.1%** | 92.8% | — |
| LiveCodeBench v6 | 85.0% | — | — |

It approaches Opus on SWE-Bench and surpasses it in mathematical reasoning. Getting this performance on the Moderato plan ($19/month at the time of writing, 2048 requests/week) is excellent value.

But Kimi K2.5's true differentiator isn't benchmark scores. It's **Agent Swarm**.

### Agent Swarm: The Swarm Intelligence Concept

Agent Swarm is an architecture that launches up to 100 sub-agents simultaneously, executing up to 1,500 tool calls in parallel. An internal orchestrator decomposes tasks into parallelizable subtasks and distributes them to specialized agents (AI Researcher, Fact Checker, etc.).

On BrowseComp, the standard mode's 60.6% jumps to **78.4%** with Agent Swarm, while execution time is reduced by up to 4.5x. Moonshot AI's swarm intelligence philosophy: "A group of moderately intelligent models often outperforms a single highly intelligent model on practical tasks."

### Design Insight: Strengths and Weaknesses of Swarm Intelligence

Analyzing the benchmarks and Agent Swarm's mechanics, I formed a hypothesis.

Kimi's strength lies in **parallel execution power**. It truly shines when multiple agents execute clearly specified tasks simultaneously. Conversely, high-level design decisions—"what to build" and "how to design it"—fall outside swarm intelligence's domain. Kimi's internal orchestrator is optimized for task decomposition and parallelization, not for "higher-level orchestrator" roles like architecture design or trade-off decisions.

In other words, **Kimi is an excellent worker, but not suited to be an orchestrator**. So the natural arrangement is: Opus acts as the orchestrator (design, decisions, review), while Kimi handles the work (implementation, testing).

One more consideration: how to instruct Kimi. If you pass a human-oriented plan ("fix the auth module") as-is, Kimi will spend time exploring "which file?" and "what are the completion criteria?" To leverage swarm intelligence's parallel execution power, agents need structured specifications with concrete file paths, verification commands, and parallelization hints. I call this **spec.md**.

## Architecture: Orchestrator + Worker

From this analysis, I designed the following setup. Opus creates the plan, converts it to spec.md after approval, and passes it to Kimi.

```text
User
  ↓ Task request
Claude Code (Opus 4.6) — Orchestrator
  ├── Plan creation (design decisions)
  ├── Kimi delegation judgment
  ├── Plan → spec.md conversion
  ├── Dispatch
  └── Review
        ↓ spec.md
Kimi K2.5 — Worker
  ├── Implementation based on spec (leveraging swarm intelligence)
  ├── Test execution
  └── Result return (on isolated branch)
```

This combines Opus's design capabilities with Kimi's execution power. Kimi's changes always happen on an isolated branch, merged only after Claude's review—a safety design that enables "just throw it to Kimi" confidence.

## Initial Design: Two-Step Commands

My first implementation used two slash commands:

```text
/kimi-spec <task summary>    → Generate spec.md
/kimi-dispatch <spec-path> → Pass to Kimi for execution
```

This worked. But using it revealed cognitive load: **users had to remember two commands**.

## The Turning Point: "Can We Integrate into Plan Mode?"

Claude Code has a plan mode (toggle with `Shift+Tab` or `/plan`). For complex tasks, it creates a plan that users approve before implementation. By hooking into this flow, users wouldn't need to learn new commands.

```text
Standard flow:
1. User requests task
2. Claude creates plan
3. User approves → Claude implements

Hybrid flow:
1. User requests task
2. Claude creates plan
3. User approves with choice:
   - "Claude implements" → Standard flow
   - "Delegate to Kimi" → Plan → spec conversion → Kimi dispatch
```

From the user's perspective, it's just "one more option on the usual approval screen." Zero learning curve.

## Is spec.md Really Necessary? — A Design Discussion

Here I paused. If we're integrating with plan mode, couldn't we just pass the plan file directly to Kimi? Is the spec.md conversion step unnecessary overhead consuming Opus tokens?

I actually considered reverting to "just pass the plan directly." But comparing them calmly, their roles are clearly different.

| | plan | spec.md |
|---|---|---|
| **Audience** | Human + Claude | Kimi (autonomous agent) |
| **Path specification** | "Fix auth module" | `MODIFY src/auth/handler.ts` |
| **Completion criteria** | "Tests pass" | `pytest --cov=src` achieves 80%+ |
| **Parallel hints** | None | `[INDEPENDENT]` tag |

**Plan and spec have different audiences.** A plan is for human reading and judgment; a spec is instructions for autonomous agents to execute without hesitation.

Kimi K2.5 is smart enough to work with vague instructions. But under the Moderato plan's **2048 requests/week** constraint, waste from Kimi "searching around" for steps is significant.

- **Opus conversion cost**: A few thousand tokens (cheap)
- **Kimi step savings**: 10-20 steps/task (directly impacts quota)

Spec conversion is an **investment in quota conservation**. I decided to keep it.

## Implementation: Having Kimi Create the Rules

As the first real-world test of the hybrid environment, I delegated the creation of "plan mode integration rules" to Kimi itself.

### spec.md Content

```markdown
# Spec: 001 -- Kimi Plan Integration

## Tasks
### Task 1: Create Kimi Delegation Rules [INDEPENDENT]

Files to create:
- CREATE ~/.claude/rules/common/kimi-delegation.md

Requirements:
- When to Suggest (proposal criteria)
- When NOT to Suggest (prohibitions)
- Plan Approval Flow (approval process)
- Plan to Spec Conversion (conversion procedure)
- Quota Awareness (quota consciousness)

Verification:
- Confirm 5 sections exist
- Confirm reference to kimi-wrapper.sh
```

### Kimi Execution Results

```bash
$ kimi --prompt "$(cat spec-001.md)" --thinking --yolo --max-steps-per-turn 100
```

Actually, `kimi-wrapper.sh` handles model specification and working directory assignment, but the essential options are above.

**First dispatch result: about 10 seconds. 6 steps.** Read 3 existing rule files → Understood format → Generated 119-line rule file → Verification passed.

Because the spec specified concrete paths, section structure, and verification commands, Kimi didn't hesitate at all about "what to create."

### Quality of Generated Rules

```markdown
# Kimi Delegation

## When to Suggest
- Simple implementation tasks — boilerplate, CRUD, standard patterns
- Mechanical changes across multiple files — renaming, format unification
- User explicitly specifies Kimi
...

## Quota Awareness
| Change Scale | Recommended Approach |
|----------|---------------|
| 1-2 files, under 50 lines | Direct Claude implementation |
| 3+ files, 100+ lines | Actively propose Kimi delegation |
```

Consistent with existing rule formats, with concrete judgment criteria. Passed Opus review without changes.

:::details File Structure (Full Picture)

Final file listing for the hybrid environment:

```text
~/.kimi/
├── config.toml          # Moderato profile (max_steps=100)
├── config.swarm.toml    # Swarm backup
└── credentials/         # OAuth credentials

~/.claude/
├── bin/
│   ├── kimi-wrapper.sh          # Claude → Kimi dispatcher
│   └── kimi-profile-switch.sh   # Moderato ⇔ Swarm toggle
├── commands/
│   ├── kimi-spec.md             # spec generation (manual)
│   └── kimi-dispatch.md         # dispatch & review (manual)
├── rules/common/
│   └── kimi-delegation.md       # plan mode integration rules ← Kimi created
└── templates/hybrid/
    └── spec-template.md         # spec template
```

:::

<!-- textlint-disable -->
:::details Moderato Plan Optimization Settings
<!-- textlint-enable -->

Constraints and corresponding settings for Kimi Moderato plan ($19/month):

| Setting | Value | Why |
|------|-----|-----|
| max_steps_per_turn | 100 | Step count = request consumption |
| tool_call_timeout_ms | 120000 | Maintain for parallel tool calls |
| wrapper TIMEOUT | 300s | 300s is enough for 100 steps |

If upgrading to Swarm plan, `kimi-profile-switch.sh swarm` toggles it instantly.

:::

## Key Learnings

### 1. Spec Precision = Quota Efficiency

Specifying concrete paths, section structures, and verification commands in spec.md dramatically reduces Kimi's exploration steps. This time: 6 steps to completion. With vague instructions, it would have needed 20-30 steps.

### 2. Integration with Existing Workflows is Key

Rather than teaching new commands, embedding in existing plan mode has overwhelmingly lower adoption barriers. From the user's view, it's just "one more option on the approval screen"—near-zero learning cost.

### 3. Safety Design Between Agents

Kimi's changes always happen on isolated branches. Merging only after Claude review enables casual "just throw it to Kimi" confidence.

## Summary

First dispatch succeeded in 10 seconds with 6 steps. Confirmed that the spec conversion overhead significantly improves Kimi's quota efficiency.

This setup's essence is "dividing roles between LLMs and embedding handoffs into existing workflows." At $19/month for Kimi Moderato plus Claude Code, individuals can build a practical multi-agent development environment.

Next steps: exploring parallel dispatch for multiple tasks and automatic PR creation from Kimi results.
