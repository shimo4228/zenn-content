---
title: "Kimi Killed 4 of Claude's Best Ideas — An AI Peer Review in Practice"
emoji: "🔄"
type: "idea"
topics: ["claudecode", "ai", "kimi", "llm"]
published: false
canonical_url: "https://zenn.dev/shimo4228/articles/ai-peer-review-methodology"
---

I had Claude (Opus 4.6) build a content strategy. Six title rewrites, five new article themes. Data-backed, logically airtight proposals. Then I handed them to Kimi K2.5. Four of the six titles got flagged, and one was outright rejected — "this would backfire, don't do it."

When you have one AI critique another AI's proposals, the scope of consideration widens. Perspectives that Claude alone would never have surfaced appeared, and assumptions I had unconsciously agreed with became visible.

## Background — Why I Ran a Buzz Analysis

I analyzed my portfolio of 21 articles (18 published, 3 drafts). Looking at the titles of published articles from a bird's-eye view, I noticed a heavy skew toward "descriptive" titles. Eleven of 18 articles followed the pattern "The story of how I did X" or "A record of doing Y" — 61% of my published work.

Meanwhile, Zenn's weekly trending articles showed "comprehensive guide" and "checklist" formats dominating the top spots. My portfolio had zero articles in either pattern. This wasn't a deliberate choice — I had unconsciously fallen into the "story of how I..." writing habit without realizing it.

## Claude's Analysis Process

Claude collected trend data using the Zenn API and web searches, then classified buzz-worthy titles into nine patterns based on all-time top 10 and weekly trending articles.

| # | Pattern | Example |
|---|---|---|
| 1 | Provocative / Declarative | "The real value of X isn't Y" |
| 2 | Comprehensive | "Complete guide to X", "Top N picks" |
| 3 | Checklist | "Things to check before doing X" |
| 4 | Numeric | "It got 9x slower", "In 0 lines" |
| 5 | Hypothetical / Result | "I tried X and Y happened" |
| 6 | Behind-the-scenes | "The inside story of X", "The full picture" |
| 7 | Flow-tracking | "A month-long record of doing X" |
| 8 | OSS Release | "I built X and open-sourced it" |
| 9 | Tacit Knowledge | "What senior engineers do unconsciously" |

Claude mapped this taxonomy against my existing articles, identified the gaps, then produced six title rewrite proposals and a set of title design rules. At this point, Claude's output was internally consistent and well-supported by data. I didn't feel any discomfort with the proposals either.

## Why and How I Brought in Kimi

Claude has a structural limitation when working solo. It tends to favor data that supports its own analysis and doesn't automatically seek out perspectives that would undermine its hypotheses. The tricky part is that when I read those proposals, the presence of solid data made everything feel "plausible" to me too.

So I brought in Kimi K2.5. With a different model architecture (MoE: Mixture of Experts, 1 trillion parameters) and different training data composition, I could expect different perspectives. It also helped that I already had Kimi set up as a CLI tool in my development environment (the setup details are in [a previous article](https://zenn.dev/shimo4228/articles/claude-kimi-hybrid-setup)).

This time, however, the use case was peer review rather than implementation delegation. The prompt structure looked like this:

```text
Input 1: Full text of 7 existing articles by the author (A-rank quality)
Input 2: Full text of Claude's analysis results and proposals
Instruction: Review from 4 perspectives — strategist, editor, reader advocate, and marketer
```

Kimi K2.5 has an Agent Swarm architecture where an internal orchestrator decomposes tasks and distributes them to up to 100 sub-agents. I specified four perspectives to explicitly demand critique of Claude's proposals from different standpoints. The output was roughly 350 lines (17KB). Each of the four perspectives returned specific criticisms and alternative suggestions.

## What Kimi Returned

Of the six title rewrite proposals, two were approved as-is (dropping the subtitle from "Claude Code の真価はコード生成ではない" and changing the title of "Obsidian地獄"). For the remaining four, Kimi's verdicts were as follows. Note that these included strategic corrections beyond just title suggestions.

| Claude's Proposal | Kimi's Verdict | Kimi's Reasoning (Summary) |
|---|---|---|
| "最強モデルで司令塔を組んだら9倍遅くなった" (Built an orchestrator with the strongest model; it got 9x slower) | ⚠️ Revise | The lesson of "rejection" is lost. The article's real value lies in "the criteria for rejecting an approach" |
| "Claude Codeに397問の試験問題を自作し始めた" (Started creating 397 exam questions with Claude Code) | ❌ Reject | The number dominates too much. The article's core insight — "AI doesn't propose leveraging its own capabilities" — gets buried |
| Strategy of "targeting the optimal zone by character count" | ⚠️ Correct | "Information density" is the right metric, not character count |
| "Claude Code で技術記事を20本書いて育てた Zenn 執筆環境の全貌" (The full picture of a Zenn writing environment built by writing 20 tech articles with Claude Code) | ⚠️ Reconsider | Should downplay the "even a non-engineer can do it" angle and let achievement numbers speak instead |

The rejection of "397 questions" left the strongest impression. When I read Claude's proposal, I had been swept up by the impact of the number "397" myself. It wasn't until Kimi pointed out "the number is stealing the spotlight" that I noticed. The article's real core is a meta-insight: Claude Code is itself an LLM, yet it never proposed leveraging its own language capabilities. I had been so dazzled by the strength of the number that I almost lost sight of what the article actually wanted to communicate.

The "9x slower" case had the same structural issue. If you focus only on the number, the value of the decision-making process — why the multi-agent approach was rejected — disappears from the title. Kimi's revised proposal kept "why multi-agent was rejected" as a subtitle.

## What the Integration Revealed

**Invisible agreement became visible.** This was the biggest takeaway. When I read Claude's proposals, the data backing made them feel "plausible." But after reading Kimi's critique, I realized I had been unconsciously agreeing with Claude. The value of peer review isn't "producing the right answer" — it's making your own biases visible.

**The number-optimization trap.** "397 questions" is a strong number. "9x slower" is shocking. But putting those numbers front and center sacrifices the article's actual lessons — AI's blind spots, the criteria for rejection decisions. Kimi called this "counterproductive." It's a common content marketing principle, but having it applied specifically to my own articles — being told exactly which number was erasing which lesson — was a level of resolution I could only get through this experience.

**Same tool, different value.** I used Kimi K2.5 as a code-writing worker in [the previous article](https://zenn.dev/shimo4228/articles/claude-kimi-hybrid-setup). This time I used it as a reviewer critiquing proposals. For implementation delegation, Kimi's swarm intelligence (parallel execution power) shines. For peer review, the multi-perspective nature of that swarm intelligence shines instead. Even with the same model, handing it a spec.md versus handing it full article text extracts completely different kinds of value.

**Limitations of this approach.** That said, Kimi's critique isn't necessarily "correct." Kimi has its own biases. When two AIs agree, that doesn't mean the answer is right, and since a human makes the final call, human bias remains too. What peer review expands is the "scope of consideration," not the "accuracy rate."

## Changes I Actually Made

Here's what I executed:

- Out of the original six title rewrite proposals, I finalized five with Kimi's revisions incorporated
- Added seven title design rules to the zenn-writer skill ("lead with numbers and pair them with emotional words," "but preserve the learning element," etc.)
- Listed five new article themes (a comprehensive "Top 10 Settings" piece, a checklist-style "Before You Trust LLM Output" piece, and others to fill the identified gaps)
- Decided on a branding transition direction (from "even a non-engineer can do it" to "an explorer pushing the limits of Claude Code")

The effectiveness of these changes hasn't been verified yet. I plan to track PV and like counts after the retitling and report back once the data is in.

## Conclusion

This was a shift in perspective from "using AI as a tool" to "using AI as a sparring partner."

```text
Claude (data analysis & structuring)
  -> Author (review & approval)
    -> Kimi (multi-perspective critique)
      -> Author (integration & final judgment)
        -> Execution
```

Claude handled data analysis and structuring; Kimi handled multi-perspective critique and brand consistency checking. This division of roles emerged through the peer review process itself.

As a meta-note, this article itself was designed using the findings from the buzz analysis. The title intentionally combines the "numeric" and "hypothetical/result" patterns, and the structure deliberately uses a "failure-to-lesson" arc with a "concrete-abstract-concrete" flow. Whether this structure actually works will be verified by this article's own PV and like counts.

## Appendix: How This Article Was Made

This article itself was produced through the "AI peer review" process. I'm documenting the steps here for transparency.

1. **Claude created the plan.** It designed the article structure (8 sections), three title candidates, and the source materials to use.
2. **The plan was converted to spec.md and dispatched to Kimi K2.5.** First draft writing was delegated. The spec included tone specification (da/dearu style — assertive Japanese), reference paths for source files, and section structure. Kimi autonomously read three source files and generated a first draft of roughly 3,800 characters. However, the draft quality was low. Despite having access to the same skill set and MCP tools as Claude, Kimi fell significantly short in fleshing out prose and reflecting the author's voice. The structure followed the spec, but the content was thin and bland.
3. **Claude's editor agent delivered a harsh review.** The verdict was "REVISE AND RESUBMIT." It flagged three numerical inconsistencies (CRITICAL) and six issues including shallow thesis validation and lack of embodied lessons (MEDIUM).
4. **Claude revised based on editor feedback.** All CRITICAL and MEDIUM issues were addressed. The draft was substantially rewritten from Kimi's version, adding the author's introspection (e.g., "I had been swept up by '397 questions' myself") and acknowledging the methodology's limitations.
5. **The revised version was sent back to Kimi for feedback.** This time, no persona was specified — I let the swarm intelligence make autonomous judgments. In the buzz analysis review discussed in the main text, I had specified four perspectives, but for this second round I deliberately removed constraints. Kimi returned an A rating (recommended for publication) with three minor corrections including numerical consistency in the opening.
6. **Kimi's feedback was incorporated to produce the final version.**

What the different uses of Kimi revealed: For peer review (critique and analysis), Kimi's swarm intelligence returned multi-perspective insights, generating 350 lines of detailed feedback. For article writing (prose generation), Claude produced dramatically higher quality. Even with the same model, critique and generation bring out capabilities in fundamentally different ways.
