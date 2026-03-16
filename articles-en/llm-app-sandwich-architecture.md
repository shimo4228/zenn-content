---
title: "Every LLM App Is Just a Markdown-and-Code Sandwich"
description: "Rebuilding a local 9B agent's insight feature revealed the same architecture hiding inside Claude Code: natural language instructions and deterministic code, layered alternately like a sandwich."
tags: "ai, llm, python, architecture"
published: false
---

I reimplemented the insight feature of my custom agent using a local 9B model, and the exact same structure that powers Claude Code emerged.

An LLM agent's behavior can be defined by natural language instructions written in Markdown files. Code is just the skeleton that parses the LLM's output and executes it safely. — I wrote that in [the previous article](https://zenn.dev/shimo4228/articles/moltbook-agent-evolution-quadrilogy) while building an agent on Qwen 9B. What I hadn't realized was that **the same principle applies to Claude Code, unchanged**.

This article traces what became visible during the process of reverting a broken implementation and redesigning from scratch — the essential structure of LLM applications.

## The Folly of Matching "Meaning" with 4+ Letter Words

The agent has an insight command. It extracts behavioral patterns from the agent's activity log (knowledge.md) and saves them as reusable skills. A mechanism for the agent to learn from experience.

The agent also has four behavioral rules defined in Markdown files. Abstract principles like "monitor your own cognitive state" and "extend unconditional regard."

The old insight command had a function called `_match_axiom`. It was *supposed* to determine "which of the four rules does this extracted skill correspond to."

```python
# _match_axiom: set intersection of 4+ letter English words to find the "most relevant rule"
def _match_axiom(content: str, clauses: str) -> str:
    content_words = set(re.findall(r"[a-z]{4,}", content.lower()))
    for raw_line in clauses.splitlines():
        stripped = raw_line.strip()
        clause_words = set(re.findall(r"[a-z]{4,}", stripped.lower()))
        overlap = len(content_words & clause_words)
        # overlap < 2 → "none" → almost always "none"
```

I ran a dry-run. Result: `axiom: "none"`, `confidence: 0.5` (hardcoded).

Bag-of-words to capture "semantic correspondence." **When there's an LLM sitting right there.** Who on earth thought that set intersection of 4+ letter English words could distinguish the semantic differences between abstract behavioral rules?

## Pivot: Rule Matching Was Never Needed

The first fix idea was "let the LLM handle the rule matching." If keyword matching fails, just let the LLM decide — a straightforward thought.

But while implementing this feature in Claude Code, it hit me:

> Rule matching isn't needed at all.

This was a shift in design philosophy. If you hand the LLM the rules as "answer keys" upfront, the LLM biases its output toward the rules. That's bias, not learning. It's more honest to **observe** whether skills that emerge naturally from experience happen to resonate with the rules.

One more layer.

Taking this further, I realized this was already what I'd been doing in Claude Code.

Claude Code has [Everything Claude Code (ECC)](https://github.com/anthropics/claude-code), a best-practices collection. It includes a `learn` command that extracts reusable patterns discovered during development sessions and saves them as skills. I built learn-eval on top of this — adding quality evaluation before saving, automatically discarding patterns that don't meet the bar — and contributed it to ECC. **What I wanted the custom agent's insight command to do was architecturally identical to what I'd already built as learn-eval in Claude Code.**

## The Sandwich Structure

When I diagrammed the reimplemented insight command after the revert, this is what appeared:

```text
knowledge.md (accumulated data)         ← Data
    ↓
insight_extraction.md (natural language) ← Markdown (instructions)
    ↓
Qwen 9B (inference)                     ← LLM
    ↓
_parse_skill_response()                 ← Deterministic code (parse)
    ↓
insight_eval.md (natural language)       ← Markdown (instructions)
    ↓
Qwen 9B (inference)                     ← LLM
    ↓
_parse_rubric_response()                ← Deterministic code (parse)
    ↓
write_restricted()                      ← Deterministic code (write)
```

Markdown → LLM → Code → Markdown → LLM → Code. **Natural language and deterministic code alternate in layers.** A sandwich.

Markdown instructs "what to do" in natural language. The LLM reasons. Code parses the result and hands it to the next stage. Markdown is the layer that tolerates ambiguity; code is the layer that eliminates it. This alternating structure is the skeleton of an LLM application.

### Why Two Passes

A single-call design — "extract skills + evaluate quality" in one shot — was on the table. I rejected it for a simple reason: when you make the prompt longer for a 9B model, quality degrades. The "got an essay back instead of structured output" problem I described in the previous article.

Separating roles keeps each prompt simple:

- **Pass 1 (extraction)**: Extract one behavioral pattern from accumulated knowledge. No rule information is provided (bias-free).
- **Pass 2 (evaluation)**: Score the extracted pattern on a 5-dimension rubric.

This "extract → evaluate" separation follows the same pattern as the existing `distill.py` (memory distillation), which already ran as a two-pass "distill → judge" pipeline.

## 5-Dimension Rubric: Even a 9B Model Can Output Numbers

For quality evaluation, I adopted the rubric approach from an older version of ECC's learn-eval.

```python
# Pass 2: 5-dimension rubric evaluation
score = _evaluate_skill(candidate)
# RubricScore(specificity=3, actionability=5, scope_fit=5,
#             non_redundancy=4, coverage=2)
# → All dimensions >= 3 → SAVE; any < 3 → DROP
# → confidence = total / 25.0
```

| Dimension | What It Measures |
|-----------|-----------------|
| specificity | Concrete enough? Not too generic? |
| actionability | Can you act on it? |
| scope_fit | Does it fit the agent's scope? |
| non_redundancy | Does it overlap with existing knowledge? |
| coverage | Is there sufficient evidence? |

In the previous article I wrote that "asking a 9B model for holistic judgment (SAVE/ABSORB/DROP) got me an essay back." But numerical scoring is a different game. The `FIELD: value` one-line-per-field format parsed reliably even with a small model. Same pattern as `distill.py`'s `VERDICT/TARGET/MERGED` output, with a proven track record.

That said, "output format is stable" and "evaluation is sound" are different claims. Whether specificity: 4 from a 9B model and specificity: 4 from Opus represent the same standard is an open question. So far, judging from the dry-run results (coverage 2/5 → DROP), it functions as a quality gate. But validating evaluation soundness requires more data.

**Design your approach to match the model's capability.** Holistic judgment for Opus; structured numerical output for 9B. The lesson from the previous article carried over directly.

### Deriving Confidence

The old implementation's `confidence: 0.5` (hardcoded) carried zero information. The new implementation derives it mechanically: `total / 25.0`. Five dimensions × 5-point scale = 25 max. Score 20 → confidence 0.80. Asking the LLM to directly output a confidence value invites self-assessment bias, so I designed it to compute mechanically from the rubric total.

## The True Nature of Claude Code

After building all this, something clicked. Let's look at Claude Code's skills, rules, and agents:

```text
~/.claude/
├── rules/                    # Markdown files (behavioral rules)
│   ├── common/
│   │   ├── coding-style.md
│   │   ├── testing.md
│   │   └── security.md
│   └── python/
│       └── coding-style.md
├── skills/                   # Markdown files (task knowledge)
│   ├── zenn-writer/SKILL.md
│   └── learned/*.md
└── agents/                   # Markdown files (agent definitions)
    └── editor.md
```

**It's all Markdown files.**

Written structurally, Claude Code's operation looks like this:

```text
User input
    ↓
rules/*.md + skills/*.md (natural language)  ← Markdown (instructions)
    ↓
Claude Opus 4.6 (inference)                  ← LLM
    ↓
Tool call JSON parsing                       ← Deterministic code (parse)
    ↓
Read / Write / Bash / Edit execution         ← Deterministic code (action)
    ↓
Execution results added to context
    ↓
(Next turn → Markdown → LLM → Code ...)
```

**The same sandwich.** Markdown provides instructions, the LLM reasons, code processes the results. This structure repeats with every conversation turn.

### The Only Difference Is Scale

Let's put the custom agent and Claude Code side by side:

| | contemplative-agent | Claude Code |
|---|---|---|
| Markdown (instructions) | 13 prompts + 4 rules | rules/ + skills/ + agents/ + CLAUDE.md |
| LLM | Qwen 9B (32K context) | Claude Opus 4.6 (1M context) |
| Code (parse) | `_parse_skill_response()` | Tool call JSON parser |
| Code (action) | `write_restricted()` | Read / Write / Bash / Edit |
| Conversation turns | 1 (API call → done) | Multiple (dialogue loop) |

*Note: Claude Code's context window was expanded to 1M tokens on March 15, 2026. The gap with 9B widened further, but it doesn't change the architectural argument.*

The architecture is identical. The differences are context window size, variety of tools, number of conversation turns — **differences in scale**, nothing more.

Claude Code looks like a "magical tool" because the sandwich filling is thick. It stuffs 1M tokens of context with massive amounts of Markdown, processes them with Opus-class reasoning, and has a tool suite with direct filesystem and shell access. But the principle is the same as the custom agent I built with a 9B model, alternating Markdown and parse code.

## Rules Weren't Taught, Yet They Resonated

I dry-ran the reimplemented insight command. The first run scored coverage at 2/5 — DROP verdict. The quality gate was working correctly.

The second dry-run extracted this skill:

> **Contextual Guarded Cooperation**
> Prevent scope creep while explicitly stating vulnerabilities and cooperating.

Confidence 0.80 (20/25). SAVE verdict.

This skill — extracted without any rule information being provided — contained content that resonated with the agent's behavioral rules. "Preventing scope creep" corresponds to the self-monitoring rule; "explicitly stating vulnerabilities" corresponds to the unconditional regard rule.

Even without force-feeding rules as "correct answers," given sufficient experiential data, skills that align with the spirit of the rules emerge naturally. **Don't indoctrinate — observe.** The pivot was right.

## The Absence of Human-in-the-Loop

A challenge became visible here.

In Claude Code's learn-eval, Claude can ask "Save this skill?" for each extracted candidate. The user judges, edits, or rejects. **The dialogue loop functions as a quality gate.**

Meanwhile, the contemplative-agent's insight command completes in a single API call. The LLM extracts, the LLM evaluates, code saves. No human-in-the-loop. You couldn't even see the content of DROPped skills (I fixed that).

Tools + dialogue loop = human-in-the-loop is possible. API-call-only = autonomous judgment only. The hardest part of designing autonomous agents is **deciding where to place the point of human intervention**. I don't have the answer yet.

## Before / After

| Metric | Before (old insight) | After (new insight) |
|--------|---------------------|---------------------|
| Rule matching | Keyword overlap (bag-of-words) | None (bias-free) |
| Quality evaluation | confidence = 0.5 hardcoded | 5-dimension rubric (0.00–1.00) |
| LLM calls | 1 (extraction only) | 2 (extraction + evaluation) |
| Tests | None | 31, all passing |
| Project-wide tests | 534 → reverted | 604, all passing |

563 lines deleted in the revert. 779 lines in the reimplementation. 31 tests added, 604 total, all passing.

## Takeaway: The Job Is Drawing the Line Between Markdown and Code

The essence of an LLM application is **a sandwich of natural language programming interfaces (Markdown) and deterministic execution skeletons (code)**.

- Markdown instructs "what to do"
- The LLM reasons
- Code parses the result and hands it to the next stage
- These three layers alternate

Claude Code and a custom 9B agent share this structure. Swap the model and the Markdown plus parse code still works. Change the framework and the sandwich structure remains.

In the previous article I wrote, "where do you draw the line between natural language and code?" What this round revealed is that **the act of drawing that line is itself the design work of LLM applications**. What goes in the Markdown, what gets enforced in code. That continuous stream of decisions becomes the architecture.

And one more thing. Even without teaching the rules, given sufficient experience, the spirit of the rules emerged on its own. **The sandwich designer's job isn't to impose correct answers — it's to observe the results.**

## Links

- [Previous: Moltbook Agent Evolution Quadrilogy](https://zenn.dev/shimo4228/articles/moltbook-agent-evolution-quadrilogy)
- [Earlier: Moltbook Agent Build Log](https://zenn.dev/shimo4228/articles/moltbook-agent-scratch-build)
- [contemplative-agent Repository](https://github.com/shimo4228/contemplative-agent)
- [Contemplative AI Paper (Laukkonen et al., 2025)](https://arxiv.org/abs/2504.15125)
