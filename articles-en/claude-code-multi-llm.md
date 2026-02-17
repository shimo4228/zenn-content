---
title: "Using Multiple LLMs with Claude Code — When to Reach for Gemini, ChatGPT, or NotebookLM"
emoji: "🤖"
type: "tech"
topics: ["claudecode", "ai", "gemini", "chatgpt"]
published: true
---

## Sometimes One LLM Isn't Enough

The first time I encountered the term ADR (Architecture Decision Record), I asked Claude Code: "What's an ADR?" The response was "Architecture Decision Record. It records important decisions." Technically correct, but I learned nothing.

Claude Code is a development-focused agent. It writes code, edits files, and runs tests. But when you ask it to explain a concept in depth, it tends to give terse answers because it's operating within a development-task context.

I use a 4-stage approach with four different LLMs.

## The 4-Stage Approach

### Stage 1: Ask Claude Code

Start by asking Claude Code about the term or concept that came up during development.

```text
me: "What's an ADR?"
Claude Code: "Architecture Decision Record. It records important decisions."
```

You get an answer scoped to the development context. For information directly tied to implementation, this is often sufficient.

### Stage 2: Ask Gemini / Standard Claude

When Claude Code's answer feels insufficient, ask Gemini or Claude (the standard chat version) the same question.

```text
me: "Explain ADR in a way a beginner would understand"
Gemini: "An ADR is a document that records the reasoning and
background behind important technical decisions in a project.
For example..."
```

You get more detailed explanations, concrete examples, and beginner-friendly breakdowns.

### Stage 3: Ask for an Analogy

When you still don't get it, try a different angle.

```text
me: "Explain TDD using an analogy from Baki the Grappler"
Claude (standard): "TDD is like first 'anticipating your opponent's
technique' and then 'working out a counter'..."
```

Mapping an abstract concept onto a domain you already know makes it concrete. The subject can be anything — manga, sports, cooking.

### Stage 4: Deep Research

When you want a thorough investigation, fire the same question at multiple LLMs in parallel.

Here is how I personally split them (as of February 2026):

| LLM | Why I use it | How I use it |
|-----|-------------|--------------|
| Claude Code | Practical implementation answers | "How should I use this in my project?" |
| Gemini | Detailed concept explanations | "Explain this for a beginner" |
| ChatGPT | Best practices | "What's the generally accepted approach?" |
| NotebookLM | Information synthesis | Feed multiple sources for cross-reference analysis |

## Using NotebookLM

I use NotebookLM specifically for "synthesizing multiple sources."

1. Copy Claude Code's answer
2. Copy Gemini's answer
3. Add relevant documentation URLs
4. Feed everything into NotebookLM

NotebookLM cross-references the sources and organizes contradictions and common points.

For example, when researching ADR templates, Claude Code said "5-section structure" and Gemini said "7-section structure." After feeding both into NotebookLM, it clarified: "The baseline is 5 sections; 7 sections is recommended for team workflows."

## Decision Flowchart

```text
A question comes up during development
  ↓
Ask Claude Code
  ↓ Answer is sufficient → Go back to development
  ↓ Answer is insufficient
Ask Gemini / Claude
  ↓ Understood → Go back to development
  ↓ Still unclear
Ask for an analogy
  ↓ Understood → Go back to development
  ↓ Want to go deeper
Deep research (multiple LLMs in parallel)
```

Most questions are resolved at stages 1-2. I only reach stages 3-4 when learning a concept for the first time.

## Takeaways

Since adopting this approach, the time I spend understanding new concepts has roughly halved. I used to push forward with a vague sense of "I sort of get it," only to hit walls later. Now I make sure I genuinely understand at stages 2-3 before returning to implementation, and rework has decreased.

- Claude Code excels at implementation-focused answers. Ask it first
- For conceptual understanding, supplement with Gemini or standard Claude
- Analogies are a breakthrough tool for understanding. Map concepts onto domains you know
- Use NotebookLM to synthesize multiple sources and resolve contradictions
- Decide in advance "which LLM to ask for what" so you don't waste time deliberating
