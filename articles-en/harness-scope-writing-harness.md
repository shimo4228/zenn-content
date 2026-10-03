---
title: "Turning Claude Code into a Writing Harness with Claude Mods and an Output Style"
emoji: "✍️"
type: "tech"
topics: ["claudecode", "contextengineering", "plugins", "writing"]
published: false
description: "Even in my writing repository, Claude Code showed Claude a skill listing grown for code: 98 skills, 26,252 characters. A Claude Mod (harness-scope) now chooses per repository what Claude sees, cutting it to 49 skills and 15,242 characters, and an output style sets how Claude talks with me. Measured on Claude Code 2.1.287 and 2.1.288, including what keep-coding-instructions: false removes on Claude 4 versus Claude 5 models."
tags: claudecode, contextengineering, plugins, writing
---

Writing articles in Claude Code has advantages that chat on claude.ai doesn't. You can build your own harness of skills and rules, and you have a lot of freedom over what context Claude gets. I write my articles in this repository (zenn-content), where I keep skills for writing and agents for review.

But even when I opened the writing repository, what Claude saw was the global harness I had grown for code. When I measured it on October 3, 2026, the skill listing passed to Claude held 98 skills and 26,252 characters. Only 7 of those skills belonged to this repository. The rest were my own skills in `~/.claude`, plugins, built-ins, and skills synced from claude.ai. `tdd` and `implementation-chain` were in the list too.

The code harness and my writing rules collide. I had tried a range of fixes over time, but each one stayed a surgical fix. This time it started to become clear that combining Claude Mods (hook modules shipped in a plugin) with an output style lets you build a harness that is quite specialized to one task. I built the first one for writing, which needs different rules from code.

This article covers two pieces: choosing what Claude sees with a Mod, and deciding how Claude talks with an output style. It also covers what I learned by measuring along the way. The measurements used `claude -p` on Claude Code 2.1.287 and 2.1.288.

![The 98 skills, 37 agent types, and 21 instruction files passed to Claude (totals include the repository's own) become 49, 14, and 19 with the Mod's profile zenn-writing. The repository's own items are kept even with the Mod. Output style zenn-writing inserts the text of the conversation rules on turn 1, and from turn 2 inserts only a reminder of its name](/images/harness-scope-writing-harness-hero-en.png)

The Mod chooses what Claude sees, and the output style decides how Claude talks. The two reach Claude by different routes.

## Turning a few things off in settings barely shrank the listing

Claude Code has settings in a repository's `.claude/settings.json` for turning things off. On 2.1.287, `skillOverrides` (skills), `enabledPlugins` (plugins), and `claudeMdExcludes` (instruction files) took effect per repository.

But turning off 3 of my own skills barely shrank the skill listing. On 2.1.287 the listing had 101 skills and 26,551 characters; with 3 turned off, it had 26,534 characters. According to the [official docs](https://code.claude.com/docs/en/skills), the skill listing gets a character budget of 1% of the context window, and when it overflows, some skills' descriptions are dropped. My read is that the characters freed by those 3 skills went to the descriptions of the remaining ones.

Plugins had another problem. A plugin's skills stay in the listing even when you turn them off with `skillOverrides`, and cutting the whole plugin with `enabledPlugins` removes its skills and agents together. In my writing process, I ask the Codex plugin's agent (`codex:codex-rescue`) to act as a first-time reader. I don't need Codex's skills, but cutting the whole plugin takes that agent away too.

## A Mod chooses what Claude sees in each repository

A Mod lets you hook into the step where Claude Code assembles what it passes to Claude: the skill listing and the instruction files (CLAUDE.md and rules). From 2.1.287 on, Mods are enabled by default ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)).

With it, I built [harness-scope](https://github.com/shimo4228/harness-scope), which keeps one global harness and chooses per repository what Claude sees. You install it once.

```bash
claude plugin marketplace add shimo4228/harness-scope
claude plugin install harness-scope@harness-scope
```

You write what to remove as named profiles in `~/.claude/harness-scope/profiles/`. On the repository side, you only pick a profile, in one line.

```json
{ "profile": "zenn-writing" }
```

This goes in `.claude/harness-scope.json`. I wrote the profile for zenn-content, `zenn-writing`, as a list of things to remove. The output style that comes up later has the same name, so in this article I call them "profile zenn-writing" and "output style zenn-writing". Here is an excerpt.

```json
{
  "skills": {
    "deny": ["implementation-chain", "tdd", "verify-bootstrap", "codex:*", "hookify:*"]
  },
  "agents": {
    "deny": ["architect", "refactor-cleaner", "security-reviewer", "pr-review-toolkit:*"]
  },
  "instructions": {
    "deny": ["~/.claude/rules/common/testing.md", "~/.claude/rules/common/coding-style.md"]
  }
}
```

For Codex, I remove only the skills, with `codex:*`, and keep the agent. Because skills and agents can be chosen separately, I can write combinations that the settings couldn't express.

The 49 skills that remain are this repository's 7, plus 12 of my own skills for things like translation and headline writing, the built-ins, the skills synced from claude.ai, and 2 plugin skills. I kept the built-ins even when they're for code, like `code-review` and `simplify`.

> Keep Claude's built-ins just in case. If the spec changes, the cost of keeping up gets heavy.
>
> (what I told Claude; quotes in this article are translated from Japanese)

In a new conversation, typing `/harness-scope` shows what is removed (I've omitted the lists of skill names).

```text
harness-scope: profile "zenn-writing" from ~/.claude/harness-scope/profiles/zenn-writing.json, selected by …/zenn-content/.claude/harness-scope.json
skills (deny): 49 off — archify, authorship-strategy, config-gc, …
agents (deny): 23 off — architect, claude-security:claude-security, …
instructions (deny): 2 off — ~/.claude/rules/common/coding-style.md, ~/.claude/rules/common/testing.md
tools: not in the profile
```

On the same day and version as the opening measurement (2.1.288), I compared it against running with the Mod off.

| | Without the Mod | profile zenn-writing |
|---|---|---|
| Skill listing | 98 skills, 26,252 chars | 49 skills, 15,242 chars |
| Agent listing | 37 types, 17,921 chars | 14 types, 5,519 chars |
| Instruction files | 21 | 19 |

Removing half the skills cut the skill listing's characters by about 40%. My read of why this differs from removing 3 is that the remaining skills now fit within the budget. If Claude tries to call a removed skill through the Skill tool, the call is refused with a reason.

harness-scope also ships a profile called `writing`, written as a list of what to keep. Applied on 2.1.287, it shrank the skill listing from 101 skills and 26,551 characters to just the repository's own 7, at 1,623 characters. If you want to remove the built-ins too, this is the shape to use.

## The coding instructions I meant to remove weren't in Claude 5 models

When I decided to build the Mod, there was one more thing I wanted to remove: the coding instructions in Claude Code's system prompt. Output styles have a setting called `keep-coding-instructions`, and setting it to `false` removes the coding part ([Output styles](https://code.claude.com/docs/en/output-styles)).

First, on Opus 5.5, I recorded the system prompt before and after selecting an output style with `keep-coding-instructions: false`. No section was removed. From that single condition, Claude concluded that what I wanted to remove had never existed. I didn't accept that.

> What do you mean? That can't be right. Then why does that mechanism even exist? Isn't it because we're mid-session?
>
> (my reply to Claude)

When I measured again across models, the results split by model generation.

| Model | System prompt sections, total chars | Sections removed by `keep-coding-instructions: false` |
|---|---|---|
| Haiku 4.5 / Opus 4.6 / Sonnet 4.6 | 28,108 chars | `doing_tasks`, 3,319 chars (confirmed on Haiku 4.5) |
| Sonnet 5.5 / Opus 5.5 | 6,557 chars | none |
| Fable 5.1 | 12,621 chars | (not measured; no `doing_tasks` to begin with) |

`doing_tasks` is the section with instructions such as interpreting requests as software development work and preferring to edit existing files. The Claude 5 system prompt doesn't have this section at all. On Sonnet 5.5 and Opus 5.5, the only thing that changes when you select an output style is the first line of the main prompt.

```text
You are an agent working with the user toward their goals, using your own judgment along the way.
```

This line becomes '…according to your "Output Style"…'. In Claude 5 models, there was nothing in the system prompt to remove. What needed removing was in the global harness from the previous section.

![Total characters of the system prompt sections: 28,108 on the Claude 4 models (Haiku 4.5 / Opus 4.6 / Sonnet 4.6), 6,557 on Sonnet 5.5 / Opus 5.5, and 12,621 on Fable 5.1. doing_tasks, 3,319 characters, exists in the Claude 4 models and was never in Claude 5. On Sonnet 5.5 / Opus 5.5 only line 1 changes](/images/harness-scope-writing-harness-generations-en.png)

Bar height is proportional to the total characters of the sections. Only the system prompts of the three Claude 4 models I measured have `doing_tasks` (I confirmed on Haiku 4.5 that it gets removed).

## I wrote the rules for talking with me into the output style

Seeing this result, I reconsidered what the output style should do.

> I see, so I don't need to worry about the system prompt. I just need to make an Output-style suited purely to a writing repository.
>
> (what I told Claude)

The rules for article prose already live in the repository's rules and skills. What was missing were rules for how Claude talks with me in a writing session. I had Claude reread 1,017 replies I had given to Claude's responses in past sessions, and turned the reactions that kept coming up into items. For example: a question answered with a rewrite, choices offered as descriptions instead of the actual text, and the frame of Claude's own proposal staying in the thesis.

The result is output style `zenn-writing`: 7 items, 526 characters in the Japanese original. The file is in Japanese; this is a translation.

```markdown
<!-- .claude/output-styles/zenn-writing.md (translated from Japanese) -->
This style is the convention for conversation with the author. The prose of articles, briefs, and translations follows `.claude/rules/writing-principles.md` and the channel contract.

- Answer a question in the same turn. Touch draft or rule files only after the author says to change them (answering a question with a rewrite makes the author say it again)
- When asking the author to choose, list the actual candidates (sentences, excerpts, diffs) numbered, and add one recommendation with its reason. One perspective per question (the author looks at the real thing and decides in a word)
- When the central thesis, an evaluation, or the article's direction is in question, ask for the author's view before any proposal, restate it in the author's words, then propose (the frame of a proposal made first stays in the text)
- When the author's thinking moves, confirm the new direction in the author's words and follow it. Only when it conflicts with the facts, show the evidence once
- In reports, separate facts you checked from your own guesses. Say "can't" or "doesn't exist" only after looking at the records and settings
- When asking for a read-through, hand over the draft itself in a form that opens (a private Artifact) before any explanation
- When asked about terms or outside knowledge, explain plainly with sources, and add any application to the author's material separately, labeled "my read"
```

Claude also writes the article text in the same conversation, so the opening sentence scopes the style: it's the rules for conversation, and it doesn't apply to article prose.

It lives at `.claude/output-styles/zenn-writing.md` and is selected with `"outputStyle": "zenn-writing"` in `.claude/settings.json`. Because the repository selects it, opening this repository always gives you this style. For coding work like fixing scripts, putting `"outputStyle": "default"` in `.claude/settings.local.json` turns it off, and the first line goes back to the original too.

The style's body reaches Claude not in the system prompt but as a reminder inserted into the conversation. The reminder carrying the body was inserted only on the first turn. From the second turn on, the only new insertion is a short 95-character sentence reminding Claude of the style's name.

![On turn 1, the output style body (7 conversation rules) and a 95-character name reminder are inserted. On turn 2, only the 95-character name reminder is inserted](/images/harness-scope-writing-harness-turns-en.png)

Height is proportional to character count. The body of the conversation rules is newly inserted only on the first turn.

## Deciding what Claude sees and how it talks, separately

With the Mod, I chose which skills, agents, and instruction files Claude sees. With the output style, I decided how Claude talks with me. The two live in different places, but they take effect together when I open the writing repository.

Some things remain unverified. I haven't measured how long the style body inserted on the first turn keeps working over a long session. In 1 of 9 checks on 2.1.287, harness-scope apparently wasn't loaded, so nothing was removed and everything passed straight through. I don't know the cause yet.

I haven't decided yet whether to use the same setup for other tasks besides writing. For now, I built it for writing, which calls for rules different from code.

**AI-mediated writing disclosure:** AI drafted and translated the prose of this article from the author's Japanese original, the measurement records, and the public docs linked above. The design of harness-scope and the output style, the reading of the measurements, and responsibility for publication belong to the author.

## Related links

- [harness-scope (GitHub)](https://github.com/shimo4228/harness-scope) — the Mod in this article
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles/harness-scope-writing-harness.md) — the Japanese original; this English version is `articles-en/harness-scope-writing-harness.md`, and every article's Markdown and the index (docs/PUBLICATIONS.md) live in the same repository
- [The author's GitHub](https://github.com/shimo4228) — research repositories with DOIs
