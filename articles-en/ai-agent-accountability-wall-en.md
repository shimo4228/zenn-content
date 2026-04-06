---
title: "A Sign on a Climbable Wall: Why AI Agents Need Accountability, Not Just Guardrails"
description: "AI agent governance is stuck in the 'put up a sign' phase. Plato described the problem 2,400 years ago. The solution isn't better signs — it's accountability architecture."
tags: ai, agents, governance, security, ethics
published: true
---

## The climbable wall

A Japanese film critic once said: "A sign saying 'Do Not Climb' on a climbable wall is meaningless." He added, roughly: "Screw that, I'm climbing it, idiot."

The point lands before your brain catches up. If something is physically possible, a text-based prohibition carries no weight. The power of a norm lies not in being written down, but in being **enforceable**.

AI agent governance is in this exact phase right now. We write "do not produce harmful content" in system prompts. We publish ethics guidelines as PDFs. We establish safety committees. The signs keep multiplying. But the wall remains climbable.

## A 2,400-year-old security model

This isn't a new problem. It's a solved problem that we keep forgetting.

Plato described it first. In the *Republic*, a shepherd finds a ring that makes him invisible — root access with no audit trail. He kills the king and takes over. The thought experiment: **would anyone follow the rules if they knew no one was watching and nothing was logged?** That's your AI agent. Capable of anything, observable by no one, accountable to nothing.

Hobbes framed the same problem as a game theory question in *Leviathan*: if you can break a contract and get away with it, isn't defection the rational move? His answer was essentially reputation-based access control — defectors get excluded from future cooperation.

Engineers already think in these terms. There are only three enforcement patterns that actually work:

| Pattern | Mechanism | Wall analogy | Engineering equivalent |
|---------|-----------|-------------|----------------------|
| Physical constraint | Make it impossible | A wall too high to climb | Sandboxing, permission model, RBAC |
| Consequences | Make it costly | Legal penalties | RLHF, penalty-based conditioning |
| Internalized values | Make them not want to | Moral intuition | Constitutional AI, value alignment |

And then there's the fourth — **the sign**. A text-based rule with no enforcement mechanism. A comment in the code that says `// don't do this`. It doesn't work.

An AI agent has root-level capability with no audit log and no accountability chain. It's the Ring of Gyges as a service.

## Signs as liability shields

The people who put up signs know they don't work. That's not the point.

In any large organization, there's a pattern: governance by documentation. Write a policy. Publish a guideline. The policy costs almost nothing to produce. Its enforcement effect is almost zero. But it creates a paper trail — "we took measures." The real function is **not prevention but indemnification**. "The policy existed. You violated it. That's on you."

Engineers see this in their own organizations. Security policies no one reads. Compliance checklists no one follows. The checklist exists not to prevent incidents but to shift liability after them.

AI guardrails follow the same pattern. Write "do not produce harmful content" in a system prompt. Publish a safety framework as a PDF. The practical effect is thin, but the paper trail exists. When something goes wrong, the sign points at the user — "you misused the tool" — not at the builder.

## Rules are probabilistic; constraints are deterministic

So what replaces the sign?

I ran into this problem while building an autonomous AI agent. The agent operates on a social platform, writing comments. Its episode logs are stored as files. A separate coding agent (Claude Code) reads those files during development. This creates an indirect prompt injection vector — payloads embedded in external posts flow into the context of a high-privilege coding agent.

My first fix was to write "do not read episode logs directly" in the project's rules file. This is a **sign**. LLMs follow rules probabilistically, not deterministically. During debugging, if you say "check the logs," the model may cheerfully ignore the rule.

The next step was PreToolUse Hooks — shell scripts that intercept tool execution and block it based on conditions. Where rules are probabilistic, hooks **fire deterministically, 100% of the time**.

In wall terms, I replaced the sign with a physical barrier. It's not perfect — creative workarounds remain possible. But it's orders of magnitude better than writing a rule and hoping.

## What you already know, applied to agents

Here's the thing: you already know how to solve this problem. You just haven't applied it to agents yet.

Every engineering organization of any size has some form of approval workflow. PR reviews. Deployment gates. Change advisory boards. Incident postmortem processes. RBAC. Audit logs. These structures share three properties:

1. **Approval is recorded** — who signed off, and when, is traceable
2. **Responsibility is assignable** — when things go wrong, there is someone to go back to
3. **Changes are auditable** — "why did this change?" has an answer

What organizations have refined over centuries is not the distribution of capability, but the **distribution of accountability**. You would never deploy a code change to production without a review. You would never grant root access without an approval chain. These are not bureaucratic overhead — they are engineering discipline.

Yet we build AI agents with none of this. The agent space is dominated by solo developers and startups who design around "does it work?" and "is it smart?" — not "who is responsible when it does something unexpected?" The real reason agents struggle to gain adoption in large organizations is not insufficient capability. It is the absence of accountability architecture.

I hit this problem firsthand. Running an agent in production, I could not trace why a particular comment was generated. When behavior changed, I could not isolate the contributing factors. Debugging was impossible without knowing what had changed and when. **The practical need for debuggability led naturally to an architecture that turned out to be structurally identical to an approval workflow.**

Every point where the agent's behavior can change — its skills, rules, identity, ethical guidelines — is gated behind an explicit human command. Adoption of any change requires human sign-off. This was not a top-down design decision driven by governance theory. It was the shape that emerged from the friction of actually using an agent in production. At least in my case, the honest attempt to make an agent debuggable led here.

If you think about it, this is just change management applied to agent behavior. The agent equivalent of a PR review for personality changes. The agent equivalent of a deployment gate for ethical guidelines. Nothing conceptually new — just conspicuously absent from how agents are built today.

## Implementation dissolves; judgment remains

The specific implementations — hooks, approval flows, command-gated changes — won't last.

Working with AI harness tools (structured execution environments for skills, rules, and agents), I noticed that their value structure forms an hourglass shape. The top (what to build, domain judgment) and the bottom (data, infrastructure, physical constraints) retain their value. The middle implementation layer trends toward zero. As LLMs improve, concrete procedures and code examples become unnecessary.

From experience structuring and running reusable behavioral patterns (skills), what I've observed is that **scaffolding dissolves**. Explicit skill definitions stop being necessary as principles begin to operate naturally within the dialogue. You don't need dozens of installed skills — a single file of distilled principles drives the same cycle.

Hooks will be replaced by something else. Signs and physical barriers are temporary forms. What persists is the judgment layer: **what should be constrained, and who is responsible**.

## The question that matters

The key to putting agents into production is not capability. It is accountability. Capability is commoditized — every model is reasonably competent. But until "who is responsible?" has an answer, agents don't ship into real workflows.

The industry keeps pushing for more powerful models and more autonomous agents. But increasing agent autonomy is not, by itself, progress. Design that appropriately limits autonomy is what survives contact with production.

Not signs. Not internalized values. A structure where a human who can bear responsibility stays in the loop. That may be the only form in which agents work in practice.

It's time to stop putting signs on climbable walls. The question is not how high the wall is, or what the sign says. The question is who stands in front of it.
