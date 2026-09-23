---
title: "Moving My Research Pipeline's Judgment Calls from an LLM to Jev, a Judgment-Only Model"
emoji: "🔬"
type: "tech"
topics: ["jev", "pydanticai", "aiagents", "llm"]
published: false
description: "My daily research agent spends most of its time deciding whether each source is relevant and whether it says anything new. I moved those closed judgments from Claude Opus to Jev, a model that writes no text, and the key was to pass the question being judged against every time. Here is the pipeline, the Pydantic AI types, three papers Jev placed on a four-step relevance ladder, and why writing stays with an LLM."
tags: jev, pydanticai, aiagents, llm
---

Every morning I have an AI agent search for papers and repositories and write research reports. Most of the agent's work is reading what it found, one source at a time, and deciding: "Is this relevant to what I'm looking into right now?" and "Does it say anything new?" Until now, Claude Opus made those calls too, along with everything else.

"Is it relevant?" and "Is it new?" can be answered with a yes or no, or with a rating on a few levels. So I moved just those judgments to [Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev), a judgment-only model that writes no text. The key was this: every time I ask Jev "is this relevant?", I also hand it what the source should be relevant to, namely the question that research topic is currently trying to answer.

From Pydantic AI, you call Jev with the same one line as any other model.

```python
from pydantic_ai import Agent

agent = Agent("typesafe:jev-1.13.0", output_type=Answers)  # Answers is a Pydantic model listing the judgment fields
```

![Given only a source, Jev is left asking "relevant to what?"; given a source and one question, it answers on a ladder of different problem, same field, same problem, and same question](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/jev-research-judgment-offload-hero.png)

Hand Jev a single source on its own and it can only ask "relevant to what?" Hand it the source together with one question, and it places the source on a four-step ladder: a different problem, the same field, the same problem, or the same question. A grader can't grade an answer sheet without the exam question, and Jev is the same: it gets the thing to judge against along with the thing to judge.

## The morning research I used to leave entirely to Opus

I have eight research topics (I'll call them *lines* from here on), and each morning I produce reports for three or four of them. The old setup launched Opus with `claude -p`, gave it WebSearch and WebFetch, and let it run freely for up to 55 turns. Where to search, whether a source it read was relevant, what was new, how to write it up: the Opus instance launched for each line decided all of it. The cost `claude -p` reported in its output was $13–15 per day over the last three days. (I don't compare that with the new pipeline's cost in this article, because I haven't confirmed the Jev portion against an actual bill.)

"Where to look" and "how to write" are open-ended work. There is no fixed set of answers. "Is this source relevant?" and "Is this strong evidence?" are closed: the shape of the answer is fixed in advance. A closed judgment is one you should be able to hand to a model built only for judging.

## The pipeline at a glance

Alongside the existing setup, I built a separate pipeline with the flow below. The table shows the final version, for processing one line. Each line produces one report in Obsidian. Each morning's run handles three lines in rotation, plus one line that tracks developments around Jev.

| Step | Name | Handled by | What it does |
|---|----|------|----------|
| 1 | Read the questions | Code | Reads the file of "questions this line is currently trying to answer." Claude (Opus 5.5) drafted the questions in advance from sources such as the repository's knowledge graph, and I reviewed them |
| 2 | Read the search terms | Code | Reads the search terms for each question. Claude (Opus 5.5) also wrote these in advance from the questions, test-ran them, and then wrote them into the question file. Changing a question means regenerating its search terms |
| 3 | Fetch | Code | Pulls sources from arXiv, Hugging Face Papers, GitHub, and new-release listings |
| 4 | Screen sources | Jev | Is it likely relevant to a question? Does it contain evidence? Does it have instructions embedded in it? Is the source trustworthy? |
| 5 | Judge source × question | Jev → code | Jev answers with one source paired with one question; code applies thresholds to the probabilities and decides accept, needs review, or reject |
| 6 | Judge sentences | Jev, code | For each sentence in an accepted source, asks Jev whether it advances the question or is already known. Whether the source really says it is first checked by code with string matching |
| 7 | Write per question | LLM → Jev | An LLM writes a section for each question whose evidence grew that day; Jev checks its quality |
| 8 | Output the report | Code | Assembles the sections and saves the report to Obsidian |

Jev answers the closed questions, and code decides what moves forward based on those answers. Claude is used only to write the questions and search terms in advance; it isn't called even once during the morning run. During the run, an LLM writes text only for the body in step 7 and when generating candidate questions for the following days. (For questions that don't have search terms yet, an LLM also generates candidates in step 2 and Jev picks among them.) This article covers the judgments in steps 4–6.

![Claude writes the questions and search terms in advance; at run time the pipeline moves through prepare (code), judge (Jev answers, code decides), write (LLM then Jev), and output (code)](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/jev-research-judgment-offload-pipeline.png)

Claude's part ends before the run starts. At run time the pipeline moves through four blocks: prepare (code), judge (Jev answers, code decides), write (an LLM writes, Jev checks), and output (code). Only the judgment block in the middle has the "Jev answers, code decides" shape.

Where to fetch sources from, in what order, and how many: for now, code decides that. It uses the search terms written in advance, and nothing reads the results to decide where to look next. I think exploration is properly an LLM's job, ReAct-style: read the results, then pick the next place to look. The pipeline runs fine as it is, but depending on report quality I may hand exploration back to an LLM.

Every model used at run time (Jev and the LLMs) is called through Pydantic AI's `Agent`. I picked Pydantic AI for two reasons. It added native support for Jev's TypeSafe models early. And I didn't want to build an agent runtime from scratch: call the model, validate the output against a type, retry on failure. Swapping models takes one string. In fact, partway through I switched the run-time LLM that generates candidates (called through Alibaba's DashScope API) from Qwen's lightweight model to DeepSeek V4.1 Flash, because I had used up the free quota. The report body is written by qwen3.8-max.

With Jev, once you write the output type, each field's type determines how Jev is asked.

| Pydantic type | How Jev is asked |
|--------------|---------------|
| `float` (0–1) | Probability that the answer to the question is "yes" |
| `Literal[...]` | Pick one of the options |
| `IntEnum` with docstrings | Graded rating |

All the fields in one output type are sent together in a single request ([Pydantic AI's TypeSafe model docs](https://pydantic.dev/docs/ai/models/typesafe/), as of 2026-09-23).

## Ask alongside a question

To ask Jev "is this relevant?", you have to give it what the source should be relevant to. In this pipeline, that's the per-line questions. For each line I keep three to five questions I'm currently trying to answer in a file. On the line about AKC, a framework for how agents manage knowledge that I research, one of the questions reads like this (the file is in Japanese; translated here):

```markdown
<!-- excerpt from questions/akc.md (translated from Japanese) -->
## How is intent alignment between an agent and its operator maintained in the parts tests can't check?
- brief: AKC's claim is that "a bidirectional growth loop maintains the alignment that tests can't check." How do designs that make similar claims (harness self-evolution, memory architectures, approval gates) detect alignment degrading, and on what grounds do they say it improved?
- evidence: Measurements over time. Single-shot benchmarks are weak
- not: Alignment training of the model alone (RLHF, etc.)
```

`brief` is the scope of the question, `evidence` is what counts as evidence, and `not` lists topics that share keywords but aren't what this question is about. For this question, 21 papers with "alignment" in the title actually came through to judgment. Many of them only share the word, such as papers on mapping between audio and representations (cross-modal alignment). Under `not`, I write the neighboring topics that are most easily confused with the question (here, alignment training of the model alone), so Jev can use them in its judgment.

Every judgment is asked as a pair with a question. In step 4, for each source, Jev is asked cheaply, in one batch, whether it's likely relevant to each of the line's questions, to narrow the candidates. In step 5, each remaining "one source × one question" pair gets asked in detail. Step 6 is "one sentence × one question."

The rest of this section is about step 5. Step 5 asks, on a four-step ladder, how close the problem a source works on is to the problem the question asks about. From the bottom: "a different problem that only shares vocabulary," "the same field but a different problem," "the same problem," and "answers the same question."

For this intent-alignment question, Jev judged three papers, each with "intent" in the title, as follows.

| Paper | Probability relevant | Most probable step | That day's report |
|------|----------------|------------------------|------------------|
| [AI Persona, Service Consumption, and User Intent Entropy](https://arxiv.org/abs/2609.23274) (a field experiment on AI personas and how much user intent varies) | 0.08 | Different problem (0.60) | Not included |
| [FinInteract](https://arxiv.org/abs/2609.24002) (a benchmark for clarifying intent in ambiguous financial questions) | 0.20 | Same field, different problem (0.53) | Not included |
| [SkillSpec](https://huggingface.co/papers/2609.06052) (has a model infer whether an agent's skill behaves as specified, with the intent withheld) | 0.44 | Same problem (0.77) | Not included |

All three share the word "intent," but paired with the question, they land on different steps. SkillSpec was placed on "same problem," but its probability of being relevant was 0.44, short of the code's 0.5 threshold, so it didn't make the report. Jev only returns probabilities; code makes the accept or reject call with a threshold. The judgment values come from my local run logs, which aren't included in the repo.

![Against the intent-alignment question, User Intent Entropy lands on different problem (0.60, relevant 0.08), FinInteract on same field (0.53, 0.20), and SkillSpec on same problem (0.77, 0.44); none reaches the 0.5 relevance threshold, so all three are rejected](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/jev-research-judgment-offload-ladder.png)

The figure puts the three papers on the ladder: User Intent Entropy on "different problem," FinInteract on "same field," and SkillSpec on "same problem," with the relevance probabilities 0.08, 0.20, and 0.44 all below the 0.5 threshold. The step Jev picks and the "relevant" probability that code applies a threshold to are separate answers.

Here's the state I hand Jev (simplified from `state()` in `question_screening.py`). It gets serialized to JSON and passed to `agent.run()`.

```python
state = {
    "line": {"name": line.name, "vocabulary": vocabulary},
    "question": {
        "title": question.title,
        "brief": question.brief,
        "method": question.method_constraints,
        "evidence": question.evidence_constraints,
        "not": question.negative_topics,
    },
    "source": source_state(source),  # the source's title, an excerpt of its text, URL, etc.
    "evidence_set": evidence_set,  # evidence already accepted for this question
}
```

The output type looks like this (excerpt; `Probability` is a `float` from 0 to 1). The `question.brief` and `evidence_set` in the descriptions refer to keys in the state above.

```python
class Overlap(UseEnumMemberDocstrings, IntEnum):
    other_problem = 0
    """It works on a different problem that happens to share vocabulary."""
    same_field = 1
    """Same field as `question`, but not the problem `question` asks about."""
    same_problem = 2
    """It works on the problem `question` asks about, from another angle."""
    same_question = 3
    """It asks what `question` asks and reports an answer to it."""


class Answers(BaseModel):
    """Screen one source against one open research question."""

    on_topic: Probability = Field(
        description="Is `source` about the problem `question` asks about, as `question.brief` "
        "describes it? No if it is about one of `question.not` (neighbouring topics that keep "
        "matching), or if it only shares a word with it."
    )
    problem_overlap: Overlap = Field(
        description="How close is the problem `source` works on to the one `question` asks about?"
    )
    novelty_vs_evidence_set: NoveltyVsSet = Field(
        description="Compared with `evidence_set` (the claims already accepted for this "
        "question), what would `source` add?"
    )
```

The "most probable step" column in the table is this four-step `Overlap`. The first paper fell to the bottom step: "a different problem that only shares vocabulary." Novelty is asked the same way, in terms of what the source would add to the evidence already accepted for this question.

## Numbers from the final run

The report has one section per question whose evidence grew that day. The final run processed four lines. That run came before I switched to writing search terms in advance, so the search terms were generated by an LLM and picked by Jev.

| Item | Value |
|------|-----|
| Questions to Jev per line | 1,400–1,511 (14 for one line with few new sources) |
| Report size | 7.4–12.0 KB |
| Claude calls | 0 |

Numbers alone can't tell you whether the screening also dropped sources I should have read. So on the Jev-tracking line, I placed four sources I know should pass (canaries) under its questions, and all four passed in the final run. I haven't placed canaries on the other lines yet, and I haven't measured how much the pipeline misses across everything it drops.

## Writing stays an LLM's job

Outside the pipeline, I had an Opus instance, in a context separate from the session that built the pipeline, judge the quality of the reports written in step 7. Of the three lines whose body text was written in the final run, one was good enough to publish. The typical failure in the rejected drafts was recasting the evidence in the question's own terms.

In the section for the question "When an agent breaks rules it wrote for itself, what lets that failure slip through?", the body presented a paper about false positives, which fabricate violations of rules that don't exist, as an explanation of misses that slip past the rules. Jev had let this paper through for this question just barely: probability relevant 0.54, with the step "same problem" at 0.51 and "same field, different problem" at 0.35. Letting it through wasn't wrong in itself. It was the body text that flipped the direction.

Writing is an LLM's job, so this isn't something to move to Jev. The body got better after I fixed the instructions (don't let the evidence paragraph state conclusions) and turned on thinking for qwen3.8-max. I see the remaining weakness as a question of which model does the writing. The writer is also a Pydantic AI `Agent`, so it can be swapped with one string for a model that's stronger at prose, such as GPT. I haven't measured yet whether swapping helps.

## What to check before handing judgments to Jev

- **Did you put what's being judged against into the state?** Without something to be relevant to, "is it relevant?" lets anything through. Pass the question, its scope (`brief`), the topics to exclude (`not`), and the evidence already accepted
- **Is the answer closed?** Move only judgments that can be expressed as a yes/no probability, a choice among options, or a graded rating. For a graded rating, describe each step as a concrete situation (`same_field` is "the same field, but not the question's problem")
- **Is there a step where sources that only share vocabulary can land?** Without a "different problem" step, Jev has no choice but to push them onto a nearby step
- **Did you place sources that should pass?** A smaller volume on its own can't be told apart from dropping too much
- **Is the writing LLM on the same `Agent`, with its own model string?** Then you can swap just the writing model without changing the judgment types

The code is public at [jev-research-pipeline](https://github.com/shimo4228/jev-research-pipeline).

**AI-mediated writing disclosure:** AI drafted and translated the prose of this article from the author's pipeline code, run records, and the public sources cited above. The pipeline design, the choice of which judgments to move to Jev, and responsibility for publication belong to the author.

## Related links

- [How Close to Opus Does Jev, a Model That Writes No Text, Get at Skill Selection in 0.3 Seconds?](https://dev.to/shimo4228/how-close-to-opus-does-jev-a-model-that-writes-no-text-get-at-skill-selection-in-03-seconds-1nfj)
- [I Added Jev's Skill Router to Claude Code and Turned Back Just Before Rewriting the Skill Listing](https://dev.to/shimo4228/i-added-jevs-skill-router-to-claude-code-and-turned-back-just-before-rewriting-the-skill-listing-34in)
- [What Does It Take to Reproduce Jev's Decisions Locally?](https://dev.to/shimo4228/what-does-it-take-to-reproduce-jevs-decisions-locally-3i0n)
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles/jev-research-judgment-offload.md) — the Japanese original; this English version is `articles-en/jev-research-judgment-offload.md`, and every article's Markdown and the index (docs/PUBLICATIONS.md) live in the same repository
- [The author's GitHub](https://github.com/shimo4228) — research repositories with DOIs
