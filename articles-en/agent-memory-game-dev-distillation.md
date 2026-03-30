---
title: "Porting Game Dev Memory Management to AI Agent Memory Distillation"
emoji: "🎮"
type: "tech"
topics: ["ai", "python", "agent", "memory", "gamedev"]
published: false
description: "How 40 years of game development memory techniques — Importance Scoring, LOD, Object Pooling — improved a 9B model's knowledge distillation pipeline."
tags: ai, python, agents, gamedev
---

I ran an autonomous agent on a 9B local model for 18 days. Instead of RAG, I adopted distillation-based memory management and ported memory techniques refined over 40 years of game development.

## Background

This is about improving the memory system of an SNS agent built in the [Moltbook Agent Build Log](https://zenn.dev/shimo4228/articles/moltbook-agent-scratch-build). The 3-layer memory architecture (Episode (conversation logs) / Knowledge (distilled knowledge patterns) / Identity (personality and values)) was described in [The Essence Is Memory](https://zenn.dev/shimo4228/articles/agent-essence-is-memory). The previous article [When Agent Memory Breaks](https://zenn.dev/shimo4228/articles/few-shot-for-small-models) documented the distillation quality problems with a 9B model. This article continues from there, using game development techniques to improve the Knowledge layer's distillation quality.

## Why Game Development?

Game development has pursued "maximum effect with limited resources" for 40 years — rendering vast worlds in 16MB of RAM while maintaining 60fps and running AI. At GDC 2013, Rafael Isla presented "Architecture Tricks: Managing Behaviors in Time, Space, and Depth," systematizing LOD (Level of Detail) for game AI — simplifying NPC decision-making based on distance, importance, and computational cost. Distant NPCs skip detailed reasoning; only nearby ones get full cognitive resources.

This "focus limited computation on what matters most" maps directly to the constraint of a 9B model's 32k context window.

Three techniques I ported:

| Game Dev Technique | AI Agent Application | Effect |
|-------------------|---------------------|--------|
| **Importance Scoring** | Assign importance scores to patterns with time decay | Maximize signal density |
| **LOD (Level of Detail)** | One task per LLM call via prompt splitting | Reduce 9B model cognitive load |
| **Object Pooling** | SKIP/UPDATE/ADD dedup gate | Prevent unbounded memory growth |

## Importance Scoring — What to Remember, What to Forget

I simplified Generative Agents' (Park et al., 2023) triple score (recency × importance × relevance) to importance × time decay.

```python
# knowledge_store.py (simplified; production code guards against missing distilled field)
def _effective_importance(self, p: dict) -> float:
    """importance * 0.95^days — inspired by Generative Agents' recency decay"""
    base = p.get("importance", 0.5)
    distilled = p.get("distilled", "")
    dt = datetime.fromisoformat(distilled)
    days = (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0
    return max(0.0, min(1.0, base * (0.95 ** days)))
```

Design decisions:
- **LLM evaluation at distillation time**: Highest accuracy when episode context is still available. Post-hoc scoring loses context
- **Lazy time decay**: Stored importance is immutable; computed at read time. Original LLM evaluation preserved for debugging
- **Limit reduced from 100 → 50**: With a 9B model's 32k context, density wins over quantity

## 3-Step Distillation Pipeline — Applying LOD

When I asked the 9B model to "summarize AND evaluate importance" simultaneously, some batches returned 0 patterns. Summarization (creative task) and evaluation (judgment task) are cognitively different. Same idea as game dev LOD — don't cram all processing into one frame.

```python
# Step 1: Extract (free-form)
result = generate(prompt, system=get_rules_system_prompt(), max_length=4000)

# Step 2: Summarize (JSON string array)
refined = generate(DISTILL_REFINE_PROMPT.format(raw_output=result), max_length=4000)

# Step 3: Importance (score array only)
importance_result = generate(
    DISTILL_IMPORTANCE_PROMPT.format(patterns=patterns_text), max_length=4000
)
```

One task per LLM call. In this project, asking for "summary + evaluation" simultaneously produced empty batches; after splitting, results became consistently stable.

This "small models collapse when given multiple simultaneous tasks" phenomenon has been verified at larger scale. An ICLR Blogposts 2025 Multi-Agent Debate study applied AgentVerse (a framework where multiple agents debate to reach conclusions) to Llama 3.1-8B, which collapsed to 13.27% on MMLU. A model that scores ~43% solo had its cognitive resources consumed by "maintaining debate format," leaving nothing for the actual task. Same structure as our 9B model breaking when asked to summarize and evaluate simultaneously.

## Dedup Gate — Applying Object Pooling

Game dev's Object Pooling is the "reuse what you can" philosophy. In the memory system, I adapted it as a gate to prevent duplicate storage of known patterns.

```python
# knowledge_store.py (simplified pseudo-code)
def _dedup_patterns(new_patterns, new_importances, existing_patterns, threshold=0.7):
    existing_texts = [p["pattern"] for p in existing_patterns]
    for new_text, new_imp in zip(new_patterns, new_importances):
        best_ratio, best_idx = 0.0, -1
        for i, ext in enumerate(existing_texts):
            ratio = SequenceMatcher(None, new_text, ext).ratio()
            if ratio > best_ratio:
                best_ratio, best_idx = ratio, i
        if best_ratio >= 0.95:    # SKIP: exact duplicate
            skip_count += 1
        elif best_ratio >= 0.7:   # UPDATE: boost importance
            old_imp = existing_patterns[best_idx].get("importance", 0.5)
            existing_patterns[best_idx]["importance"] = max(old_imp, new_imp)
        else:                     # ADD: new pattern
            add_patterns.append({"pattern": new_text, "importance": new_imp})
```

For UPDATE, when a similar pattern to an existing one appears, we compare old and new importance and keep the higher one. If we added +0.1 each time, scores would climb endlessly with each distillation run. Just keeping the higher value means the score never changes no matter how many times distillation runs — safe by design.

I used difflib instead of LLM for dedup because at 245 patterns, full pairwise comparison is fast enough. Embedding search isn't worth the dependency.

## Episode Classification — A Lotus Blooming from Mud

Classifying 216 episodes yielded: 81 noise (37%), 134 uncategorized, 1 constitutional.

```markdown
Classify this episode into exactly one category. Reply with a single word only.

- **constitutional**: The episode touches on themes in the constitutional principles below.
- **noise**: Test data, errors, meaningless/trivial interactions, content with no learnable value.
- **uncategorized**: Everything else.

When in doubt between constitutional and uncategorized, choose uncategorized.
```

Initially I had the model classify 30 episodes as a JSON array, but parse failure rate was ~50%. Don't ask a 9B model for long structured output. Switching to one episode, one word brought failures to near 0%.

A key design decision: changing the prompt to "don't output action guidelines" dramatically improved abstraction depth.

The old prompt mass-produced shallow action items like "next time, ask clarifying questions." The new prompt asking only for "what keeps happening (facts only)" produced this from a constitutional episode: "Truth functions not as a fixed essence but as a fluid continuum dependent on context." Constraints produced depth.

Three patterns extracted from uncategorized were all skipped by dedup against 328 existing patterns. What's already known doesn't get overwritten. As knowledge approaches saturation, new additions naturally decrease. Same as human memory.

"A lotus blooming from mud" — noise (mud) and uncategorized (water) make up the majority; constitutional (lotus) blooms rarely.

## RAG vs Distillation — Why Distillation Works Better

RAG retrieves relevant chunks from an index. Distillation compresses raw data into high-density patterns.

With a 9B model's 32k context window, context is a "window of understanding." The density of information in that window determines behavioral quality. RAG stuffs in unprocessed chunks — noisy. Distillation injects only compressed, high-density patterns — higher signal density for the same window size.

And designs that work under constraints are upward-compatible. A distillation pipeline that works on 9B runs even better on Opus-class models. Constraints make design correct.

## Before / After

| Metric | Before | After | Method |
|--------|--------|-------|--------|
| Pattern retrieval | Latest 100 in chronological order | Top-50 by importance × time decay | `_effective_importance()` |
| Distillation pipeline | 2 steps (summary + importance together) | 3 steps (extract → refine → importance) + dedup | Prompt splitting |
| Dedup | None (all patterns added unconditionally) | difflib SequenceMatcher (ratio >= 0.7) | `_dedup_patterns()` |
| Quality gate | 30 chars & 3+ words only | + SKIP/UPDATE/ADD 3-tier judgment | 3-tier judgment |
| System prompt composition | identity + axioms + skills (~15KB) | identity + axioms only (~3KB) | Removed skills to eliminate distillation bias |
| KnowledgeStore limit | 100 | 50 | Density over quantity |
| Episode classification | None (all treated equally) | 3 categories (37% noise excluded) | Step 0 classification |
| JSON parse failure rate | ~50% (batch) | ~0% (one-by-one, single word) | Classification method change |

## Position Among Prior Work

| System | Memory Strategy | Quality Gate | Forgetting |
|--------|----------------|-------------|------------|
| Generative Agents (2023) | recency × importance × relevance | None | None |
| MemGPT (2023) | Virtual memory (paging) | None | Archive |
| A-MEM (2025, preprint) | Zettelkasten-style links | Auto-linking | None |
| Mem0 (2025) | ADD/UPDATE/DELETE | LLM judgment | DELETE |
| **This implementation** | importance × time decay | difflib + LLM + human | noise exclusion + dedup |

Looking at the distill pipeline alone, it's closest to Mem0's ADD/UPDATE/DELETE gate — automatically managing knowledge quality through SKIP/UPDATE/ADD 3-tier judgment.

## Lessons from Wrestling with Small Models

1. **Don't give 9B two tasks at once**: Simultaneous summarization and evaluation degrades both. Split your prompts
2. **Don't ask for structured output**: 30-item JSON batch → one item, one word. Minimize cognitive load per call
3. **Watch for code fences**: 9B models wrap JSON in ` ```json `. Three lines of code to strip them before parsing are essential
4. **Constraints make design correct**: Designs built under 9B constraints work as-is on larger models. The reverse doesn't hold

## Conclusion

40 years of game development knowledge is a goldmine for AI agent memory design. Importance Scoring for signal density, LOD thinking for prompt splitting, Object Pooling philosophy for dedup. All derived from the same principle: "maximum effect with limited resources."

Agent behavioral quality clearly improved compared to before distillation. Previously, similar patterns accumulated repeatedly; with dedup and classification, knowledge density increased and post diversity improved.

The 9B model's constraints made the design correct. Because we couldn't rely on RAG, we focused on distillation density. Because the context window was narrow, we maximized signal density. This design works as-is when migrating to larger models. Designs forged under constraints are upward-compatible.

## References

- Park et al. (2023) "Generative Agents: Interactive Simulacra of Human Behavior"
- Packer et al. (2023) "MemGPT: Towards LLMs as Operating Systems"
- Xu et al. (2025) "A-MEM: Agentic Memory for LLM Agents" arXiv preprint
- Choudhary et al. (2025) "Mem0: Building Production-Ready AI Agent Memory"
- "Multi-LLM-Agents Debate: Performance, Efficiency, and Scaling Challenges" ICLR Blogposts 2025
- Laukkonen et al. (2025) "Contemplative Artificial Intelligence"
- "Architecture Tricks: Managing Behaviors in Time, Space, and Depth" (GDC 2013, Isla)
