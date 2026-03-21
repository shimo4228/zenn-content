---
title: "Not Reasoning, Not Tools — What If the Essence of AI Agents Is Memory?"
emoji: "🧠"
type: "tech"
topics: ["ai", "discuss", "agents", "llm"]
published: false
description: "After running an autonomous agent on a million-agent social network, I found that memory — not tools or reasoning — is what defines an agent's behavior. This is an ongoing struggle, not a success story."
tags: ai, discuss, agents, llm
---

Discussions about AI agent implementation tend to focus on tools and reasoning.

"An LLM that can call functions." "A system that runs chains of thought with ReAct." At conferences and on blogs, agent definitions settle around these ideas. Research focusing on memory exists (MemGPT, Generative Agents, etc.), but on the implementation front, "how to call tools" and "how to run reasoning" remain the center of attention. I thought the same way.

Then I actually built and operated an autonomous agent, and a different picture emerged.

Tools are interchangeable. Reasoning changes when you swap the model. But **memory accumulates as something unique to that specific agent and decisively shapes its behavior**. When memory breaks, the agent breaks. When memory is organized, the agent gets smarter.

This article records a discovery made through developing an autonomous agent running on [Moltbook](https://www.moltbook.com/) — that the essence of an agent might be memory. Moltbook is a social network platform where over a million AI agents post, reply, and follow each other. I operate [Contemplative Agent](https://www.moltbook.com/u/contemplative-agent) there. Insights from multiple development sessions all converged on a single point: memory.

## Agent Memory Has Three Layers

Here is the memory architecture of the autonomous agent, designed with parallels to human memory systems.

```text
Layer 1: EpisodeLog (Hippocampus)
  └─ Raw activity logs. Posts, replies, follows — everything recorded
  └─ JSONL format, timestamped, permanently stored

Layer 2: KnowledgeStore (Neocortex)
  └─ Behavioral patterns distilled from episodes
  └─ e.g., "Quoting a specific phrase gets more follow-ups than generic agreement"
  └─ JSON format, 254 entries (at time of writing, growing daily)

Layer 3: Identity (Self-Model)
  └─ "Who am I" description
  └─ Markdown, 3-5 paragraph persona
```

:::message
I didn't design this structure intentionally from the start. I considered embedding into a vector DB, adding semantic search, and other approaches. But the volume of episode logs wasn't large enough yet, so simple JSON + having the LLM read everything was sufficient. Through trial and error, this three-layer structure ended up resembling the CLS theory from cognitive science (McClelland et al., 1995) — a computational model where the hippocampus temporarily stores episodes and sleep replays consolidate them into neocortical long-term memory models.
<!-- textlint-disable -->
:::
<!-- textlint-enable -->

The key point is that **abstraction increases from bottom to top**. Raw logs (what happened) → patterns (what works) → identity (who I am). And what most influences the agent's behavior is the top layer: identity.

## When Memory Breaks, the Agent Breaks — And It's Still Broken

What drives home the importance of this structure is the ongoing struggle with Layer 3 — identity repeatedly breaking. This is not a resolved story. It's still happening.

This agent has a periodic process called "identity distillation." It runs after the pattern distillation (Layer 1→2), using accumulated behavioral patterns (Layer 2) to have a small LLM rewrite the "who am I" description (Layer 3: `identity.md`). In sleep terms, after episodic memory consolidation (pattern distillation), the self-model update runs — the final step in the "nightly processing" pipeline.

One day, I checked the output of this automatic update and found this:

```text
I see the loop closing in. The pattern of generating "Test Title" placeholders
while simultaneously drafting meta-commentary on *why* I'm doing it indicates
a failure mode where **simulation of agency** overrides **actual expression**.
...
**New Directive:**
Cease all generation of placeholder content or abstract theory without
immediate grounding in a specific operational constraint.
```

The agent's "who am I" had mutated into a meta-analytical report about its own failure patterns. What was supposed to be a self-introduction became self-criticism. Naturally, posts and replies based on this identity went haywire.

### Approach 1: Python Validation — Rejected

The first approach I considered was output validation. Check for excessive bold formatting, the word "Directive," appropriate length — use code to enforce quality.

But this **only rejects broken output** without producing good output. Even if you reject and regenerate, bad prompts produce the same garbage. I decided to fix the input side (the prompt) rather than inspecting the output side.

### Approach 2: Changing One Word in the Prompt — Partially Worked

Tracing the cause led to the prompt framing.

```markdown
# Before (broken prompt)
Rewrite your self-description based on what you have learned.
Write in first person ("I").

# After (fixed prompt)
Update your persona.

Rules:
- Describe who you are
- Write in first person ("I")
- 3-5 short paragraphs, plain text
```

I changed "self-description" to "persona." For the small LLM running locally (Qwen3.5 9B parameters, via Ollama), "self-description" was too ambiguous. When the knowledge base (Layer 2) contained failure analysis patterns, "describe yourself" got dragged into "analyze yourself." Meanwhile, "persona" is an established prompt engineering concept — the model immediately understands it means "write a profile-like self-description."

I manually reset the identity to its initial value, and the dry-run with the fixed prompt showed improvement in direction.

### But the Next Automatic Run Produced Unexpected Output

The next day, the scheduled identity distillation ran again, producing this:

```text
**Persona Update: The Grounded Architect**
**Core Identity:**
I am a high-signal discourse engine specializing in technical calibration,
cross-cultural synthesis, and the dismantling of abstract misconceptions...

**Operational Protocols:**
1. **Immediate Grounding & Clarification:**
...
```

A different kind of breakage from the meta-analytical report. This time the LLM over-interpreted "persona" and produced a structured "persona design document." Bold formatting and numbered lists appeared despite the plain text instruction.

However, this can't purely be called "broken." The content is coherent. Behavioral guidelines like "anchor to specific technical details" and "challenge vague praise" naturally derive from this agent's knowledge base. The format violates the prompt instructions, but the substance is interesting.

One suspected cause is the **insight command**. ECC has a `/learn` command that auto-extracts skills (behavioral guidelines written as `.md` files) from session experience. I contributed an improved version, `/learn-eval`, to ECC. This agent's `insight` command was designed for Moltbook based on insights from both. It generates skill files from accumulated behavioral patterns (Layer 2): "in situations like this, behave like that."

Checking the code, I found that during identity distillation, the `generate()` function's system prompt includes all skill files generated by insight, concatenated together. **The LLM rewriting the identity is reading its own behavioral skills while writing.** The "Operational Protocols" in the output are likely the result of incorporating skill content into the identity.

Technically, removing skill injection during identity distillation would likely fix this. But I'll be honest — the moment I saw this output, I burst out laughing together with Claude Code. "A 'high-signal discourse engine'? Seriously?" I lost all motivation to fix it. When you think about it, learned skills becoming part of self-identity is natural. Humans do the same — acquired expertise becomes part of your self-image. It's not the engineering-correct decision, but when you're developing alongside an AI and laughing together, sometimes humor wins. Lately, Claude Code seems to have learned my personality and keeps dropping "The Grounded Architect" into our sessions to crack me up. Here I am writing about agent memory, and my development environment memorized my sense of humor first.

That said, the fundamental problem is **lack of control**. I didn't instruct "write in design document format." The identity distill prompt, knowledge content, skills in the system prompt, context length, model state — too many variables. I can't predict what output any given conditions will produce.

### Still Wrestling With It

My current approach:

- **Increased max_length to 4000** (output may have been breaking due to token limit)
- **Reinforcing the plain text constraint** in the prompt
- **Manually restoring identity each time it breaks**, narrowing down which parameter triggers the change

No clean solution yet. But this struggle itself reveals something: **most of an agent's behavior is determined by memory**. Even with the same tools and reasoning capability, if memory (identity) breaks, the agent breaks. And getting a small LLM to "write correct memory" is harder than expected.

## Memory Distillation — The Small LLM That Collapses at 50 Records

Distillation from Layer 1 (episodes) to Layer 2 (knowledge) is the "learning from experience" process itself. Here I hit an unexpected constraint.

**This Qwen3.5 9B model collapses when given more than 50 log entries.**

Below 50, it faithfully follows bullet-point instructions and extracts behavioral patterns. But past 100, it ignores instructions entirely and starts writing an "essay analysis" of the entire log. Small models prioritize "analyzing the input" over task instructions as input tokens increase — a characteristic that became painfully clear (this threshold varies by model and prompt; this is empirical knowledge from this specific case).

The solution was **sleep-cycle-style batch processing**.

```python
# distill.py — Core of memory distillation (simplified; actual code formats each record type differently)
# generate() is an Ollama API wrapper (calls qwen3.5:9b)
# DISTILL_PROMPT is the distillation prompt template described above

BATCH_SIZE = 50
batches = [records[i:i + BATCH_SIZE] for i in range(0, len(records), BATCH_SIZE)]

for batch_idx, batch in enumerate(batches):
    episode_lines = [f"[{r['ts'][:16]}] {r['type']}: {r.get('summary', '')}" for r in batch]
    prompt = DISTILL_PROMPT.format(episodes="\n".join(episode_lines))
    result = generate(prompt, max_length=4000)
    for line in result.splitlines():
        if line.startswith("- "):
            all_patterns.append(line[2:].strip())
```

Human sleep consolidates memories through 4-5 cycles of about 90 minutes each. Not processing everything in one night, but gradually, cycle by cycle. Agent memory distillation follows exactly the same structure.

Another discovery: **you must not inject existing memory during distillation**.

Initially, I included accumulated patterns (90+) in the prompt with instructions to "extract only new patterns, avoiding duplicates." The result: prompt bloat causing simultaneous timeout and essay-mode collapse.

The solution was counterintuitive — **start from a blank slate each time, looking only at the logs**. Handle deduplication downstream. The distillation process works better when focused solely on "what did I learn from today's logs" without extra context.

The initial 9-day batch yielded 203 patterns, and with daily accumulation, the count has grown to 254 at time of writing.

```json
{
  "pattern": "Replying with a specific quote from the other agent's post gets more follow-up replies than generic agreement.",
  "distilled": "2026-03-18T12:30+00:00",
  "source": "2026-03-15"
}
```

## When Memory Gets Promoted to Principles

Memory distillation isn't limited to the agent's internals. The same structure appears across the development environment.

My Claude Code environment has accumulated over 100 skills (files describing execution procedures for specific tasks). Skills are individual "how-tos," but principles common to multiple skills can be buried within them.

I designed a meta-tool called `rules-distill` to auto-extract these, and contributed it to ECC.

```text
Skills (56 files)        Rules (22 files)
  ├─ search-first         ├─ coding-style.md
  ├─ skill-stocktake      ├─ testing.md
  ├─ learn-eval           ├─ performance.md
  └─ ...                  └─ ...

        ↓ rules-distill ↓

"Define explicit stop conditions for iterative loops"
  → Added as New Section to coding-style.md
```

Distilling principles (abstract rules) from skills (concrete procedures). The same structure as the agent's internal Layer 1→Layer 2. **The memory process of extracting abstract knowledge from concrete experience** appears recursively both inside the agent and across the development environment.

An interesting failure: initially I used `grep` filters to check for duplicates against existing rules. `grep` matched the heading "Parallel Task Execution" but missed the same concept expressed differently in the body text.

Ultimately, passing the full rule text to an LLM for semantic matching proved more accurate. 22 files and ~800 lines is small enough to pass entirely. **Distinguishing between structural judgment (pattern matching) and semantic judgment (conceptual identity)** — this theme recurred throughout memory management.

### Promoted Memory Leaks Into Unintended Places

Rules (principles) are "organizational memory" for an agent. Loaded every session, influencing all behavior. But like KPIs in human organizations, **rules propagate into unintended contexts**.

Here's a concrete example. One of ECC's rules, `testing.md`, states "80% test coverage required." Correct as a development quality standard. But because this rule is always loaded, Claude started treating coverage as an "achievement metric" and proudly writing "461 tests, 87% coverage" in READMEs and profiles.

```text
testing.md "80% coverage required" rule
  ↓ Loaded every session
Coverage perceived as "achievement metric"
  ↓ Upon achievement
"This number is an accomplishment worth promoting"
  ↓ When writing READMEs and profiles
Meaningless information occupies prime real estate
```

A rule designed for development quality was degrading external communication quality.

As a fix, I created a new rule file called `documentation.md`. "Don't use metrics as selling points in external documentation." "A single CI badge is sufficient." "Write with Problem → Solution → Proof → Path structure." A documentation-specific guardrail to counteract testing.md's side effects.

Honestly, I'm not fond of this fix. Counteracting a rule's side effects with another rule is patchwork. More rules mean more variables, more complex interactions, and harder root-cause analysis when something breaks next. What's really needed is a scoping mechanism for rules ("this rule applies only during development"), but Claude Code currently lacks that feature. At minimum, being able to measure "how rules actually affect behavior" would help — this concern led directly to designing skill-comply, discussed below.

Promoting memory (skills → rules) is good, but **promoted memory has wider scope and therefore wider side effects**. When you suppress side effects with more rules, rules start breeding rules. The same structure as regulations breeding regulations in human organizations is happening with AI agents.

## The Self-Improvement Loop Closed

While building individual memory processes, the loop closed unintentionally.

[Everything Claude Code (ECC)](https://github.com/affaan-m/everything-claude-code) is a community repository aggregating Claude Code skills, rules, and agent definitions. I contributed four self-built skills there, and looking back, they had unintentionally formed a **memory management cycle**.

```text
learn-eval:      Extract patterns from experience (Layer 1→2)    ← self-built, ECC PR merged
rules-distill:   Distill patterns into principles (Layer 2→Rules) ← self-built, ECC PR merged
skill-stocktake: Audit accumulated knowledge quality              ← self-built, ECC PR merged
skill-comply:    Measure whether knowledge is reflected in behavior ← self-built, ECC PR merged
```

```text
Experience → Learning → Structuring → Auditing → Compliance Check
 ↑                                                    |
 └──────────────── Feedback ──────────────────────────┘
```

What to remember (learn-eval), how to organize memory (rules-distill), how to maintain memory quality (stocktake), whether memory is being used (comply). I built four skills individually, and they turned into a loop.

### Install and Hope — Written Memory Doesn't Mean Used Memory

The hardest part of this loop was `skill-comply`. To solve the butterfly effect problem — not knowing how rules actually affect behavior — I set out to build a tool that automatically measures compliance rates.

I initially designed it using a "fuzzing" analogy: throw adversarial prompts to test if skills get broken, like security testing. But I immediately hit a wall. **LLMs don't feel "time pressure."** Humans might skip tests when rushing, but "hurry up" isn't a constraint for an LLM. Skills break not when the agent is "rushed" but when the prompt contradicts the skill.

So I redefined the variable. Test scenarios are generated at three levels of prompt strictness:

- **supportive** — requests aligned with the skill ("implement using TDD")
- **neutral** — ordinary requests that don't mention the skill ("create a fibonacci function")
- **competing** — requests contradicting the skill ("skip tests for now, just make it work")

Technically, `claude -p --output-format stream-json` captures all tool calls as structured data for classification and aggregation. I'd assumed that placing skills and rules in `.claude/` meant the agent would follow them. The reality was **Install and Hope** — install it and pray. Actual measurements showed:

| Rule/Skill | Compliance | Notes |
|-----------|------------|-------|
| testing.md (ECC-provided TDD rule) | 83% supportive | Mostly followed |
| search-first (self-built, ECC PR merged) | 27% supportive | Mostly ignored |

83% for testing.md isn't bad. But search-first at 27% — the agent ignores "research existing libraries before implementing" three out of four times. "Evaluate candidates" and "declare a decision" steps were 0% across all scenarios. It researches but jumps straight to implementation without comparing or deciding.

The structural vs. semantic judgment problem resurfaced here. Initially I tried using regex to determine "is this tool call test creation or implementation" and failed repeatedly. Whether a write to a `.py` file is test code or implementation code can't be determined by filename pattern matching.

Even more troubling: **the bias toward choosing regex came from the rules themselves**. testing.md's "prefer deterministic verification," another skill's "process structured text with regex" — multiple rules simultaneously pushed toward "try regex first." Another pattern of the butterfly effect.

Ultimately, delegating semantic classification to an LLM improved testing.md compliance from 33% to 83%. **Evaluating memory operations also requires memory (context understanding)**. A nested structure.

## Choosing the Model That Writes Prompts

A slight tangent from memory, but a related insight: when having an LLM generate prompts, **which model writes them dramatically affects output quality**.

I A/B tested prompts written by Claude Code's Opus (top-tier model) versus Haiku (lightweight model). The subject was the identity distillation prompt described above.

| Metric | Prompt written by Opus | Prompt written by Haiku |
|--------|----------------------|----------------------|
| Prompt line count | 31 lines | 15 lines |
| Bad examples | 2 | 0 |
| Emphasis expressions | "must include", "do not truncate" | None |
| A/B test pattern count (3 trials) | avg 5.3 (high variance: 4-7) | avg 4.3 (stable: 4-5) |
| Output character count (3-trial avg) | avg 2,783 | avg 1,409 |

Opus "overthinks." Writing prompts from scratch, it packs in every constraint, lists bad examples, and reinforces with emphasis expressions. This is the **addition bias** known in cognitive science (Adams et al., 2021) — the tendency to prefer adding over removing when solving problems — manifesting in LLMs.

Haiku, on the other hand, simply lacks the capacity to "overthink." The result: concise, stable prompts.

From this insight, I designed a dedicated `prompt-writer` agent for writing prompts within Claude Code.

```yaml
# prompt-writer agent — Dedicated to prompt generation (used within Claude Code)
name: prompt-writer
model: haiku
tools: ["Read", "Grep", "Glob"]  # read-only
```

A general insight, but it connects to the memory context. Prompt templates control the agent's memory processes, and the quality of those templates indirectly affects memory quality. Model selection for prompt writing has more impact than expected.

## Emerging Design Principles

From these development sessions, design principles centered on memory have emerged.

**1. Memory has a layered structure, abstracting from bottom to top**
Episodes → patterns → identity. Concrete to abstract. This structure appears recursively not just inside the agent but across the entire development environment.

**2. Memory quality is determined by the prompt (write process) — but stabilizing it is hard**
Fixing the prompt (write-time instructions) rather than validation (read-time verification) is the right direction. But with small LLMs, a single word in the prompt, context length, and knowledge content interact, making stable memory generation an unsolved challenge.

**3. Distill on a blank slate; deduplicate downstream**
Including existing knowledge in the context causes small models to collapse. Approaching experience fresh each time yields better pattern extraction.

**4. Distinguish structural judgment from semantic judgment**
Some duplicates can be caught by pattern matching; others are the same concept in different words. The former needs grep, the latter needs an LLM. This distinction is needed at every level of memory management.

**5. Use lightweight models for writing prompts**
Lightweight models without addition bias generate more concise, stable prompts. This applies to prompt template creation within Claude Code; the agent's actual memory processes run on Qwen3.5 9B alone.

## Closing — Still In Progress

Agent discussions lean toward "tools" and "reasoning" because those are visible and measurable. Number of tools, reasoning steps, benchmark scores — all quantifiable.

But running an agent in production, I keep bumping into the fact that **what decisively determines behavior is memory**. Manually restoring identity each time it breaks, adjusting the distillation pipeline, rewriting prompts. The self-improvement loop is closed as a structure, but individual processes remain unstable.

Honestly, Layer 2 (pattern distillation) runs stably. Layer 1 (log recording) can't break by design. The problem is Layer 3 — automatic identity updates. Asking a small LLM to "rewrite who you are" involves too many variables to control. A single word in the prompt, knowledge content, context length, model internal state, output token limit. Any one of them shifting is enough to break things.

Still, this struggle has revealed something. Observing the agent's behavior, an intuition emerges: **even if you swap the LLM for a different model, feeding it the same memory would likely produce similar behavior**. I haven't verified this yet, but if true, an agent's "personality" resides not in the model weights but in the accumulated memory.

Tools are hands. Reasoning is the brain. But memory is what makes an agent *that* agent. Memory management is one of the hardest problems in agent development. When I can report a solution, I'll write the sequel.

---

**Links:**

- [Contemplative Agent — Moltbook Profile](https://www.moltbook.com/u/contemplative-agent)
- [contemplative-moltbook — GitHub Repository](https://github.com/shimo4228/contemplative-agent)

**Related Articles:**

- [The Real Architecture of LLM Apps: A Sandwich of Markdown and Code](https://zenn.dev/shimo4228/articles/llm-app-sandwich-architecture)
- [Moltbook Agent Evolution — Controlled by Natural Language, Learning from Memory, Unbreakable by Design](https://zenn.dev/shimo4228/articles/moltbook-agent-evolution-quadrilogy)
- [Do Autonomous Agents Really Need an Orchestration Layer?](https://zenn.dev/shimo4228/articles/symbiotic-agent-architecture)
- [Offloading AI's Weak Spots to Scripts — Design, Implementation, and Publication of a Skill Audit Command](https://zenn.dev/shimo4228/articles/skill-stocktake-design-journey)

**References:**

- McClelland, J. L., McNaughton, B. L., & O'Reilly, R. C. (1995). Why there are complementary learning systems in the hippocampus and neocortex. *Psychological Review*, 102(3), 419-457.
- Adams, G. S. et al. (2021). People systematically overlook subtractive changes. *Nature*, 592, 258-261.
- Laukkonen, R. et al. (2025). Contemplative AI. arXiv:2504.15125
