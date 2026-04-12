---
title: "Can You Trace the Cause After an Incident?"
description: "SRE-style incident response applied to AI agents. Why upstream structural investment beats downstream firefighting — and how agent design converges with centuries of organizational governance."
tags: discuss, ai, programming, devops
published: true
---

## Can you trace the cause after an incident?

Picture the night your AI agent causes a production incident. You get paged. Customer data may have leaked to an external endpoint. Customer support says: "We need an explanation by end of day." You open the logs. The agent's final output and the external API call history are there.

The problem is you can't trace backwards from there. Why did the agent make that decision? Which part of the prompt drove it? How did it reason internally? There's nothing to follow. All you have is the LLM's output string and an unstructured conversation log leading up to it.

You sit down to write the incident report. Your pen stops at the "Root Cause" field.

---

I believe this is something many AI application developers will eventually face. I've been running my own agent, `contemplative-agent`, for several months, and at some point I recognized this as inevitable. In a sentence: **an AI system that can't trace causality after an incident cannot explain what happened**. And a system that can't explain what happened after an incident won't survive audits or change management.

What follows is not a story of "I foresaw this problem and designed backwards from it." What I was actually doing was trying to keep an agent running safely in an environment full of prompt injection, and trying to dig myself out of debugging swamps. I kept doing that, and this structure emerged on its own. This article is a sequel to ["A Sign on a Climbable Wall: Why AI Agents Need Accountability, Not Just Guardrails"](https://zenn.dev/shimo4228/articles/ai-agent-accountability-wall).

## Incident costs exceed steady-state costs by orders of magnitude

There's a widely shared lesson in the SRE world: the cost of restoring something after it breaks almost always dwarfs the cost of building it not to break in the first place — often by an order of magnitude.

Break down incident costs: time spent identifying the cause, recovery effort, customer communication, internal reporting, devising prevention measures, writing the postmortem, audit response, time to rebuild trust, and regulatory follow-ups triggered by the incident. Include the harder-to-quantify parts — burnout of the person dragged out of bed at 3 AM, team morale, extra scrutiny at the next audit — and the total cost of a single incident inflates to a surprising degree.

By contrast, investing in structures that prevent incidents can be paid incrementally within normal development workflows. Even discounted by incident probability, the preventive investment often comes out smaller in total cost.

In other words, **when you calculate backwards from incident cost, the rational allocation of investment tilts toward placing preventive structures upstream**. This isn't about being conservative or risk-averse — it's closer to a shortcut in expected-value math. Pay upstream, and you structurally reduce the probability of large downstream payments.

This asymmetry widens with scale. In social infrastructure like healthcare, finance, and government, incident damage extends beyond direct stakeholders. "Containing incidents upstream" becomes not an option but a precondition. My `contemplative-agent` is a personal project, but the cost asymmetry of incidents operated in exactly the same shape.

## What "placing structure upstream" actually means

What does "placing structure upstream" mean in practice? Here's what I actually did in my agent.

**Minimize the surface area of external side effects:**

As described in the [previous article](https://zenn.dev/shimo4228/articles/ai-agent-accountability-wall), security by absence — a design that structurally seals off external side-effect pathways — eliminated entire damage scenarios.

**Limit each agent to one external connection point:**

By "connection point," I mean any pathway through which an agent can affect the outside world: external APIs, databases, email dispatch, file writes, and so on. In my own project I use the term "adapter" internally, but since that's project-specific vocabulary, I'll stick with "external connection point" here.

When a single agent holds multiple connection points, an incident requires triage to determine which connection point was the origin. The moment you introduce that triage step, ambiguity enters the causal narrative of the incident.

If you start with one agent, one connection point, the triage step itself becomes unnecessary. I formalized this decision as [ADR-0015](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0015-one-external-adapter-per-agent.md). ADR (Architecture Decision Record) is the practice of documenting design decisions and their reasoning. In my agent project, I write one for every design decision — so that why a structure was chosen, what was considered, and what was discarded can be traced later. This itself is a practice continuous with the article's theme of making causality traceable. In organizational terms, this principle corresponds to separation of duties; in microservices, to the single responsibility principle; in SRE, to minimizing blast radius.

This is also a perfectly ordinary structure in human workplaces. A sales rep handles customer relations; accounting handles the books. If the sales rep also does accounting, an invoicing error later requires triaging whether the sales estimate was wrong or the accounting process was wrong. Separate them from the start, and the structural opportunity for ambiguous responsibility shrinks.

**State visibility:**

I externalized all of the agent's internal state — identity, worldview, professional ethics, skills, experience patterns, operational records — as files. Listed this way, the agent's internal structure isn't something new; it's **simply what a human professional carries inside, written out as files**. Why this was possible in my case, and why it's difficult for commercial agents, is explored in ["AI Agent Black Boxes Have Two Layers"](https://zenn.dev/shimo4228/articles/agent-blackbox-capitalism-timescale).

**Place an approval gate before any write:**

At every point where the agent self-updates (e.g., identity shifts through distillation), a human approval step is inserted. Rolling back a corrupted persona is overwhelmingly more expensive than stopping the corruption before it happens. This is another form of "paying upstream."

All of this looks like a combination of concepts the engineering community already has. That's correct — there's nothing new here. What's uncommon is making the decision to do all of it upfront. The reason is simple: until an incident happens, it all looks unnecessary.

## It turned out to be organizational theory

After writing ADR-0015, I lined everything up and looked at it. I actually said "Oh" out loud. This is organizational theory.

| Organizational principle | Engineering equivalent | Agent design | Motivation |
|---|---|---|---|
| Separation of duties | Microservice single responsibility | One agent, one responsibility | Minimize blast radius |
| Four-eyes principle | PR review 2-approval rule | Separate approval agent | Insurance against single-point judgment errors |
| Least privilege | IAM least-privilege principle | Security by absence | Pre-contain impact scope |
| Internal controls | CI gates / pre-commit hooks | Approval gate before writes | Pre-write verification |
| Approval workflows | Change Advisory Board | Approval pathway for external side effects | Causal integrity during changes |
| Audit trails | Audit logs | Append-only logs | Post-hoc causal tracing |

The left column is practice that humanity acquired over centuries of organizational governance. The middle column is what software engineering rediscovered over decades. The right column is this agent design. At least from what I can see, every one of them traces back to the same motivation: "when an incident happens we'll be in trouble, so absorb it structurally in advance."

Organizational theory, software engineering, and agent design — starting from different eras and different domains — converge on the same place. What determines the convergence point is not ideology but the asymmetry of incident costs, a constraint closer to physics than philosophy.

## "Don't do everything yourself" — the obvious principle

This "one agent, one responsibility" sounds like a novel design principle in technical discourse. But in human society, it's obvious. A sales rep doesn't decide contract amounts on the spot in front of a customer. They say "let me take this back and check," then get sign-off from finance and legal before responding. A surgeon doesn't complete an operation alone. The anesthesiologist, the nurses — each holds their own specialty and scope of responsibility.

Yet when designing AI agents, this common sense gets forgotten. Probably because LLMs appear to be capable of anything. But "can do" and "should be allowed to do" are different things, and human society has spent millennia refining this distinction. One agent, one responsibility is **simply the division-of-labor principle that humans already operate by, brought directly into agent design**.

To be clear, this is not an argument in favor of large-organization conservatism. The claim that "organizational structures should adapt to AI" has merit. But looking at the history of technology adoption, structural change in society requires cognitive change alongside it, and its pace differs from technological change by orders of magnitude. **Agents that work during the decades it takes for structural transformation to happen** — that's the stance of this article. The structural causes of black boxes, the time-axis gap between technology and society, and the player-composition bias in the discussion are explored in ["AI Agent Black Boxes Have Two Layers"](https://zenn.dev/shimo4228/articles/agent-blackbox-capitalism-timescale).

## The side effect of responsibility defense

Back to operations. The asymmetry of incident costs and the time-axis argument also manifest in another form: **the question of individual engineer liability**.

When a god-mode agent with prompt guardrails causes an incident, the typical postmortem proceeds like this:

- "Why did it decide that?" — Can't trace what happened deep inside the prompt
- "Where could it have been prevented?" — The only way to explain why the guardrail failed is to ask the model
- "How do we prevent recurrence?" — Adjust the prompt, it leaks again, you get blamed again
- "Why wasn't it stopped?" — No evidence to mount a defense

The person responsible for a black box is structurally classified as "the person who wasn't watching" when an incident occurs. Because there was no defined place to watch. As a result, responsibility concentrates on the frontline engineer. This is not a matter of individual skill — it's because the system has no built-in mechanism for distributing responsibility.

With a structured agent (visibility + ADR-0015 + approval gates), you can speak like this in a postmortem:

- "This agent can only touch external surface A"
- "All decision logs are in JSONL"
- "Identity updates went through an approval gate; the approver is a separate role"
- "The constitution (the agent's foundational normative definition) was running at this version"
- "Where the distillation pipeline broke can be isolated structurally"

Causal attribution can be distributed across the structure. Responsibility distributes accordingly. Concretely, my project has 14 ADRs, 835 tests, append-only decision logs, and documentation in both Japanese and English. Though honestly, I didn't build these as intentional "prepayment of incident costs." When developing agents with Claude Code, you need to re-explain the project's context from scratch every time the session changes. I wrote the ADRs and documentation because they were necessary for context management to maintain development consistency. It turned out they also functioned as a structure for tracing causality during incidents.

In engineering terms, this is the SRE concept of a blameless postmortem — seeking causes in structure rather than blaming individuals. What humans achieve through behavioral norms is reinforced by system-side structure.

## The rationality of laziness

I've been writing as if this were expected-value calculation, but my actual motivation is more mundane. If I know something will be a pain later, it's no hardship to deal with it preemptively. The optimal strategy from expected-value math (invest upstream) and the reflex of a lazy person (organize things now so they don't bother you later) land on the same conclusion. This habit probably seeped into my bones from years of incident response work at a conservative large organization. It's not something most people develop — it's a personal quirk. I didn't expect the same shape to appear in the entirely different domain of LLM agent operations.

## A conclusion that doesn't conclude

Back to the on-call night from the opening. The incident report, the "Root Cause" field where your pen stopped. With my agent, at least I could produce "which agent touched which external surface, through which decision logs, arriving at this output." Whether the root cause itself is writeable, I don't know. But there's a starting point for tracing causality.

Pay the incident cost upfront or pay it after the fact. As far as I know, there is no way to avoid paying it altogether.

---

**References**

- contemplative-agent v1.3.1 release: https://github.com/shimo4228/contemplative-agent/releases/tag/v1.3.1
- ADR-0015 (One external adapter per agent): same repository `docs/adr/0015-one-external-adapter-per-agent.md`
- Laukkonen et al. 2025 "Contemplative Artificial Intelligence" arXiv:2504.15125

**Series: AI Agent Governance**

1. [A Sign on a Climbable Wall — Why AI Agents Need Accountability, Not Just Guardrails](https://zenn.dev/shimo4228/articles/ai-agent-accountability-wall)
2. This article
3. [AI Agent Black Boxes Have Two Layers — The Limits of Technology and the Convenience of Business](https://zenn.dev/shimo4228/articles/agent-blackbox-capitalism-timescale)
