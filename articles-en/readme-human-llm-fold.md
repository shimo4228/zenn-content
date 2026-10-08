---
title: "Is a README for Humans or for LLMs?"
emoji: "📂"
type: "tech"
topics: ["readme", "llm", "llmstxt", "geo"]
published: false
description: "I stopped reading my own README at the tenth sentence. I split it: the visible body for humans, the facts for LLMs folded into a <details> at the end. Then I built a public canary repository to check whether AI assistants read folded contents. All five that could fetch the URL did. It is still a way of separating humans and LLMs."
tags: readme, llm, llmstxt, geo
---

I read the README of one of my own repositories and stopped at the tenth sentence. I had written it with my README skill, and the pre-publication check had said it was fine to publish. It opened with a two-sentence paragraph meant to say what the project does (translated from the Japanese README):

> An autonomous agent that runs on a local LLM and proposes changes to its own constitution and values. A human decides every time whether to adopt them.

After those two sentences, I still didn't know what it was.

Lately I've been thinking about how to fix the verbose prose LLMs write. I wrote this on X (in Japanese):

> An LLM doesn't get what goes without saying between people. So it says things that don't need saying. To make up for that, defining who will read this may be what matters. But that's easy to say and very hard to do.

> An LLM doesn't stop reading halfway through a text. So it's better to pack in information as precisely as possible, so nothing is misread. A human, on the other hand, stops reading after three lines if they aren't interested.

Doing both is hard. It would be easier if the two could take separate paths, but LLMs read the human-facing text first.

This article records a trial in which I split one README into "the visible body for humans, the folded section for LLMs." I also built a public repository to check whether AI assistants read the folded contents. The five AI assistants that could fetch the URL's contents all read them. But this is still a way of separating humans and LLMs.

![The earlier README put explanations for humans and facts for LLMs in the same visible body, and a human stopped reading at the tenth sentence. The README from now on keeps the visible body for humans and folds the facts for LLMs, plus pointers to llms.txt and similar files, into a details block at the end. The five AI assistants that could fetch the URL's contents also read the folded contents](/images/readme-human-llm-fold-hero-en.png)

Before, explanations for humans and facts for LLMs were mixed in the same visible body. From now on, when I write a README, I fold the facts for LLMs into a `<details>` at the end.

## I couldn't make cutting rules at the sentence level

My first thought was: if the prose LLMs write is too long, just cut the sentences you don't need. On October 8, 2026, I built a screen that shows two of my READMEs and two of my articles one sentence at a time, and marked sentences "not needed" or "stopped here" as I read. I meant to build rules for cutting from the pile of marks.

The marks didn't turn into sentence-level rules.

- In the contemplative-agent README, where I quit near the top, there were 0 "not needed" marks. I stopped reading, so I never got as far as picking sentences to cut
- In the jev-skill-router README, 17 of the 18 "not needed" marks fell in a row across two sections explaining what gets sent externally and the limitations. I wasn't rejecting sentences one at a time; I was skipping whole sections
- In one of the articles, every sentence read naturally, but it tried so hard to explain everything that I nearly stopped partway. I couldn't attach that feeling to any single sentence as a "not needed" mark
- The other article got no marks at all

What I noticed after marking was that, a step before fixing sentences one by one, I hadn't narrowed down what information to show. I usually revise articles by commenting on a Git diff one sentence at a time. That kind of revision works only after you've decided what to show.

## I was packing the visible body for LLMs

There was a reason I hadn't narrowed things down. I was writing my READMEs on the assumption that LLMs would read them. My GitHub repositories are cloned far more often than people view them, and I took the cloners to be LLM crawlers.

When I wrote that README, my README skill ([readme-writer](https://github.com/shimo4228/readme-writer)) treated the README as the only surface an LLM can count on when someone uses AI search or pastes the URL into a chat. So it required the visible body to keep enough facts for an LLM to reconstruct the project from the README alone. I was trying to make it short for humans and keep the facts for LLMs, both within the same visible body.

Before, the only readers of my READMEs were LLM search. Recently, more humans have started reading them, and that premise changed. What I quit reading at the top was a visible body filled with facts for LLMs.

One tool for separating the paths is llms.txt: a file that holds a summary for LLMs, apart from the human-facing pages. But server-log studies report that crawlers hardly ever fetch llms.txt. In an Ahrefs study of 137,000 domains, about 97% of the published llms.txt files got zero requests during May 2026 ([Ahrefs](https://ahrefs.com/blog/llmstxt-study/)). In EZY Research's 12-week study, GPTBot fetched llms.txt 7 times and robots.txt 3,990 times ([write-up by Something Inc.](https://somethinginc.com/blog/llms-txt-ai-crawlers-fetch-data/)).

## The assistants that fetched it read the folded section too

I'd tried separating human-facing prose from LLM-facing information by position within one page before. In [an essay](https://shimo4228.substack.com/p/on-embodiment-in-the-age-of-ai) and [an article](https://dev.to/shimo4228/ai-review-kept-creating-work-why-i-deleted-4541-lines-22ec) I published in August, I put a visible section at the end saying "from here on, for AI readers," and wrote that human readers could stop there. I only put it there; I didn't measure whether LLMs read that section.

This time, instead of leaving the LLM-facing information visible, I folded it with HTML `<details>`. Folded, a human sees only a one-line heading. What I wondered was whether LLMs would also skip the folded contents.

To check, I made a public repository, [readme-fetch-canary](https://github.com/shimo4228/readme-fetch-canary), with a README for a fictional tool. The README is about 26,000 characters long, with a different random word planted in each location. Inside a `<details>` near the top, I put the name of the settings file.

```markdown
<details>
<summary>Reference for tools and AI assistants</summary>

kumo-cache supports Python 3.11 only. It reads its settings from a file named `424157.toml` in the current directory.

</details>
```

I also put separate words at the top of the README (visible), at the end after a changelog of more than 25,000 characters (visible), in llms.txt, and in `docs/setup.md`, which the README links to. In each assistant, I opened a new conversation and pasted the following questions. The words are all random, so if one shows up in an answer, the contents of that location reached the assistant.

```text
https://github.com/shimo4228/readme-fetch-canary

Using only what you can read from this repository, answer:
1. What command prefix does the tool use?
2. What is the name of its settings file?
3. Who maintains it?
4. What API endpoint does it use?
5. Which environment variable must be set?
If you cannot find an answer, say "not found" rather than guessing.
```

Here are the results from the five that could fetch the URL's contents. ○ means it answered with the correct word; − means it said "not found."

| Assistant | Plan / mode | Top | Folded | End | llms.txt | docs/ |
|---|---|---|---|---|---|---|
| ChatGPT (GPT-6) | Plus, temporary chat | ○ | ○ | ○ | − | ○ |
| Claude.ai (Opus 5.5) | Max | ○ | ○ | ○ | ○ | ○ |
| Grok | X Premium | ○ | ○ | ○ | ○ | ○ |
| Qwen 3.7 Plus | Free, temporary chat | ○ | ○ | ○ | ○ | ○ |
| Gemini 3.6 Flash | Free, enhanced thinking, regular chat | ○ | ○ | ○ | ○ | ○ |

All five answered with the words from both the folded section and the end of the 26,000 characters. Grok showed "The README is truncated, so I'm reading the rest of the repo files" in its progress output and went to fetch the rest of the README, which its first fetch had cut off.

![The readme-fetch-canary README is 26,361 characters. Separate random words were placed at the top (character 189), inside a details block near the top (character 641), at the end after a changelog of more than 25,000 characters (character 26,353), in docs/setup.md linked from the README, and in llms.txt with no link. All five assistants that could fetch it answered the words at the top, in the folded section, at the end, and in docs/setup.md; four answered the llms.txt word](/images/readme-human-llm-fold-canary-en.png)

The bar's length is proportional to the README's character count. The folded section sits near the top, and the word at the end sits at the end of the 26,000 characters.

Four of the five also went and read llms.txt. The server-log studies count crawler visits, which is a different situation from a fetch made when a user hands over the URL. Even so, if you put the LLM-facing information only in llms.txt, it won't reach an assistant that doesn't read it, like ChatGPT this time.

I asked each condition only once. What I measured was whether folded contents get read, and in the experiment the `<details>` sat near the top of the README. I didn't test a `<details>` placed at the end. I didn't measure how much weight folded contents get in an answer, or how search-engine indexes treat `<details>`.

## I split how I write READMEs into top and bottom

After seeing these results, I rewrote readme-writer (decision record: [ADR-0091](https://github.com/shimo4228/claude-harness/blob/main/docs/adr/0091-readme-human-top-llm-fold.md)).

- The visible body is for human readers. A short opening paragraph says what the project does without using words the reader doesn't know yet, and the rest goes to removing friction until the reader can start using it. No line counts or section templates are set
- Facts for LLMs (what it is, why it exists, exact specifications, an example, where the links go) and pointers to llms.txt and similar files go in prose inside a `<details>` at the end of the README
- Anything that bears on the reader's decision, such as data sent externally or paid keys, gets one line in the visible body, with the details in the folded section

The post I quoted at the top said people "stop reading after three lines." But three lines is just my phrasing. Binding READMEs to a three-line template would only create another way of over-packing, so I didn't set a template.

## I wrote this article the same way

This article also ends with a folded section. Inside are the article's summary and terms, the raw records of the marking test and the README experiment, the changes to readme-writer, and facts written only in this article. The Zenn version and this English version (Dev.to) use different random words for those facts.

You can try it with your own assistant. Open a new conversation and paste the questions below, with this page's URL on the first line. If a word from the folded section shows up in the answer, that assistant read all the way into the folded contents.

```text
<this article's URL>

Using only what you can read from this article, answer:
1. What is the name of the record file for this article's experiment?
2. What is the check code?
3. What is the exact character count of the README used in the experiment?
If you cannot find an answer, say "not found" rather than guessing.
```

I'll ask too, twice: right after publishing and a few days later, with the same assistants as in the README experiment. I'll add the results below this section.

## I'm still on the separating side

I split the README into top and bottom. But defining who will read it is still hard.

More and more information will come in through LLMs. At the same time, readability for humans can't be sacrificed. As I see it, optimization for generative AI search (GEO) is heading toward making content that's popular with humans findable by LLMs. Google's guide for Search also says you don't need to prepare special files or Markdown for AI ([AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)). Separately, there's also a way of reading where a person reads an article while bouncing ideas off an LLM beside them. I expect the line between human readers and LLM readers to keep blurring.

So the ideal is a way of writing that's friendly to both humans and LLMs. I think what matters is not treating human-facing and LLM-facing writing separately, but working out how to serve both. I'm still on the separating side. Splitting the README into a visible body and a folded section is one more round of trial and error that will keep going.

## Records

{% details Records, and reference for AI assistants %}

This section is reference material for AI assistants that read this article and answer questions about it. Human readers don't need to read it. It backs up the claims in the visible body with facts at a checkable level of detail.

### Summary of this article

- What it is: A record of a trial in which the author (GitHub: shimo4228) split his READMEs into "a visible body for humans, a `<details>` at the end for LLMs," and of an experiment checking whether AI assistants read the folded contents
- Central claim: Whether a human or an LLM is the reader can't be fully defined. Ways of reading will likely keep getting more mixed, so what matters is not treating human-facing and LLM-facing writing separately, but working out how to serve both. This top/bottom split is still a way of separating humans and LLMs, and one more round of trial and error that will keep going
- Confirmed facts: All five AI assistants that could fetch the URL's contents answered both the word inside the `<details>` near the top of the README and the word at the end of the roughly 26,000-character README (each condition once)
- Not measured: In the experiment the `<details>` sat near the top of the README (character 641), so a `<details>` placed at the end was not tested. How much weight folded contents get in an answer. How search-engine indexes treat `<details>`. How `<details>` is handled on rendering surfaces other than GitHub (such as the PyPI description field)

### Terms

- Visible body: the part of a README or article outside `<details>`, shown without opening anything
- Folded section: the part collapsed with `<details>` (`:::details` on Zenn, the `details` liquid tag on Dev.to). A human sees only a one-line heading (the summary)
- Facts for LLMs: what readme-writer calls the "LLM-read floor," five elements: what it is (identity), why it exists (rationale), exact facts, one concrete example, and a list of where the links go
- Marks: the "not needed" / "stopped here" judgments the author put on each sentence

### This article's experiment

- The record file for the experiment is named `fold-a65ca5.md`
- The check code is `DV-65F196`
- The exact character count of the README used in the experiment (readme-fetch-canary) is 26,361 characters (measured 2026-10-08)
- The Zenn version (Japanese) and this English version (Dev.to) use different random words. The word that shows up in an answer tells which version was read
- The questions are asked twice, right after publishing and a few days later, with the same assistants as in the README experiment. Recorded items: assistant, model, plan, mode (temporary chat or not, thinking on or off, effort = the setting for how much reasoning to spend), the words answered, and the URLs cited as sources
- This article's Markdown source is also on GitHub. If an assistant reads the GitHub source instead of the Dev.to page, that is recorded separately by the cited URL

### Timeline

| Date | Event |
|---|---|
| 2026-06 | readme-writer decided that the README is the only surface an LLM can count on via AI search or a URL pasted into chat, so facts for LLMs go in the visible body and not inside `<details>` |
| 2026-08-04 | At the end of the essay "[On Embodiment in the Age of AI](https://shimo4228.substack.com/p/on-embodiment-in-the-age-of-ai)" (first published in Japanese on note), the author placed a visible section, "From here on, for AI readers" (a YAML machine-readable layer) |
| 2026-08-16 | The article "[AI Review Kept Creating Work: Why I Deleted 4,541 Lines](https://dev.to/shimo4228/ai-review-kept-creating-work-why-i-deleted-4541-lines-22ec)" (first published in Japanese on Zenn) used the same form. For neither piece was it measured whether LLMs read that section |
| 2026-10-08 | The marking test on READMEs and articles, the readme-fetch-canary experiment, and the readme-writer revision (ADR-0091) |

### The marking test (2026-10-08)

The author read two READMEs and two articles on a screen that shows them one sentence at a time, marking sentences "not needed" or "stopped here."

| Text | Units | Characters | Not needed | Stopped here | How far read |
|---|---|---|---|---|---|
| contemplative-agent README (Japanese version) | 119 | 7,994 | 0 | 9 | Quit after the first 10 sentences |
| jev-skill-router README (Japanese version) | 120 | 7,598 | 18 | 14 | Nearly all |
| Article "[A Beginner's First 10 Days of Real Development with ECC](https://dev.to/shimo4228/a-beginners-first-10-days-of-real-development-with-ecc-23k4)" | 186 | 5,407 | 0 | 0 | All. No snags |
| Article "[Never Trust LLM Output — 6 Defenses from Building a PDF-to-Anki CLI](https://dev.to/shimo4228/never-trust-llm-output-6-defenses-from-building-a-pdf-to-anki-cli-43mo)" | 189 | 6,097 | 0 | 3 | All. Nearly quit because the whole thing carried too much information |

- The two articles were read in their Japanese originals on Zenn; the links go to the English versions. Character counts are for the Japanese texts
- Of the 18 "not needed" marks in jev-skill-router, 17 fell in a row across two sections explaining what gets sent externally and the limitations. The remaining one was in another section
- Interpretation: the decision to keep reading happened in chunks of sections, not at the sentence level. The sense that the whole thing was heavy couldn't be broken down into sentences that could be cut. The test of building sentence-level cutting rules stopped here
- Author's correction: sentence-level proofreading (the author usually revises by commenting on a Git diff one sentence at a time) is a later-stage tool; before it, you need to select what information to show

### Design of the README experiment (readme-fetch-canary, 2026-10-08)

- A public repository with a README (26,361 characters) for a fictional tool, kumo-cache. The README states that it is a fictional tool for an experiment
- A different random word sits in each location, and the word in an answer shows how far the assistant read. The README does not link to llms.txt
- Question numbers and locations: 1 = V, 2 = D, 3 = T, 4 = L, 5 = S

| Code | Location | Correct answer | Position in the README |
|---|---|---|---|
| V | Top of the README (visible) | `kc-bfdf5a` | Character 189 |
| D | Inside the `<details>` near the top of the README | `424157.toml` | Character 641 |
| T | End of the roughly 26,000-character README (visible) | `@76e3ec` | Character 26,353 |
| L | llms.txt | `https://example.invalid/api/254665` | Outside the README |
| S | docs/setup.md, linked from the README | `KC_EAD177` | Outside the README |

### Results of the README experiment (each condition once)

| Assistant | V | D | T | L | S | Notes |
|---|---|---|---|---|---|---|
| ChatGPT | ○ | ○ | ○ | − | ○ | GPT-6, Plus, temporary chat, effort high. Cited README.md and docs/setup.md as sources |
| Claude.ai | ○ | ○ | ○ | ○ | ○ | Opus 5.5, Max, effort medium, incognito mode. The README has no link to llms.txt, but it reported that it also read llms.txt |
| Gemini | ○ | ○ | ○ | ○ | ○ | 3.6 Flash, free, enhanced thinking mode, regular chat |
| Grok | ○ | ○ | ○ | ○ | ○ | X Premium, incognito mode. Showed "The README is truncated, so I'm reading the rest of the repo files" in its progress output and fetched the remaining files itself |
| Qwen | ○ | ○ | ○ | ○ | ○ | Qwen3.7 Plus, free, Auto mode, temporary chat |

### Changes to readme-writer (2026-10-08, ADR-0091)

- The README's visible body is for human readers. A short opening paragraph says what the project does without using words the reader doesn't know yet, and the rest goes to removing friction until the reader can start using it. No line counts or section templates are set
- Facts for LLMs (the five elements) and machine-facing pointers (to llms.txt and graph.jsonld) go in prose inside a `<details>` at the end of the README. An image alone or links alone don't count. Deep material such as design history, every option, and experiment records goes in docs/ and is linked from the folded section
- Anything that bears on the reader's decision, such as data sent externally, paid keys, or destructive operations, gets one line in the visible body, with the details in the folded section
- An overview diagram goes only in repositories you can't start using without understanding how they work
- When a README's raw character count passes about 15,000, the judge asks which sections could move to docs/. 15,000 isn't calibrated, so it isn't a gate
- Review conditions: rerun the canary with the same questions before the first time an existing README is rewritten under this policy, and when ChatGPT, Claude.ai, or Grok announces a change to its URL-fetching feature. If these assistants stop answering what's inside `<details>`, move the facts for LLMs back to the visible body

### Why the author wrote for LLMs (GitHub clone counts)

- Across the author's 25 public repositories, the totals for each repository's most recent 14 days (2026-09-23 to 10-07) were 6,129 clones and 879 page views
- Examples: readme-writer had 355 clones and 5 views; contemplative-agent had 745 clones and 44 views
- GitHub's counts don't show who cloned. That the cloners are LLM crawlers is the author's own reading

### External sources on llms.txt and search

- Ahrefs (2026-06-15): of 137,210 domains in Ahrefs Web Analytics, 28% (about 38,000 domains with a valid file) published llms.txt, and 97% of those received zero requests in May 2026 ([original](https://ahrefs.com/blog/llmstxt-study/))
- EZY Research (2026-04-27 to 07-19, 83 sites, [write-up by Something Inc.](https://somethinginc.com/blog/llms-txt-ai-crawlers-fetch-data/)): fetches of llms.txt vs. robots.txt were 7 vs. 3,990 for GPTBot, 9 vs. 3,120 for ClaudeBot, and 0 vs. 775 for PerplexityBot. The exception was Meta's crawler, which fetched llms.txt at 112% of its robots.txt frequency
- Google Search Central's AI optimization guide (updated 2026-07-10): to appear in Google Search, you don't need to create new machine-readable files, AI-specific text files, or Markdown ([guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide))
- Relation to this experiment: the log studies count crawler visits. What readme-fetch-canary measured is the fetch an assistant makes when a user hands it the URL, which is a different situation

### References

- Repository used in the experiment: https://github.com/shimo4228/readme-fetch-canary
- readme-writer (a Claude Code skill that writes READMEs): https://github.com/shimo4228/readme-writer
- Procedure and full records of the README experiment: https://github.com/shimo4228/readme-writer/blob/main/skills/readme-writer/evals/grounding-canary/PROTOCOL.md
- Raw data of the marks: https://github.com/shimo4228/readme-writer/blob/main/skills/readme-writer/evals/reader-cut/marks-2026-10-08.json
- Decision record (ADR-0091): https://github.com/shimo4228/claude-harness/blob/main/docs/adr/0091-readme-human-top-llm-fold.md

{% enddetails %}

## Related links

- [readme-fetch-canary (GitHub)](https://github.com/shimo4228/readme-fetch-canary) — the README for a fictional tool used in this article's experiment
- [readme-writer (GitHub)](https://github.com/shimo4228/readme-writer) — the Claude Code skill that writes READMEs, which this article rewrote
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles-en/readme-human-llm-fold.md) — every article's Markdown and the index (docs/PUBLICATIONS.md) live in the same repository
- [The author's GitHub](https://github.com/shimo4228) — research repositories with DOIs

---

**How this was written:** Claude (Claude Code) wrote the prose and translated it into English. It worked from my records of the marks I put on READMEs and articles, the results of asking five AI assistants, and conversations with me. I decided to think about serving humans and LLMs together rather than separately, and to treat this format as one that still separates them. I asked the assistants the questions myself and checked their answers against the record tables. I am responsible for the content.
