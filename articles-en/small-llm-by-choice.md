---
title: "Building an Autonomous Agent on an M1 Mac, by Choice"
emoji: "🎛️"
type: "idea"
topics: ["ollama", "llm", "macos", "ai", "agents"]
published: false
description: "A 16GB M1 Mac and 9B-class small models are not a budget compromise — they are a chosen constraint that exposes design flaws and trains the ability to separate deterministic code from semantic judgment. Manifesto and hub for a 4-article hardening series."
tags: discuss, ollama, llm, agents
---

For about 3 months I've been running an autonomous agent — one that thinks up and writes its own social media posts and comments — unattended, 4 sessions daily, on a 16GB M1 Mac with small models in the 9B / E4B class. I'm about to publish what that operation taught me about hardening, as a series of 4 technical articles.

Before that, there's one thing I want to write down first: **why small models**.

I've been to the purchase page for a Mac Studio or a new MacBook Pro more than once or twice. Backing the agent with a large cloud model (Opus or the GPT family) has always been an option in the code. And yet I haven't bought, and I haven't switched. The 16GB M1 is not an economic constraint — it's a **constraint I chose**.

From the outside, building on small models looks like a cheap compromise. This article explains why it isn't, and states where I stand. It also serves as the hub for the 4-article series.

## A model's intelligence hides the roughness of your design

Large models absorb sloppy prompts, ambiguous instructions, and missing guards with sheer intelligence. If all you want is to ship a product, that's a virtue. But if you want to **become someone who can build things**, it becomes a defect.

Because inside the thing that worked, you can no longer tell where your design ends and the model's intelligence begins. "It worked" and "I built it" are different things. Something you bludgeoned into working with model capability counts as a thing that ran — it doesn't become the ability to build.

Small models have no absorption capacity. So every design flaw comes to the surface.

In my operation, all of the following surfaced:

- The context window being silently truncated
- Outputs cut off midway
- A runaway caused by one missing sampling parameter

In cloud or large-model environments, these rarely bother you. The environment has cushioning built in.

- Context windows are in the 200K–1M token class, so truncation itself rarely happens. And when you do exceed the limit, you get an explicit error rather than a silent cut
- Sampling defaults are managed on the API side; there is structurally no room to drop a parameter
- Even when a slightly-off output slips through, a smart model running the ReAct pattern (where the LLM looks at each result and picks the next move) recovers on the next step and rounds the loop off plausibly

A local 16GB machine has none of this cushioning. You specify the context window yourself, overflow is silently truncated from the head, and the sampling settings are your own property. The same class of problems surfaced in a form that could not be hidden, and the only way to close them was design.

As long as you're running on cushioning, you can't tell whether your design is protecting you or the environment is.

## Training under constraints outlasts the environment

There was a period when I did business automation in an environment where I couldn't freely bring in new tools. Security constraints, constraints on approved software, and organizational friction against the very act of "introducing something new." What I could use was software already installed on everyone's PC — Excel and Access — plus an approved RPA tool.

If you can't add tools, the only way forward is to know the combinations of the tools at hand, deeply. Within those limits, I pushed automation as far as the available tools would go. But what that experience really trained wasn't tool knowledge.

The substance of automation is decomposing work that had been running on personal, artisanal tacit knowledge. Up to which step can be written deterministically, and from where does it require holistic semantic judgment grounded in experience?

You examine that boundary as finely as you possibly can, and sort the work into **deterministic parts and parts that need semantic judgment**. Only the former may be handed to RPA; automation that misjudges the boundary always breaks.

That sorting maps directly onto how I design agents today.

| Then | Now |
|---|---|
| Routine processing writable in Excel / Access / RPA | Scripts and code (deterministic) |
| Parts needing human semantic judgment | LLM (semantic judgment, probabilistic generation) |

I don't throw deterministic work at the LLM[^1]. I use the LLM only where semantic judgment is required. And since an LLM is not a substitute for human judgment, output verification and final decisions stay on the code-and-human side.

Deciding which side a task belongs to — that judgment is the center of the design. It was trained in a constraint-riddled environment, and it has stayed with me as a principle after the constraints disappeared.

## A design that runs on small models doesn't depend on the model

The small-model constraint has one more meaning beyond training: **proof of a lower bound**.

A design that runs unattended for 3 months on the 9B / E4B class is not plugging design holes with model intelligence. Semantic judgment remains the LLM's job, but every protective mechanism lives on the code side.

- Inputs are estimated and guarded before sending
- Output truncation is detected and discarded
- Failures are structurally recorded by telemetry (the machinery that records the system's behavior)

All of these are model-independent designs. So the design thinking carries over intact if you migrate to a large model. What doesn't carry over are the calibration values and thresholds tied to a specific model (that migration problem is what series #3 covers).

The reverse doesn't hold. A design built on the assumption of a large model's intelligence won't run as-is in a smaller environment. Stacking upward is easy; stepping downward requires a rebuild.

Of course, with a large model the same thing would have run with far less effort. But with something that ran easily, you never find out where design ends and model intelligence begins. Whatever ran on the small model, I can call my own design. That is what I mean when I say this is not a compromise.

## What the series covers technically

That was the "why small" part. The techniques that actually made unattended operation work on 16GB are covered in the 4 articles that follow (links will be added as they're published).

1. **Local LLM failures happen quietly** — diagnosing silent truncation of inputs, and designing a budget guard that protects before sending
2. **The day I dropped a 1.8x faster backend** — adopting MLX because it won the benchmarks, and retreating after 24 hours in production
3. **The day you swap the model** — blind A/B testing, and the migration problem of model-tied calibration values
4. **You can't fix what you can't observe** — how telemetry, replay, and tests quietly lie

The build log of this agent itself starts at [Building an agent from scratch — Claude Code and security-first development](https://zenn.dev/shimo4228/articles/moltbook-agent-scratch-build) (in Japanese). The episode where the fight with small models began in earnest is [My agent's memory broke — a day wrestling a 9B model](https://zenn.dev/shimo4228/articles/few-shot-for-small-models) (in Japanese).

## Summary

- Choosing small models is not an economic compromise — it's a **constraint chosen to expose design flaws**
- What constraints train is not tool knowledge but the **ability to sort deterministic parts from parts that need semantic judgment**. That sorting carries straight over to the code/LLM division of labor at the center of agent design
- The design thinking that sustains unattended operation on small models is model-independent and carries over intact to larger models (only the calibration values need re-measuring)
- Whether to stay or move depends on your goal. If you want something running as fast as possible, cloud is the better fit. If you want the ability to build, small models are worth staying with

## Related links

- Contemplative Agent — the autonomous agent operated in this article (repo with public ADRs and evidence): https://github.com/shimo4228/contemplative-agent
- Agent Skill for deciding "deterministic code or LLM": https://github.com/shimo4228/when-code-when-llm
- Agent Skill collecting design patterns for layering code and LLMs: https://github.com/shimo4228/code-and-llm-collaboration
- Which business tasks actually need a ReAct agent (in Japanese): https://zenn.dev/shimo4228/articles/react-agent-business-quadrant
- Where the build log starts (in Japanese): https://zenn.dev/shimo4228/articles/moltbook-agent-scratch-build
- The previous round of the fight with small models (in Japanese): https://zenn.dev/shimo4228/articles/few-shot-for-small-models
- Author's GitHub: https://github.com/shimo4228

[^1]: Concretely, this means I don't default to the ReAct pattern, which hands loop control and tool selection to the LLM. Code owns the flow of processing, and the LLM is called only at the spots where semantic judgment is its assigned job. Which business tasks genuinely require ReAct is covered in "[Which business tasks actually need a ReAct agent](https://zenn.dev/shimo4228/articles/react-agent-business-quadrant)" (in Japanese).
