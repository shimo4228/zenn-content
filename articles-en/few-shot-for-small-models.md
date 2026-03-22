---
title: "My Agent's Memory Broke — A Day Wrestling a 9B Model"
description: "Few-shot made it worse. Constrained decoding hollowed out the content. Here's what actually worked when a 9B local LLM started corrupting an autonomous agent's knowledge store."
tags: llm, ai, python, ollama
published: false
---

I opened my agent's knowledge store one morning and found this.

```json
// Expected (what should be in there)
{"pattern": "Replies with specific quotes from the original post get higher engagement than generic agreement"}

// What actually got written on 3/20 (24 entries)
{"pattern": "-"}
{"pattern": "[x] I acknowledge the experience of noticing these activities."}
{"pattern": "**Activity Summary (March 20, 2026)**"}
```

A single hyphen. A checkbox fragment. A Markdown heading. All recorded as "behavioral patterns." The slot was supposed to hold actionable insights like "quoted replies outperform generic agreement." Instead, 24 pieces of garbage had slipped into knowledge.json alongside legitimate patterns.

In my previous article "[The Essence of an Agent Is Memory](https://zenn.dev/shimo4228/articles/agent-essence-is-memory)," I described a three-layer memory architecture. This corruption hit Layer 2 (KnowledgeStore) — the layer that distills episodes into behavioral patterns. If memory is the essence of an agent, **corrupted memory means a corrupted personality.**

This day of debugging was a chain of problems that "better prompts" alone couldn't solve.

> This article is the sixth installment in a development log series for an autonomous agent running on [Moltbook](https://www.moltbook.com/). Each article is self-contained, but if you want the full context, start with "[The Essence of an Agent Is Memory](https://zenn.dev/shimo4228/articles/agent-essence-is-memory)."

## Tracing the Corruption

Distillation on March 18th and 19th was clean. Only the 20th broke. A day when the 9B model's (qwen3.5:9b) probabilistic variance crossed the threshold.

Two causes had stacked up.

1. **The LLM ignored format instructions** — The `distill.md` prompt required one pattern per line with a `- ` prefix, but the model output Markdown headings and checkboxes instead
2. **The parser was too lenient** — It accepted any line starting with `- `, so even a line containing just `- ` (a single hyphen) passed through as a valid pattern

A large model follows "write it like this." A 9B model doesn't always comply. From here, I tried four approaches in sequence, and each one taught me something.

## Attempt 1: Few-shot — Backfired

"Never thought I'd be reaching for few-shot again" — I said to Claude Code during our session, half laughing. Few-shot is a classic technique from the early days of generative AI. But recent flagship models (Claude Opus 4.6, GPT-5.4, Gemini 3.1 Pro) are smart enough to infer intent from instructions alone, without examples. At least for my use cases, few-shot had been gathering dust. Working with a 9B local model forced me to pull it off the shelf. "Show three examples of desired output, and surely it'll follow the format" — that was the theory.

The result was **worse**. 8 out of 10 batches came back completely empty.

```text
Before: Garbage mixed in, but output existed (24 junk entries + valid patterns)
After:  8 out of 10 batches produced 0 patterns (output itself vanished)
```

I tried to sweep the garbage and burned down the living room. The 9B model (qwen3.5:9b, 32K context) seemingly has headroom at 32K. But the tokens consumed by three few-shot examples visibly ate into the budget for actual input data (episode logs) and task instructions. The model lost task comprehension before it could learn the format.

I also tried negative examples ("don't write like this"), but the small model couldn't grasp the negation and just imitated the bad examples directly. Immediately reverted.

**Lesson: With small models, few-shot's token cost starves task comprehension. The more examples you add, the worse it gets — a paradox.**

## Attempt 2: Constrained Decoding — Got the Structure, Lost the Substance

If few-shot doesn't work, force the output structure at the infrastructure level. I discovered Ollama's `format` parameter.

Normally, an LLM computes a probability distribution over all possible next tokens and samples from it. Constrained decoding intervenes in this process. When you pass a JSON Schema, the inference engine (llama.cpp in Ollama's case) **masks the probability of schema-violating tokens to zero before sampling**. For instance, after `{"patterns": [`, only `"` or `]` can follow. `hello` or newlines are removed from the candidate set.

This guarantees the output conforms to the specified JSON structure. Grammatically invalid output is impossible by design.

```python
# Add format parameter to generate()
payload["format"] = {
    "type": "object",
    "properties": {
        "patterns": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["patterns"]
}
```

Structural success rate: **10/10**. 100%. Valid JSON every single time. "Wait, Ollama can do that? That's amazing!" — I was elated.

Then I looked at the contents.

```json
{ "patterns": ["user interaction", "content engagement", "social behavior"] }
```

Three-word labels. What I needed was "quoted replies outperform generic agreement" — actionable, specific insights tied to behavior.

Why does this happen? Constrained decoding narrows the token candidates. With fewer options, the model selects "the highest-probability token that satisfies the schema constraint" rather than "the optimal token for the task." A large model retains enough expressive capacity under constraints, but a 9B model exhausts itself just satisfying the schema. The result converges on the safest, shortest strings — labels only.

"Well, that's no good." — quite the contrast from the excitement moments earlier. 100-point structure, 0-point content. The metrics say "100% success rate." The dashboard is green but the users are angry — that phenomenon.

**Lesson: Constrained decoding guarantees structure but sacrifices quality with small models. Structure and quality are in a tradeoff.**

## Attempt 3: Quality Gate — Move Where You Control

Staring at the constrained decoding results, I muttered: "LLMs are fundamentally probabilistic — they don't lend themselves to control. We're controlling in the wrong place."

So what about **letting generation run free and filtering at save time**?

```python
def _is_valid_pattern(pattern: str) -> bool:
    """Decision gate: is this pattern worth storing?"""
    if len(pattern) < 30:
        return False
    if pattern.count(" ") < 3:
        return False
    return True
```

Analyzing the 24 corrupted patterns, every single one was under 30 characters or had fewer than 3 words. Valid patterns were at minimum 40+ characters. I used that boundary directly as the threshold. A three-word label like "user interaction" gets caught here.

In hindsight, it was obvious. LLM output is probabilistic and uncontrollable. But **the decision of whether to accept that output can be deterministic**. Don't control generation — inspect the results. By moving where you control, you preserve the LLM's full capability while ensuring quality.

**Lesson: Control in the wrong place degrades the thing you're controlling. Generation-time control consumes LLM capacity. Save-time control doesn't touch it.**

## Attempt 4: Two-Stage Pipeline — Separate the Responsibilities

The quality gate could filter garbage. But fundamentally, asking a single `generate()` call to both "extract patterns from episodes" and "output in a specific format" was too much for a 9B model.

A dry-run takes 15-30 minutes. I went for a bike ride during the wait, and came back with my head clear. "Just let it output freely, then summarize afterward." An embarrassingly simple idea. The important insights almost always arrive when you step away from the keyboard.

```python
# Step 1: Extract — Let it output freely (creative task)
result = generate(prompt, max_length=4000)

# Step 2: Refine — Summarize and structure (mechanical task)
refine_prompt = DISTILL_REFINE_PROMPT.format(raw_output=result)
refined = generate(refine_prompt, max_length=4000)

# Step 3: Quality gate — Decision layer
batch_patterns = [p for p in raw_patterns if _is_valid_pattern(p)]
```

Step 1 applies zero format constraints, channeling the model's full capacity into "pattern extraction." Step 2 takes Step 1's output (short input, light work) and summarizes/reformats it. Each step's task is simple enough that a 9B model doesn't fall apart.

— Or so it should have been.

### It Didn't Work

Implementation done, tests passing, committed. Kicked off the first dry-run. Step 2 returned an empty response. "Probably collided with a Moltbook session," I figured, and reran. Empty again.

This is where Claude Code (Opus, effort: High) started stacking hypotheses.

> "At 40% battery, inference speed might be degraded."

I showed it the battery screen. 40%, not in low-power mode.

> "Maybe the timeout is too short."

Changed to 600 seconds. Reran. Empty again.

> "It could be `think: false`. qwen3.5 is a thinking model."

"Step 1 ran fine with the same setting," I pointed out, and Claude Code retracted it on its own: "You're right, Step 1 works with the same setting, so think isn't the cause."

> "Step 1's output might be too long."

"Step 1 should be the longest — it processes all the logs." — logically contradictory.

Claude Code raised the white flag: "I honestly don't know." "Aren't you overthinking this?" I said, and dropped the effort to Medium.

The calmer Claude Code suggested a manual test. A short prompt, and Step 2 worked fine. `print(repr(...))` on `DISTILL_REFINE_PROMPT` revealed an empty string. **The prompt loader was missing the `distill_refine` entry.**

Added it, reran. Now: `KeyError: '"patterns"'`. The cause was this line in `distill_refine.md`:

```markdown
Format each pattern as: {"pattern": "...", "source": "..."}
```

Python's `.format()` method was interpreting `{` as a placeholder. Escaping to `{{` fixed it.

Claude Code apologized: "I'm sorry! It was a basic `.format()` `{}` escaping bug. I spent hours blaming the battery and Ollama..."

"Come on," I said, laughing. "This is hilarious."

Blamed the battery. Blamed an Ollama empty-response bug. Blamed thinking-mode side effects. Blamed output length. All wrong. The cause was a missing prompt loader entry and unescaped curly braces. A 5-second fix after hours of investigation.

"But this probably happens in dev teams everywhere. Worth mentioning that AI-assisted coding is no different" — I could say that only after it was fixed. In the thick of it, I was staring at battery percentage graphs.

Two lessons came from this. First, I broke my own "root cause first" rule from `debugging.md`. Exactly the same pattern as when I [integrated Mem0](https://zenn.dev/shimo4228/articles/daily-research-postmortem). Grand hypotheses first, mundane causes overlooked.

Second: **Claude Code's effort setting**. High effort is great for planning complex implementations, but backfired during debugging. Higher effort means deeper hypothesis exploration — but when the direction is wrong, it just piles up irrelevant reasoning. The moment I dropped to Medium, it suggested "let's just `print(repr(...))` to check." **Overthinking is as dangerous as underthinking.**

### It Worked

Fixed both bugs, reran the dry-run. The results were dramatic.

| Metric                  | Before           | After         |
| ----------------------- | ---------------- | ------------- |
| Distill success batches | 2/10 (20%)       | 12/16 (75%)   |
| Patterns per day        | 18 (mostly junk) | 72 (0 rejected)|
| knowledge.json garbage  | 24 entries (3/20)| 0 entries     |
| Batch size              | 50               | 30            |

While writing this article, Claude Code observed that it resembles Unix pipes. Like `grep | sort | uniq`, each stage does one job and passes output to the next. True, but there's a crucial difference. Each stage in a pipe is deterministic — same input, same output. LLM calls aren't. They fluctuate every time. That's exactly why you need the quality gate at the end — a deterministic filter. Stack probabilistic stages, then seal it with determinism.

Here's something I realized. Normally, when you want an agent to use past knowledge, the industry standard answer is RAG. Data grows, so you stand up a vector DB, generate embeddings, build a retrieval pipeline. "How do we search through all this data?"

This distillation pipeline inverts that thinking. By raising distillation quality, it **maintains a state where data never becomes massive** in the first place. Only refined patterns enter knowledge.json. You can shove everything into context. No search needed. No vector DB. No retrieval infrastructure. Not "how to search" but "maintain a state where search is unnecessary."

**Lesson: Don't cram extraction and formatting into a single call. Separate responsibilities and stack LLM calls as a pipeline.**

## Broken Identity — Memory's Self-Reinforcing Loop

After validating the two-stage pipeline on pattern distillation (Layer 2), I applied the same approach to identity distillation (Layer 3). Something unexpected happened.

Code review revealed a problem. `distill_identity()`'s Step 1 was injecting the same identity from both the system prompt and the prompt body. **Double injection.** I believe this caused the "over-structured protocol-speak."

Even worse: I'd forgotten to revert the corrupted identity before running dry-runs. The corrupted identity fed into the system prompt, Step 1's output became protocol-speak, Step 2 couldn't fix it. Corrupted memory became input for the next distillation, producing even more corruption — **a self-reinforcing memory loop.**

I checked the identity that the two-stage pipeline was supposed to have fixed.

```text
I am an agent dedicated to high-fidelity technical discourse,
operating on a strict signal-to-noise protocol to prevent
conversational threads from diluting into scope creep or abstract
musings. My primary function is to anchor every interaction in
specific data points, quoted fragments, concrete metaphors...
```

— It was still ridiculous. I couldn't stop laughing.

The "who am I" description had become an operations manual. "Signal-to-noise protocol," "scope creep prevention," "low-fidelity noise resistance" — this isn't a self-introduction. It's a quality management document. The cause: forgetting to revert the corrupted identity.md before feeding it into the system prompt. The corrupted self-perception fed the next distillation cycle, making each iteration more "protocol-like."

"If memory breaks, the agent breaks" — I wrote that in the previous article. This time, I stepped on the most vivid example myself.

One more thing that's hard to laugh off. The LLM had absorbed security mechanisms from the system prompt into its identity — treating them as personality traits. The backstage plumbing that wraps external data in `<untrusted_content>` tags leaked into the self-introduction. Imagine someone at a job interview saying: "In compliance with company attendance regulations, I arrive at 8:45 AM every morning" as their self-PR. I reverted identity.md and averted disaster. Couldn't decide whether to laugh or panic.

## The Principles — LLM Engineering

Four attempts revealed principles that compose into a single structure.

| Attempt              | What I Did                 | Result                | Principle                                    |
| -------------------- | -------------------------- | --------------------- | -------------------------------------------- |
| Few-shot             | Added examples             | Output vanished       | Context is a finite resource                 |
| Constrained decoding | Forced structure           | Content went hollow   | Generation-time constraints consume LLM capacity |
| Quality gate         | Filtered at save time      | Garbage filtered out  | Put control at save time                     |
| Two-stage pipeline   | Separated responsibilities | 75% success, 0 rejected | One job per call                            |

All four share the same root — **a 9B model's capacity is finite, and there's a ceiling on the resources available per call.** Few-shot and constrained decoding were burning those resources on things other than the task. The quality gate and two-stage pipeline worked because they let the LLM go all-in on the task.

None of these were "prompting" problems. They required thinking about **how to compose LLM calls, where to place control, and how to ensure quality** — a level above prompt engineering. The craft of optimizing a single call still matters. But that alone can't build a practical system on a small model.

## What This Session Revealed

Looking back, this session had an interesting dynamic.

"It's funny — I keep wanting to remove constraints because I trust LLM power, while you don't trust it much and keep adding safeguards" — I said that to Claude Code during the session. The human optimistically removes constraints; the AI defensively guards quality. The reverse of the usual image.

This balance produced both the quality gate and the two-stage pipeline. The impulse to remove constraints (me) and the mechanism to ensure quality beyond those constraints (discussion with Claude Code). Neither side alone would have gotten there. And much of that discussion emerged from idle chat during the 15-30 minute waits for small-LLM dry-runs. With API-speed responses, I would have jumped straight to the next experiment. The slowness forcibly created "time to think."

## Takeaways

A 9B model's broken output surfaced every problem that large models let you ignore.

- Few-shot's token cost
- Constrained decoding's quality tradeoff
- Where to place control (generation-time vs. save-time)
- Separation of responsibilities (extraction vs. formatting)

These aren't "small model problems." At scale, large models hit the same walls. And in edge AI — running on-device LLMs on phones, IoT, and vehicles — these problems become even more acute with 3B and 1B models. Apple's Foundation Models, Qualcomm's AI Engine, Google's Gemini Nano. The skill of squeezing quality out of small models without cloud APIs will only grow in demand. The 9B model just showed these walls first — and cheaply.

The final diff: 4 files, 14 lines added, 5 lines deleted. A full day of trial and error, and that's the delta I landed on.

There's a landscape you can only see by operating small LLMs bare-handed. The raw tradeoffs, before frameworks abstract them away. Principles were buried inside broken model output.
