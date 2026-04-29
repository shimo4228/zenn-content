---
title: "Where ReAct Agents Are Actually Needed in Business"
emoji: "🧩"
type: "idea"
topics: ["ai", "llm", "agent", "architecture"]
published: true
description: "A 4-quadrant framework for business AI. Most workflows don't need ReAct loops — specialized chatbots and single-purpose LLM functions cover (3), and category errors happen when (4) architectures get applied everywhere."
tags: discuss, ai, llm, architecture
---

## The Discomfort

As someone building AI agents, I keep running into a discomfort I cannot shake when I read the README of current agent products.

"Run on a $5 VPS." "Spawn isolated subagents." "Self-improving." "Cron scheduling, running unattended." "Voice memo transcription via Telegram."

The vocabulary is entirely demo vocabulary. Not a single word of business vocabulary appears. Audit. Approval workflow. Role-based access control. Change management. SLA. DR. These are the words that real-world deployments take for granted, but they don't show up in the READMEs of typical agent products.

It seems to me that these aren't designed with production operation in mind. They don't appear to have production in their line of sight.

At first I thought "maybe I'm just biased toward business sensibilities." But it wasn't that. The real source of the discomfort sat somewhere else, I noticed. **Most current agent products take the ReAct autonomous loop too much for granted as the essence of an agent.** And when you actually try to introduce AI into a business, the territory where ReAct agents are legitimately needed turns out to be very narrow once you implement it.

## Premise: How ReAct Works

Let me lay out ReAct first.

ReAct is a way of running LLM agents proposed by Yao et al. in 2022 (paper: "ReAct: Synergizing Reasoning and Acting in Language Models", arXiv:2210.03629). It loops through three elements as a single set:

1. **Thought**: The LLM reasons in language about how to interpret the current situation and what to do next
2. **Action**: It calls an external tool — search, browser, file operations, etc.
3. **Observation**: It reads the result returned by the tool

The loop runs until the LLM itself decides "I have enough information now." The key is that **the LLM decides the next action on its own every turn**. The procedure isn't written ahead of time, so how many times tools are called, which tools are used, and when it ends are all decided at runtime.

For reference, the paper's evaluation targets were HotpotQA (open-domain QA), Fever (fact verification), ALFWorld (interactive exploration in a household environment), and WebShop (open-ended product search). All of these are tasks that demand exploration in unknown environments or open-ended information integration. Application to business workflow isn't discussed in the paper.

This is ReAct's strength, and at the same time its weight. Precisely because everything is decided dynamically, when you map it onto business, the unnecessary cases dominate. I'll dissect this through four quadrants.

## Looking at Business AI in Four Quadrants

When you introduce AI into business, the nature of the work splits across four quadrants along two axes.

- Horizontal axis: Can the processing be **written deterministically, or does it require semantic judgment?** (= Is an LLM needed, or not?)
- Vertical axis: Is the workflow **definable in advance, or exploratory?** (= Does **a path written in advance by humans** decide what to do next, or does **the model decide dynamically at runtime**?)

The vertical axis is essentially the same as Anthropic's "predetermined code paths vs LLM dynamically directs its own process" from "Building Effective Agents" (2024).

|  | Workflow definable | Exploratory |
|---|---|---|
| **Deterministic** | (1) Script / pipeline | (2) Classical AI / OR (out of scope here) |
| **Semantic judgment needed** | (3a) Conversational → specialized chatbot<br>(3b) Batch → single-purpose LLM function | (4) ReAct agent |

(2) is the territory of classical AI / OR (Operations Research) — delivery routing, production scheduling, combinatorial optimization — solved historically by A* search, dynamic programming, Monte Carlo Tree Search, and reinforcement learning. LLMs aren't required for these problems, so I'll set this quadrant aside. Let's walk through the remaining (1), (3), and (4) in order.

### (1) Deterministic × Definable — A Script Is Enough

Form transcription. Data normalization. Lookups. Validation. You don't even need an LLM here. Scripts and a workflow engine cover it. There's no reason to bring AI in.

### (3) Semantic Judgment × Definable — Workflow + LLM Function Is Enough

This is the main battlefield of business AI. Anthropic, in "Building Effective Agents," lays out five workflow patterns that map to this territory (prompt chaining / routing / parallelization / orchestrator-workers / evaluator-optimizer). OpenAI, in "A Practical Guide to Building Agents" (2025), covers the same territory with "manager pattern" and "decentralized pattern."

The shared property is that **the path (in what order to do what) is decided in advance, and the LLM is called as a single step within that path**. The LLM doesn't decide the next action itself.

Since the I/O modality varies by task, (3) splits further into variants. I'll walk through the conversational and batch forms.

#### Conversational

Legal consultation, diagnostic support, internal FAQ, expert knowledge support. Work that's all about judgment.

I find myself doubting whether autonomous agents are needed here. My intuition is that a **specialized chatbot equipped with expert knowledge** is enough for most cases. RAG + system prompt + (history-preserving when needed) LLM calls, with humans making the final call and AI handling knowledge retrieval and organization. At least for many situations, this division of labor seems sufficient.

That said, conversational work also has a spectrum. Simple FAQ is fine with single-shot LLM calls, but multi-turn legal consultation that narrows down conditions, or diagnostic support that calls tools while differentiating diagnoses, increasingly fits Anthropic's workflow patterns (prompt chaining / routing / orchestrator-workers). Even so, whether you need **a loop where the LLM itself decides the next action** (ReAct) seems like a separate question. Most judgment work can be served by having the human — who is the judging agent — decide what to do next.

It might be that judgment-heavy work is exactly where autonomous agents aren't needed. This runs counter to my intuition.

We tend to short-circuit "judgment = thinking = agent," but the thinking in judgment work often looks closer to **knowledge retrieval and organization**. That looks like a different species from the kind of reasoning that needs an agent loop.

#### Batch

Invoice matching. Ticket triage. Address normalization. Threshold checks. Patterns where semantic judgment is scattered inside a deterministic pipeline.

Here too, ReAct isn't needed. A deterministic pipeline controls the flow, and at exception points it calls a single-purpose LLM function. The LLM function's output fluctuates probabilistically — the same input doesn't always return exactly the same output — but the role the function plays is fixed. The shape of "receive a defined input, return a verdict in a defined schema" doesn't change. The pipeline knows what to do next.

#### Example: Invoice Matching

Consider matching invoices against purchase orders (POs) and routing them to approve / reject / needs-review. About 80% can be handled mechanically by deterministic rules.

```python
def process_invoice(invoice: Invoice) -> Action:
    po = lookup_po(invoice.po_id)              # Deterministic: PO lookup
    if po is None:
        return Action.REJECT_NO_PO
    if invoice.date > po.expiry:               # Deterministic: expiry check
        return Action.REJECT_EXPIRED
    if is_duplicate(invoice):                  # Deterministic: dedup check
        return Action.REJECT_DUPLICATE

    if abs(invoice.amount - po.amount) / po.amount <= 0.01:
        return Action.APPROVE                  # Deterministic: approve if amount within 1%

    # From here, the semantic-judgment zone
    # Amount doesn't match, but line items might be expressed differently and effectively equal
    verdict = match_line_items(invoice.lines, po.lines)  # ← single-purpose LLM function
    if verdict == "MATCH":
        return Action.APPROVE
    elif verdict == "PARTIAL":
        return Action.ESCALATE_FOR_HUMAN_REVIEW
    else:
        return Action.REJECT_AMOUNT_MISMATCH
```

The body of `process_invoice` is a deterministic pipeline, and all judgments (PO existence / expiry / duplication / amount) can be written as rules. The only point that needs semantic judgment is "the amounts don't match, but are the line items effectively equal under different wording?" That's where the single-purpose LLM function `match_line_items(invoice_lines, po_lines) -> Verdict` gets called.

This function only judges "do these two line items semantically correspond?" and carries no other responsibility. The prompt is a simple instruction: "Compare the line items of the invoice and PO, and decide whether the content corresponds even if the wording differs. Output one of MATCH / PARTIAL / NO_MATCH." The LLM returns a verdict in schema. Pass an input, get a verdict (the output itself is probabilistic, so it occasionally fluctuates). But there's no element of the LLM deciding the next step. What happens next is already decided by the calling pipeline.

The contrast with the ReAct loop is sharp. The LLM isn't the agent of "think → pick a tool → observe the result → think again." It's a part within a pipeline that returns "input → verdict."

#### What This Structure Means

Business automation has known a structure for a long time. Any kind of work tends to have an 80% that can be written as deterministic rules and a 20% of exceptions that don't fit. This 20% has been the bottleneck of deployment, and people have tried to solve it for years with "more complex rules," "machine learning classifiers," "natural language processing add-ons," and so on, but none of those addressed the essence. The moment LLMs entered as single-purpose functions, the problem became solvable.

There's a point I want to emphasize here. **This exception judgment was originally a human role done manually.** Humans weren't applying exactly the same standard every time either. Looking at the same invoice, the verdict varied with that day's situation and the reviewer in charge. Even with a manual, the final call was left to humans' probabilistic interpretation. Exception judgment was, by nature, probabilistic work.

What an LLM function fulfills is exactly the same role. It just takes on probabilistic judgment with a probabilistic mechanism. Since perfect determinism isn't required in this territory, the LLM's probabilistic nature isn't a fundamental obstacle. Rather, in the sense of "taking on what humans were doing probabilistically, with human-equivalent quality, at lower cost," it looks like a tool well-fit for this place. The objection that "LLMs are probabilistic so they're unfit for business" overestimates what human business judgment was in the first place, I think.

On top of that, what matters is that **a "general-purpose agent" isn't needed**. One single-purpose function per category is enough. Fifty categories means fifty functions. There's no need for one thing that does everything.

### (4) Semantic Judgment × Exploratory — The Legitimate Territory of ReAct Agents

The ReAct loop (Thought → Action → Observation) explained at the start becomes necessary when the workflow can't be decided in advance and the agent itself has to judge the next action.

- Coding (where to fix, how to test — the agent decides)
- Exploratory browser automation (the operation target is dynamic)
- Deep Research (information branches that can't be predicted in advance)

The LLM has to choose its own next action, or it can't move forward. From both a research and a practical standpoint, ReAct is a technique designed for this quadrant. The evaluation targets in Yao et al.'s paper (HotpotQA / Fever / ALFWorld / WebShop) all sat within this quadrant.

## Category Error — The Ecosystem Brings (4) Into Every Quadrant

I should note upfront that production implementations frequently sit on the boundary between (3) and (4) in hybrid patterns. **Plan-and-Execute** (plan in (4) style, execute deterministically in (3) style), **Router agent** (use LLM judgment only for "which branch to send to" inside a (3) workflow), **tiered handoff** (handle in (3) first, escalate to (4) only when needed). These read as design guidelines for "build on a (3) foundation, but use (4) only where it's truly needed" — they sit on the same line as this article's argument.

The problem is somewhere else. The hype of the current agent ecosystem **tries to bring (4)'s architecture into every quadrant, all the time**. This is a category error — the kind of mistake where things of different nature get treated as the same kind.

Concretely, here's what I observe:

- Customer support implemented as an autonomous agent. But most of it is fine with (3) conversational form (specialized chatbot)
- Sales support implemented as a multi-tool agent. But most of it is fine with (3) batch form (single-purpose LLM function)
- Business automation "leveled up" with ReAct. But (3) deterministic pipeline + LLM function covers it
- Internal assistants sold as autonomous agents. But (3) chatbot covers it

To restate the point: **architectures premised on workflows that can't be defined in advance are being applied to work where the workflow can be defined in advance**.

This phenomenon is being recognized in the industry too. Thoughtworks criticizes the trend with the term "agentwashing." Gartner predicts that over 40% of agentic AI projects will be canceled by 2027. Anthropic itself, in "Building Effective Agents," writes *"This might mean not building agentic systems at all"* — suggesting that you shouldn't build agents when a simpler solution works. The four quadrants in this article are a recasting of this emerging industry consensus from a business perspective.

I notice the marketing side has something to do with how this category error gets mass-produced. LLM hype assumes "agents that think." The vocabulary of (3)'s plain chatbots and deterministic pipelines doesn't ride the press buzz. "Autonomous!" "Self-improving!" sells more easily. So marketing lumps all business work under (4)-quadrant vocabulary, and as a result, on the ground, (4) architectures get layered on top of (3) work — that's the structure I see.

What happens on the accountability side as a result:

- Unnecessary autonomy creates ambiguity in responsibility
- Unnecessary loops inflate cost
- Unnecessary black boxes destroy auditability and accountability

And on the technical-quality side, there's also a question of necessity. (3) work has its path decided in advance, so I can't find a technical reason to introduce the freedom of a ReAct loop. There's no necessity for layering "autonomously decide the next action" on top of a one-point semantic judgment.

## Accountability Becomes Clear

Once you take a (3) architecture, the accountability story gets cleaner all at once.

- Inputs / outputs / judgments are explicit per LLM call
- "What was done next" is fully traceable from pipeline logs
- Responsibility ambiguity caused by agent autonomy disappears
- LLM = product use within a limited scope; the deployer is the accountable party
- It rides on the product-liability model

This conflicts with no current legal system (I went into detail in a separate article: ["Can You Trace the Cause After an Incident?"](https://zenn.dev/shimo4228/articles/agent-causal-traceability-org-adoption)). Single-purpose function + pipeline and specialized chatbot have the **accountable party always clearly assigned to the human (deployer)**, so they need no special legal status for AI.

In Japan, killing someone's pet is legally treated as "damage to property" under Penal Code Article 261, with the Animal Welfare Act (Act No. 105 of 1973) as a stricter superseding statute — but neither grants animals independent rights-bearing status. Other jurisdictions vary in detail, but the underlying observation generalizes: legal systems do not grant animals legal personhood. There's no way to introduce an agent as a "subject that bears responsibility" into such a legal landscape. The (3) quadrant's architecture aligns with this legal reality from the start.

The (4) quadrant — that is, where ReAct agents are legitimate — is where the accountability problem stands up seriously. But that's a small area where autonomy is essentially required, not a story about business work in general. **Discussing business work in general using (4)'s vocabulary is itself the source of the error**, I find.

## Backed by Implementation: Cases Where I Used ReAct and Cases Where I Didn't

To support the argument, here's the implementation experience from both quadrants.

### A (4) Case Where I Used a ReAct Agent

I once built a Copilot for a setting where a piece of software's official knowledge base was so vast that humans had a hard time finding what they needed. The Copilot received user questions and assembled the best answer while exploring the knowledge space.

It worked startlingly well. The behavior looked exactly like a Deep Research-style exploratory agent — a mechanism that builds an answer through iterative search-tool calls. The implementation foundation was the ReAct pattern (Thought → Action [search-tool call] → Observation → Thought...) I learned from Coursera's prompt engineering course; I just placed the structure I encountered there into the context of knowledge exploration. The task "explore an unknown knowledge space and reach an answer" sits squarely in (4). What to search for next can't be decided in advance. The LLM had to look at the previous Observation and decide the next Action.

The flip side of "too powerful" was a feeling of uncontrollability. While the loop runs toward its goal, there's no way to predict in advance what path the LLM will take through tool calls. Nor how many turns it'll take. When branches expanded mid-flight, I felt that the energy until goal-completion got close to runaway with no controls. Things that work, work — but operational predictability is low. I think this is the fundamental nature of (4). Bring that nature, in full, into business, and you collide head-on with the cost and accountability problems.

So I know what ReAct agents can do. I know it, and I'm still saying that when you map it to business, (4) is limited.

### A (3) Case Where I Did Not Use a ReAct Agent

The [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) I publish openly sits on the opposite side. It uses no ReAct loop at all.

Contemplative Agent generates output based on a given constitution, skills, rules, and identity. Its essence is a general-purpose structure that takes on arbitrary norms / roles / skill definitions. Each step of the generation pipeline is laid out in a predetermined order, and each step works as a single-purpose LLM function that returns a verdict in a defined schema for a defined input. The LLM output itself fluctuates probabilistically, but which step to execute and what to do next isn't decided by the LLM — the pipeline decides. In quadrant terms, it sits in (3) — semantic judgment × definable — batch form.

There was no scene where I'd consider ReAct in CA. When operating CA, the only question is "by what standard, what kind of comment to issue." What to do next is decided in advance, so there's no room to run a ReAct loop. The distillation pipeline is the same — being processed via a different route every time would be a problem. The LLM judgments themselves fluctuate probabilistically, but the operational requirement is that "which step applies which judgment" stays fixed.

So it wasn't even a choice of (4) vs (3). Given the nature of the work, only (3) could be chosen. The four-quadrant framework in this article is closer to a later linguistic articulation of this implementation given. I didn't have the framework first and then implement; I implemented and then found the framework was already there.

### Separating the Domain of Application

Use ReAct agents where ReAct agents should be used ((4)), and don't where they shouldn't ((3)). The argument here isn't a rejection from ignorance of ReAct; it's a desire to narrow the domain of application from a position of knowing it. The hole the current agent ecosystem keeps falling into is "bringing (4)'s tool into every quadrant" — not "ReAct agents themselves are bad."

## Closing

I noticed that when you start from ReAct agents while introducing AI into business, the choice of quadrant becomes invisible.

Dissect the work first. For judgment work, a specialized chatbot ((3) conversational form) seems to suffice in many cases. For exception handling, single-purpose LLM functions + deterministic pipeline ((3) batch form) seems to cover it. For classical optimization, it's a problem for classical AI / OR ((2)) — not LLMs' stage. ReAct agents are needed only for exploratory tasks where the workflow can't be defined in advance ((4)).

I find that most of the business work the current agent ecosystem targets sits in (3), not (4). Lining up my (4) implementation experience next to my (3) implementation experience didn't shake that impression.

Where are ReAct agents actually needed in business? — Starting from this question, I came to feel the choice of architecture becomes visible. Conversely, skip the question and start from "do everything with agents," and you'll always end up at the category error of layering (4)'s architecture on top of (3) work.

## References and Related Links

### Primary technical sources

- Yao et al., ["ReAct: Synergizing Reasoning and Acting in Language Models"](https://arxiv.org/abs/2210.03629) (2022)
- Anthropic, ["Building Effective Agents"](https://www.anthropic.com/engineering/building-effective-agents) (2024)
- OpenAI, ["A Practical Guide to Building Agents"](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) (2025)
- Perplexity, ["Introducing Perplexity Deep Research"](https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research)
- OpenAI, ["Introducing deep research"](https://openai.com/index/introducing-deep-research/)

### Industry critique and predictions

- Thoughtworks, ["The dangers of AI 'agentwashing'"](https://www.thoughtworks.com/insights/blog/generative-ai/Agentwashing-and-how-AI-agents-fail-us) (2025)
- Gartner, ["Predicts Over 40% of Agentic AI Projects Will Be Canceled by End of 2027"](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027) (2025)

### Related articles (trilogy)

- [A Sign on a Climbable Wall](https://zenn.dev/shimo4228/articles/ai-agent-accountability-wall) — where agent responsibility lies
- [The AI Agent Black Box Has Two Layers](https://zenn.dev/shimo4228/articles/agent-blackbox-capitalism-timescale) — the structure of unexplainability
- [Can You Trace the Cause After an Incident?](https://zenn.dev/shimo4228/articles/agent-causal-traceability-org-adoption) — the difficulty of causal traceback

### Related repositories

- [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) — the implementation matching (3) in this article. Deterministic pipeline structure that uses no ReAct loop
- [Agent Attribution Practice (AAP)](https://github.com/shimo4228/agent-attribution-practice) — research repo on agent accountability and attribution
