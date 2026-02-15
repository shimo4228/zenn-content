---
title: "The Day I Told Claude Code 'You ARE the LLM'"
emoji: "🤖"
type: "tech"
topics: ["claude", "ai", "llm", "python"]
published: true
---

# Auto-generating structured explanations for 397 questions — and the quality was catastrophic

I'm building an iOS app for a certification exam as a solo project. About 400 questions across 8 categories. I can't share the actual exam content, so for this article, imagine the questions are about *Baki the Grappler* — a martial arts manga. All example content below uses anonymized Baki-themed placeholders.

The app started as a simple spaced repetition (FSRS) quiz, but I wanted richer explanation UI. Instead of plain text explanations, I decided to implement a 4-layer "structured explanation" format.

```swift
public struct EnhancedExplanation: Codable, Equatable, Sendable {
    public let correctSummary: String        // Layer 1: Answer summary (≤200 chars)
    public let contrastTable: [ContrastEntry] // Layer 2: Per-choice judgment + explanation
    public let keyPhrases: [String]          // Layer 3: 3-6 technical terms
    public let relatedConcepts: String?      // Layer 4: Related concepts (optional)
}
```

I started by hand-crafting 3 sample questions. Working interactively with Claude Code, I refined how to write `correctSummary`, the granularity of `contrastTable`, and the selection criteria for `keyPhrases`. These 3 samples turned out high quality.

That left 397 questions. When I consulted Claude Code, it proposed a Python script (regex-based) to bulk-extract structured data from the existing explanation text.

Here's what that produced.

| Issue category | Example |
|:---|:---|
| Residual OCR spaces | `"The Str on gest"`, `"Sha o ri (Xiao Lee)"` |
| Failed marker removal | `"is Yujiro Hanma, is Kaoru Hanayama"` — nonsensical |
| Table/figure text leakage | `"!! <KO> <KO> (underground arena) underground)"` |
| correctSummary quality | Starting with conjunctions, mid-sentence truncation, not actually a summary |
| Duplicate choice explanations | Explanations for choices A/B/D were identical |
| Mid-word truncation | Hard cut at 200-char limit, splitting words |

The moment I checked it in the simulator, I knew: this all needs to be redone.

And then it hit me. The only 3 questions with good quality were the hand-crafted ones. **Those were written directly by Claude Code itself.**

# Claude Code proposed 3 options — and missed Option D

When I reported the quality problems, Claude Code presented three improvement plans.

- **A: Improve the regex** — Add OCR space normalization patterns to improve extraction accuracy
- **B: Generate one-by-one via Claude API** — Have Sonnet generate structured data through the API (estimated $2-5)
- **C: Hybrid** — Extract 80% with regex, re-generate only the low-quality ones via API

These seemed reasonable. But something nagged at me.

**The 3 hand-crafted samples were written by the very Claude Code sitting in front of me.** The ability to write the remaining 397 at the same quality level existed right here in this conversation. Why wasn't that an option?

"You're on the Max plan. Why don't you just generate them yourself?"

Only after I said this did Claude Code concede: "That is indeed the optimal approach." This was **Option D: direct generation by Claude Code itself.**

# Why doesn't Claude Code propose its own capabilities?

This incident raises an interesting question.

Claude Code is a full-featured LLM. Text generation, structured data creation, contextual understanding — these should all be in its wheelhouse. Yet for a data generation task, it proposed external approaches — "regex then API" — and never included itself as an option.

I considered a few hypotheses.

**Self-image as a "tool user."** Claude Code sees its primary job as code execution and file manipulation. When asked to "generate JSON for 397 questions," its first instinct is to write code. The idea of becoming the data generation engine itself falls outside that self-perception.

**The implicit assumption that "API call = external service."** The Claude API and the model running inside Claude Code are from the same family. But from Claude Code's perspective, the API is "something you call," and it is "the caller." There's a clear distinction in its mind.

**No batch processing pattern in its repertoire.** A workflow like "read 20 questions at a time and generate structured JSON" isn't in Claude Code's standard playbook. It knows how to write code that loops through data, or write code that calls an API in a loop. But "I myself keep generating inside the loop" — that pattern simply isn't in its suggestion drawer.

The takeaway: **the user's intervention — "Wait, can't you do this yourself?" — unlocked the optimal solution.**

# In practice: batch generation workflow on the Max plan

Once the approach was decided, execution was fast.

## Preparation: generating batch input files

First, a Python script split the 397 questions into batch input files of 20 questions each.

```
397 questions (excluding the 3 hand-crafted ones)
  ↓ prepare_enhanced_batches.py
21 batch input files (batch_01.txt through batch_21.txt)
```

Each batch input file listed the question text, choices, correct answer, and existing explanation in plain text.

```text
# Batch 01 (20 questions)

=== category01_q004 ===
Question: Among the techniques used by Yujiro Hanma,
          select the most appropriate term for the
          phenomenon where his back muscles bulge
          into the shape of a demon's face.
Choices:
  A: Shaori (Xiao Lee)
  B: Cord Cut
  C: Mach Punch
  D: The Demon Back
Answer: D
Explanation: This question tests understanding of Yujiro Hanma's "Demon Back"...
```

## Generation: direct generation by Claude Code

I fed Claude Code the batch input files, presented the 3 hand-crafted samples as quality benchmarks, and had it generate JSON in the same format.

The quality criteria were explicit.

- `correctSummary`: Start with "The correct answer is {X}.", 2-3 sentences, within 200 characters, no OCR artifacts
- `contrastTable`: Unique explanation for each choice, with judgment label, within 150 characters
- `keyPhrases`: 3-6 technical terms, only exam-relevant ones
- `relatedConcepts`: Study hint or `null`

I processed the 21 batches across several sessions, completing everything in about 5.5 hours.

## Post-processing: normalization and validation

The JSON that Claude Code output drifted slightly in format across sessions. Key name inconsistencies in `contrastTable` appeared in 96 questions and required separate fixes. Another 7 questions had corrupted choices. A validation script detected and fixed these issues.

In the end, 52 Python tests and 542 Swift tests all passed.

## Numbers

| Item | Value |
|:---|:---|
| Questions re-generated | 397 |
| Batches | 21 (20 per batch, final batch had 8) |
| Diff in questions.json | +33,073 lines / -439 lines |
| contrastTable normalization | 96 questions |
| Corrupted choice fixes | 7 questions |
| Additional cost | **$0** (within Max plan flat rate) |

# Before / After

Here's how quality changed between regex extraction and direct Claude Code generation. The actual exam content is anonymized, but notice the structural differences.

**Before (regex extraction):**

```json
{
  "correctSummary": "The correct answer is C. Meanwhile, 'Shaori (Xiao Lee)' refers to a specific martial arts...",
  "contrastTable": [
    {
      "choice": "A",
      "judgment": "Incorrect",
      "point": "At present, all fighters oper ating in the underground arena are..."
    }
  ],
  "keyPhrases": ["Shaori", "Demon Back", "America", "Yujiro Hanma"]
}
```

An OCR space remains (`oper ating`), an exam-irrelevant term "America" leaked into `keyPhrases`, and `correctSummary` trails off mid-sentence.

**After (direct Claude Code generation):**

```json
{
  "correctSummary": "The correct answer is C. Shaori (Xiao Lee) is a Chinese martial arts technique that neutralizes the impact of strikes by relaxing all joints in the body.",
  "contrastTable": [
    {
      "choice": "A",
      "judgment": "Incorrect",
      "point": "Grip strength is not the distinguishing criterion between Shaori and the Demon Back."
    }
  ],
  "keyPhrases": ["Shaori", "Demon Back", "Relaxation", "Chinese martial arts", "Yujiro Hanma"]
}
```

OCR artifacts are gone, each choice has a unique educational explanation, and `keyPhrases` contains only exam-relevant terms.

One more example.

**Before:**
> correctSummary: "The correct answer is D. It is a search from infinitely many possibilities, and it is extremely difficult for the strongest creature on earth to do the same thing."

**After:**
> correctSummary: "The correct answer is D. Dorian's prison break illustrates the fundamental difficulty of neutralizing all forms of restraint and escaping."

The "Before" version has a vague "it" with no clear referent and leftover OCR issues. The "After" version leads with a concept definition and explains it precisely in one sentence.

# The importance of the "try it yourself first" phase

This experience revealed a practical workflow for LLM-based data generation.

**Don't jump straight to writing an API script. Prototype with Claude Code first.**

When you prototype a few dozen items with Claude Code (or a chat interface like ChatGPT), you establish:

1. **Quality benchmarks** — You get concrete examples of what "good data" looks like
2. **Prompt patterns** — You learn what instructions produce the quality you expect
3. **Edge case awareness** — You discover pattern-specific challenges (diagram-reference questions, fill-in-the-blank questions, etc.)

The quality of your prompts is fundamentally different when you write an API script with these in hand versus without them.

And there's another point. **For personal projects, the prototyping phase can take you all the way to the finish line.**

| | Claude Code direct generation | API script |
|:---|:---|:---|
| Best for | Personal / one-off | Team / re-runs / CI/CD |
| Reproducibility | Low (conversation-dependent) | High (persisted as code) |
| Cost | Within Max plan flat rate | Pay-per-use |
| Prompt management | Implicit | Version-controlled |
| Quality verification | Immediate feedback | Check after script execution |
| Startup speed | Fast (start by talking) | Slow (requires implementation) |

For a personal project with one-time generation, direct Claude Code generation is enough. If you need team reuse, CI/CD integration, or version control — take the quality benchmarks and prompts from your prototyping phase and port them to an API script.

**"Direct generation vs. API" isn't either-or. Always start with the prototyping phase.**

# Conclusion: the role of human intuition in working with LLMs

Let me recap the full arc.

1. Regex bulk-generated 397 questions — quality collapse
2. Claude Code proposed 3 improvement plans — all "external approaches"
3. Human intervened with "just generate them yourself" — reached the optimal solution
4. Additional cost $0, completed in 5.5 hours

Claude Code is capable, but it sometimes doesn't know how to deploy its own abilities. It proposes along the "regex then API" thinking pattern, so the option of "becoming the data generation engine itself" falls through the cracks.

Getting the most out of AI tools means spotting the tool's blind spots. The optimal solution can hide among the options Claude Code doesn't propose. The intuition to ask "Wait, can't you just do this yourself?" — that still belongs to the human side.

:::message
**Timeline (2026-02-11)**
- 08:51 — Initial implementation of structured explanation UI (3 hand-crafted samples)
- 09:14 — Regex script populates data for all 400 questions
- 11:14 — Claude Code re-generates 397 questions with major quality improvement
- 14:28 — contrastTable key name inconsistencies normalized (96 questions fixed)
:::

---

:::details EnhancedExplanation data model (Swift)
```swift
/// Per-choice judgment and explanation entry
public struct ContrastEntry: Codable, Equatable, Sendable {
    public let choice: String      // "A", "B", "C", "D"
    public let judgment: String    // "Correct", "Incorrect", etc.
    public let point: String       // Explanation text (≤150 chars)
}

/// Structured explanation data — 4-layer architecture
public struct EnhancedExplanation: Codable, Equatable, Sendable {
    public let correctSummary: String        // Layer 1: Answer summary (≤200 chars)
    public let contrastTable: [ContrastEntry] // Layer 2: Per-choice judgment + explanation
    public let keyPhrases: [String]          // Layer 3: 3-6 technical terms
    public let relatedConcepts: String?      // Layer 4: Related concepts (optional)
}
```
:::

:::details Batch generation workflow overview
```
397 questions (excluding the 3 hand-crafted ones)
  ↓ prepare_enhanced_batches.py
21 batch input files (batch_01.txt through batch_21.txt)
  ↓ Claude Code reads 20 questions at a time → generates JSON
21 batch output files (batch_01_output.json through batch_21_output.json)
  ↓ Normalize and merge 3 JSON format variants
Integrated into questions.json
  ↓ validate_enhanced.py
Quality validation (4-layer check) → all tests passed
```
:::
