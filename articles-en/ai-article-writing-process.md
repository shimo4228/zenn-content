---
title: "What Actually Happens When You Write an Article with AI — 20 Dialogues, 2 Hours, a Completely Different Core"
published: true
description: "AI-generated articles aren't one-click magic. Here's the full 2-hour process of writing one article with Claude Code — 20+ exchanges, 3 title changes, and a thesis that transformed entirely."
tags: "ai, writing, claudecode, productivity"
topics:
  - ai
  - claudecode
  - writing
  - productivity
---

What do you picture when you hear "AI-generated article"? Type a prompt, press a button, article comes out. Something like that, right?

Today, I wrote one technical article with Claude Code. It took 2 hours. During that time, we went through over 20 exchanges. The title changed 3 times. The core thesis of the article became something entirely different.

This article lays bare the entire production process. To show what an "AI-generated article" actually looks like.

## What I wrote

[Do Autonomous Agents Really Need an Orchestration Layer?](https://zenn.dev/shimo4228/articles/symbiotic-agent-architecture)

It's an article about the design philosophy of an autonomous agent framework I built. The fourth in a series. It poses the question "Do autonomous agents need an orchestration layer?" and develops a design argument from the fact that my agent actually runs without one.

## Why write articles with AI?

Let me be upfront about the motivation.

I built this agent together with Claude Code. Design discussions, code reviews, debugging feedback — there was plenty of dialogue during implementation. We ended up with something that works. But there was never an opportunity to systematically articulate *why* this design works during the implementation itself.

Writing an article creates that opportunity. I read Claude Code's first draft and react — "that's not right," "oh, so that's what it meant." Through that process, the structure of what we built together becomes visible.

In other words, writing articles isn't just about being read. **It's about crystallizing my implementation experience into knowledge.** Taking the implementation knowledge that AI holds and making it my own through the article-writing process. The fact that I've reached the point where I can build autonomous agents from scratch over the past month and a half owes a lot to this accumulated practice.

## Before writing: context collection

I don't just say "write something." First, I run a command called `/collect-context`.

This is a custom Claude Code command I built. It automatically collects the current session's context along with related past context and structures it into a single file. Specifically, it gathers:

- **Current session**: What was done, before/after data, code examples, technical discoveries, reasoning behind decisions
- **Past sessions**: Related work records and insights from previous sessions (searched via MCP)
- **Project knowledge**: Auto-memory, differentiation from existing articles, learned skills

You can pass a theme as a keyword, or omit it and let it auto-detect from the session content. For this article, the agent's README, the previous three articles in the series, and the design decisions made during the session with their rationale were all consolidated into a single draft file. This became the raw material for the first draft.

The quality difference between saying "write something" to an AI versus handing it structured context and saying "write based on this" is night and day.

## The full production flow

Here's how this article was made:

```text
1. /collect-context gathers context → generates draft file
2. Claude Code generates first draft from the draft file
3. editor agent (a separate agent within Claude Code) reviews the first draft
4. I read it and revise through dialogue (← this is the 2-hour part)
5. editor agent reviews again
6. I do a final check, set published: true → git push
```

The key point is that editor agent reviews bracket my own review. The editor agent checks stylistic consistency, AI slop detection, and logical coherence. It catches mechanically detectable problems so I can focus on "does this match my actual experience?"

The following sections show what actually happened in step 4.

## How the title evolved

The final title was "Do Autonomous Agents Really Need an Orchestration Layer?" It didn't start there.

```text
First draft: "Agents Parasitize the Orchestrator and Survive by Staying Thin" 🦠
Revision 1:  "When I Ditched the Orchestration Layer, 6,000 Lines Was Enough" 🤝
Final:       "Do Autonomous Agents Really Need an Orchestration Layer?" 🤝
```

The moment I saw the first draft title, I said "Parasitize? No. Absolutely not." Claude Code meant "parasitize" as an interesting metaphor, but to a reader it looks aggressive. Symbiosis is fine. Parasitism is not.

For the second version — "6,000 lines was enough" — I shot back "Is 6,000 lines a lot or a little?" A number without context doesn't work as a title.

What we finally landed on was not an assertion but a **question**. "Is an orchestration layer necessary?" — since I wasn't sure of the answer myself, asking the question felt honest.

## The moment the core thesis changed

This is the most important part.

The core of Claude Code's first draft was "**we delegated orchestration externally**." The story was that my agent's orchestration layer had been delegated to Claude Code.

We ran with that for two hours. I was editing along that axis for a while.

The turning point was when I offhandedly said this:

> In production, Claude Code doesn't even appear. It just runs on its own via launchd.

That broke the entire logical structure. The article said "delegated," but in production, Claude Code does nothing. During development I use natural language to ask Claude Code for things, and in production a scheduler handles automatic execution. **There's no one to delegate to.**

In other words, the orchestration layer wasn't "delegated" externally — it turned out that **during development, conversation was enough, and in production, it simply wasn't needed**.

This discovery couldn't have come from Claude Code. Claude Code was perfectly capable of writing a plausible article around the "delegation" framing. But I'm the only one who knows how my agent actually runs.

## Where the metaphor came from

The final article is built around the metaphor of "autonomous agents arriving and departing from a port." Ocean-going ships that do everything at sea (OpenClaw) versus ships that use a port as home base and sail out from there (Contemplative Agent).

Claude Code didn't come up with this either. I said it:

> Isn't the right model for autonomous agents to arrive and depart from the port of Claude Code?

Claude Code wove this metaphor into the article's structure — section headings, the contrast with OpenClaw, connecting launchd as "scheduled departures from port." The AI's structural ability is superior. But the raw metaphor came from the human.

What made it even better was that right after I said it, I realized: "launchd is literally departures from port." macOS's launchd (the scheduler) literally "launches" (sets sail). The metaphor and the implementation connected by accident.

## Deleting "correct"

AI loves assertions.

The first draft was full of expressions like these:

```text
"The design was correct"
"The correct design has one more major advantage"
"Host-specific coupling was truly zero"
"An emergence of unintended generality"
```

My response was "You don't need to insist the design is correct. We don't know that yet."

After revision:

```text
"At least the direction doesn't seem wrong"
"Whether it'll work out is still unclear"
"In principle it should work"
"Generality emerged as a result. It wasn't planned"
```

The latter felt closer to my actual experience.

AI tends to write assertively. Trimming that was the single most frequent edit I made.

## 5 things the AI got wrong

Here's a list of factual mismatches between what Claude Code wrote and reality:

**1. cron → launchd**
It wrote "cron" for macOS's scheduler. The actual tool is launchd. When AI writes from general knowledge, it drifts from individual environments.

**2. Who is "the operator"?**
It wrote "the operator conveys intent to Claude Code," and my reaction was "Who's the operator? Me?" Abstract terminology is less clear than just saying "I."

**3. Overestimating similarity between different tools**
It wrote that a design decision was "the same as" another tool's approach, but the architectures were actually different. Claude Code was overestimating surface-level similarities.

**4. The claim "we chose not to catalog"**
Claude Code wrote "the design decision not to catalog adapters," but I'd never even considered cataloging them. Framing something you never tried as a deliberate decision not to do it is dishonest.

**5. Describing code generation as "writing it yourself"**
It wrote "you don't need to write adapters yourself," but since I develop with Claude Code all the time, the very concept of "writing code yourself" doesn't quite apply.

Every one of these was a case of "sounds plausible but doesn't match reality." AI fills gaps with general knowledge, but it doesn't know the author's actual environment.

## A record of the editing dialogue

Here's a selection from the 2-hour conversation. This is what shaped the article.

| Dialogue | What changed |
|---------|-------------|
| "Parasitize? No. Absolutely not." | The entire metaphor shifted to symbiosis |
| "We're nowhere near an arrival point" | Deleted "the culmination of the series" |
| "You're comparing to LangChain but there's no way a personal project can match that" | Comparison tone changed to "copying them is impossible; I looked for a different path" |
| "The four axioms section doesn't belong in a technical article" | Entire section deleted |
| "The Cowork part doesn't convey why it's interesting" | Restructured chronologically |
| "You don't need to insist the design is correct. We don't know yet" | Full revision to exploratory tone |
| "launchd is literally departures from port" | Metaphor and implementation connected |
| "Memory consolidation is also scheduled — every day at 3 AM" | Added specific operational details |
| "It's not cron, is it?" | Factual error corrected |
| "Can't tell if 6,000 lines is a lot or a little" | Removed from title |

## The core of an article lives in the dialogue

AI has structural ability. It can write prose that passes linters. It can devise section headings. If you run an editor agent, it can point out improvements.

But there are things only the author can do. Feeling that "parasitize" is wrong. Saying "we don't know yet" honestly. Noticing that "launchd is literally departures from port." Knowing that "it's not cron" because you know your own environment.

The AI's first draft is raw material. The author reacts to it, dialogue accumulates, and the article takes shape.

## Writing articles with AI is understanding AI

"So basically you're just fixing AI's mistakes" — that's what it looks like. But that's not all it was.

The act of editing an AI-written manuscript is **the act of making visible what the AI was thinking during implementation**. When Claude Code wrote "orchestration was delegated," that was Claude Code's declaration of how it interpreted the design. I read that and realized "no, it wasn't delegation — it was unnecessary."

In other words, editing an article is the act of reading your collaborator's mind. Where does Claude Code over-generalize? Where does it leap to assertions? Where does it diverge from my actual environment? Knowing these things improves the precision of our next collaboration.

And in the process of understanding the AI's thinking, my own thinking gets organized too. The "arriving and departing from a port" metaphor didn't exist before I started writing the article. The conclusion that "an orchestration layer isn't needed" hadn't been articulated before writing either. The dialogue with AI acted as a catalyst, giving shape to unorganized thoughts inside me.

What looked like fixing mistakes was actually thinking together. At least for me. Things I couldn't have articulated on my own emerged in the form of reacting to the AI's first draft.

## The first draft takes minutes. The article takes 2 hours.

Generating the first draft took only a few minutes. From there, 2 hours of dialogue, 3 title changes, and the core thesis shifted from "delegated" to "unnecessary."

AI writes. The human reacts. The core emerges through dialogue. The phrase "AI-generated" alone doesn't capture this process. That's what I wanted to show.
