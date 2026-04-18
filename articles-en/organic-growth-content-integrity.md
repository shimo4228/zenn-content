---
title: "Organic Growth and Content Integrity in an AI Writing Team"
emoji: "🌱"
type: "idea"
topics: ["claudecode", "ai", "writing", "design"]
published: true
published_at: 2026-04-18 07:00
tags: discuss, ai, claudecode, writing
description: "When AI agent components grow organically, they optimize locally and contradict globally. A design principle resolved 32 contradictions without throwing everything away."
---

In a [previous article](https://zenn.dev/shimo4228/articles/claude-code-zenn-writing-env), I wrote that "the environment gets a little smarter with each problem." Building a writing environment with Claude Code—turning problems into skills, scripts, and agents—was a fresh experience.

Two months later, the cycle kept running. Agents grew to 5, skills to 11. I wrote 42 articles in that environment.

Then I ran an audit and found 32 contradictions. The parts that were supposed to be smart were saying different things to each other.

## The System That Grew

Over 63 days, the `.claude/` directory grew into this structure:

```text
.claude/
├── agents/ (5)        # editor, essay-reviewer, fact-checker, zenn-drafter, devto-translator
├── skills/ (11)       # writing-team, zenn-writer, publish-article, schedule-publish, ...
├── refs/ (3)          # writing-standards, translation-rules, schedule-schema
└── rules/ (1)         # content-integrity

scripts/
├── publish.py          # Dev.to cross-post
├── scheduled_publish.py # Scheduled publishing
└── tests/ (8 files)    # 147 tests, 86% coverage
```

When writing a single article, the system works like this:

1. **Writing**: The zenn-writer skill provides tone and style guidelines. The zenn-drafter agent can handle first drafts
2. **Review**: editor (structure, code quality) and essay-reviewer (logic, tone) evaluate the article from their respective angles. fact-checker verifies factual claims
3. **Publishing**: The publish-article skill presents a pre-publication checklist, and schedule-publish determines posting timing
4. **Cross-posting**: The devto-translator agent translates the Japanese article into English and posts it to Dev.to. publish.py handles the API-level cross-posting

Each component carries its own set of rules. zenn-writer has a title character limit. editor has a banned list for AI slop (hollow boilerplate phrases). devto-translator has translation style rules. Each one embeds "the best judgment for its own scope."

None of this was planned from the start. It accumulated through cycles of writing articles, hitting problems, and systematizing solutions. The growth pattern I described in the previous article kept going for two straight months.

## 32 Contradictions Found at Once

It started with a casual thought: "I should reorganize the writing team." Before building a new orchestrator, I wanted to understand the current state, so I used Claude Code's sub-agent feature to run three audits in parallel: style/tone audit, translation/publishing flow audit, and gap analysis.

The results were unexpected. 32 problems surfaced at once.

Take the title character limit. zenn-writer said "50 characters max," zenn-drafter said "60 characters max," and zenn-format said "50-60 characters." Three components, each saying something slightly different.

The AI slop banned list was worse. editor, zenn-drafter, and zenn-writer each had their own slightly different copy. One list banned "画期的" (groundbreaking) while another didn't include it at all.

Three components claimed ownership of translation: the translate-article skill, the devto-translator agent, and the publish-article skill. The most telling case was translate-article—its own description said "for end-to-end workflows, devto-translator agent is recommended." It was negating its own reason to exist.

Why does this happen? Incremental construction produces local optima. Each component is optimized for "the context at the time it was created." A skill built in February reflects February's judgment; an agent added in March reflects March's knowledge. But no mechanism existed to guarantee overall consistency. The same structure as "technical debt" in software development had emerged in the knowledge layer of AI agents.

Here are the audit results in numbers:

| Metric | Before (pre-audit) | After (redesign) |
|--------|--------------------|--------------------|
| Contradicting rules | 12 (char limits, AI slop lists, tone rules, etc.) | 0 (consolidated into refs/) |
| Duplicated rule locations | 8 (AI slop copy-pasted in 3 places, etc.) | 1 each |
| Components with ambiguous ownership | 4 (3 claiming translation, etc.) | 1 owner each |
| Shared references (refs/) | 0 | 3 (writing-standards, translation-rules, schedule-schema) |
| ADRs (Architecture Decision Records) | 0 | 2 (Content Integrity, Orchestration) |

Of the 32 problems, 12 contradictions, 8 duplications, and 4 ownership ambiguities formed the core. The rest were derivative inconsistencies stemming from these.

## A Tool's Existence Creates Bias

Among the 32 issues, the one that made me think the most was the catchify skill.

catchify was a skill that rewrote article openings to be more dramatic and headings to be more emotional. I built it in February as "a tool to make things catchy" and actually used it on several articles.

The problem was that merely having this tool created pressure to use it. After finishing an article honestly, not running it through catchify felt like cutting corners. The tool's existence itself was biasing the author's judgment.

This isn't just a software problem—it applies to organizations and workflows too. Introduce a code review tool and suddenly every PR "needs" a review. Add a step to the CI pipeline and removing that step meets resistance. Tools don't just "add options"—they raise the cost of choosing not to use them.

I abolished catchify. No tool, no bias.

## Content Integrity — A Principle That Resolved Contradictions

Abolishing catchify was treating a symptom. What I needed was a criterion for "what's okay to automate."

That's where the Content Integrity principle was born. The trigger was a feeling: "I want to put my thoughts out honestly." But I didn't want to reject SEO optimization entirely. Choosing better words for titles and optimizing tags increases the chance readers find the article without changing its content. That seemed reasonable.

The problem was optimization that changes the content itself. Rewriting the opening "for search snippets." Making headings "emotional." These are processing the author's thinking for the sake of distribution.

From here, the Content / Distribution boundary became clear:

| Layer | Examples | Principle |
|-------|----------|-----------|
| **Content** | Structure, argument, opening, headings | Follow the author's thinking. Don't change for optimization |
| **Distribution** | Title word choice, tags, emoji, posting timing | Optimize without changing content |

I recorded this principle as an ADR (Architecture Decision Record) and set it up as a rule file that loads automatically every session.

As a result, catchify was abolished. seo-optimizer had its opening rewrite feature removed, limited to title, tags, and emoji only. schedule-publish's scoring axis was renamed from "Search Magnet" to "Discoverability (can interested readers find it?)."

Most of the 32 contradictions became clear-cut decisions when held against this principle. Instead of individually squashing them through refactoring, the principle provided a decision framework that enabled consistent redesign.

## Structural Patterns for Maintaining Coherence

A principle alone can't prevent contradictions from recurring. The structure needed to change too.

**refs/ consolidation** — AI slop lists, tone rules, translation rules, and schedule schemas were consolidated into single locations (`.claude/refs/`), with each component holding only reference pointers. The AI slop list that was copy-pasted in 3 places became 1 source of truth + 3 references. Update the source and everything follows.

**ADR-first** — Record decisions before changing the system. For Content Integrity, I first wrote ADR-0001 with the reasoning and impact scope, then proceeded to abolish catchify and modify seo-optimizer. If the reasoning disappears, six months later no one knows "why catchify doesn't exist."

**Single ownership per concern** — Translation belongs to devto-translator only. SEO belongs to seo-optimizer only. One concern, one owner. A component like translate-article that "negates its own existence" is a sign of overlapping responsibilities.

## Interruptions That Improved the Design

What was interesting was the redesign process itself.

The redesign happened through dialogue with Claude Code. I communicated the direction, and Claude Code planned and executed. It started with a plan to "build an orchestrator," but before implementation began, I interrupted three times.

> "If the components contradict or duplicate each other, it won't be organic, will it?"

Without this, I would have layered an orchestrator on top of existing contradictions.

> "Shouldn't we write ADRs first?"

Without this, the reasoning behind decisions would have been lost.

> "SEO itself is fine. It's changing the content that's the problem."

Without this, I might have abolished SEO optimization entirely.

There's a lot of attention on having AI agents plan and execute autonomously. But in this case at least, human interruptions improved the design quality. Autonomous execution is efficient, but reassessing premises comes from outside.

## Conclusion

The previous article concluded that "the environment gets a little smarter with each problem."

Two months later, I realized that smart parts contradict each other. Components optimized incrementally don't maintain coherence as a whole. This isn't limited to AI agent knowledge layers—I believe it's a fate shared by every organically growing system.

And what resolved those contradictions wasn't individual refactoring, but a principle called Content Integrity. "Content is determined by the author's thinking. Distribution optimizes without changing content." This single statement became the criterion for deciding which of the 32 contradictions to keep and which to abolish.

Organic growth requires periodic audits and a principle to anchor decisions.
