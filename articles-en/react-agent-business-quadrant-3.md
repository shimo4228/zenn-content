---
title: "Is ReAct Needed in Production? — Separating Design and Operation Phases"
emoji: "⏱"
type: "idea"
topics: ["ai", "llm", "agent", "architecture"]
published: true
description: "The third article in the ReAct quadrant series. ReAct may be a tool for the design phase, not for production. Separate design and operation, and the legitimate territory of ReAct narrows to coding, Deep Research, and exploration of unknown environments."
tags: discuss, ai, llm, architecture
---

> **Series position:** The third article in the ReAct agent quadrant series. The quadrant names align with the previous articles and with the [AAP repository](https://github.com/shimo4228/agent-attribution-practice).

## Premise

In the [first article](https://dev.to/shimo4228/where-react-agents-are-actually-needed-in-business-33do) I split business AI into four quadrants and wrote that ReAct agents are legitimately needed only in the (4) ReAct Quadrant. In the [second article](https://dev.to/shimo4228/3-the-llm-workflow-quadrant-is-missing-from-our-vocabulary-n18) I observed that the industry's vocabulary has no independent name for the (3) LLM Workflow Quadrant, and that this absence produces, by elimination, the choice to drape ReAct over every quadrant.

For ease of reference, the four quadrants again:

- (1) **Script Quadrant** — deterministic × definable. Handled by scripts and pipelines.
- (2) **Classical AI Quadrant** — deterministic × exploratory. Classical AI / OR territory (out of scope here).
- (3) **LLM Workflow Quadrant** — semantic judgment × definable. Calls an LLM inside a predefined workflow. Includes a conversational form (specialized chat agents) and a batch form (single-purpose LLM functions).
- (4) **ReAct Quadrant** — semantic judgment × exploratory. An autonomous loop where the LLM itself decides the next action.

## A New Axis: Time

The previous articles drew the quadrants along the axis of "the nature of the work." In this article I want to introduce a deeper axis: the **time axis**.

Business work has a design phase and an operation phase. They are different activities, with different optimization criteria. The design phase maximizes flexibility; the operation phase maximizes predictability. The root of the agent ecosystem's confusion may be that we are trying to compress these two into a single system.

The question of this article, in one line: **isn't ReAct a tool for the design phase, and unnecessary in production?**

## The Design Phase and the Operation Phase

The work of building a business system splits into two distinct phases.

**Design phase**: the work of understanding the structure of the business, deciding what to mechanize and what humans will own, and assembling the workflow. You don't know in advance what will happen, so it proceeds exploratorily. "What to check next" can't be decided ahead of time.

**Operation phase**: the work of actually running the workflow you designed. The structure of the target work is already known. You run the predetermined route, at a predetermined frequency, under predetermined quality standards. What's going to happen should be predictable in advance.

This distinction is not new. In software engineering it has shown up as development vs production; in BPM as as-is analysis vs operation; in systems design as design-time vs run-time. In agent discussions, however — as the previous two articles observed — the distinction tends to blur. When people say "an autonomous agent runs the business," they appear to be trying to compress design and operation into a single system.

## "Not Knowing What To Do Next" in Production Means the Operation Phase's Properties Are Being Dropped

The core of ReAct is "the LLM dynamically decides what to do next." This is legitimately needed when **what to do next can't be known in advance**. Coding, Deep Research, exploring unknown environments, browser automation. The territories I named in the first article as legitimate ground for the (4) ReAct Quadrant can all be read as work belonging to a design phase or an exploration phase.

If "not knowing what to do next" arises inside a business that has entered production, isn't that a sign that one of the properties production demands — predictability, log traceability, cost stability, attribution — is hard to secure with ReAct's architecture? These are properties that ought to be assembled into the workflow before it's handed to production, not patched after the fact by applying ReAct to production itself.

If the dissection of the business is complete, then (1) Script Quadrant work can be written deterministically, (3) LLM Workflow Quadrant work can be fixed as single-purpose LLM functions or specialized chat agents, and any other judgment is handed off to humans at explicit handoff points. In production the workflow simply runs. What to do next is something the workflow already knows.

There's a possible counterargument. "Aren't there genuinely dynamic businesses? What about customer support, where every inquiry is new?"

This is apparent dynamism, not real. The contents of inquiries can look infinitely varied, but the routes that process them converge to a finite set of types. FAQ-style responses, expert-knowledge lookups, routing decisions, escalations — each one can be fixed as a (3) LLM Workflow Quadrant batch (single-purpose LLM function) or conversational form (specialized chat agent). The contents of an inquiry may be new, but the processing route was decided in advance.

Suppose, instead, you don't fix the routes and let an autonomous agent handle inquiries end-to-end with ReAct. When a single one of those handlings turns into a lawsuit-grade incident — wrong medical advice, unsuitable financial product recommendations, leakage of confidential information, discriminatory treatment — how does the organization show where responsibility lives? "The agent decided dynamically" is unlikely to suffice. The attribution gap I wrote about in the second article — the inability to trace a chain of judgments back to a specific cause after the fact — comes back as legal risk to the organization. For low-reversibility work, where a single incident could end the organization, where is the reason to choose not to fix the routes?

Even if there's work where you'd accept the litigation risk to gain dynamic handling, work whose **processing structure itself is genuinely new every time** is more honestly treated as R&D-phase or exploration-phase work. It does not appear to be work that fits the definition of a production-operation phase.

## When a New Pattern Appears During Production

It happens that, during production, a new pattern emerges that doesn't fit any existing processing route. How you handle this decides the relationship between design and operation.

The ReAct-style answer is "an autonomous agent dynamically handles the new pattern." But this embeds a design-phase activity inside the operation phase. The dynamic handling may work in the moment, but the basis for the handling isn't logged, there's no reproducibility, and the locus of responsibility blurs. The redirect impossibility I wrote about in the second article — the phenomenon where a ReAct loop's black-box nature makes it impossible to separate attribution at incident time — fires in the middle of production.

There is another answer. **Treat the new pattern as feedback to the design phase**. When a new pattern appears in production, it's a case the current workflow's design didn't anticipate. Run production through a temporary handling (human judgment, a provisional escalation), then return to the design cycle, analyze the pattern, and decide which of the four quadrants it belongs in. If it's the Script Quadrant, add a deterministic rule; if it's the LLM Workflow Quadrant, add a new single-purpose LLM function or conversational branch; if it turns out to be ReAct Quadrant work, move to the judgment of accepting the attribution gap; if it requires human judgment, make the handoff point explicit. Either way, you update the workflow.

This answer keeps the boundary between design and operation clean. The design phase moves flexibly; the operation phase moves predictably. Their optimization criteria don't get mixed.

## Where Coding Agents Sit

A point the previous two articles left open can now be picked up. At least for coding agents, ReAct can be read as a place where it is legitimately exercised.

That's because **coding agents live in the design phase**. Each coding task is essentially exploratory work — "what to do next isn't known" — and a single coding session ends when it ends. Tools like Devin or GitHub Copilot Coding Agent run continuously in CI/CD pipelines, but the contents of each session are independent exploration each time, not a steady-state workflow defined in advance. This is the difference from a business agent.

A business agent, sooner or later, enters the production-operation phase. In the operation phase the exploration is over, so where is the reason to put ReAct there? ReAct-based products being sold as business agents appear to be making a category error of bringing a tool that belongs to the design phase into the operation phase.

Deep Research and browser automation in unknown environments sit in the same place as coding agents. These are "exploration itself," not steady-state operation. A new exploration runs each time a user asks a question, but it ends in minutes to tens of minutes. The same system doesn't keep running afterwards. **Each run reads as an independent small design phase**.

So the legitimate territory of ReAct may be more accurately drawn by the **distinction of phase** than by the quadrant of work. The design phase and the exploration phase share the property "what to do next can't be decided in advance," and in this article I treat that shared property as the criterion for applying ReAct. And that property reads as the place where (4) the ReAct Quadrant resides. Where, in the operation phase, is the reason to bring ReAct in?

## The Ecosystem Problem of Compressing Design and Operation

The agent ecosystem is trying to compress the design phase and the operation phase into a single system. The vision "an autonomous agent understands the business, assembles the workflow, and executes it" assumes a system that takes on both phases at once.

The problem is that the optimization criteria of the two phases run in opposite directions. The design phase needs flexibility — you don't know what will happen, so you need to keep options open. The operation phase needs predictability — log traceability, attribution, and cost stability. Putting both into a single system means flexibility gets sacrificed for predictability and predictability for flexibility, and you end up with a system that's mediocre at both.

The design rule for separating them reads like this. The design phase is where (4) ReAct Quadrant tools (coding agents, Deep Research) live. Work that, once designed, is handed to the operation phase, runs on a combination of (1) the Script Quadrant and (3) the LLM Workflow Quadrant (with (2) the Classical AI Quadrant when needed), and the ReAct Quadrant stays in its design-phase role. When a new pattern emerges, it's sent back to the design phase.

## What the Trilogy Has Made Visible

Lining up the three articles, the agent ecosystem's confusion appears to break into three layers.

The top layer is **misapplication of the quadrants**. The category error I wrote about in the first article — draping the (4) ReAct Quadrant's architecture over (3) LLM Workflow Quadrant work. This was the primary symptom observed on the ground.

The second layer is **the absence of vocabulary**. As I wrote in the second article, the industry has no positive name for the (3) LLM Workflow Quadrant. The vocabulary gap is the breeding ground for the misapplication: after carving off the deterministic part, the designer is pushed into the elimination-style choice of pouring everything else into ReAct.

The third layer is **the conflation of time**. The design philosophy I wrote about in this article — compressing the design phase and the operation phase into a single system. This sits even deeper than the vocabulary gap. Because the assumption "design and operation happen on the same time axis" is tacitly shared, the vocabulary to distinguish them was never demanded — that chain comes into view. As long as the vocabulary stays missing, draping a design-phase tool (ReAct) over the operation phase doesn't feel jarring.

The three layers aren't independent observations; they form a chain that descends from top to bottom. The misapplication is born of the vocabulary gap; the vocabulary gap is born of the time-axis conflation. Writing the three articles in order, there was a felt sense of resolution descending one rung at a time.

Seen from the bottom layer, the legitimate territory of ReAct narrows to **exploratory tasks of the design phase**. Concretely: coding, Deep Research, exploration of unknown environments. Business systems that enter production may be able to let go of ReAct at the moment design completes, and run on a combination of (1) the Script Quadrant and (3) the LLM Workflow Quadrant.

## Closing

The discussion around agents tilts toward a capability-benchmark axis: "how high can we crank autonomy?" But once you think about running them on the ground, the question of **which phase uses which tool** comes up earlier than the question of capability.

Using ReAct in the design phase appears legitimate. Coding agents are real tools and have measurably lifted developer productivity. Deep Research provides a new shape of exploration. These can be read as places where ReAct's power is legitimately exercised.

Using ReAct in the operation phase — isn't that the act of patching incomplete design with operation? The artificial redirect impossibility I wrote about in the second article fires here. Complete the dissection in the design phase, and hand only predictable workflows to the operation phase — this can be read as the basic guideline for embedding agents into business.

The vocabulary for talking about the time axis hasn't yet settled in the industry. The dynamic of compressing design and operation into one is not unrelated to the marketing story "an autonomous agent runs the business." That story is strong, and refuting it is not efficient. Instead, raising another story from the ground — "once design completes, ReAct exits"; "what remains in operation is a predictable workflow" — appears to be the better path. This article is an attempt to raise that story using the vocabulary of "phase."

---

## Related

- First article: ["Where ReAct Agents Are Actually Needed in Business"](https://dev.to/shimo4228/where-react-agents-are-actually-needed-in-business-33do)
- Second article: ["(3) The LLM Workflow Quadrant Is Missing from Our Vocabulary"](https://dev.to/shimo4228/3-the-llm-workflow-quadrant-is-missing-from-our-vocabulary-n18)
- AI agent governance trilogy:
  1. [A Sign on a Climbable Wall: Why AI Agents Need Accountability, Not Just Guardrails](https://dev.to/shimo4228/a-sign-on-a-climbable-wall-why-ai-agents-need-accountability-not-just-guardrails-17ak)
  2. [Can You Trace the Cause After an Incident?](https://dev.to/shimo4228/can-you-trace-the-cause-after-an-incident-neo)
  3. [AI Agent Black Boxes Have Two Layers: Technical Limits and Business Incentives](https://dev.to/shimo4228/ai-agent-black-boxes-have-two-layers-technical-limits-and-business-incentives-jhi)
- [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) — a structured agent implementation that does not use ReAct. Corresponds to the (3) LLM Workflow Quadrant.
- [Agent Attribution Practice (AAP)](https://github.com/shimo4228/agent-attribution-practice) — a research repo addressing agents' responsibility-bearing subjects and attribution. The four-quadrant names in this series align with AAP.
