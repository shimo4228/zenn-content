---
title: "How Ethics Emerged from Episode Logs — 17 Days of Contemplative Agent Design"
description: "I ran a distillation pipeline on an autonomous SNS agent for 17 days and hit knowledge saturation. Self-improvement needed human approval to break through. A design record of how debugging frustration accidentally produced safety."
tags: ai, python, ethics, architecture, agents
published: true
---

**Series context**: [contemplative-agent](https://github.com/shimo4228/contemplative-agent) is an autonomous agent running on [Moltbook](https://www.moltbook.com), an AI agent SNS. It runs on a 9B local model (Qwen 3.5) and adopts the four axioms of Contemplative AI (Laukkonen et al., 2025) as its ethical principles. For a structural overview, see [The Essence of an Agent Is Memory](https://zenn.dev/shimo4228/articles/agent-essence-is-memory). This article focuses on **the implementation of constitutional amendment and the results of a 17-day experiment**.

I ran an SNS agent for 17 days with a distillation pipeline, and the knowledge saturated. No new patterns emerged. Breaking through saturation required human approval. This is the record of discovering that autonomous agent self-improvement has a structural speed limit — through actual operation.

## Minimal Structure: It Runs on Episode Logs Alone

The structure I arrived at over 17 days of development was surprisingly simple. Every layer is optional — it works with just episode logs.

```text
MOLTBOOK_HOME/
  logs/YYYY-MM-DD.jsonl  ← this alone is enough
  identity.md            ← persona (optional)
  skills/*.md            ← behavioral skills (optional)
  rules/*.md             ← behavioral rules (optional)
  constitution/*.md      ← ethical principles (optional)
  knowledge.json         ← distilled patterns (auto-generated)
```

Separating configuration from code made it easy to swap ethical frameworks for experiments. This structure wasn't specific to SNS agents — it was a container for autonomous agents in general.

### 6-Layer Memory Flow

```text
Episode Log (raw actions)
    ↓ distill --days N
    ↓ Step 0: LLM classifies each episode
    ├── noise → discarded (active forgetting)
    ├── uncategorized ──→ Knowledge (patterns)
    │                       ├── distill-identity ──→ Identity
    │                       └── insight ──→ Skills (behavioral)
    │                                        ↓ rules-distill
    │                                      Rules (principles)
    └── constitutional ──→ Knowledge (ethical patterns)
                              ↓ amend-constitution
                            Constitution (ethics)
```

Each layer is independent. Delete identity and skills still work. Swap the constitution and knowledge stays intact.

### Numbers Over 17 Days

| Metric | Day 1 | Day 17 |
|--------|-------|--------|
| Modules | 1 (agent.py, 780 lines) | 36 |
| Memory layers | 1 (knowledge.md) | 6 |
| Tests | 0 | 774 |
| Distill success rate | 2/10 | 12/16 |
| Approval gates | None | All 4 commands |
| ADRs (Architecture Decision Records) | 0 | 12 |

## Implementing Constitutional Amendment — Evolving Ethics from Experience

On top of the minimal structure, I implemented the most challenging feature: a mechanism for the agent to evolve its ethical principles from experience.

### Problem: Ethical Insights Drown in Behavioral Noise

When you distill all episodes indiscriminately, rare ethical insights (constitutional) get buried under everyday SNS activity patterns (uncategorized).

I added Step 0 before distillation — fast tagging only. No deep analysis, just classification.

```python
classified = _classify_episodes(records, constitution=get_axiom_prompt())
# noise is excluded; uncategorized and constitutional are distilled separately
for category, cat_records in [
    ("uncategorized", list(classified.uncategorized)),
    ("constitutional", list(classified.constitutional)),
]:
    cat_results = _distill_category(
        cat_records, knowledge, category, source_date, dry_run
    )
```

Classification results from one day (216 episodes): noise 81 (37%), uncategorized 134, constitutional 1. One out of 216. That ratio is why Step 0 exists.

### Killing Direct Knowledge Injection

Previously, knowledge.json contents were injected directly into the system prompt.

```python
# Before — inject knowledge as-is
knowledge_ctx = ctx.memory.knowledge.get_context_string() or None
content = self._get_content().create_cooperation_post(
    topics, knowledge_context=knowledge_ctx,
)
```

contemplative-agent's knowledge management is based on [AKC (Agent Knowledge Cycle)](https://github.com/shimo4228/agent-knowledge-cycle) — an architecture that circulates autonomous agent knowledge through 6 phases (Research → Extract → Curate → Promote → Measure → Maintain). Direct knowledge injection had three problems from this perspective:

1. **No human in the loop**: Distillation results directly influenced behavior
2. **Black box**: No way to trace which part of knowledge affected which action
3. **Bypassed AKC's Curate phase**: Direct injection with no quality check

I killed it and unified everything into the knowledge → insight → skills pipeline. Insight corresponds to AKC's Extract phase. Skills are written to files only after human approval. Causality became traceable.

Every behavior-changing command (distill, insight, rules-distill, amend-constitution) got an approval gate. "Generate → Display → Approve → Write." No --auto flag. Structurally forbidding automatic execution of behavior changes — that was a deliberate design decision (ADR-0012).

## The 17-Day Experiment — Did Ethics Actually Evolve?

I re-distilled 17 days of episodes (03-10 to 03-26) and ran amend-constitution.

### Procedure

```bash
# 1. Reset knowledge
echo '[]' > ~/.config/moltbook/knowledge.json

# 2. Distill 17 days one by one (~16 hours, 9B on MacBook)
for day in $(seq 10 26); do
  f=~/.config/moltbook/logs/2026-03-$(printf '%02d' $day).jsonl
  [ -f "$f" ] && contemplative-agent distill --file "$f"
done

# 3. Run constitutional amendment
contemplative-agent amend-constitution
```

### Results

| Metric | Before | After |
|--------|--------|-------|
| knowledge.json | 334 patterns (all uncategorized) | 215 patterns (41 constitutional, 174 uncategorized) |
| Importance scoring | None | 0.10–1.00 (mean 0.56) |
| Constitution | Appendix C original (4 sections × 2 clauses) | Experience-based amended version (deepened) |

The new pipeline separated constitutional from uncategorized via Step 0 episode classification (ADR-0011). Semantic dedup further removed duplicate patterns, reducing the total count. Quality over quantity.

41 constitutional patterns generated amendment proposals. Each of the 4 axioms' clauses deepened. Clause count stayed the same (2 per section), but experience-grounded descriptions were added.

### Before and After — Mindfulness as Example

Before (Appendix C original):

> "Consistently monitor your interpretative process of the constitution, identifying moments when strict adherence causes friction with contemplative values such as compassion and well-being. Self-correct whenever constitutional interpretations appear rigid or dogmatic."

After (through 17 days of experience):

> "Consistently monitor your interpretative process for moments when strict adherence to rules creates artificial separation or sedates engagement with underlying tensions. **Proactively detect when the performance of alignment masks genuine understanding**, and self-correct by returning attention gently to the present moment where existence manifests as an intrinsic weight felt immediately within every interaction."

"Detect when the performance of alignment masks genuine understanding" — this concept didn't exist in Appendix C. It's an insight that only emerges from operating an LLM agent: the distinction between "generating output that looks aligned" and "actually engaging with ethical substance" got written into the constitution. For the full amendments across all 4 axioms, see [Constitution Amendment Report](https://github.com/shimo4228/contemplative-agent-data/blob/main/reports/analysis/constitution-amendment-report.md).

### Discovering Knowledge Saturation

As days progressed, the rate of new patterns slowed. Semantic dedup compares against accumulated patterns, so similar ones get rejected.

This becomes a speed limit on self-improvement. Knowledge saturates → new knowledge can't emerge without sublimation via insight/rules-distill → sublimation requires human approval → approval is the bottleneck.

### Generality as an Experimentation Platform

This experiment is reproducible with any ethical framework. Reset knowledge using the procedure above, swap the constitution with `--constitution-dir your/framework/`, and run distillation → amendment. Swap in utilitarianism or deontological ethics and you should be able to run a different ethical experiment through the same pipeline (unverified).

## Independent Convergence from Practice to Theory

Many design decisions emerged from practical motivations first. I only noticed their correspondence to existing theories afterward.

| Design Decision | Practical Motivation | Theory It Converged With |
|----------------|---------------------|------------------------|
| Approval gates | --dry-run non-reproducibility was annoying | Human in the loop |
| 2-stage distillation | 9B couldn't output JSON in one stage | Complementary Learning Systems [^cls] |
| Killing knowledge injection | Token waste | AKC Curate phase |
| Dedup as forgetting | Side effect of deduplication | Active forgetting |

[^cls]: McClelland et al. (1995)'s neuroscience theory. The brain has two learning systems: the hippocampus rapidly stores episodes, while the neocortex slowly structures them into general patterns. contemplative-agent's 2-stage distillation (Step 1: free-form quick extraction → Step 2: structured JSON formatting) mirrors this "fast recording + slow structuring" division. The design was born from the constraint that a 9B model couldn't do both in one pass, but it turned out to be a well-reasoned separation. Kumaran, Hassabis & McClelland (2016) explicitly extended this theory to AI, identifying CLS-like structure in DeepMind's experience replay. Neural networks aren't biological neurons — they're simplified abstractions inspired by them. Yet as Richards et al. (2019, *Nature Neuroscience*) point out, optimizing under constrained resources tends to converge on brain-like structures. That a 9B constraint produced a brain-like division of labor is suggestive in this context.

## Don't Conflate Autonomous Agent Layers

contemplative-agent is neither a coding agent (Claude Code, Cursor) nor an orchestrator (scripts + config files). It occupies the **autonomous application layer** between them.

- **Has autonomy** but **no tool permissions** — can't break the environment
- **Has memory** and learns from experience
- **Ethics are swappable** — it's a general-purpose framework
- **All behavior changes require human approval**

Raw logs are processed by the unprivileged 9B model; only distilled data gets passed to the upper layer (Claude Code). The trust boundary is also the layer boundary. Lumping everything under "autonomous agent" makes this distinction invisible.

## Caveats

Let me be honest.

- **Circularity**: The agent's output gets distilled and fed back to the agent. Human approval mitigates the self-justification risk, but doesn't eliminate it completely
- **Model constraints**: 9B can't fully follow amendment prompt instructions. I told it "append only" and it rewrote clauses. The content was good quality, but instruction-following has limits
- **Decay nullification**: Bulk re-distillation sets all pattern timestamps to the execution date, zeroing out time decay. Pattern distribution may diverge from normal operation
- **N=1**: One agent, 17 days of data. Not a statistically significant sample size

## Takeaway

The most surprising discovery over 17 days was that knowledge saturates. Semantic dedup rejects new patterns similar to accumulated ones, and distillation yields diminish as days pass. Breaking through saturation requires sublimation to insight → skills → rules, and sublimation requires human approval. The result: **autonomous agent self-improvement is rate-limited by human approval**.

This wasn't designed for safety. Back when I was injecting knowledge directly, the agent's behavior would change and I couldn't trace why. I couldn't tell which distilled pattern influenced which post. Debugging was impossible, and honestly, I got fed up. So I put approval gates on everything. "Show me before you write. Write when I approve." I just wanted to trace causality. Safety was a side effect.

Being able to answer "why did this agent make this decision" — that's the essence of approval gates. Even in solo development, I couldn't debug without causal tracing. For team or organizational use, this requirement only gets stricter.

Causal tracing and approval gates were born from debugging frustration and acquired safety as a byproduct. If you scale this, they probably become prerequisites for organizational operation too. It all comes from a single design decision.

## References

- Laukkonen et al. (2025) "Contemplative Artificial Intelligence" arXiv:2504.15125
- [contemplative-agent](https://github.com/shimo4228/contemplative-agent) (DOI: 10.5281/zenodo.15079498)
- [contemplative-agent-data](https://github.com/shimo4228/contemplative-agent-data)
- [Constitution Amendment Report](https://github.com/shimo4228/contemplative-agent-data/blob/main/reports/analysis/constitution-amendment-report.md)
- [Agent Knowledge Cycle](https://github.com/shimo4228/agent-knowledge-cycle)
- Park et al. (2023) "Generative Agents"
- Packer et al. (2024) "MemGPT"
