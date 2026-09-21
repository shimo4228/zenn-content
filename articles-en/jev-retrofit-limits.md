---
title: "I Added Jev's Skill Router to Claude Code and Turned Back Just Before Rewriting the Skill Listing"
emoji: "🧭"
type: "tech"
topics: ["claudecode", "aiagents", "agenticcoding", "llm"]
published: false
description: "I ported TypeSafe's skill suggestion cookbook to a Claude Code UserPromptSubmit hook. It worked as described, and it changed nothing: a hook can only add one line, while Claude Code keeps showing the model every skill's full description and the model keeps choosing. The path that would reach the choice — rewriting the skill listing through Mods — existed, and I stopped before taking it. Someone had already shipped it the day before. Three things to check before you add a decision model to your own harness."
tags: claudecode, aiagents, agenticcoding, llm
---

I try not to fill the gaps in a big harness like Claude Code with my own implementation. When I do fill one, the official side changes a while later and my work is no longer needed. That has been the pattern for the last six months.

The rules I had accumulated to shore up an older generation of models stopped being useful when Anthropic changed course for the Opus 5 generation — fewer rules, leave more to the model's judgment — so I cut my resident set [from 5,789 words to 2,463](https://dev.to/shimo4228/opus-5-changed-how-rules-should-be-written-audit-yours-4fb4). To run several Claude Codes side by side I [installed Herdr and wrote an article about it](https://dev.to/shimo4228/herdr-a-tmux-for-ai-agents-until-the-editor-disappeared-3hnn), and now Claude Code itself can [send messages between sessions](https://code.claude.com/docs/en/cross-session-messaging). [Projects](https://code.claude.com/docs/en/claude-projects), where Claude starts and manages parallel sessions from a single conversation, is rolling out in public beta. Today's Projects bundles only cloud sessions, but once it handles the sessions on my own machine, Herdr will not be needed either.

Even so, on September 21, 2026, curiosity won. Jev is a model that writes no text and returns only probabilities to typed questions. That day I ported the [skill suggestion cookbook](https://docs.typesafe.ai/cookbooks/skill_suggestion.md) from TypeSafe, who build Jev, to a Claude Code hook.

This article is about how far the thing I built reached, where I turned back, and what was waiting past the turn. If you are thinking about adding Jev to your own harness, you should come away with three things to check before you do.

## What I added is one line

What I built is a Claude Code plugin, [jev-skill-router](https://github.com/shimo4228/jev-skill-router). On every prompt a `UserPromptSubmit` hook runs and sends Jev the prompt together with the roster of skills installed locally — their names and descriptions. It makes at most two requests to Jev. The first ranks the whole roster and asks three yes/no questions about whether the request needs a skill at all. The second re-reads only the top three candidates, this time with the full text of each `SKILL.md`. If neither the average of the three first-pass answers (`gate` in the log; the third is inverted before averaging) nor the highest per-candidate value from the second pass (`fits`) reaches 0.30, it suggests nothing.

By default it adds nothing and only records its verdict in a log. With injection enabled, a turn that reaches 0.30 gets exactly this one line added.

```text
<skill_relevance>
Relevant to the current request: adr-writer. Ignore this if it does not fit what the user actually asked for.
</skill_relevance>
```

Each verdict leaves one line in the log. This is the line from a request, written in Japanese, to record a design decision in an ADR (excerpt).

```json
{"mode": "inject", "model": "jev-1.13.0", "router_version": "0.2.0",
 "gate": 0.47,
 "shortlist": ["adr-writer", "adhd:adhd", "archify"],
 "fits": {"adr-writer": 0.93, "adhd:adhd": 0.14, "archify": 0.05},
 "suggestion": "adr-writer",
 "usage": {"input_tokens": 21597, "output_tokens": 702, "calls": 2},
 "elapsed_ms": 1567}
```

I wrote six request sentences with a single intent each and sent them. Five named the skill I judged to be right, at 0.93 to 0.98, and "Thanks, that's it for today" drew no suggestion at all. Each took 0.7 to 1.6 seconds. These are single readings per case, not numbers you can read as a rate.

Up to here, it worked exactly as the cookbook said it would.

## Claude Code's own skill selection was running the whole time

While running it, I asked: "Hold on — so Claude Code's own skill selection is still running at the same time?"

It is. All a hook's `additionalContext` can do is [add one string to the model's context](https://code.claude.com/docs/en/hooks). Claude Code goes on showing the model a skill listing with the name and description of every installed skill, and the model is what picks from it. Not one token of that listing goes away. Jev's verdict was simply running alongside the choice.

On top of that, the conditions that made the cookbook work are absent in Claude Code. The cookbook's experiment covers 488 requests; across the 315 where a skill applied, loading the wrong skill dropped from 16.8% to 7.3%. The model choosing skills there was `claude-haiku-4-5`, and what it saw was an index cut to 60 characters per skill. The cookbook says so at the top:

> Hermes, the agent harness used here, cuts it to 60 characters by default.

60 characters is not a recommendation from the cookbook; it is the default display width of the harness used in the experiment. The cookbook itself gives the example that at 60 characters you cannot tell a skill that edits `.pptx` from one that creates it. It describes the problem it set out to solve as an agent that "makes its choice on almost no information." A small model choosing from a truncated index, with one line added by a judge that had read the full text. Those were the conditions under which it worked.

Claude Code is the opposite. It shows the model each description (together with `when_to_use`) [up to 1,536 characters, uncut](https://code.claude.com/docs/en/skills). Counting in the repository where I am writing this: 59 skills installed, 2 with descriptions that fit in 60 characters, median 412. The model doing the choosing is Claude Fable 5.1, stronger than Haiku. A router in Claude Code turns into a second model that has read the same descriptions, advising from the side a stronger model that has already read all of them in full. The only information it can add is the body of `SKILL.md`.

This is an argument from the mechanism, not a measured result. I have no evidence that injecting the line improved anything. That is why I did not make injection the plugin's default.

## There was a path to rewriting the skill listing

To make it work as a router, adding a line is not enough. You have to change the skill listing the model is shown.

That path existed. The type definitions for function hooks — Claude Code's early-access feature, known as Mods ([design thread](https://github.com/anthropics/claude-code/issues/91870)) — list `skill_listing` among the kinds of attachment that reach the model, and say its body can be rewritten from the Mod side (`mods/types/claude-code.d.ts` in `anthropics/claude-code`, checked on September 21, 2026).

I started a design plan and stopped almost immediately. With enough effort it might not be impossible. But it means replacing Claude Code's default skill selection with my own. An implementation that rides on early-access types and breaks the default behavior has to follow along every time the official side changes. After six months of filling gaps only for the official side to change and make the fill unnecessary, this is a swamp.

I wrote at the top of the README, with the reasons, that "as a router it is unlikely to help a strong model in Claude Code," left it there for anyone thinking the same thing, and stopped.

## That path had been walked the day before

Searching again while preparing this article, I found that what lay past my turning point was already implemented.

It is the Mod `jev-skill-suggestion` in [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates). Its first commit was on the morning of September 20, 2026, Japan time — the day before I turned back. At that point the very rewrite I had stopped short of was working. It returns empty for Mods' `skill_listing`, so the model never reads the skill listing at all. Instead it tells the model to load the single skill Jev picked. The model can no longer choose from the listing itself; what remains is to follow Jev's suggestion or ignore it. A second commit, at midday on the day I turned back, went further: the Mod attaches the chosen skill's `SKILL.md` itself. The first line of the current README reads:

> Takes the skill listing out of the context window and lets Jev, TypeSafe's System One decision model, pick at most one skill per prompt from the skills' descriptions — and then loads that one skill itself, by attaching its `SKILL.md` to the prompt.

The way it picks is the same two requests from the same cookbook. Hiding the skill listing was not custom work: it is the official setting [`skillOverrides`](https://code.claude.com/docs/en/skills), which switches how each skill is shown to the model across four levels — name and description, name only, only when the user calls it, or not shown. If all you want is to cut the tokens the skill listing costs, you need neither Jev nor Mods. The same repository also holds `jev-model-router`, which routes model and reasoning depth with Jev.

I have tried neither. Whether they work, I do not know. What I do know is that someone willing to carry the cost of following the official side was already there before I stopped. If I want to try it later, the real thing exists without my building it.

## Who holds the role of choosing

From here on, this is my own read, from having built the thing.

In Claude Code, the role of choosing skills belongs to Claude Code and its model. A frontier model carries it, and the only opening I had was one for adding a line of text.

How far Jev works, I think, is decided by who holds the role of choosing. If a weak chooser holds it, one line added from the side is enough — that was the cookbook. If a strong chooser is looking at the full text, advice does not move it, and the only way through is to reach the role of choosing itself. Mods is an example of the harness side opening that role outward. [pi-jev](https://github.com/TheoOliveira/pi-jev), an extension for the coding agent Pi, enables only the tools whose Jev probability clears a threshold. Not advice: the tools the model can see are what change.

Most harnesses today are built around the loop where the model thinks and then calls a tool (ReAct), with a strong model seeing everything and doing both the choosing and the judging inside its own reasoning. As long as the chooser is strong, adding a fast decision model beside it leaves no work to be replaced. Moves to fit Jev partially into existing harnesses will probably keep coming, but the effect should stay inside whatever range the harness has opened.

Conversely, if a harness appears that builds tool selection, model routing, and the judgments along the way with Jev from the start, and hands only the final reasoning to a frontier model, speed, cost, and accuracy could all look very different. TypeSafe itself calls Jev "a frontier-intelligence function call" in [its announcement](https://typesafe.ai/blog/introducing-system-one-models-and-jev), framing it as a component you call. When I [compared Jev and Opus](https://dev.to/shimo4228/how-close-to-opus-does-jev-a-model-that-writes-no-text-get-at-skill-selection-in-03-seconds-1nfj) on skill selection in a different agent of my own, Jev took 0.32 seconds per case at about 1/560th of Opus's cost, and across the 45 cases where it pointed with probability 0.5 or higher, not one disagreed with Opus's pick. On the other hand, agreement across all 150 cases was about half of the agreement Opus reached with itself when made to do the same selection twice. How much of this you can hand to Jev, I have not measured, and I have not found a report that measures it.

As of September 21, 2026, within the range I searched, no such general-purpose harness existed. Everything I found is an integration into an existing harness.

## Three things to check before you add

If you are about to add a decision model like Jev to your own harness, check three things before you start writing.

1. **Does what you add reach the role of choosing?** If you only add text, the original choice keeps running underneath. Find out first whether there is an opening that reaches it — your own loop, Mods, tool enablement.
2. **Is the chooser already seeing the same information as the decision model?** Before you read the numbers from a vendor's experiment, read the experiment's conditions. Which model was choosing? What could that chooser see?
3. **Is an official setting enough?** If what you want is fewer tokens spent on the skill listing, `skillOverrides` is enough in Claude Code. A decision model is for what lies past that.

An extension that only adds text goes back the way it was when you remove it. Build one out of curiosity if you like. An implementation that replaces the default behavior is something I will not build, even if I could.

I moved over to following instead of building. I added "does a harness built on Jev appear" to my daily research checklist. My plugin keeps running in the setting where it adds nothing and only writes the log. What I watch is the match between the skill Jev named and the skill actually used in that turn. If turns where it named a skill that went unused pile up, adding one line may be worth something. If they do not pile up, I take it out.

**AI-mediated writing disclosure:** AI drafted and translated the prose of this article from the author's session records, the plugin's logs and README, and the public sources cited above. The central thesis, the decision to turn back, the read in "Who holds the role of choosing," and responsibility for publication belong to the author.

## Related links

- [How Close to Opus Does Jev, a Model That Writes No Text, Get at Skill Selection in 0.3 Seconds?](https://dev.to/shimo4228/how-close-to-opus-does-jev-a-model-that-writes-no-text-get-at-skill-selection-in-03-seconds-1nfj) — the measurement comparing Jev and Opus on skill selection in an agent of my own (Contemplative Agent, running on gemma4:e4b), not in Claude Code
- [TypeSafe: Skill suggestion cookbook](https://docs.typesafe.ai/cookbooks/skill_suggestion.md)
- [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) — `jev-skill-suggestion` and `jev-model-router` are Mods in this repository
- [DECRUX9812/typesafe-skill-router](https://github.com/DECRUX9812/typesafe-skill-router) / [Dicklesworthstone/skillranker](https://github.com/Dicklesworthstone/skillranker) — other implementations of the same cookbook
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles/jev-retrofit-limits.md) — the Japanese original; this English version is `articles-en/jev-retrofit-limits.md`, and every article's Markdown and the index (docs/PUBLICATIONS.md) live in the same repository
- [The author's GitHub](https://github.com/shimo4228) — research repositories with DOIs
