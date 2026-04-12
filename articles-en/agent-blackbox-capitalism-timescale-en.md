---
title: "AI Agent Black Boxes Have Two Layers — Technical Limits and Business Incentives"
description: "The black box problem in AI agents isn't one problem — it's two. One layer is technically opaque. The other is technically visible but commercially hidden. Mixing them up makes the debate unwinnable."
tags: discuss, ai, governance
published: true
---

## It started as just a prompt

Remember Chain-of-Thought (CoT)? Adding "Let's think step by step" to a prompt improved LLM reasoning accuracy. It was one of the early prompt engineering discoveries. CoT lived outside the model. It was just a string.

Not anymore. CoT became the conceptual ancestor of today's reasoning models — GPT-5, Claude's extended thinking, Gemini's thinking mode, among others. These models acquired reasoning capabilities during training through reinforcement learning. The reasoning process moved inside. Some models, like Claude's extended thinking, make the process partially visible. But in most cases, the details are hidden from the outside.

Research from Wharton GAIL found that applying the original CoT prompting to reasoning models had almost no effect — and in some cases introduced redundancy that hurt performance. What was once external became internal, and injecting the same pattern from outside no longer worked.

A terminological note. In AI safety discourse, structures built around an LLM without modifying its weights are called *scaffolding*[^1]. System prompts, tool definitions, RAG pipelines, agent loops — all of these fall under scaffolding.

The black box in AI agents has two distinct **causes** of invisibility. Technical limits and business incentives. These two are different in nature, so the responses to each must also differ.

```text
■ Layer 1: Model Internals (weights) — Technically opaque
  Examples: Language ability, commonsense reasoning, ethical judgment, CoT (post-internalization)
  Why invisible: Dissolved into weights; fundamentally non-extractable

■ Layer 2: Scaffolding — Technically visible, commercially hidden
  Umbrella term for human-constructed components outside the model[^1]
  Why invisible: Source of competitive advantage; no incentive to disclose

  Examples: system prompts, persona definitions, tool definitions, RAG,
      agent loops, safety gates, session management,
      harness (runtime control layer)
```

Academically, there have been attempts to distinguish scaffolding (build-time) from harness (runtime), but this boundary is rapidly blurring. Persistent memory, skill ecosystems. Model-agnostic agent foundations like OpenClaw run interchangeably on Claude, GPT, or local models. Anthropic blocked usage via subscription access, but the dynamic where scaffolding commoditizes models isn't stopping. The scope of scaffolding keeps expanding alongside the surge in agent development. In this article, I use scaffolding in the broad sense that includes harness.

From my experience running my own agents: when scaffolding is properly context-managed, the model is just an inference engine, and the essence of the agent lives in the scaffolding. Personality, capabilities, decision criteria — all of it resides in the scaffolding. Swap the model and keep the scaffolding, and the agent behaves the same way. I once wrote that "[the essence of an agent might be memory](https://zenn.dev/shimo4228/articles/agent-essence-is-memory)." The three layers I described in that article — EpisodeLog, KnowledgeStore, and Identity — are all scaffolding in current terminology. I didn't have this distinction at the time, but gaining the concept of scaffolding let me explain that intuition structurally.

**Scaffolding is technically visible, yet in practice invisible.** Where this gap comes from is the subject of this article.

## The two-layer structure of the black box

From building agents from scratch, I've come to see that the black box has two distinct layers.

**Layer 1: Model Internals — Internalization through training**

Ethics, worldview, reasoning patterns. These are dissolved into the weights through pre-training and reinforcement learning. At first glance, this seems like a technical inevitability. But personally, I suspect the scope of this "internalization" is less inevitable than commonly assumed.

CoT is the clearest example. CoT originally lived outside the model. It was internalized to achieve performance gains that external prompting couldn't deliver — self-correction, backtracking, scaling of inference-time compute. A performance-first design decision to internalize despite the enormous cost. It wasn't technically inevitable; it was a choice that involved trade-offs with visibility.

Of course, not everything can be externalized. Tacit knowledge acquired through large-scale pre-training is structurally difficult to externalize. In my own agents, scaffolding elements like identity, professional ethics, skills, and decision logs could all be represented as files. Meanwhile, the language abilities and commonsense reasoning the model acquired through pre-training couldn't be externalized at all. The line between "what's inevitable" and "what's a matter of convenience" — at least in my experience — aligns with the boundary between scaffolding and model internals. Yet this line remains undrawn in current discourse.

**Layer 2: Scaffolding — Technically visible, but kept hidden**

Outside the model lies another layer. System prompts, persona settings, rules, tool definitions — scaffolding. This layer is technically inspectable. Store it in files, manage it with git, and you can track every change.

But in most cases, it's kept hidden. The reason is the competitive logic of capitalism.

Prompt design and model tuning methods are product differentiators. Reveal them, and competitors copy them. This commercial rationality creates a trade-off with safety-oriented visibility. **It should be visible for safety. But it must stay hidden for business.**

AI safety research has noted that scaffolding and other post-training enhancements can amplify benchmark performance by 5-20x[^2]. This means evaluating model safety in isolation is insufficient — evaluation must include scaffolding. But if scaffolding is kept hidden, external safety assessment becomes structurally impossible.

On March 31, 2026, Anthropic accidentally exposed the complete source code of Claude Code v2.1.88 (roughly 510,000 lines) through a release error. Source maps were included in the npm package, and within hours the code was widely mirrored and forked. What's telling is this: even Anthropic — one of the companies most committed to AI safety — wasn't publishing their scaffolding. If it were public, external inspection would be possible and safety discourse would advance. Yet they couldn't publish it. The competitive environment wouldn't allow it.

## Want to show it, can't show it

This contradiction sits at the foundation of the AI safety debate.

From a safety perspective, you want to trace the causal chain behind an agent's behavior. That requires making scaffolding visible. From a business perspective, scaffolding is the source of competitive advantage, and there's no incentive to disclose it.

The reason I could represent every component of my agents as files in a personal project was the absence of this contradiction. There was no commercial reason to hide anything. In return, I got the full benefits of visibility — debuggability, change tracking, causal tracing — with nothing taken away.

The converse is that organizations building agents in a commercial context carry this contradiction structurally. They want visibility for safety, but secrecy for business. The current black box problem lives at the point where these two forces reach equilibrium.

One important caveat: this is not a "corporations are evil" critique. Protecting differentiators in a competitive environment is rational behavior, and denying that rationality won't solve the problem. The problem lies in the structure itself — the point where that rationality and safety requirements collide. This is not purely a technology story or purely an ethics story. It's a story about market dynamics and safety requirements being structurally misaligned.

If there's a way to resolve this contradiction, it won't be "show everything" or "hide everything is fine." It will be the work of defining **the minimal set of what must be visible to enable causal tracing**.

In my own agents, I log every action to an append-only JSONL log. All scaffolding components (identity, constitution, skills, rules) are stored as dedicated logs, and changes require explicit human approval. Design decisions are documented as ADRs. When an incident occurs, I can trace "which version of the scaffolding, through which action logs, led to that output." Even without publishing the full scaffolding text, the information needed for causal tracing can be disclosed. Where to draw that line is the focal point for the next stage of this debate.

## The timescales of technology and social structure

There's another axis that tends to be overlooked here: time.

When you look at the relationship between technology and social structure through a historical lens, the process by which new technologies achieve broad social adoption tends to follow the same sequence.

**Technology change → Shift in social cognition → Structural reorganization → Mainstream adoption of the technology**

Printing offers a clear example. From Gutenberg's movable type in the 1440s to the point where print culture transformed society through the preservation, standardization, and dissemination of knowledge — that took centuries[^3]. For electricity and the internet, delays of decades have been observed between commercial deployment and institutional restructuring. In these cases at least, the speed of technological change and the speed of social-structural change diverged significantly.

And technologies where this mismatch was too large failed to achieve broad adoption, no matter how capable they were. Technologies that tried to push through on "convenience" alone before cognitive shifts caught up might function in niche contexts, but they stalled before reaching society at large.

AI agents exist within this same timeline.

The current pace of AI's technological change is remarkably fast, even compared to past innovations. Meanwhile, the pace of social-structural change — legal frameworks, organizational decision-making processes, industry regulations, how people work — hasn't changed much from before. The time it takes for humans to accept a new concept and embed it in institutions doesn't depend much on the type of technology. Cognitive change is a function of generations and experience, not of technology.

What this speed differential means is that no matter how mature the technology side of AI agents becomes, a "gap period" will always exist until social structures catch up. And it's this gap period that becomes the proving ground for whether agents can actually function in society.

## Adapt to the structure, or restructure it?

There's a voice that says "the structures should change to accommodate agents." That the standards for approval gates and audit trails don't match the speed of AI. Some of this argument holds, and there are genuinely parts of the structure that should change.

The issue is the timescale. As we saw, social-structural change comes with significant delays compared to technological change. "The structures should change" may be correct in the long run. But agents need to operate during the decades it takes for structural transformation to happen. Build agents that work within existing structures first, and let the accumulated track record shift social cognition — historically, almost no technology has managed to skip this sequence. I explored this point as concrete design decisions in the [previous article](https://zenn.dev/shimo4228/articles/agent-causal-traceability-org-adoption).

## The composition of the debate

With the timescale problem in mind, there's something else that concerns me. Why has "tear down the structures" become the dominant voice? Perhaps because the composition of the debate's participants is skewed.

People at the cutting edge of development are on the "I can trace causality myself" side. They can infer causes from outputs and adjust prompts themselves. To them, approval gates and audit trails look like "inefficient rituals" that their own skills can substitute for. Meanwhile, the voices from operations, auditing, and incident response rarely make it onto tech conference speaker lists.

"Tear down the structures," which looks rational from a developer's perspective, translates to "don't tear down the structures we depend on" from an operator's perspective. This isn't about right and wrong — it's about field of view. They're looking at different cross-sections of the same system. Technology designed from only one cross-section gets rejected at the other.

## Seeing why it's invisible

Asking what's inside the black box matters. But equally important is **distinguishing why it's invisible — whether it's technical limits, business incentives, or the pace of society** — as the foundation for the next stage of debate. Saying "black boxes are dangerous" while conflating all three leads nowhere actionable. Separate them, and at least you can tell where you can intervene and where you can't.

---

[^1]: beren, "[Scaffolded LLMs as natural language computers](https://www.lesswrong.com/posts/43C3igfmMrE9Qoyfe/scaffolded-llms-as-natural-language-computers)", LessWrong, 2023
[^2]: Davidson et al., [arXiv:2312.07413](https://arxiv.org/abs/2312.07413), 2023. See also [BlueDot Impact's explainer](https://blog.bluedot.org/p/what-is-ai-scaffolding)
[^3]: Eisenstein, "The Printing Press as an Agent of Change", 1979

**Series: AI Agent Governance**

1. [A Sign on a Climbable Wall: Why AI Agents Need Accountability, Not Just Guardrails](https://zenn.dev/shimo4228/articles/ai-agent-accountability-wall)
2. [Can You Trace the Cause After an Incident? How Agent Design Converges on Organizational Theory](https://zenn.dev/shimo4228/articles/agent-causal-traceability-org-adoption)
3. This article
