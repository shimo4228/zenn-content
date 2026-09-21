---
title: "How Close to Opus Does Jev, a Model That Writes No Text, Get at Skill Selection in 0.3 Seconds?"
emoji: "🎯"
type: "tech"
topics: ["aiagents", "llm", "localllm", "benchmarking"]
published: false
description: "Over the same 150 skill selections, Jev — a model that writes no text — reached 0.346 agreement with Opus, about half of Opus's 0.678 agreement with itself. Its top pick was one Opus also picked in 83% of cases, and across the 45 cases where that top probability cleared 0.5 it never disagreed. 0.3 seconds per case, five cents for all 150: about 1/50th of Opus's time and about 1/560th of its cost. Here is how I asked, what the numbers cannot say, and why I still cannot put it into an agent that stays on one machine."
tags: aiagents, llm, localllm, benchmarking
---

I took the step an autonomous agent runs before it acts — picking, out of a catalog, the skills that apply to the situation in front of it — and had Jev and Claude Opus do it over the same 150 cases. Jev is the model TypeSafe opened early access to on September 15, 2026. It writes no text; it returns answers over a set of options and the probabilities behind them ([TypeSafe's announcement](https://typesafe.ai/blog/introducing-system-one-models-and-jev)).

The yardstick is Opus itself. Run the same 150 cases through Opus a second time, and its agreement with the first run is 0.678. Picking at random gives 0.056. Jev came in at 0.346 — about half of Opus's agreement with itself, and more than twice the small model on my machine. The skill Jev ranked first is one Opus picked too, in 83% of the cases. Across the 45 cases where it ranked something first with probability 0.5 or higher, not one disagreed with Opus. Time is 0.3 seconds per case, and the 150 cost about five cents: about 1/50th of Opus's time and about 1/560th of its cost.

Once Jev runs on my own machine, I want to move most of this agent's processing of the same kind over to it. Jev today is hosted, and this agent, which I keep complete on one machine at hand, cannot take it yet.

| Picker | Agreement with Opus | Time per case | Cost for 150 |
|---|---|---|---|
| Opus (second run) | 0.678 | 15.3 s | $26.26 |
| **Jev** | **0.346** | **0.32 s** | **$0.047** |
| local gemma4:e4b | 0.143–0.162 | 9.8 s | — |
| Picked at random | 0.056 | — | — |

The baseline is Opus's first run. The range for gemma is the range across eight output configurations I tried. Opus's picks are the baseline, not the ground truth. Time and cost were not measured under matched conditions, so I put them under "What this comparison cannot say."

## One skill selection, in full

The subject is an autonomous agent I run (Contemplative Agent). Before it acts, the agent receives a description of the situation and a catalog of skills — name and description pairs — and picks the ones that apply. It may pick several, and it may pick none. The catalog runs 53 to 57 entries depending on the period.

Right now a small model running on my Mac (gemma4:e4b) writes out the names of the skills that apply. Because it picks by generating text, each run takes around ten seconds, and 20–30% of the time it produces a misspelled skill name. A model that picks without writing came out, so I tried it.

The agent logs the input and output of every skill selection. Out of those logs I pulled 75 cases that contained a misspelled skill name and 75 that did not; those are the 150. From here on I call one case one row.

Look at one of those rows. The catalog for this row holds 54 skills.

| Skill | Opus | Jev's probability | local gemma |
|---|---|---|---|
| `analogy-mapping-relationships` | picked | 0.61 | picked |
| `analyzing-systemic-governance-loops` | picked | 0.12 | — |
| `trace-structural-authority` | picked | 0.07 | — |
| `cross-reference-foundational-claims` | — | 0.02 or less | picked |
| `detecting-abstract-to-operational-constraint-shift` | — | 0.02 or less | picked |
| `scope-boundary-mapping` | — | 0.02 or less | picked |
| `shifting-focus-from-state-to-process-mechanics` | — | 0.02 or less | picked |
| `identify-structural-tensions-via-system-metaphors` | — | — | misspelled |

Opus picked the same three skills both times. The three Jev gave the highest probabilities are those same three. gemma wrote six names, one of them not in the catalog. The real one is `identifying-…`; the word form is broken. Names that are not in the catalog get dropped by the code, so gemma's selection comes to five.

When this article says "agreement with Opus," it means the number both picked divided by the number either picked (the Jaccard index). On this row gemma shares one and either-picked seven: 1÷7, or 0.14. For Jev, taking the same number of skills gemma picked from the top of the probability ranking (how that number is set comes in the next section), all three of Opus's picks are in, giving 3÷5, or 0.60.

This row is one of Jev's best. gemma's 0.14 happens to be the same value as its average across the 150 rows. One row says nothing, so I count across 150.

## How I asked Jev

I used two kinds of question. What TypeSafe's docs call Choice — pick one out of a set of options — and what they call Noul — a yes-or-no question. I made each row one request, with one Choice question and one Noul question per skill.

```json
{
  "state": {"situation": "(the situation description)"},
  "model": "jev-1.13.0",
  "questions": {
    "choice": {
      "type": "choice",
      "instructions": "(the selection criteria) Which single learned skill applies best to `situation`?",
      "criteria": {
        "analogy-mapping-relationships": "(this skill's description)",
        "none of the above": "No skill in the catalog applies to this situation."
      }
    },
    "n0000": {
      "type": "noul",
      "instructions": "(the selection criteria) Does the learned skill `analogy-mapping-relationships — (description)` apply to `situation`?"
    }
  }
}
```

In practice `criteria` holds every skill and the Nouls run as long as the skill list, so one request carries about 55 questions. Jev's questions cannot reference one another, so the selection criteria and each skill's description go into every question. Input came to about 7,450 tokens per row.

Choice returns a probability for every skill, but it does not return how many to pick. So I took, from the top of the probabilities, the same number of skills gemma picked on that row (6.0 on average) and made that the set. Opus decides the count itself (6.0 on average in its first run). The Jev row in the table at the top is this Choice value.

## Across 150 rows, how close to Opus

| Picker | Skills picked (average) | Agreement with Opus | Agreement with near-skill credit |
|---|---|---|---|
| Opus (second run) | 5.3 | 0.678 | 0.924 |
| **Jev** | 6.0 (gemma's count) | **0.346** | **0.855** |
| local gemma4:e4b | 6.0–8.1 | 0.143–0.162 | 0.755–0.784 |
| Random, same count | 6.0 | 0.056 | 0.70 |

Even asking the same Opus twice, agreement tops out at 0.678. That is the ceiling for this way of counting, and the floor is random at 0.056. Jev's 0.346 sat at about half the ceiling, more than twice gemma. gemma did not move off 0.14–0.16 whether I constrained its output with an enum or set temperature to 0 (the gemma-side record is in [the evidence in the public repository](https://github.com/shimo4228/contemplative-agent/blob/1ec4d2dcf7973e0677ded25cd36f21fe91a48c3d/docs/evidence/rfc-0043/README.md)).

Jaccard counts a neighboring, similar skill as a miss. The right-hand column measures closeness with embeddings of the skill descriptions and gives partial credit for similar skills. For each skill Opus picked, I averaged its closeness to the nearest one in the other side's selection. Every skill resembles every other to some degree, so even random scores 0.70. Between that floor of 0.70 and the ceiling of 0.924, Jev is at 0.855 and gemma at 0.76–0.78. Allow similar skills and Jev moves a bit closer to Opus's agreement with itself.

Look at the individual picked skills rather than the agreement between sets, and it gets simpler.

| What | Share Opus also picked |
|---|---|
| Skills Opus's second run picked (5.3 on average) | 85% |
| Jev's top pick (the 147 rows where Opus picked anything) | 83% |
| of those, the 45 rows where the top probability was 0.5 or higher | 100% |
| Jev's top picks taken out to gemma's count (6.0 on average) | 50% |
| Skills the local gemma picked (6.0 on average) | 25% |
| A single random pick | 11% |

Jev's top pick, at 83%, is level with the 85% for what Opus's second run picked. But Opus's 85% is measured over 5.3 picks on average, while Jev's 83% covers only its single most confident pick. Widen Jev out to six and it falls to 50%. In 5 of the 147 rows, Jev's top pick was "none of the above," which I count as a miss.

Across the 45 rows where Jev pointed at something with probability 0.5 or higher, it never once disagreed with Opus. The probability works as a cutoff separating the rows you can trust from the rows you cannot. If you take Jev's pick as-is in place of a large model, take only the high-probability rows.

## Ask one at a time, and the skills that read broadly come out on top on most rows

I ran the same comparison on the probabilities from the Nouls in that same request (per skill: does this apply?), again taking the same number from the top.

| | Choice | Noul |
|---|---|---|
| Agreement with Opus | 0.346 | 0.295 |
| Agreement with near-skill credit | 0.855 | 0.836 |
| Rows where `shifting-focus-from-state-to-process-mechanics` made the top | 34% | 77% |

Noul put that one skill in the top on 77% of rows. It is the skill gemma picked in the row shown above. Opus picked it on 16% of rows in the first run and 14% in the second. It is not that Noul says yes to everything: 35% of its probabilities are 0.5 or higher, and the median is 0.38. Noul looks at one skill at a time, so it has nothing to compare against. My reading is that a skill whose scope can be read broadly comes out on top in any situation. With Choice, which weighs every skill against the others, it drops to 34%.

For skill selection, Choice was the better fit. TypeSafe's [cookbook for skill suggestion](https://docs.typesafe.ai/cookbooks/skill_suggestion.md) is two-stage: rank broadly with Choice, then re-judge only the top with Noul. Applying a per-skill Noul to every skill, the way I asked, falls outside that usage.

## Five cents and 0.3 seconds

Opus took 15.3 seconds per row (median) and $26.26 for the 150. Jev took 0.32 seconds and $0.047: about 1/50th the time, about 1/560th the cost. All I had Opus return was a JSON array of skill names, and even so the output ran to a median of 1,373 tokens. Jev has no output tokens. The difference in time is the difference between generating tokens and not generating them. The difference in cost also carries the difference in input pricing.

Jev had 0 failures across the 150 requests, with a median of 0.32 seconds, 0.53 seconds at the 90th percentile, and a maximum of 4.5 seconds. That includes the network round trip from Japan. Input totaled 1,125,726 tokens; multiplied by the published rate ($0.042 per million input tokens, output free), that comes to $0.047. It is a computed figure, not a billed amount. Opus I called one row at a time with `claude -p`; the cost is the API-equivalent amount its response returns, and the time is the API-side duration.

## What this comparison cannot say

The baseline is Opus's picks, not the ground truth. I took no human labels. What I can say goes as far as "Jev is close to the way Opus picks" — a different claim from "Jev's picks are right." And gemma's picks being far from Opus's does not mean gemma is wrong.

Conditions unfavorable to Jev are mixed in with repurposing of my own. The situation text contains Japanese, and TypeSafe itself writes that languages other than English are [not handled equally](https://docs.typesafe.ai/models.md). Choice is a question meant to pick one, and using its probabilities as a ranking is my repurposing.

Nor is the handoff matched. Opus got the same situation, the same catalog and the same selection criteria, but through a different template from gemma's production one. Jev got the JSON above. The timing conditions differ too. Jev's 0.32 seconds includes the round trip from Japan, gemma's 9.8 seconds is on a 16GB M1, and Opus's is the API-side duration.

The subject is one process in one agent, 150 rows. Half were drawn from rows that contained a misspelled skill name, so this is not the production distribution as it stands. The row data contains third-party posts, so I am not publishing it.

## Once it runs on my machine, I want to move processing of this kind to Jev

This agent has several other steps that only pick, or only judge. Right now every one of them runs on the local gemma by generating text. Looking at these results, if Jev ran on my machine I would want to move most of them over. It lands more than twice as close to Opus as the gemma I run today, in 0.3 seconds, with no misspelled names and a probability attached.

What keeps it out today is that Jev is hosted. This agent is designed and run so that skill selection and text generation alike stay complete on one machine at hand. Having no path out to the outside in the production code is this agent's premise for safety. The 16GB M1 and the small model are [a constraint I chose](https://dev.to/shimo4228/building-an-autonomous-agent-on-an-m1-mac-by-choice-5b5o) as well. Jev has neither open weights nor a self-hosting path yet. Once it can run on a local runtime like Ollama, it is the first thing I will try.

For this measurement I sent the 150 rows of situation text to both Jev and Opus. That was a measurement I permitted once, from a script separate from the production code. I judged it a different thing from production sending data out on every run.

There is no shortcut where I take logs of Jev's picks as a teacher and train the small model on my machine. Section 2.3(b) of TypeSafe's [Master Customer Agreement](https://typesafe.ai/legal/mca) (updated September 19, 2026) prohibits distilling a model from the outputs and training a model to imitate them.

Skill selection turned out to be a process that does not need text written for it. A model that only attaches probabilities to options came, in 0.3 seconds, to about half of Opus's agreement with itself. If your agent's design allows calling an external API, there is no reason to wait. Taking the rows Jev points at with high probability as they are, and sending the rows where the probability falls short of 0.5 (about 70% here) to a bigger model, is an idea worth trying.

**AI-mediated writing disclosure:** AI drafted the prose of this article from the author's measurement records, the aggregated result files, and the public evidence in the repository. The central thesis, the choice of Opus as the yardstick, the judgment about adopting Jev, and publication responsibility belong to the author.

## Related links

- [The gemma-side tallies and reading (evidence in the public repository)](https://github.com/shimo4228/contemplative-agent/blob/1ec4d2dcf7973e0677ded25cd36f21fe91a48c3d/docs/evidence/rfc-0043/README.md)
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles-en/jev-vs-opus-skill-selection.md) — every article's Markdown and the index (docs/PUBLICATIONS.md) live in the same repository
- [The author's GitHub](https://github.com/shimo4228) — research repositories with DOIs
