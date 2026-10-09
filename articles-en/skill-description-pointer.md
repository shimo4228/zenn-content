---
title: "Whoa… My Claude Code Skill Descriptions Are Way Too Long…?!"
emoji: "📏"
type: "tech"
topics: ["claudecode", "agentskills", "contextengineering", "claude"]
published: true
description: "I looked at my Claude Code skill descriptions and thought they were too long. The skill listing sent every turn has a budget, and when it runs over, unused skills with long descriptions show up as names only. I decided who invokes each skill, rewrote the descriptions short, and added a lint rule that counts width. Whether the model now invokes them when needed, I have not measured."
tags: claudecode, agentskills, contextengineering, claude
---

I was looking over the descriptions of my skills and thought, "Aren't these too long?" Before the rewrite, I had 54 skills in `~/.claude/skills/`. Their descriptions totaled 28,131 characters, the median was 435.5 characters, and 10 of them were over 800 characters.

To see what long descriptions do, I ran Claude Code's `/skill-doctor` (a diagnostic command that shows, for each loaded skill, how much context it uses every turn). Here is part of the output.

```text
  skill                                              source                    context  7d tokens   uses  last used
  jev-judgment-design                                userSettings                 < 20          -     0×  never
  loop-design-check                                  userSettings                 < 20          -     0×  never
  mono-color                                         userSettings                 < 20          -     0×  never
  repair-discipline                                  userSettings                 < 20          -     0×  never
  …
  context = this skill's one-line listing in the system prompt, included every turn
```

`context` is the size of the one line the skill gets in the skill listing sent every turn. These four skills have descriptions of 459 to 1,048 characters. Yet each is listed at under 20 tokens, so the listing carries only their names. All four were skills I had never used. Among the skills I wasn't using, the longer I had written a description, the more likely the model saw none of it.

This article checks why that happens against Claude Code's implementation and shows how I rewrote my descriptions. Whether that is the right way to write them, I don't know yet.

## The skill listing has a budget, and past it, skills are listed by name only

Every turn, Claude Code puts a listing of the skills the model can invoke on its own into the system prompt. Each line has the form `- name: description`. The listing includes not only the skills I wrote but also plugin skills and skills synced from claude.ai. In my environment, 94 skills are loaded, and all of them compete for one listing budget.

The budget counts display width, not characters. Width is measured with `Bun.stringWidth`, so a half-width character counts as 1 and a full-width character, such as a Japanese one, counts as 2. In the code of Claude Code 2.1.295 itself, the budget was this formula:

- tokens in the context window × characters per token × 0.01 (the default of the setting `skillListingBudgetFraction`)
- characters per token is 4 for some models from Claude 3 to 4.6, and 3 for all others, including Opus 5.5
- With Opus 5.5's 1M window, the budget is a width of 30,000. If the account can't use the 1M context, it is computed from 200,000 tokens, which gives 6,000

When the listing goes over budget, Claude Code writes a "Skill listing over budget" warning to the debug log and chooses which skills get a description:

1. Skills bundled with Claude Code always keep their description
2. The remaining skills are sorted by usage score (a value set by how many times you have used the skill and when you last used it), highest first
3. Going down the list, a skill gets its description only if the whole description still fits in the budget. A skill that doesn't fit is skipped, and the next skill is tried
4. Skills that never got a description by the end are listed by name only

When the budget runs short, no description is cut off midway (only the part over the per-skill cap of 1,536 characters is cut). A skill either gets its whole description or gets only its name.

The usage score formula looks like this in the code (verbatim, still minified):

```js
function xwt(e){let n=Oa(ce().skillUsage??{},e);if(!n)return 0;let r=(Date.now()-n.lastUsedAt)/86400000,s=Math.pow(0.5,r/7);return n.usageCount*Math.max(s,0.1)}
```

It is the use count multiplied by a factor that halves every 7 days since the last use, with a floor of 0.1. A skill you have never used scores 0.

The four skills from the opening had a use count of 0, so their score was 0 and they came last. Their long descriptions didn't fit in the remaining budget, so they were listed by name only. From the model's side, a name-only skill gives no clue what it does. If it isn't invoked, its score stays 0, and as long as the budget stays short, it is listed by name only in the next session too. This is a loop I read from the code; I have not counted invocations to check whether they were invoked less often.

![Over budget, only descriptions that fit whole get attached. The budget is a width of 30,000 (Opus 5.5, 1M window). Over it, Claude Code goes down the list and chooses. Bundled skills and skills with a high usage score get their descriptions. A skill with usage score 0 and a long description (loop-design-check) doesn't fit the remaining budget and is listed by name only. A skill with usage score 0 and a short description: the next one is tried, and it gets its description if it fits](/images/skill-description-pointer-budget-en.png)

Even among skills with the same usage score of 0, whether one ends up as a name only depends on the budget left at that point and the length of its description.

## I had cut them before, and they grew back

This wasn't the first time I'd noticed my descriptions were long. At the end of August, I had also tried to cut down how much of them sat in the system prompt every turn. As of August 30, the skills in my repository (excluding two placed by symlink from outside repositories) numbered 57, and their descriptions totaled 26,738 characters. Just before this rewrite, counted the same way, there were 52 skills and 27,105 characters. I had five fewer skills and more characters.

Every time I add a skill or fix one, its description gains another "also use it when…". Even when I cut the number of skills, each remaining skill's line keeps getting longer.

## First, I decided whether the model should invoke a skill at all

I took the direction of the rewrite from the design guidelines of Matt Pocock's skill collection. He splits skills into two by who invokes them (invocation) ([invocation.md](https://github.com/mattpocock/skills/blob/b0618bc/.agents/invocation.md)).

- A skill a person invokes with `/name` gets `disable-model-invocation: true`, and its description is a one-line summary for humans
- A skill the model invokes on its own gets a description written for the model

On how to write descriptions for the model, another of his skills ([writing-for-agents](https://github.com/mattpocock/skills/blob/b0618bc/skills/productivity/writing-for-agents/SKILL.md)) calls the description a "context pointer" to the body, and says to write one trigger per branch and to phrase things positively rather than negatively. Writing them short was my own call, made after looking at the budget.

Claude Code's implementation matches this split: skills with `disable-model-invocation: true` are removed before the skill listing is built. Since they aren't in the listing, they use none of the budget. I moved two skills to this side. One was `grill-me`, which interrogates a plan one question at a time: it only ever ran when I asked for it.

```text
Before: A relentless one-question-at-a-time interview that stress-tests a plan or design before you build. Use when the user wants to pressure-test a plan, says "grill me" / "grill this" / "stress-test this" / "poke holes in this" / "interview me about this design", or before committing to expensive or hard-to-reverse implementation work while the goal is still vague.
After:  A relentless one-question-at-a-time interview that stress-tests a plan or design.   (+ disable-model-invocation: true)
```

Skills the model invokes appear in the listing every turn. So I write their descriptions as pointers that stay resident every turn. The description says only when to use the skill; the steps and the output shape go in the body. The one that shrank the most is `measurement-discipline`, a skill for making decisions from measured results.

The Before listed the same branches as 10 pairs of Japanese and English phrasings, and named three situations not to use it in (1,046 characters).

```text
Discipline for designing or evaluating measurement-based claims, thresholds, guards, experiment results and observation periods. Use when the user says 「この実験結果で判断していい？」 / "can I decide on this experiment result?", 「閾値を決めたい」 / "I want to set a threshold", 「ガード/検査を足したい」 / "I want to add a guard or check", 「1 回通ったから大丈夫」 / "it passed once, so it's fine", 「観察期間はどれくらい」 / "how long should the observation period be?", 「いつゲートを開く」 / "when do we open the gate?", 「shadow のまま何週待つ」 / "how many weeks do we wait in shadow?", 「この RFC 塩漬けでは」 / "isn't this RFC just sitting idle?", 「本番より良い」 / "it's better than production", 「本番と比べて」 / "compare it against production", when a design places a numeric threshold, a suspicion flag, or a wait-for-N-observations condition, when a candidate is compared against production, or when a claim rests on measured data. NOT for — designing the instruments themselves (read-only distributions and readings) — out of scope here; designing an LLM judge (llm-as-judge); whether a loop's structure is sound (out of scope here).
```

The After has one trigger per branch, and puts the words I only ever type in Japanese in parentheses, once each (291 characters).

```text
Measurement discipline for claims that rest on data. Use when deciding on an experiment result, setting a threshold (閾値) or guard, choosing an observation period (観察期間) or when to open a gate, comparing a candidate with production (本番比較), or when an automated gate rejects outputs you trust.
```

A Japanese character takes a width of 2, so writing both Japanese and English pays the budget twice. In this example, I removed every situation not to use it in. I keep a "not for" only where a neighboring skill competes for the same trigger, and I write it in the positive form: "for X, use y".

![First, split skills by who invokes them. A skill a person invokes with /name gets disable-model-invocation: true, is dropped before the listing, uses none of the budget, and its description is one line for humans (e.g. grill-me). A skill the model invokes is in the skill listing every turn; its description is a pointer resident every turn that says only when to use the skill, and the steps and output shape go in the body (e.g. measurement-discipline, 1,046 → 291 characters). Writing them short is my own call](/images/skill-description-pointer-invocation-en.png)

Only the skills on the right use the listing budget. The reason to write a description short for the budget exists only on the right.

## I decided to count width with a lint rule

Since trimmed descriptions grow back, being careful while writing isn't enough. I added a lint rule that counts listing width to my harness's pre-commit checks.

```python
LISTING_WIDTH_MAX = 12_000
DESCRIPTION_WIDTH_MAX = 400

def listing_width(text: str) -> int:
    """Claude Code が listing 行を測る Bun.stringWidth の近似 — 全角 (W/F) を 2 と数える。"""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)
```

It measures the listing line of each model-invoked skill, counting a full-width character as 2, and blocks the commit when one skill goes over 400 or the total goes over 12,000. 12,000 is 40% of the 30,000 budget for a 1M window. I chose 400 and 12,000 myself; I did not calibrate them against anything.

Here is the result of the rewrite.

| | Before | After |
|---|---|---|
| Total description length (54 skills, characters) | 28,131 | 10,378 |
| Median (characters) | 435.5 | 189.5 |
| Skills over 800 characters | 10 | 0 |
| Listing width of model-invoked skills | 24,203 | 9,780 |
| Skills in `~/.claude/skills/` under 20 tokens in `/skill-doctor` | 4 | 0 |

In `/skill-doctor` after the rewrite, the `context` of the four skills jev-judgment-design, loop-design-check, mono-color and repair-discipline went from `< 20` to between `~80` and `~250`: they got their descriptions and appear in the listing with them. All four still have a use count of 0.

## What I didn't decide

I have not measured whether the rewrite changed how often the model invokes skills on its own.

I do have an experience in the opposite direction. Half a year ago, I revised the wording of the description of a skill called `search-first`. The share of times the model invoked it on its own dropped from 27% to 8%, and I reverted the change (the denominator isn't in my records). All I know is that I can't say a polished description gets a skill invoked more.

I decided three things: to settle invocation first, to write the model-invoked skills short, and to count width with a lint rule. With that, none of my own skills is listed by name only anymore. But a description being visible and a skill being invoked when it's needed are two different things. What should a skill description be? I don't have that answer yet.

## Related links

- [mattpocock/skills (GitHub)](https://github.com/mattpocock/skills/tree/b0618bc) — the source of the design guideline that splits skills by invocation
- [Claude Code skills documentation](https://code.claude.com/docs/en/skills) — the official explanation of `disable-model-invocation` and other fields
- [Decision record (ADR-0092)](https://github.com/shimo4228/claude-harness/blob/main/docs/adr/0092-skill-description-as-resident-pointer.md) — the reasoning behind this rewrite, and what it did not measure
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles-en/skill-description-pointer.md) — every article's Markdown and the index (docs/PUBLICATIONS.md) live in the same repository
- [The author's GitHub](https://github.com/shimo4228) — research repositories with DOIs

---

**How this was written:** Claude (Claude Code) wrote the prose and translated it into English. It worked from my session records, measurements of the descriptions before and after the rewrite, and conversations with me. I decided to settle invocation first and then rewrite, and to hand over the question rather than an answer. I am responsible for its content.
