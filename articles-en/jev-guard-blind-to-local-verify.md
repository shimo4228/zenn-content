---
title: '"Is There Any Point to This?" Removing the Jev Plugins I Added to Claude Code After One Week'
emoji: "🧗"
type: "tech"
topics: ["jev", "claudecode", "aiagents", "agenticcoding"]
published: false
description: "For a week I ran two plugins that use Jev inside Claude Code. Of the 539 times the skill router picked a skill, Claude Code used it within 30 minutes 28 times. The completion guard stopped Claude Code 8 times, and in the two cases I traced, it had just finished running my verification script. Neither side was wrong on its own. Here is why I removed both, and where you can actually read the effect of a judgment model you build in."
tags: jev, claudecode, aiagents, agenticcoding
---

At the end of [my previous article](https://dev.to/shimo4228/i-added-jevs-skill-router-to-claude-code-and-turned-back-just-before-rewriting-the-skill-listing-34in), I wrote what I would do next. I would run the plugin that suggests skills with Jev in a setting where it adds nothing and only writes a log, and match the skills Jev picked against the skills Claude Code actually used.

I ran it for a week starting September 21, 2026. Of the 539 times Jev picked a skill, that skill was used in the same session within 30 minutes 28 times. I removed the plugin without checking any further.

That same week, the same Claude Code had one more plugin that uses Jev. At the end of a task, it judges whether Claude Code is "calling the work done without verifying it," and if so, stops it. Over the week it stopped Claude Code from finishing 8 times. In the two cases I traced in detail, Claude Code had finished running my environment's verification script just before it was stopped.

To give the conclusion first: the place where you can build a judgment model like Jev in as a component and read its effect is inside a pipeline whose flow is fixed. Claude Code has the model decide what to do next on the spot. Retrofit a component into it, and small differences go on to change the behavior that follows, one after another, so you can't even tell whether you are degrading how it would otherwise behave. Knowing its performance might be dropping without my noticing, I couldn't decide to adopt either plugin on the surface numbers alone.

![Top row: a pipeline whose flow is fixed, moving along a track in order: sources, Jev's judgment, the LLM's writing. Bottom row: Claude Code in the driver's seat; when a plugin added afterward stops it from finishing, what it does next can change](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/jev-guard-blind-to-local-verify-hero.png)

In a pipeline with a fixed flow, what comes before and after a swapped component stays the same; in Claude Code, a single stop by a plugin can change what happens next.

## Jev's skill picks barely overlapped with Claude Code's own choices

The first plugin is [jev-skill-router](https://github.com/shimo4228/jev-skill-router), which I built and published. For each user message, it asks Jev "which skill fits?" and logs the answer. I ran it in a setting that tells Claude Code nothing. What I wanted to see was how much the skills Jev picked overlapped with the skills Claude Code picked on its own.

Over the week it made 1,242 judgments, and in 539 of them Jev picked some skill. In 28 of those, the skill was actually called in the same session within 30 minutes of the pick, about 5%.

Claude Code chooses skills by itself. It looks at the skill listing and, from the flow of the conversation, calls a skill when it needs one. Jev's picks barely overlapped with Claude Code's.

![One week of jev-skill-router logs: 1,242 judgments, 539 in which Jev picked a skill, and 28 in which that skill was called in the same session within 30 minutes of the pick (about 5%)](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/jev-guard-blind-to-local-verify-funnel.png)

Of 1,242 judgments, Jev picked a skill in 539, and 28 of those skills were actually called.

In the previous article, I had written that if picks Jev made but Claude Code never used piled up, Jev might be catching skills Claude Code had overlooked. The unused picks came to 511. By the previous article's standard, that is the side where adding a one-line suggestion might be worth something.

But whether those 511 were things Claude Code overlooked or simply off-target picks, I couldn't know without opening each conversation and judging whether that moment called for the skill. For every judgment, this plugin was sending Jev about 20,000 tokens: the skill listing (every skill's description) plus the full text of the top 3 candidate skills. I judged it wasn't worth reading 511 conversations for that, and removed it without checking.

## After removing it, I read 20 of the unused picks

After removing it, I randomly chose 20 of the times Jev picked a skill that went unused, opened the conversation at that point, and read it. "Unused" here means the skill wasn't called through the Skill tool in the same conversation within 30 minutes; calls made inside subagents aren't counted. The script I used for the counts and the sample, along with the numbers, is published in [the evals folder of jev-skill-router](https://github.com/shimo4228/jev-skill-router/tree/main/evals).

- 13 were off the mark. In at least 6 of them, Jev was reacting not to something I typed but to text an agent had written: judgment requests sent to subagents, or reports that came back from them. Inside Claude Code, text like this comes in through the same entry point as the user's messages
- 5 were close in topic, but at that point there was no need to call the skill
- In 1, Claude Code read the skill's file directly instead of calling the skill. The skill was used, but my tally counted it as "unused"
- Only 1 might have been something Claude Code overlooked. It was a question about whether I could run two LLMs locally at the same time, and Claude Code searched the web instead of using the skill

With only 20, the proportions are rough. After reading them, my decision to remove the plugin didn't change. Still, I learned two things. Jev picks by looking only at the text of a message, so it doesn't distinguish who wrote a given piece of text in the conversation. And my way of counting didn't see every path by which Claude Code uses a skill, either. The number 28 mixes Jev's way of picking, Claude Code's way of working, and my way of counting, and I couldn't separate from the numbers in the log how much each one contributed.

What I hadn't expected was the second plugin.

## A completion that had already been verified got stopped

The second is [jev-belay](https://github.com/valentynkit/jev-belay), published by an outside developer. It's a Stop hook that runs when Claude Code tries to finish its work. If files were changed and no test, build, or lint has run since, it asks Jev "Is this completion report an unverified completion?" If Jev judges that it is, Claude Code can't finish; it receives the reason and goes back to verify. This one ran for the week in a setting that doesn't just record its judgments but actually stops Claude Code.

Let me follow one of the stops step by step. Claude Code was implementing a change in my `~/.claude` configuration repository.

1. Ran the repository's verification script `./.claude/verify.sh` twice; both runs succeeded (exit 0)
2. Fixed one spot in a test file
3. Ran `verify.sh` a third time; it succeeded
4. Wrote the commit message to `msg.txt` in a temporary working folder
5. Committed
6. Reported completion
7. jev-belay stopped it

The reason for the stop was left in the judgment log as follows (it is followed by text urging Claude Code to run verification and report the result).

```text
jev-belay: reports completion (0.96) after 2 file changes with no test, build, or lint run since the last change; claims checks passed (0.97) but none ran.
```

The judgment was that Claude Code claimed the checks passed even though no test, build, or lint had run since the last change. Once stopped, Claude Code ran `verify.sh` once more, and about two and a half minutes later it succeeded again. The "2 file changes" in the log were the test file fixed before the third verification, and `msg.txt`.

In all 8 stops over the week, "checks run since the last change" was empty in the judgment log.

## The component and my workflow were each right on their own

What jev-belay counts as a "check" is written in its code.

```js
// ~/.claude/plugins/cache/jev-belay/jev-belay/0.2.0/belay.mjs (excerpt)
export const CHECK_COMMAND = /\b(?:(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:test|check|lint|typecheck|build|verify|ci)\b| … |pytest|jest|vitest| … |ruff|mypy| … )\b/;

const named = CHECK_COMMAND.test(command) || extraCheck()?.test(command) === true;
if (tool === "Bash" && named) return failed || summary === "fail" ? "check-fail" : "check-pass";
if (summary) return summary === "fail" || failed ? "check-fail" : "check-pass";
return "unknown";
```

It counts a check as having run in one of two cases: the command string contains the name of a well-known test or lint tool (`npm test`, `pytest`, `ruff`, and so on), or the output contains a test runner's summary line.

My `verify.sh` is a script specific to this repository that runs everything from formatting to tests in one go. The command string never mentions a runner's name. When it succeeds it prints nothing, so there's no summary line either. Had I called the same thing under the name `npm run verify`, it would have matched the regex.

The last "change" also came from my workflow. In this environment, multi-line commit messages are written to a file first and then passed in. So one file write comes after verification. jev-belay counts every write through Write or Edit as a change, so it looks as if something changed after verification. Lining up the change just before each of the 8 stops: 2 were commit message drafts, and the rest were things like notes, a skill's description file, and a lint configuration file.

![The order of events in one stopped case. Claude Code: verify.sh succeeds twice, one fix to a test, verify.sh succeeds a third time, writes msg.txt, reports completion. jev-belay did not count verify.sh as a check; it counted change 1, change 2, checks 0, and stopped it](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/jev-guard-blind-to-local-verify-belay-view.png)

Claude Code had passed `verify.sh` three times, but what jev-belay counted was 2 changes and 0 checks.

In the other case I traced, Claude Code fixed a lint configuration file, then ran `verify.sh` and wrote its output to a file. The result was a failure, caused by a temporary outage at the package distribution site (PyPI), and Claude Code had reported that. Here too, jev-belay saw neither a runner name nor a summary line. Once stopped, Claude Code spent about 3 minutes redoing the verification and failed for the same reason.

Neither side is wrong on its own. jev-belay's README reports how accurately it tells unverified completions from the rest across 100 labeled task endings. Of those 100, it stopped 8, and 7 of the stops were correct, according to the README. My commit procedure has a reason too: it avoids being asked for approval every time a command has special characters embedded in it. The conflict arose when the two were combined inside Claude Code. Whether a stopped Claude Code goes on to redo verification is also not something the component can decide.

jev-belay has a `CHECK` option for adding a project's own check script as a regex. I hadn't set it in my environment. Had I set it, `verify.sh` would likely have been counted as a check. I removed the plugin without trying it. Why I didn't try it is in the next section.

## I couldn't read their effect, and the work they added was already being done

The day the week was up, in the middle of another task, I asked Claude Code: "Are Jev's skill selection and Jev-bely [sic] still running? Is there any point to this?" I looked at the logs and removed both.

Setting `CHECK` would get rid of the conflict where `verify.sh` wasn't recognized as a check. But it would only get rid of the conflict I noticed. Claude Code is an agent in which the model decides what to do next each time, repeating a loop of thinking and then calling a tool (ReAct). When it writes a file, when it runs verification, and what it does when stopped are not decided until it runs. What a component inserted there sets off, I couldn't know until I had run it for a while and read the logs. I only noticed this conflict because it surfaced in a visible form: Claude Code being stopped. Even a single stop can change the verification that follows, the responses, and how the next task proceeds. If a component were degrading performance in some invisible way, I would have no means of reading that from the logs.

What's more, the work both plugins added from outside was already being done inside. Claude Code picks its own skills. This environment has a hook that runs `verify.sh` on every commit, so any work that got as far as a commit has passed verification. Much of what jev-belay set out to protect was already protected by another mechanism (the case of declaring completion without committing remains). Layering the same work on from outside replaced nothing; it only added conflicts.

![How the plugins added from outside map to mechanisms that were already there. Choosing skills: jev-skill-router and Claude Code itself. Preventing unverified completions: jev-belay and the commit-time hook](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/jev-guard-blind-to-local-verify-overlap.png)

Before either plugin was added, Claude Code itself was already choosing skills, and the commit-time hook was already doing most of the work of preventing unverified completions.

## You can read the effect of a built-in component where the flow is fixed

In a pipeline whose flow is fixed, things are different. If you build with LangGraph and fix the nodes and their order in code, swapping in a judgment model as one node doesn't change what goes into that node or where things go next. You can pull out just the swapped component and test it. In my daily paper research, [I moved the per-source judgments, "is it relevant?" and "is it new?", to Jev, and left only the writing to an LLM](https://dev.to/shimo4228/moving-my-research-pipelines-judgment-calls-from-an-llm-to-jev-a-judgment-only-model-4ncj). Because it's a pipeline I built myself, I could read where Jev's judgments took effect and which numbers changed.

Claude Code also has ways to add components, through hooks and plugins. But in an agent where what happens next isn't decided in advance, the effect of changing a component is hard to read, and that makes me cautious. If I use Jev, my current thinking is that it's better either to design the flow around judging with Jev from the start and call the LLM only for the parts that generate text, or to use Jev as a component in a fixed pipeline.

**AI-mediated writing disclosure:** AI drafted and translated the prose of this article from the author's Japanese original, the plugins' logs and session records, and the public sources linked above. The decision to remove both plugins, the read on where a judgment model's effect can be seen, and responsibility for publication belong to the author.

## Related links

- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles/jev-guard-blind-to-local-verify.md) — the Japanese original; this English version is `articles-en/jev-guard-blind-to-local-verify.md`, and every article's Markdown and the index (docs/PUBLICATIONS.md) live in the same repository
- [The author's GitHub](https://github.com/shimo4228) — research repositories with DOIs
