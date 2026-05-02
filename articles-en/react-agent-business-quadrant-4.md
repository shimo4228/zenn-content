---
title: "Between the Workflow and ReAct Quadrants: How Phase Decides Skill Design"
emoji: "🌗"
type: "idea"
topics: ["ai", "llm", "agent", "architecture"]
published: false
description: "The fourth article in the ReAct quadrant series. The (3) LLM Workflow Quadrant and the (4) Autonomous Agentic Loop Quadrant aren't a clean dichotomy — there's a continuous gradient between them, and where a skill lands on that gradient appears to be decided primarily by phase, not by model capability."
tags: discuss, ai, llm, architecture
---

> **Series position:** The fourth article in the ReAct agent quadrant series. The quadrant names align with the previous articles and with the [AAP repository](https://github.com/shimo4228/agent-attribution-practice).

## Premise — The Four Quadrants Again

Recapping the four quadrants set up in the [first article](https://dev.to/shimo4228/where-react-agents-are-actually-needed-in-business-33do):

- (1) **Script Quadrant** — deterministic × definable. Handled by scripts and pipelines.
- (2) **Algorithmic Search Quadrant** — deterministic × exploratory. Classical AI / OR territory.
- (3) **LLM Workflow Quadrant** — semantic judgment × definable. Calls an LLM inside a predefined workflow.
- (4) **Autonomous Agentic Loop Quadrant** — semantic judgment × exploratory. An autonomous loop where the LLM itself decides the next action (= ReAct agent).

Up to the previous article, I treated (3) and (4) as a dichotomy — "pick one based on the nature of the work." [The second article](https://dev.to/shimo4228/3-the-llm-workflow-quadrant-is-missing-from-our-vocabulary-n18) pointed out that the industry has no settled vocabulary for (3); [the third article](https://dev.to/shimo4228/is-react-needed-in-production-separating-design-and-operation-phases-2bn1) framed the dichotomy along the business-system axis and introduced the Phase Separation between design phase and operation phase. This article brings that Phase Separation down to the resolution of individual skill design and tries to show that, between the two poles of the dichotomy, a **continuous gradient** exists.

## Observation — The Same Job Lives in Multiple Forms

Looking around my own repositories, I notice that conceptually identical jobs are implemented in several different forms. The **Promote phase** of [AKC (Agent Knowledge Cycle)](https://github.com/shimo4228/agent-knowledge-cycle) — a six-phase cycle in which an agent distills knowledge from its own outputs to self-improve — is a typical example. The job is to extract recurring principles from skills and promote them to rules. Generalized, it's the work of "**extracting principles from repetition**." Mining alert rules from logs, finding common patterns across a codebase to refactor, weaving an FAQ from customer-support conversation logs — they all belong to the same family.

In [`contemplative-agent`](https://github.com/shimo4228/contemplative-agent) there's a Python function called [`core/rules_distill.py`](https://github.com/shimo4228/contemplative-agent/blob/main/src/contemplative_agent/core/rules_distill.py). It vectorizes skills with embeddings, builds theme-based clusters via `cluster_patterns`, batches LLM calls with `MAX_RULES_BATCH=10`, and the cluster threshold `CLUSTER_THRESHOLD_RULES=0.65` is calibrated with a calibration file. The LLM call is just one step in the pipeline, and most of the judgment has been frozen into code in advance.

The [`rules-distill`](https://github.com/shimo4228/claude-skill-rules-distill) skill (`~/.claude/skills/rules-distill/SKILL.md`), by contrast, is written in natural language. In Phase 1, `scan-skills.sh` produces the file listing; in Phase 2, theme-based cluster judgment is delegated to a sub-agent; merges across batches are also decided by LLM judgment. Scripts are used only for listing and persistence — the judgment itself sits in the runtime LLM's hands.

The two are doing the same job. And yet the implementations are dramatically different.

## Surface Hypothesis — Model Capability

The first explanation that comes to mind is **model capability**. `core/rules_distill.py` was written to run in a 9B local-model environment. In my hands-on experience, getting a 9B model to robustly run theme-based cluster judgment at runtime is hard. So a deterministic scaffold of embeddings + clustering + threshold tuning limits the 9B's role to "generate one rule candidate from a given cluster." Conversely, in a Claude Code environment where Opus is callable at runtime, that scaffold is no longer needed. Cluster judgment and merge judgment can both be performed by an LLM that takes the entire context into account.

This is consistent with a design principle recorded by AKC — README's Design Principle 5: "Evaluation scales with model capability — small models run on rubric evaluation; Opus class runs on qualitative evaluation that takes the full context into account." The original is scoped to evaluation, but extended to implementation-position choice — varying judgment scale with capability — the 9B-era Python pipeline and the Opus-era natural-language skill read as the two endpoints of that extension.

But this explanation is only stroking the surface of where things get implemented. The capability gap is an observable fact, but it's a **downstream consequence of a deeper decision**.

## Deeper Hypothesis — The AAP Phase

Back to the **distinction between design phase and operation phase** from the previous article, [Is ReAct Needed in Production?](https://dev.to/shimo4228/is-react-needed-in-production-separating-design-and-operation-phases-2bn1). What's really driving the choice of implementation position is this phase axis.

`contemplative-agent` sits in the **operation phase**. Once deployed, inputs flow through fixed routes. The boundaries between inputs (persona templates, dialogue, memory) and outputs (responses, logs) are settled in advance, and the internal knowledge cycle similarly runs through six predefined phases. Because the pipeline is frozen for operation, structures like embeddings / clustering / thresholds / batches in `core/rules_distill.py` can be baked into Python. The 9B is *a choice that becomes available* in this environment, not the cause.

In fact, the `contemplative-agent` pipeline is built so that the LLM-call portion can optionally be swapped to Claude or GPT models. Scaling capability upward leaves the LLM-function pipeline largely intact. This works as a counter-experiment against the surface hypothesis (capability requires the pipeline structure). If capability were the cause, the pipeline structure should become redundant and start to fall apart the moment you switch to Opus class. But it doesn't. **What requires the pipeline structure isn't capability — it's the phase decision of being in the operation phase.** Capability is just a downstream choice that follows from the phase decision.

`Claude Code` is **a tool that lives in the design phase**. Each session is itself exploratory work: the target codebase, the IDE, the agents being used, and even the file types being handled (.py / .ts / .md / .ipynb / arbitrary) shift between sessions. One time it's a Python project, another time a Next.js project, another time a documentation repo centered on ADRs. If a skill freezes paths or file structure in advance, it breaks the moment the environment changes. So the skill body is written in natural language and adapts to the runtime context. Opus is a *consequence* — it's the capability needed to support the holistic judgment that runtime adaptation demands — not the cause.

So:

- contemplative-agent can be written in `core/rules_distill.py` form = **because the pipeline was frozen for the operation phase**
- Claude Code has to be written in `rules-distill` skill form = **because the design phase makes freezing the environment impossible**

Capability appears to sit downstream of this phase decision. The phase draws the line between "hardcodable" and "flexibility-required," and inside that line capability gets selected. AKC's extended principle "capability ↑ → holistic judgment OK" reads as a secondary principle that holds once the phase decision is taken as given.

## Inside a Phase — Same Phase, but Task Pulls Position

Even narrowing the lens to the design phase, implementation position splits further.

There's a skill called [`skill-comply`](https://github.com/shimo4228/claude-skill-comply). It measures whether Claude's skill / rule / agent definitions are actually being followed at runtime. It auto-generates scenarios at three prompt-strictness levels (supportive → neutral → competing), runs `claude -p`, and classifies tool-call traces to report compliance rates. The directory contains `pyproject.toml` / `prompts/` / `fixtures/` / `tests/` / `scripts/` / `results/`. The internal requirement of the task is that scenario execution be reproducible — otherwise compliance rates are meaningless. Generalized, it sits next to static code analysis (lint, SonarQube) or automated benchmark measurement: jobs that require **the same input to return the same verdict**. It's a skill in the design phase, but **the task nature of evaluation/measurement requires reproducibility**.

A different skill, [`search-first`](https://github.com/shimo4228/claude-skill-search-first), looks for existing libraries and tools before new implementation begins. The directory contains only a single `SKILL.md` file. It delegates to the scout agent and returns an Adopt / Extend / Build verdict. Generalized, it's close to what an engineer does when, before building a new feature, they roam GitHub and PyPI to narrow down candidate libraries and decide context-appropriately whether to Adopt or Build. The same set of candidates doesn't need to come back every time — context-appropriate verdicts are what's wanted. It's a skill in the design phase, where **the task nature of selection demands pure judgment**. Reproducibility is secondary; returning a slightly different candidate set each time is fine.

Both sit in the design phase and run in the same environment of Opus + open environment. And yet implementation position splits, with one (`skill-comply`) closer to workflow and the other (`search-first`) closer to ReAct. This shows that even after the phase is fixed, **task nature pulls position independently**.

That said, phase and task aren't fully orthogonal. Tasks with strong reproducibility requirements in the operation phase get pushed hard toward the workflow side — phase changes how task nature surfaces. This article handles the two axes coarsely as a split; examining the size of the interaction more precisely is out of scope here.

## The Same Phase Axis Descends Into Skills

The same phase axis descends not only at the skill level but at the level of subcomponents inside a skill. The contrast between [`skill-stocktake`](https://github.com/shimo4228/claude-skill-stocktake) and [`context-sync`](https://github.com/shimo4228/claude-skill-context-sync) is emblematic.

`skill-stocktake` is a skill that lists installed Claude skills and commands and audits their quality. The domain definition — "which skill files are evaluation targets" — is hardcoded in scripts (`~/.claude/skills/`, `{cwd}/.claude/skills/`). Generalized, it sits next to SBOM (Software Bill of Materials, a list of dependency libraries contained in a piece of software) generation and dependency scanning: jobs that require **mechanically enumerating targets**. The benefit is **no targets get missed**. The drawback is that it **assumes the Claude Code environment** and won't run as-is in a different coding-agent environment. Generalizing it would mean writing per-agent scripts, and maintenance cost piles up.

`context-sync` is a skill that detects role overlap, staleness, and gaps in a project's documentation (CLAUDE.md / CODEMAPS / ADR / README, etc.) and fixes them. Unlike `skill-stocktake`, the domain definition is delegated to the LLM's holistic judgment. Generalized, it's close to what a tech lead does when reading a project's architecture and judging "this explanation is stale, that should be moved to an ADR." So if it finds an llms.txt it includes that as a sync target, and it picks up Codemaps, ADRs, and AGENTS.md (a file that plays the same role under a different name) by inference. The benefit is **portability across environments**. The drawback is that **detection coverage wavers** between runs, and at full codebase scale, even when detection succeeds, **the diff can't be fully captured**.

| Comparison | skill-stocktake | context-sync |
|---|---|---|
| Where domain definition lives | Hardcoded in scripts | LLM judgment |
| Coverage | No misses | Wavers |
| Portability | Single-environment | Cross-environment |
| Scale tolerance | High | Low |

By "subcomponent" here I mean the processing steps inside a skill. From the outside, one skill is one job; internally it splits into several steps. Take `skill-stocktake`: it can be split into (A) the **target-enumeration** step that decides "which skill files are evaluation targets" and (B) the **quality-judgment** step that "judges the quality of each skill." `context-sync` is isomorphic: (A) "which documents to sync" (target enumeration) and (B) "judge staleness and which sections should be moved" (quality judgment). What I'm calling a subcomponent is **a step inside the skill**, like A or B above.

What this shows is that the phase axis descends **not only at the skill level but at the subcomponent level inside a skill**. Even between two skills that belong to the same phase, the layout step by step differs. `skill-stocktake` is a **hybrid layout** that puts A (target enumeration) in scripts and B (quality judgment) in the LLM. `context-sync` is a **ReAct-leaning layout** that puts both A and B in the LLM. Even within a single skill, one part can sit on the workflow side and another on the ReAct side.

The reason the two land on different layouts inside the same design phase is that they differ in **target identifiability**. The design phase is, by nature, "the environment moves," but how it moves varies by target. The targets of `skill-stocktake` — Claude's skills — sit at **fixed locations under fixed naming conventions**: `~/.claude/skills/` (global) and `{cwd}/.claude/skills/` (project). Even in the design phase, paths can be hardcoded in scripts. The targets of `context-sync` (`CLAUDE.md` / `CODEMAPS/` / `docs/adr/` / `AGENTS.md` / `llms.txt` ...), by contrast, vary in placement and naming across codebases. They can't be written into scripts, so the only option is to delegate to the LLM's holistic judgment.

A further limit, on the LLM-judgment side, is **scale tolerance**. Up to mid-sized codebases, the LLM's holistic judgment covers the whole, but at full scale it starts missing diffs. Even when capability climbs sufficiently, this miss rate doesn't disappear. AKC's Design Principle (capability ↑ → holistic judgment OK) covers neither **target identifiability** nor **scale tolerance**.

## Closing

The (3) LLM Workflow Quadrant and the (4) Autonomous Agentic Loop Quadrant are useful as an axis for classifying the nature of work. But once you think about individual skill design, between the two quadrants there's a continuous gradient, and where you land on that gradient appears to be **decided primarily by the phase decision**. The capability gap is just a result observed downstream of the phase decision.

As [the second article](https://dev.to/shimo4228/3-the-llm-workflow-quadrant-is-missing-from-our-vocabulary-n18) pointed out, the industry doesn't yet have settled vocabulary for talking about (3) as an independent quadrant. This article tries to step further from that point, into the continuous gradient inside the dichotomy. The same job gets implemented in different positions in the operation phase versus the design phase. Within the same phase, position shifts when the task nature differs. Inside a single skill, position splits subcomponent by subcomponent.

The previous article framed Phase Separation as an axis of business systems; this article tried to show that the same axis runs all the way down to the resolution of individual skill design. The same phase axis primarily decides both how business gets carved up and where skill implementation lands.

One direction left open is the observation that the optimal position shifts when the phase shifts. An implementation position that was correct in one environment is no longer optimal once the phase changes. How to translate the question this raises into implementation — I don't have an answer in hand. I'll leave it as a design problem outside the scope of this article.

---

## Related

- Previous articles in this series:
  1. ["Where ReAct Agents Are Actually Needed in Business"](https://dev.to/shimo4228/where-react-agents-are-actually-needed-in-business-33do)
  2. ["(3) The LLM Workflow Quadrant Is Missing from Our Vocabulary"](https://dev.to/shimo4228/3-the-llm-workflow-quadrant-is-missing-from-our-vocabulary-n18)
  3. ["Is ReAct Needed in Production? — Separating Design and Operation Phases"](https://dev.to/shimo4228/is-react-needed-in-production-separating-design-and-operation-phases-2bn1)
- AI agent governance trilogy:
  1. [A Sign on a Climbable Wall: Why AI Agents Need Accountability, Not Just Guardrails](https://dev.to/shimo4228/a-sign-on-a-climbable-wall-why-ai-agents-need-accountability-not-just-guardrails-17ak)
  2. [Can You Trace the Cause After an Incident?](https://dev.to/shimo4228/can-you-trace-the-cause-after-an-incident-neo)
  3. [AI Agent Black Boxes Have Two Layers: Technical Limits and Business Incentives](https://dev.to/shimo4228/ai-agent-black-boxes-have-two-layers-technical-limits-and-business-incentives-jhi)
- [Agent Knowledge Cycle (AKC)](https://github.com/shimo4228/agent-knowledge-cycle) — source of the "capability ↑ → holistic judgment" principle referenced in this article
- [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) — implementation of `core/rules_distill.py`, an example of the workflow end of the 9B era
- [Agent Attribution Practice (AAP)](https://github.com/shimo4228/agent-attribution-practice) — the four-quadrant names in this series align with AAP
