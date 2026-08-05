---
title: "Claude Code's Memory Has No Vectors — Try ADRs Before Memory RAG"
emoji: "🗂️"
type: "idea"
topics: ["rag", "claudecode", "aiagents", "contextengineering", "adr"]
published: true
description: "Claude Code's memory is plain Markdown plus an index — no embeddings, no vector DB. A two-axis decision rule for when RAG wins and when structured memory + ADRs win, backed by an embedding clustering failure and prefix-cache A/B measurements from my own agent."
tags: discuss, rag, claudecode, contextengineering
---

There is not a single vector in Claude Code's memory implementation.

Counting my project's auto-memory directory: 89 plain Markdown files plus one `MEMORY.md` that indexes them. No embeddings, no vector DB, no chunking — nothing (measured on 2026-08-05).

```bash
$ ls ~/.claude/projects/<project>/memory/*.md | wc -l
89
$ find ~/.claude/projects/<project>/memory -type f ! -name "*.md"
# → One manual backup only. Zero vector assets
```

Code search is the same. Current Claude Code (as of 2026-08) searches code with Grep / Glob / Read, and there is no built-in mechanism that builds an embedding index. This isn't someone's claim — it's a fact you can verify today by opening your own Claude Code.

What's interesting is that this is not "not implemented yet" — it's the result of **trying it and removing it**. Early versions used RAG + a local vector DB, and the author, Boris Cherny, has explained why it was dropped. He first said this [on Hacker News in February 2025](https://news.ycombinator.com/item?id=43164253) and restated it in [an X post in February 2026](https://x.com/bcherny/status/2017824286489383315). Here is the X version:

> Early versions of Claude Code used RAG + a local vector db, but we found pretty quickly that agentic search generally works better. It is also simpler and doesn't have the same issues around security, privacy, staleness, and reliability.

If you're giving an agent memory, the default answer is memory RAG or graph RAG. My position is the opposite. **If you're building memory RAG or graph RAG, first try plain ADRs (Architecture Decision Records) and structured memory. I believe it will solve most of your problem.**

Let me say upfront: this is not an anti-RAG argument. My own agent (a self-built agent I run separately from Claude Code — details below) runs on the full benefit of embeddings. This article is about scope: **under which conditions RAG wins, and under which conditions letting the model read wins**.

This article does two things:

1. Decompose RAG into a single question — "who makes the relevance judgment, and when" — and derive **a decision rule for when RAG wins and when it loses**
2. Back that rule with observations of Claude Code's implementation, plus failures and measurements from my own environment (embedding clustering over-merging, a prefix-cache A/B test)

## Decomposing RAG — who makes the relevance judgment

The core of RAG is not "search." It is **who decides, and when, what is relevant to this context**.

Embedding-based RAG places that judgment like this:

- **At write time**: documents are converted to embedding vectors and stored. From then on, the only information available for retrieval is this frozen representation
- **At read time**: the query is vectorized with the same embedding model, and "relevance" is judged by vector similarity (cosine similarity being the standard choice)

The similarity computation itself runs at read time. But the judge is the embedding model — a model that doesn't read the conversation's context, doesn't grasp the question's intent, and was frozen at training time. In other words, RAG is **a design that delegates the relevance judgment occurring at every read to a weak, frozen judge that doesn't read context**. Under conditions where LLMs are weak or expensive, this is still a rational division of labor.

Note that what I decomposed here is bare embedding search (single-stage dense retrieval). Stacks with query rewriting, hybrid search, and metadata filters move part of the judgment outside the embedding — but that is an evolution in the direction of piling corrective devices around a weak judge. This weakness is well known in practice, which is exactly why rerankers — feeding the search results to an LLM for re-judgment — became a standard later stage. A reranker is a design that concedes: "for the final judgment, letting the model read is more reliable." For frontier-class LLMs, context processing is the core job, and there is no dimension on which vector similarity beats their ability to read the full text and judge "which of these matters for the current question." Compared to bare embedding search, letting the model read as much as it can read wins on judgment quality.

If that's true, the design question changes. Not **"how do we search"** but **"can the model read it"**.

## The decision rule — when RAG is needed, when it isn't

Here is the decision map up front. Two axes.

| | **Frontier-class LLM** | **Weak LLM (small local model, etc.)** |
|---|---|---|
| **Readable scale** (memory, hundreds of docs) | **Structured memory + ADRs**. No vector search — let the model traverse from an index and read | Embeddings are effective (you can't afford the cost of reading) |
| **Unreadable scale** (large corpus) | Agentic search (grep + read) or RAG | RAG |

- **The right column and the bottom row are RAG's legitimate territory**: searching large corpora, fuzzy recall that keywords can't catch, and cases where the LLM itself is weak. Building these with RAG is correct.
- The problem is the **top-left**. If you're building an embedding pipeline for an agent's self-memory — a store that you (or the agent) write to and that the LLM can read in full — you are delegating a high-value judgment to a weak judge. This article's claim applies to that quadrant only.

One clarification: the top-left claim is not "eliminate search." It is a reassignment — **move the relevance judgment back from the embedding to the LLM, and demote retrieval to plain file reading**. A new design problem remains: how to maintain the index (more below).

The rest of the article backs this top-left quadrant with three pieces of evidence.

## Evidence 1: Claude Code's implementation — search is demoted to a tool

Claude Code's memory runs on plain Markdown plus an index alone. Pulling the structure from the [official docs](https://code.claude.com/docs/en/memory) (as of 2026-08), it comes down to three points:

1. **Only the index is resident**: only the first 200 lines (or 25KB) of `MEMORY.md` are loaded each session
2. **Write-time compression is enforced**: as the index approaches its limit the harness warns, and exceeding it returns an error demanding a rewrite. The compression protocol — "keep one entry per line, push details out to topic files, consolidate and delete stale entries" (the gist of the official docs) — is enforced by the tool, not by the model's good intentions
3. **Bodies are read on demand**: topic files are not loaded at startup; when needed, Claude reads them with the ordinary file tool (Read)

The third point is the crux. **Retrieval is not an independent pipeline — it has been demoted to an ordinary tool call.** The judgment of "what to read" is made at runtime by the LLM looking at the index, not by an embedding.

Anthropic itself does not frame this structure as an ad-hoc omission. The September 2025 post [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) explicitly states the "just in time" approach as a design principle: instead of pre-processing all data, keep lightweight identifiers (file paths, etc.) and load with tools at runtime. "Structured note-taking (agentic memory)" — the agent writing Markdown notes — is also recommended in the same post, and Claude Code's implementation today remains consistent with this published direction.

:::message
The same post (2025-09) also states the trade-off: "runtime exploration is slower than retrieving pre-computed data." The speed counterargument is addressed in Evidence 3 below.
:::

## Evidence 2: embeddings can't see "the concrete difference" — my failure

I have been running an autonomous agent unattended for months on a small local model on an M1 Mac, and within that I have concretely failed with embedding clustering. The record is public, in [ADR-0046](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0046-stocktake-llm-grouping-over-embedding-clustering.md).

I built duplicate detection for the agent's auto-extracted skills using embedding cosine similarity + clustering:

- The skills share boilerplate vocabulary, so **skills that are behaviorally distinct scored 0.90+ cosine similarity**
- Linkage clustering chained those pairs, **over-merging 18 skills into a single blob**
- Switching back to passing all skill bodies to a single LLM call for classification recovered a sensible result: **18 → 5 groups + 8 independent**

This was not a "bad threshold tuning" failure. The ADR records the alternatives considered — raising the cosine threshold from 0.80 to 0.90 didn't separate them, and neither did changing the linkage method, because boilerplate vocabulary dominates this store. The concrete difference — same vocabulary, different instructed behavior — simply does not show up as distance in embedding space. An LLM reading the full text sees it. At readable scale, letting the model read wins — a real instance of the top-left quadrant.

## Evidence 3: "select and inject" breaks the cache — a prefix-cache A/B

"Reading everything is slow and expensive, so retrieve only the relevant part and inject it" — that's RAG's speed argument. But when you measure it, a hidden cost appears: **injection whose content changes every call breaks the prefix cache every call**. The prefix cache is the mechanism that, when the head of the prompt matches the previous call, reuses that evaluation and skips input processing (it exists both in local llama.cpp and in frontier APIs).

I ran a controlled A/B locally (Ollama / gemma4:e4b, num_ctx=32768, M1 16GB) on 2026-08-05 ([raw data public](https://github.com/shimo4228/contemplative-agent/blob/main/docs/evidence/adr-0081/skillsel-cache-ab-20260805.jsonl)). We compare prefill time (prefill: the evaluation of the input prompt portion).

| Condition | Prefill time |
|---|---|
| ~32K-char system prompt, first call (cold) | 38.85s |
| Repeat call with **byte-identical** system (5/5 reproduced) | **0.061–0.064s** |
| Repeat call with part of system (skill-injection section) swapped | Full cold every time (6.3–7.1 ms/tok) |

Note: only the third row is token-normalized (ms/tok) because rotating the skill-injection section made the system size vary between 29K and 57K chars. The "full cold every time" verdict rests on all cold calls consistently landing at 6.3–7.1 ms/tok.

Byte-identical is roughly 600x faster. Swap any part, and even with a shared head, the cache barely helped.

Production telemetry (30 days, n=1,213) shows the same structure. The configuration that selects and injects skills per call (n=604) has a p50 of 56.1 seconds; the configuration that injects everything without selection (n=609) has a p50 of 28.3 seconds. **The side that "injects only what's needed" is 2x slower in wall-clock time.** The production aggregate is not a controlled experiment, so I won't overclaim — but it is consistently explained by the same mechanism as the A/B above: selection changes the system prompt every call, so every call pays a cold prefill.

:::details Measurement caveat — token-count-based monitoring cannot see the cache effect
On the Ollama path, `prompt_eval_count` reports the full prompt token count (6,202 in this experiment) even on cache hits. Actually evaluating 6,202 tokens in 0.061 seconds is physically impossible, so hit detection is only possible via `prompt_eval_duration`. If you only watch token counts, "inject everything" will keep looking expensive.
:::

This is a local llama.cpp measurement, and partly specific to a prompt layout whose shared head is only ~2K chars. But frontier API prompt caching is also conditioned on prefix matching from the start of the prompt, so the principle is the same — **everything after a variable injection point gets recomputed every call**. If you put the stable part first and inject retrieval results at the tail, you protect the cache for the head; but a design that splices retrieval results into the middle of the system prompt, or has a long shared section after the injection point, pays the same cost measured here. The lesson: "what to inject, and where" is not just a retrieval-precision question — it is a cache-design question.

## Objection: "you just moved the cost to write-time discipline"

I think the strongest objection to all of the above is this:

> RAG's advantage is zero write cost. Throw everything in, search later. ADRs and structured memory demand write-time discipline — compression, indexing, curation. Haven't you just traded search complexity for a documentation discipline that most teams cannot sustain?

My response has two parts.

**First, that discipline can be carried by the agent, not by humans.** As Evidence 1 showed, Claude Code's auto-memory has the agent itself doing the work of choosing what to keep, compressing it, and updating the index. My 89 files weren't written by me being meticulous — the agent accumulated them from session learnings. The folk wisdom that "documentation discipline never lasts" is about human teams; with an LLM on the write side, the premise has changed.

**Second, reads and writes are asymmetric.** A write happens once per piece of information; the read-time relevance judgment happens every session, every time. RAG delegates that every-time judgment to a weak judge, placing the cost and the quality degradation on the high-frequency side. Having a strong judge (an LLM) compress and organize once at write time is not a cost shuffle — it is **a correct move to the low-frequency side**.

## My own agent runs on the full benefit of RAG

In the decision table I wrote "with a weak LLM, embeddings are effective." The very agent whose failure I showed in Evidence 2 is exactly that case — far from not needing RAG, it runs supported by embeddings.

This agent runs on a small local model (8B class) as a [deliberately chosen constraint](https://dev.to/shimo4228/building-an-autonomous-agent-on-an-m1-mac-by-choice-5b5o). Measured cold prefill is 6.3–7.1 ms/tok (same agent and same model as the A/B in Evidence 3). It cannot afford to "read and judge every time" over a knowledge store of hundreds of patterns.

So pattern classification, duplicate detection, and noise filtering are built on embeddings ([ADR-0019](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0019-discrete-categories-to-embedding-views.md)). Strictly speaking this is not retrieval-augmented generation itself but "embeddings as a judge" — yet it is the same core design this article decomposed: delegating relevance judgment to a frozen judge. The effect shows up in numbers — replacing LLM-call-based classification with embeddings cut LLM time by about 20 minutes per day (ADR-0019, recorded as of 2026-04; that is an embeddings-vs-LLM-calls comparison, not a comparison against a "let the model read" configuration). In this environment, this division of labor clearly wins.

There is no contradiction with the failure in Evidence 2. That case was a one-off judgment over 18 skill bodies — readable scale — so moving back to the LLM was correct. This case is also readable in scale, but the classification fires daily at high frequency, and an 8B model cannot pay the "read every time" cost, so embeddings are correct — the same agent, with the decision rule applied per mechanism.

In other words, my environment sits in the right column of the table (weak LLM), where the RAG-side design is the right answer. Conversely, an agent with Opus or a GPT-class frontier model as its backend has its self-memory in the top-left quadrant (frontier-class LLM x readable scale) — and building an embedding pipeline there means outsourcing judgment to a weak judge while a strong judge is standing right there. **The same design is correct in one quadrant and wrong in another** — that is this article's decision rule.

## Why "ADR" specifically

Among structured memory formats, there is a reason I recommend ADRs (Architecture Decision Records) in particular. The thing that rots fastest in an agent's memory is "why we decided this," and the ADR is the format that pins it down as a unit of **decision + context + rejected alternatives**.

- **Write-time compression is built into the format**: the act of writing an ADR is itself the compression of "what was decided, and on what grounds"
- **Expiry is handled**: ADRs carry status (accepted / superseded), and new decisions explicitly override old ones. The problem of contradictory memories cohabiting in a vector store doesn't arise — the format prevents it
- **The graph can be drawn by hand**: reference links between ADRs ("ADR-0046 refines ADR-0016") are drawn by the author at write time. The relationships that graph RAG tries to infer at runtime get fixed at the moment they are best known

My public repo has 89 English ADRs (a different store from the 89 auto-memory files at the top — the equal count is coincidence), and Claude Code traverses them with grep and Read at the start of a session. Vector search never enters the picture.

## Summary

- The core of RAG is delegating relevance judgment to a weak, frozen judge that doesn't read context. Where LLMs are weak or expensive it remains a rational division of labor — but in the quadrant where a frontier-class LLM handles a readable scale, it is degraded context processing
- The decision rule is two axes: **readable scale x LLM strength**. For large corpora, fuzzy recall, and weak LLMs, RAG remains legitimate
- If you are in the agent self-memory x frontier-class LLM quadrant, before building an embedding pipeline, try **an index + plain Markdown + ADRs**. Claude Code runs that design in production today, and the write discipline can be carried by the agent
- "Select and inject" has a measurable hidden cost: it breaks the prefix cache after the injection point on every call

All numbers, failures, and ADRs from my environment are in a public repo. Verification and refutation are welcome.

## Related links

- Contemplative Agent — public repo with this article's ADRs and measurement data: https://github.com/shimo4228/contemplative-agent
- Series hub "Building an Autonomous Agent on an M1 Mac, by Choice": https://dev.to/shimo4228/building-an-autonomous-agent-on-an-m1-mac-by-choice-5b5o
- Claude Code official docs (memory): https://code.claude.com/docs/en/memory
- Anthropic "Effective Context Engineering for AI Agents": https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic Prompt caching (prefix-matching spec): https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Author's GitHub: https://github.com/shimo4228
