---
title: "Never Trust LLM Output — 6 Defenses from Building a PDF-to-Anki CLI"
emoji: "🃏"
type: "tech"
topics: ["claude", "anki", "python", "llm"]
published: true
---

## Introduction

In [the previous article](https://qiita.com/shimo4228/items/06d48f19bde5e6401a85), I wrote about my first 10 days of real development in an Everything Claude Code (ECC) environment. It was the story of a beginner who didn't even know git, learning development by running the PDCA cycle over and over.

This time, I'll talk about **pdf2anki** — a tool I built during the second half of those 10 days.

### The Problem Was Content, Not the App

To study for the G-Kentei exam, I built a quiz app based on spaced repetition. A web version in Python/Streamlit, an iOS version in Swift/SwiftUI. I implemented them with TDD in the ECC environment, recording design decisions in ADRs, and had working software in two weeks.

After it was done, I realized: **I had reinvented Anki.**

There's no point spending two weeks rebuilding something that Anki has refined over 20+ years. But during development, the real bottleneck became clear. It wasn't the app — it was the **content**.

In the iOS version, I implemented an algorithm that extracted 410 Q&A pairs from PDF text using regex and an LLM. But accuracy was unstable due to formatting inconsistencies and chapter structure mismatches. Things like "Chapter 1" vs. "Chapter1" (a single space difference) would break the matching.

If I had a tool that could "automatically generate high-quality Anki cards from any text," I could leave the app itself to Anki.

That's how [pdf2anki](https://github.com/shimo4228/pdf2anki) was born.

```bash
$ pdf2anki convert textbook.pdf -o cards.tsv
```

It's a CLI tool that takes PDF, text, or Markdown as input and outputs flashcards (TSV/JSON) using the Claude API.

In this article, I'll describe the **6 pitfalls** I hit while building pdf2anki, and the defenses I put in place. So that anyone starting to use the Claude API can avoid stepping in the same holes.

The "keep asking questions relentlessly" approach from the previous article hasn't changed. I kept asking Claude Code "Why this approach?" and "Are there alternatives?" The design decisions that emerged from those Q&A exchanges — I'll lay them out as honestly as I can.

---

## 1. Design for Broken JSON — Because LLM Output Will Break

### What Happened

When you ask the Claude API to generate cards, the returned JSON sometimes can't be parsed as-is.

Even if the prompt says "return only JSON," Claude sometimes wraps it in ` ```json ``` ` markdown fences. Explanatory text appears in the middle of arrays. Extra commas, missing closing brackets.

LLM output is probabilistic. Instructions like "return it this way" come with no 100% guarantee.

### The Failed Approach

Initially, I tried parsing the entire response with `json.loads()` and retrying the whole thing on failure. Even if just 1 card out of 10 had a broken format, all 10 would be regenerated. API costs ballooned unnecessarily.

### Defense: Validate Per Card and Accept Partial Success

```python
for i, item in enumerate(data):
    try:
        card = AnkiCard.model_validate(item)
        cards.append(card)
    except (ValidationError, TypeError) as e:
        logger.warning("Skipping invalid card at index %d: %s", i, e)
```

If 1 out of 10 is broken, we save the other 9.

**Not "all or nothing" but "accept partial success."** I think this is a principle that applies to any tool that integrates LLMs.

JSON wrapping (` ```json ``` `) gets stripped with regex before parsing. It's unglamorous preprocessing, but these small defensive layers are what keep LLM integrations stable.

:::message
**Takeaway:** Write LLM output parsing with the assumption that it will break. Instead of retrying the whole batch, skip individual failures and log them for resilience.
:::

---

## 2. LLM-Generated Card Quality Is All Over the Place

### What Happened

Even when JSON parses correctly, content quality is not guaranteed.

Examples of problem cards that actually appeared:

- Front side says only "Please explain." Explain what?
- Back side exceeds 500 characters. It's a report, not a card.
- A single card crams in 3 different concepts. Anki cards should be one concept per card.
- A list-type question is output in Q&A format. It should be a cloze deletion.

"We used an LLM, so it's fine" was a dangerous assumption.

### The Failed Approach

I first tried having the LLM re-evaluate all cards. Since both generation and evaluation hit the API, costs simply doubled. 200 API calls for every 100 cards. Not realistic.

### Defense: A 3-Layer Pipeline for Quality Assurance

**Layer 1 (Code-based, no LLM): Heuristic Scoring**

Score each card 0–1 across 6 axes, with a weighted sum threshold of 0.90 to pass. No LLM calls.

| Axis | Weight | What It Checks |
|---|---|---|
| Front quality | 25% | 10–200 characters, presence of question mark |
| Back quality | 25% | 5–200 characters, conciseness |
| Card type fit | 15% | Is list content incorrectly formatted as Q&A? |
| Bloom level | 10% | Does the cognitive level match the content? |
| Tag quality | 10% | Are hierarchical tags present? |
| Atomicity | 15% | One concept per card? |

The atomicity check was interesting. It splits the back side by sentence-ending punctuation and flags cards with too many sentences as "multiple concepts mixed together."

```python
# 3+ sentences on the back → suspected multi-concept
sentences = [s for s in _SENTENCE_SPLIT_RE.split(back) if s.strip()]
if len(sentences) >= 3:
    score = max(0.3, 1.0 - len(sentences) * 0.15)

# Conjunctions like "また、" (moreover) / "さらに" (furthermore) → extra penalty
if _MULTI_CONCEPT_RE.search(back):
    score = max(0.2, score - 0.15)
```

When conjunctions like "moreover" or "furthermore" appear, the card is likely overloaded with information. Cards that a human would look at and think "this should be split" — the code can detect them.

**Layer 2 (LLM-based): Only cards scoring below 0.90 go to Claude for critique**

The critique result is one of three options: `improve` (rewrite), `split` (divide), or `remove` (delete). Maximum 2 rounds.

The key point: **not every card hits the LLM.** Cards scoring 0.90 or above pass through Layer 1 untouched. In practice, 60–70% of generated cards passed Layer 1. Only 30–40% needed LLM critique.

**Layer 3 (Code-based, no LLM): Duplicate Detection**

Detects duplicates using Jaccard similarity on character bigrams. If front-side similarity exceeds 0.7, a duplicate flag is raised.

Same idea as the TDD approach from ECC that I described in the previous article. Just as you write tests first, you define quality criteria first. Without criteria, you end up with "it feels better" and nothing more.

:::message
**Takeaway:** Separate "what LLMs can judge" from "what code can judge." Using an LLM for judgments that code can handle isn't a precision issue — it's a cost issue.
:::

---

## 3. API Costs Are Scary When You Can't See Them

### What Happened

The Claude API is pay-per-use. Sonnet costs $3/M tokens for input, $15/M tokens for output.

How much does processing a 100-page PDF cost? **You don't know until you run it.**

During early testing, I accidentally processed a long PDF and burned through nearly $2. For a personal learning tool, that hurts.

### Three Defenses

**1. Pre-execution cost estimates**

The `preview` command shows an estimate without hitting the API.

```bash
$ pdf2anki preview textbook.pdf
Estimated cost: $0.42 (Sonnet) / $0.11 (Haiku)
Sections: 12 | Chunks: 8 | Tokens: ~45,000
```

The user decides "that's acceptable" before running `convert`.

**2. budget_limit to prevent runaway costs**

`CostTracker` has a budget cap (default $1.00), checking cumulative cost with every API call. If it's exceeded, processing stops.

```python
@dataclass(frozen=True, slots=True)
class CostTracker:
    budget_limit: float = 1.00
    records: tuple[CostRecord, ...] = ()
```

Note `frozen=True` — making it immutable. The "immutability principle" I mentioned in the previous article pays off here. Each API call returns a new `CostTracker` instance. No risk of values being mutated mid-process, so "how much have we spent so far" is always accurate.

**3. Automatic model selection based on text volume**

Short texts (under 10,000 characters, fewer than 30 cards) route to Haiku at roughly 1/4 the cost. Longer texts go to Sonnet.

```python
_SONNET_TEXT_THRESHOLD = 10_000   # character count
_SONNET_CARD_THRESHOLD = 30      # card count
```

A simple threshold branch, but it drastically reduces processing costs for short texts.

:::message
**Takeaway:** Any tool using a pay-per-use API needs three things: "pre-execution estimates," "runtime caps," and "model routing." Protecting the user's wallet is the developer's responsibility.
:::

---

## 4. Split a Long PDF Wrong and You Destroy Card Context

### What Happened

Claude's input token limit is roughly 200K, but throwing a massive amount of text at once degrades card quality. Splitting is necessary.

### The Failed Approach

Initially, I split text by equal character counts. Naturally, this cut right through the middle of chapters.

Cards generated from a chunk containing "the second half of Chapter 3" mixed with "the first half of Chapter 4" had broken context. Terms defined in one chapter got conflated with concepts from another.

### Defense: Section-Based Splitting + Breadcrumbs for Context

I switched to splitting logically by Markdown headings (`#`, `##`, `###`).

Each section gets a **breadcrumb** — like the "Home > Products > iPhone" navigation on websites, showing where you are in the overall hierarchy.

```
breadcrumb: "Main Body > Chapter 1: Meaning of the Title > 1.1 Etymology"
```

Claude reads this breadcrumb and understands "we're discussing etymology in Chapter 1 right now." Just having this context at the top of each chunk made the generated cards significantly more accurate.

The heading hierarchy is tracked with a `heading_stack` dictionary. When an H2 appears, all H3 entries below it are cleared.

```python
heading_stack: dict[int, str] = {}
# H2 appears → clear H3
keys_to_remove = [k for k in heading_stack if k >= level]
```

If a single section exceeds 30,000 characters, it gets sub-divided at paragraph boundaries, with `(cont.)` appended to the heading to indicate continuation.

### Japanese Text Gotchas

Two of them.

First: handling text with no Markdown headings. For Japanese books, I added fallback detection for patterns like "第一章" (Chapter One), "（1）", and "一、" (traditional numbering).

Second: token estimation errors. The constant `CHARS_PER_TOKEN = 4` is based on English. Japanese runs about 2–3 characters per token, so cost estimates end up at roughly half the actual amount. This is a known, unfixed issue. For Japanese text, the coefficient should be adjusted to around 2.5.

:::message
**Takeaway:** When feeding long text to an LLM, split at "semantic boundaries." Mechanical character-count splitting destroys context. Attaching "where are we in the document" metadata to each chunk significantly improves output quality.
:::

---

## 5. Image Support Is a Fight Against Cost

### What Happened

PDFs contain not just text but also figures and charts.

The Claude API can accept **images as input (Vision)**, not just text. You send a photo or diagram, and Claude understands "what's in this image" and responds accordingly. Using this, I could generate cards from textbook figures and tables too.

"Why not just throw every page in as an image via Vision?" I thought.

Then I calculated the cost and snapped out of it.

Image token cost is `(width × height) ÷ 750`. Converting all 100 pages to images means roughly 150K tokens for images alone. Combined with text, that's 300K tokens — about $1. Text-only would be around $0.15. **A 7x cost difference.**

### Defense: Three Thresholds to Control Image Processing

**1. Image coverage threshold: 20%**

Using pymupdf, I calculate the image area on each page. Only pages where images occupy 20% or more of the page area go to Vision. Text-heavy pages are handled fine with text extraction.

**2. DPI: Fixed at 150**

Vision's constraints are 1568px on the long edge, 1.15 megapixels max.

- 300 DPI: Sharp but doubles token count. Over 3,000 tokens per image.
- 72 DPI: Cheap but text in figures becomes unreadable.
- **150 DPI: Minimum resolution where text remains legible. About 1,500 tokens per image.**

**3. Maximum 5 images per page**

5 images × 1,500 tokens = 7,500 tokens. Combined with budget_limit, no runaway costs.

These three compromises kept Vision-enabled processing costs to 1.5–2x text-only. Not 7x.

:::message
**Takeaway:** Vision is capable but expensive. Resist the temptation of "just throw everything in as images." Process what text extraction can handle as text. Reserve images for only the pages that truly need them.
:::

---

## 6. If You Can't Measure Prompt Changes, Improvement Is Gambling

### What Happened

When you rewrite a prompt, you can't tell whether card quality went up or down. "It feels better" isn't reassuring. LLM output is non-deterministic — the same prompt produces different results every time.

### Defense: Automated Quality Testing via Keyword Matching Against Expected Cards

In LLM development, automated output quality evaluation is called **Eval**.

In pdf2anki, I defined expected outputs in YAML — "this text should produce cards like these" — and compared them against actual output.

```yaml
- id: "dl-001"
  text: |
    過学習（オーバーフィッティング）とは、訓練データに対して
    過度に適合し、未知のデータに対する汎化性能が低下する現象である。
    対策としてドロップアウト、早期終了、データ拡張などがある。
  expected_cards:
    - front_keywords: ["過学習", "何"]
      back_keywords: ["訓練データ", "汎化性能", "低下"]
      card_type: qa
    - front_keywords: ["過学習", "対策"]
      back_keywords: ["ドロップアウト", "早期終了", "データ拡張"]
      card_type: qa
```

It calculates match rates based on whether generated cards contain the expected keywords, then outputs Recall, Precision, and F1 scores.

```bash
$ pdf2anki eval --dataset evals/dataset.yaml
Recall: 0.78 | Precision: 0.85 | F1: 0.81
```

Keyword matching isn't perfect. It can't recognize that "neural network" and "神経回路網" mean the same thing.

But what matters is detecting **regression** — whether a prompt change made things worse than before. Not perfect semantic understanding. Running `pdf2anki eval` after every prompt change and checking that F1 hasn't dropped — that alone turns improvement from gambling into engineering.

Same lesson I learned from TDD in ECC. With tests, you can refactor with confidence. With Eval, you can rewrite prompts with confidence.

:::message
**Takeaway:** Manage LLM output quality with "test cases." The automated evaluation doesn't need to be perfect. Just being able to "detect regression" dramatically changes the productivity of prompt improvement.
:::

---

## Conclusion

Building pdf2anki was a continuous series of compromises.

| What I Wanted | Reality | Compromise |
|---|---|---|
| Get perfect JSON from the LLM | Output breaks | Skip individual failures, accept partial success |
| Evaluate all cards with the LLM | Costs double | Heuristics filter 60–70% |
| Use it without worrying about cost | Pay-per-use is scary | Estimates + caps + model routing |
| Split text evenly | Context breaks | Section splitting + breadcrumbs |
| Throw every page in as an image | 7x the cost | Coverage threshold + DPI + image limits |
| Judge prompt improvements by feel | Can't detect regression | Keyword-match Eval |

None of these are "ideal designs." They're all products of negotiating with reality.

One decision criterion carried me through the entire development process: **"If I don't do this, what else could I accomplish in the same amount of time?"**

Midway through, I considered "shouldn't I add OpenAI support too?" I had $10 in credits left. Implementation estimate: 1,000 lines, 10 hours. That works out to $1/hour to recoup $10. In those same 10 hours, I built image card generation, a TUI, and the Eval framework instead.

The ECC PDCA cycle from the previous article was running here too.

- **Plan**: Keep asking Claude Code "Why this approach?" to understand the design rationale
- **Do**: Write tests first with TDD, then implement
- **Check**: Measure prompt quality with Eval, verify card quality with heuristics
- **Act**: Record in ADRs "why we dropped OpenAI support" and "why the image threshold is 20%"

The Claude API is a capable tool. But the moment you think "just hit the API and it's solved," costs balloon, quality becomes unstable, and debugging gets painful. What unlocks the API's potential is the defensive design you build around it.

I hope this article is useful to anyone walking the same path.

pdf2anki is [open source on GitHub](https://github.com/shimo4228/pdf2anki).
