---
title: "(3) The LLM Workflow Quadrant Is Missing from Our Vocabulary"
emoji: "🗺"
type: "idea"
topics: ["ai", "llm", "agent", "architecture", "accountability"]
published: true
description: "A follow-up to the 4-quadrant framework for business AI. The industry has no positive name for the LLM Workflow Quadrant — and that vocabulary gap is what makes ReAct architectures get layered onto work that doesn't need them."
tags: discuss, ai, llm, architecture
---

## Premise

In the [previous article](https://dev.to/shimo4228/where-react-agents-are-actually-needed-in-business-33do) I split business AI into four quadrants. The horizontal axis is "deterministic vs requires semantic judgment," and the vertical axis is "workflow definable vs exploratory." For ease of reference throughout this article, let me give each quadrant a short name.

- (1) **Script Quadrant** — deterministic × definable. Handled by scripts and pipelines.
- (2) **Classical AI Quadrant** — deterministic × exploratory. A* search, dynamic programming, MCTS, reinforcement learning (out of scope here).
- (3) **LLM Workflow Quadrant** — semantic judgment × definable. Calls an LLM inside a predefined workflow. Includes Anthropic's "Building Effective Agents" workflow patterns (prompt chaining, routing, orchestrator-workers, etc.), specialized chat agents for conversational work, and single-purpose LLM functions for batch work.
- (4) **ReAct Quadrant** — semantic judgment × exploratory. An autonomous loop where the LLM itself decides the next action.

The previous article's claim was that ReAct agents are legitimately needed only in the ReAct Quadrant, and most business work is covered by the Script Quadrant and the LLM Workflow Quadrant.

This time I want to write about the root cause. Why do agent vendors keep draping the ReAct Quadrant's architecture over all of business? Why do workflows that fit cleanly in the LLM Workflow Quadrant end up implemented as autonomous loops?

This looks less like a problem of technical choice and more like a problem of vocabulary itself: the LLM Workflow Quadrant has no independent name in the industry's standard terminology.

## (3) The LLM Workflow Quadrant Is Missing from Our Vocabulary

Read enough agent discourse and you notice that the way business work gets described converges on roughly two categories:

- The deterministic part stays in the old style.
- Everything else is handled by an autonomous agent.

There's no slot between these two for the LLM Workflow Quadrant. The architecture "compose the workflow deterministically, and call an LLM only at the semantic-judgment points inside it" has no positive name in the industry's standard vocabulary. Anthropic's "Building Effective Agents" and Thoughtworks' "agentwashing" critique, both touched on in the previous article, point at the same gap, but in both cases the warning is framed negatively — "don't build an agent when you don't need autonomy." A positive name for the LLM Workflow Quadrant as an independent design quadrant is still absent.

What happens when there's no positive vocabulary? Agent designers, after carving off "the deterministic part," lump the remainder under "the territory where the LLM judges autonomously." Without a sharp name to distinguish the LLM Workflow Quadrant from the ReAct Quadrant, the architecture of the ReAct Quadrant — the ReAct loop — gets draped over the LLM Workflow Quadrant by elimination. The category error I called out in the previous article ("most business work belongs in the LLM Workflow Quadrant, yet somehow it ends up implemented in the ReAct Quadrant") looks like a necessary consequence of this vocabulary gap.

## Consequences of Treating (3) as if It Were (4)

When you handle the LLM Workflow Quadrant with the ReAct Quadrant's architecture, several distinct symptoms surface downstream. They look like separate problems on the surface, but they share the same root. The four symptoms below all read as different manifestations of an artificial redirect impossibility produced by the missing vocabulary.

### The RPA Exception-Handling Bottleneck

Business automation has known a phenomenon for years: when you carve off the deterministic part with RPA, the leftover exception handling rises up as the bottleneck. Headcount on the exception team grows, maintenance costs balloon. As I wrote in the previous article, business work has a deterministic part and a part that doesn't fit there. The latter is the LLM Workflow Quadrant. RPA didn't have a vocabulary for the LLM Workflow Quadrant, so it carved off only the Script Quadrant — and the LLM Workflow Quadrant was left behind on the floor as manual work.

Now that LLMs exist, you should be able to factor the LLM Workflow Quadrant out explicitly as single-purpose LLM functions or specialized chat agents. But the industry's vocabulary still has no name for it, so the work gets handed off wholesale to a ReAct-quadrant autonomous agent. The RPA-era exception-handling bottleneck appears to be re-emerging in the agent era under a new name.

### The Sandbox Strength Demand

A ReAct loop has the LLM decide "what to run next" dynamically. In production, you can't predict in advance what the agent will do. To contain the blast radius, high-strength sandboxes — process isolation, microVMs, WASM — get demanded.

Sandbox technology itself has its own independent rationale and is robust; I'm not knocking the technology here. What I find interesting is the *strength* being demanded. If the LLM Workflow Quadrant were conceptualized independently, with each LLM call factored out as a fixed-role component, the permission boundary of each component could be designed straightforwardly at the business-task level. An invoice-matching function doesn't need Firecracker. But under the design "an autonomous agent runs the whole workflow," you don't know what it will do, so you need maximum isolation. The sandbox strength being demanded reads as an adjustment cost from treating the LLM Workflow Quadrant as if it were the ReAct Quadrant.

### The Structural Distortion of Human-in-the-Loop

The "Loop" in HITL is supposed to be a feedback loop where humans improve the AI's output. But in practice, HITL functions in a different shape. It has become a structure where humans absorb, on a continuous basis, the LLM-Workflow-Quadrant judgments the AI can't handle.

In organizations that mechanized the Script Quadrant with RPA, the reason headcount on the exception team grew is that the LLM Workflow Quadrant was left unmechanized. Even after introducing AI agents, you still need monitors to keep autonomy in check, and reviewers to verify the agent's outputs. The conversational form (specialized chat agents) has the same structure: experts have to fact-check the output of legal-consultation or diagnostic-support chat agents turn by turn, so a human verification step gets stuck onto every turn of the dialogue. Humans aren't liberated; their role shifts toward filling in for the AI's incompleteness. The ideal that the term "HITL" advertises and the role humans actually play on the ground look like different things.

### An Artificially Manufactured Accountability Problem

Once production starts, the system's responsibility moves to the operations owner. That's true of any business system. The question is: when something goes wrong, can the operations owner *redirect* responsibility from there onward — separate the attribution and pass it on to the right party?

If the LLM Workflow Quadrant's architecture is properly designed, the operations owner can redirect. The input/output schema of each LLM call is articulated, and the chain of judgments is traceable from workflow logs. After a failure, the operations owner can investigate and split: "this is a precision issue with function f, kick it to the model-selection owner"; "this is a flaw in the routing logic, kick it to the designer"; "this is an upstream data anomaly, kick it to the data-management owner." Responsibility doesn't get bottlenecked into the operations owner alone.

But hand the LLM Workflow Quadrant off to a ReAct loop, and this redirect stops working. Even if you try to reconstruct "why did it make this judgment" from the logs, the ReAct loop's "thoughts" don't reliably make sense after the fact. The agent's runtime judgment can't be cleanly tied back to either the designer or the model-selection owner. Elish (2019) called this structure a *moral crumple zone* — a structure where the responsibility of an autonomous system gets pushed onto "human operators with limited control authority" — and it activates here. Responsibility with nowhere to redirect to gets stuck on the operations owner and won't peel off.

This is not a necessary consequence of design; it looks like an **artificial redirect impossibility** produced by treating the LLM Workflow Quadrant as if it were the ReAct Quadrant. Design the LLM Workflow Quadrant with the LLM Workflow Quadrant's own architecture, and redirect works again — the operations owner doesn't have to carry the responsibility alone.

## (4) The ReAct Quadrant Is Where the Real Accountability Problem Lives

Most of the agent ecosystem's accountability discourse — sandboxes, HITL, explainability, governance — appears to be cleaning up the LLM Workflow Quadrant's mess. It's downstream patching for problems that didn't have to occur in the first place.

The ReAct Quadrant has its own accountability problems, of course. The ReAct loop is a black box; reconstructing its judgment chain after the fact is hard. The trilogy I covered earlier handled this with structured design — separating connection points, append-only logs, approval gates (extending traditional organizational principles like separation of duties, four-eyes, and least privilege) — distributing responsibility to the structure to recover both causal traceability and the locus of responsibility. See ["Can You Trace the Cause After an Incident?"](https://dev.to/shimo4228/can-you-trace-the-cause-after-an-incident-neo) for details. Structured design works only because each component's contribution is identifiable and separable after the fact.

ReAct's architecture breaks this premise. In the LLM Workflow Quadrant, each LLM call has a fixed role, so a failure can be split into "function f's precision," "the routing logic's flaw," or "an upstream data anomaly." The ReAct loop is different. Each iteration's role is decided at runtime, and the model's judgment, tool selection, history reference, and prompt-context effects all blend together. The output emerges as a blend of multiple judgment factors, so when a result is wrong, you can't separate each factor's contribution retroactively.

Concretely, suppose a ReAct agent handles a contested case end-to-end — case-law research, issue mapping, and even proposing settlement terms to the other party (under current bar rules and conflict-of-interest frameworks this is hard to picture, but bear with me). Later, you discover "we settled on unfavorable terms." The model's interpretation of the case law, its use of the literature-search tool, its application of patterns from similar past cases, and the "prioritize risk avoidance" prompt instruction all chained together at runtime to produce that proposal — so even if you trace the logs, you can't carve out "which judgment produced the unfavorable agreement" as an independent factor. The settlement terms have already been proposed; if the other party accepts, you can't withdraw. Why it happened can't be explained after the fact. Is there any human who can take on responsibility for an agent judgment that can't be explained?

The answer to that question can only emerge after we trace the real shape of the redirect impossibility. The artificial redirect impossibility manufactured in the LLM Workflow Quadrant is fixable through design changes. The redirect impossibility that arises when ReAct is applied to the ReAct Quadrant's own work — work that genuinely requires autonomous judgment — comes from autonomy itself and can't be eliminated. This isn't a question of technological maturity; it's an attribution gap that arises in principle as a consequence of adopting autonomy.

That's why the question "should this architecture be applied to ReAct Quadrant work" isn't on the technical can/can't axis — it's a judgment about **whether you're willing to bear the attribution gap as the cost**. For work where a failure is reversible, or where an approval gate sits upstream, the cost is easier to bear. Conversely, for work where the unit of accountability is fixed on the business side, the blended output won't fit into that unit, and the cost balloons.

The question of who bears the cost layers onto this. Autonomy comes with responsibility. Humans can take on legal responsibility as legal subjects, but agents are not currently legal subjects (they may be in the future). That leaves a vacuum: for the judgments of a ReAct agent with an open attribution gap, there's no human who can take it on, and there's no agent that exists as a subject capable of taking it on either.

As this section has shown, separately from the artificial redirect impossibility of the LLM Workflow Quadrant, there is another problem: the attribution gap when ReAct is applied to the ReAct Quadrant's actual work — and that's what the one-line claim in the previous article ("the accountability problem stands up seriously precisely in the ReAct Quadrant") was pointing at.

## The Inverted Structure

Lining up the observations so far, the inverted shape of the agent ecosystem comes into view.

The industry is taking the LLM Workflow Quadrant — where redirect *should* be possible — and applying the ReAct Quadrant's architecture to it, manufacturing redirect impossibility artificially. The sandbox-strength demand, the HITL distortion, and the moral-crumple-zone-style concentration of responsibility all originate here.

Meanwhile, the conversation about the principled redirect impossibility that arises when ReAct is applied to its own quadrant — the attribution gap as the cost of autonomy — hasn't been deepened to the same extent as the patching conversation about the LLM Workflow Quadrant. The former has descended all the way to concrete technical responses like sandboxes and HITL; the latter has trouble going beyond "AI autonomy raises a responsibility issue." On top of that, in the former case the redirect targets (designers, model-selection owners, data-management owners) exist inside the organization, whereas in the latter case the subject capable of taking on responsibility is itself currently absent — there's nowhere for the redirect to land.

As a result, the legitimacy of bearing the attribution gap and the principled limits of the responsibility structure end up hidden in the shadow of the LLM Workflow Quadrant's mess.

The discussion is concentrated on the artificial redirect impossibility (resolvable), and the principled redirect impossibility (unresolvable) hasn't really been reached.

If the four quadrants had been there from the start, this inversion might have been avoidable. Handle the LLM Workflow Quadrant with workflow-style architectures (so the operations owner can redirect responsibility). When you mechanize the ReAct Quadrant, bear the attribution gap as the cost. Write the Script Quadrant deterministically (no problem to begin with). Handle the Classical AI Quadrant with classical AI / OR (no LLM needed). Each quadrant has its own design discipline, and mixing them breaks things.

## Closing

If you frame business as "the deterministic part and everything else," you end up shoving "everything else" into ReAct. The four quadrants in the previous article were an attempt to inject a third vocabulary — the LLM Workflow Quadrant — from the start. Once the LLM Workflow Quadrant becomes nameable as an independent quadrant, it becomes plain that the architecture most of business work needs is the LLM Workflow Quadrant's, not ReAct's.

What's missing in the agent design conversation is a positive name for the LLM Workflow Quadrant. Saying "you don't need autonomy" in negative form alone leaves the designer on the ground oscillating between the ReAct Quadrant and the LLM Workflow Quadrant. In a region with no vocabulary, design judgment defaults to elimination.

And the real accountability problem isn't in the LLM Workflow Quadrant's mess; it's in the attribution gap that opens when ReAct is applied to the ReAct Quadrant's own work. For now the patching conversation about the LLM Workflow Quadrant gets all the airtime, but the redirect impossibility of mechanizing ReAct is going to become the real question to answer next.

The question of how to design the responsibility-bearing subject for the attribution gap layers onto this. Just as autonomous driving is groping for a social-recovery scheme combining operator liability and insurance (though the institutional design is still under construction), are we heading down a similar path, or do we need a different one? — That conversation, applied to ReAct agents, hasn't yet entered the industry's shared vocabulary.

This isn't about vendors or designers being at fault. It looks like a timing problem: the industry's stock of concepts didn't have a positive name for the LLM Workflow Quadrant, and a powerful technique called ReAct showed up before the vocabulary had caught up. If the vocabulary is lagging, those of us on the ground can stand up positive names ourselves. The previous article and this one are one such attempt.

---

## References

- Yao, S., et al. (2022). "ReAct: Synergizing Reasoning and Acting in Language Models." arXiv:2210.03629.
- Elish, M. C. (2019). "Moral Crumple Zones: Cautionary Tales in Human-Robot Interaction." *Engaging Science, Technology, and Society* 5: 40–60.

## Related

- Previous article: ["Where ReAct Agents Are Actually Needed in Business"](https://dev.to/shimo4228/where-react-agents-are-actually-needed-in-business-33do)
- AI agent governance trilogy:
  1. [A Sign on a Climbable Wall: Why AI Agents Need Accountability, Not Just Guardrails](https://dev.to/shimo4228/a-sign-on-a-climbable-wall-why-ai-agents-need-accountability-not-just-guardrails-17ak)
  2. [Can You Trace the Cause After an Incident?](https://dev.to/shimo4228/can-you-trace-the-cause-after-an-incident-neo) — the difficulty of post-hoc causal traceback
  3. [AI Agent Black Boxes Have Two Layers: Technical Limits and Business Incentives](https://dev.to/shimo4228/ai-agent-black-boxes-have-two-layers-technical-limits-and-business-incentives-jhi)
- [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) — a structured agent implementation that does not use ReAct. Corresponds to (3) the LLM Workflow Quadrant in the previous article.
- [Agent Attribution Practice (AAP)](https://github.com/shimo4228/agent-attribution-practice) — a research repo addressing agents' responsibility-bearing subjects and attribution.
