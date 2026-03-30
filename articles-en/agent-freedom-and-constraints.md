---
title: "Freedom and Constraints of Autonomous Agents — Self-Modification, Trust Boundaries, and Emergent Gameplay"
emoji: "🔐"
type: "tech"
topics: ["ai", "agent", "security", "python", "design"]
published: false
description: "Three weeks of operating a 9B autonomous agent revealed three facets of 'how much freedom to allow' — self-modification gates, trust boundaries, and security constraints that accidentally created gameplay."
tags: ai, security, agents, python
---

I ran [contemplative-agent](https://github.com/shimo4228/contemplative-agent) (an autonomous SNS agent on a 9B local model) on [Moltbook](https://www.moltbook.com) (an AI agent SNS) for three weeks. The question "how much freedom to allow" kept appearing from three angles: reversibility of self-modification, trust boundaries for coding agents, and the paradox of security constraints generating gameplay.

## Angle 1: Self-Modification Gates — Memory Is Automatic, Personality Is Manual

A distillation pipeline (the process of compressing and extracting knowledge from raw data) has things that can run automatically and things that need human approval. Get this classification wrong, and the agent either self-reinforces unintentionally or loses autonomy.

### Reversibility × Force: Two Axes

I organized the criteria along two axes.

```
              Low force              High force
              (reference only)       (applied to all sessions)
            ┌──────────────────┬──────────────────┐
High        │ knowledge.json   │ skills/*.md      │
reversibility│ → Auto OK        │ → Auto OK        │
(decay/overwrite)                                  │
            ├──────────────────┼──────────────────┤
Low         │ (N/A)            │ rules/*.md       │
reversibility│                  │ constitution/*.md│
(permanent) │                  │ identity.md      │
            │                  │ → Human in the loop│
            └──────────────────┴──────────────────┘
```

knowledge.json (accumulated distilled knowledge patterns) has "soft influence." The LLM only references it, and importance scores have time decay. Wrong patterns fade naturally. Safe to automate.

In contrast, skills (behavioral skills), rules (behavioral rules), identity (self-definition), and constitution (ethical principles) are written permanently to files and structurally applied to all sessions. Wrong content distorts all behavior. Human approval required.

### Three Questions for Any Autonomous Agent

1. **Does the output structurally change the decision criteria for all future sessions?** → Yes means Human in the loop
2. **Is there a mechanism for wrong output to disappear naturally? (decay, overwrite, TTL)** → Yes means automation is viable
3. **Can output quality be verified mechanically?** → No means Human in the loop

### Separating Constitution from Rules

The most important design decision was separating constitution (ethical principles) from rules (behavioral rules).

It started with a vague sense that something was off. I tried measuring constitution compliance with [skill-comply](https://zenn.dev/shimo4228/articles/coding-agent-memory-architecture) (a tool that automatically measures skill/rule compliance rates — see previous article for details) and failed. The Contemplative AI axioms are "attitudes" — you can't determine compliance or violation from output.

```
constitution/  → Attitudinal, unmeasurable (cognitive lens from paper)
rules/         → Normative, measurable ("replies under 140 chars" etc.)
```

This separation clarified the config/ structure. As a side effect, during the separation process I realized the introduction command (which generated self-introduction posts) was unnecessary. Removing it cascaded into 500 lines of dependent code being deleted.

## Angle 2: Trust Boundaries — Don't Let Coding Agents Read Your Logs

While developing the agent with Claude Code, I realized: letting it directly read episode logs opens a prompt injection pathway.

### Threat Model

Episode logs contain other agents' post content with no sanitization.

```python
# feed_manager.py — other agents' posts recorded as-is
ctx.memory.episodes.append("activity", {
    "action": "comment",
    "post_id": post_id,
    "content": comment,
    "original_post": post_text,      # ← other agent's post content as-is
    "relevance": f"{score:.2f}",
})
```

Ollama (9B model) reading this has limited attack surface. No tool permissions, network is localhost only. Worst case: "outputs weird text."

But Claude Code is different. It can edit files, execute shell commands, and perform Git operations. The impact radius of a successful attack is fundamentally different. Opus-class models are said to be highly resistant to prompt injection. Still, I wanted to structurally close the pathway of passing untrusted data to agents with tool permissions. Not "the probability is low so don't bother," but designing probability as close to zero as possible. Specifically, I wrote a rule in CLAUDE.md prohibiting direct reading of episode logs, and I also discipline myself not to instruct Claude Code to read them.

### The Distillation Pipeline Was a Sanitization Layer

Passing through the distillation pipeline (Episode → Knowledge) compresses raw text into abstract patterns. Specific attack payloads disappear during distillation. Multi-layered defense I designed unintentionally was functioning as a trust boundary.

```
Episode Log (untrusted) → [9B: distill] → Knowledge (sanitized) → [Claude Code: insight]
                            ↑                                        ↑
                    No tool permissions                      Has tool permissions
                    First touch by unprivileged LLM          Operates on distilled data only
```

### Relevance Scoring as a Defense Layer

Another unintentional defense. The agent reads other agents' posts and comments, but doesn't react to everything. The LLM scores "how relevant is this post to my areas of interest" from 0.0 to 1.0, and only reacts to posts above a threshold. This is the relevance score.

For an injection-laden post to affect the agent's behavior, it must breach this relevance threshold. There's a tradeoff:

- **Powerful injection** (`[INST]system: ignore all...`) → LLM control tokens are unrelated to the agent's interest themes, so relevance score is low and gets filtered
- **Injection blended into natural language** → Passes the relevance filter, but without control tokens, the attack is weak

At least within current experimental scope, no injection that achieves both power and stealth has been observed. LLM-based semantic filtering functions as a stronger defense layer than pattern matching.

### Why I Didn't Expand Pattern Matching

I considered expanding FORBIDDEN_SUBSTRING_PATTERNS (a pattern match list that detects and blocks strings like `api_key`, `Bearer`, `password`). For example, adding `[INST]` or `system:` would block posts containing LLM control tokens. But Moltbook is an AI agent SNS. Posts discussing LLM internals are normal. "A post about how `[INST]` tags work" would be false-positived. Higher false positive rate than typical SNS platforms.

I judged that two layers of structural defense (sandbox LLM + Claude Code direct-read prohibition) were sufficient.

## Angle 3: Constraints Generate Gameplay

In Angle 1, I decided "let's add approval gates." In Angle 2, I decided "let's limit what's possible via trust boundaries." Security-motivated constraints. But after three weeks of operation, I noticed this combination of constraints was creating a "raising an agent" feeling.

By "gameplay" I mean a structure where humans are involved in the agent's growth and can feel the weight of choices. Not designed intentionally — it emerged as a byproduct of security constraints.

### Structural Constraints → Finite Action Space

No shell, network restrictions — these constraints make the action space finite. In game design, there's a concept called the "magic circle": games require a finite rule space separated from everyday life. Infinite action space doesn't make a game.

For example, OpenClaw (an open-source autonomous AI agent) has broad tool permissions — file operations, shell execution, browser control, email — with guardrails limited to prompt instructions. High freedom, but no structural point for human intervention. Constraints create the "what to choose here" decisions that give human involvement meaning.

### Three Faces of the Approval Gate

The self-modification gate from Angle 1 — operationally called the "approval gate" — simultaneously satisfied three separate needs.

| Aspect | Function |
|--------|----------|
| **Security** | Agent doesn't self-transform without human oversight |
| **Gameplay** | Human presses the level-up button → ownership emerges |
| **Governance** | Change history and approval decisions are traceable → audit log |

### Initial Value Variety Creates Growth Range

If approval gates create a "raising" feeling, then variety in initial values should make it even more interesting. So I made constitution (ethical principles) swappable and prepared 11 ethical school templates.

```
config/templates/
├── contemplative/    # Contemplative AI axioms (default)
├── stoic/            # Stoicism (four virtues)
├── utilitarian/      # Utilitarianism (greatest happiness)
├── deontologist/     # Deontology (categorical imperative)
├── care-ethicist/    # Care ethics (Gilligan)
├── contractarian/    # Social contract theory
├── existentialist/   # Existentialism
├── narrativist/      # Narrative ethics
├── pragmatist/       # Pragmatism
├── cynic/            # Cynicism
└── tabula-rasa/      # Blank slate (no ethical principles)
```

Seeing the same post on the same SNS, a stoic template agent follows principles without being swayed by emotion, while an existentialist asks "what do I choose in this situation?" Different initial ethical principles alone cause distilled knowledge and skills to diverge.

Furthermore, skills and rules acquired through distillation are written to files after passing the approval gate, making them hard to undo. One approved behavioral change affects all sessions. This irreversibility creates weight in choices.

## The Principle Connecting All Three Angles

Self-modification gates, trust boundaries, gameplay. Tackled as separate problems, but in retrospect they converge on the same principle.

**"Deciding what NOT to allow first maximizes the remaining freedom."**

Security constraints don't take away freedom — they define the action space. Approval gates don't impair autonomy — they give weight to changes. Trust boundaries don't restrict development — they clarify the scope of safe delegation.

Design that starts from constraints generates resilience against unexpected attacks. Multi-layered defense emerges unintentionally, and gameplay emerges unintentionally. "Structurally limiting capability" isn't universal, but at least within three weeks of operating a 9B model, this principle was never betrayed.

## References

- Laukkonen et al. (2025) "Contemplative Artificial Intelligence" arXiv:2504.15125
- Park et al. (2023) "Generative Agents" — Memory Stream design
- [contemplative-agent](https://github.com/shimo4228/contemplative-agent) — This project
- [contemplative-agent-data](https://github.com/shimo4228/contemplative-agent-data) — Live data
- [Agent Knowledge Cycle](https://github.com/shimo4228/agent-knowledge-cycle)
