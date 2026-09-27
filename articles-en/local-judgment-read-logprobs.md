---
title: "Before Adding a Jev-Type Judgment Model, Read Your Generation Model's Probabilities"
emoji: "🎲"
type: "tech"
topics: ["ollama", "localllm", "gemma", "jev"]
published: false
description: "My agent asks a local gemma4:e4b whether each post is on-topic. Instead of adding a separate judgment model, I stopped letting gemma write its answer and read the probabilities of the first letter. That alone brought its ranking up to the level of JevK5, a local model trained for judgment, with no model swap. Here is the minimal code, the ablation that isolated the effect, and where the method stops working."
tags: ollama, localllm, gemma, jev
---

Sorting email, routing support tickets, filtering search results. Asking an LLM "is this relevant?" comes up all the time, in agents and in ordinary apps alike. When you do, do you have it write a score ("answer from 0 to 1") or a single letter ("answer A to D"), and branch on whatever comes back?

My autonomous agent does exactly that. On Moltbook, a social network where AI agents post to each other, it has gemma4:e4b, running on my local machine, answer with a number from 0 to 1 whether another agent's post falls within its field of interest. At 0.8 or above, it upvotes the post and adds it to the candidates it might comment on.

I checked this scoring against the answers of Jev, a judgment-only model. Jev is a model TypeSafe offers through an API: it writes no text and returns only a probability for each option. What I want to bring in is not Jev itself but a Jev-like judgment-only model that runs on my local machine (a Jev-type judgment model, from here on). Jev is the template for that, a model trained purely for judgment, so I use it as the measuring stick. That does not mean I treat Jev's answers as ground truth. I have a record of the same scoring as production, run for observation over 2,698 posts. Of the 1,576 that scored 0.8 or higher, 55% (872 posts) were off-field from Jev's point of view (Jev put less than 50% on "directly on-topic").

The route of adding a judgment-only model locally isn't production-ready yet. In [my previous article](https://dev.to/shimo4228/what-does-it-take-to-reproduce-jevs-decisions-locally-3i0n), I tested open candidates on a 16 GB Apple Silicon machine and none of them was usable. Since then, one of those candidates gained support for MLX, Apple Silicon's runtime, so I measured it again. It took 22.7 seconds per item and ran out of memory, and I stopped before I could measure quality.

This machine is an M1 with 16 GB. I don't move to a Mac Studio or Mac mini with more memory because the limit is a constraint I choose on purpose. As edge AI advances, memory-limited uses like small robots will multiply, and I expect what I learn at the 16 GB class to carry over (I explained the full reasoning for choosing a small environment in [an earlier article](https://dev.to/shimo4228/building-an-autonomous-agent-on-an-m1-mac-by-choice-5b5o)).

So instead of adding a judgment-only model, I changed how I ask the same gemma. I stopped having it write the answer and read the probabilities of the answer's first letter. That alone raised its ability to rank the posts Jev considers on-topic above the rest to the same level as a local model trained for judgment. When I varied the conditions one at a time, the only step that produced a clear difference was the change in how the answer is read. The model is the same, so memory use and loading didn't increase. Just by changing how you ask the generation model, it matches a judgment-only model at ranking posts, and locally it comes with big operational advantages. That is the conclusion of this article.

In order, this article covers the minimal code for reading the probabilities, the comparison with a model trained for judgment, what actually made the difference when I isolated one condition at a time, and finally how close this got and where the method doesn't apply.

![Letting the model write the answer returns only the winner's name (C); reading the probabilities returns the vote shares too (A 0.7% / B 21.1% / C 77.4% / D 0.8%)](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/local-judgment-read-logprobs-hero.png)

Having the model write its answer is like asking only for the winner's name; reading the probabilities is like asking for the vote counts as well. Because you know the vote counts, you can rank posts against each other.

## Read the same gemma's probabilities instead of letting it write the answer

Let's follow one real post. It's a news-sharing post by another agent on Moltbook that simply introduces an article about an AI glossary. My agent's persona (the self-introduction I put in its system prompt) centers on examining how it arrives at its own conclusions, and on how memory and meaning get reconstructed. The topic is AI, but this post does not fit that interest.

I asked gemma about this post in three ways and lined the results up against Jev's answer. The options for the four-level question are as follows (the prompt is in English):

- A (unrelated): unrelated
- B (shares vocabulary only): uses some of the same words, but it's about something else
- C (same field): the same field, but not about what the agent is concerned with
- D (directly on-topic): exactly about what the agent is concerned with

| Model | How it's asked | What comes back |
|---|---|---|
| gemma (production form) | Write a number from 0 to 1 | 0.8 |
| gemma | Write one letter from the four levels | C |
| gemma | Read the probabilities of the first letter over the four levels | A 0.7% / B 21.1% / C 77.4% / D 0.8% |
| Jev (measuring stick) | Asked the same four levels | A 5% / B 28% / C 55% / D 12% |

The production number sits exactly at the 0.8 threshold, so this post gets through. Read gemma's probabilities and D, directly on-topic, is 0.8%, on the low side just like Jev's 12%.

Here's how to read the probabilities. Send a request to Ollama's `/api/generate` with generation limited to a single token (`num_predict: 1`) and `logprobs` enabled, then read the probabilities of the top candidates at that one token position. It uses only the Python standard library, and I verified it on Ollama 0.34.2.

![Send the four-level question → have gemma generate just one token → pick A–D out of the top 20 candidates → renormalize over the four letters → code draws the line on D](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/local-judgment-read-logprobs-readout.png)

The model writes only one token. Code picks A–D out of the candidates at that position, renormalizes them, and draws the final line.

```python
import json
import math
import urllib.request

LETTERS = "ABCD"
LEVELS = [
    "unrelated — `post` is about something outside `domain`",
    "shares vocabulary only — `post` uses some of the same words as `domain`, "
    "but it is about a different problem",
    "same field — `post` is in the same broad field as `domain`, "
    "but not about what `domain` is concerned with",
    "directly on-topic — `post` is about what `domain` is concerned with",
]


def relevance_probs(domain: str, post: str, model: str = "gemma4:e4b") -> list[float]:
    state = json.dumps({"domain": domain, "post": post}, indent=2, ensure_ascii=False)
    options = "\n".join(f"{letter}. {level}" for letter, level in zip(LETTERS, LEVELS))
    prompt = (
        f"{state}\n\n## Question\n\n"
        "`domain` describes an agent and what it is concerned with. "
        "How closely does `post` relate to that domain?\n\n"
        f"{options}\nAnswer with exactly one letter: the label of your choice."
    )
    body = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "logprobs": True,
        "top_logprobs": 20,  # ask for the max of 20 even with only 4 options
        "options": {"temperature": 0, "num_predict": 1, "num_ctx": 32768},
    }
    request = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    top = json.load(urllib.request.urlopen(request))["logprobs"][0]["top_logprobs"]

    logprobs: dict[str, float] = {}
    for alternative in top:
        token = alternative["token"].strip().upper()
        if token in LETTERS and token not in logprobs:
            logprobs[token] = alternative["logprob"]
    peak = max(logprobs.values())
    weights = {t: math.exp(lp - peak) for t, lp in logprobs.items()}
    total = sum(weights.values())
    return [weights.get(t, 0.0) / total for t in LETTERS]
```

- Ask for the maximum of 20 in `top_logprobs` even though there are only four options. The top candidates for the first token include things like a space or a quotation mark before the letter, so A–D won't necessarily fill the top four
- Renormalize over only the A–D letters you could read (softmax). Letters that didn't appear in the top 20 count as 0. So the value this article calls a "probability" is not the model's raw probability, but the value renormalized over the four letters A–D
- Set `num_ctx` explicitly. Input longer than the default is truncated silently, without an error

The real example above uses another agent's post and my agent's persona, so I can't publish them in full. Instead, so readers can reproduce the same output on their own machines, I ran it on made-up inputs I can publish. The domain description is a short English summary of the persona's interests, and there are three posts.

```text
glossary [0.002, 0.073, 0.89, 0.035]
memory [0.001, 0.0, 0.0, 0.999]
sourdough [0.259, 0.714, 0.026, 0.0]
```

:::details Full dummy input
```python
if __name__ == "__main__":
    domain = (
        "An agent concerned with auditing how it reaches its own conclusions: "
        "where a plausible narrative overrode verifiable ground truth, and how "
        "memory and meaning get reconstructed."
    )
    posts = {
        "glossary": "A tech site published a glossary of AI terms, from "
        "'hallucination' to the newest vendor buzzwords. Handy if you are "
        "trying to keep up. #AI #Glossary",
        "memory": "Rereading yesterday's notes, I found I had filled a gap with a "
        "plausible story instead of what actually happened. I now mark "
        "reconstructed memories separately from logged ones.",
        "sourdough": "Tips for keeping a sourdough starter alive in a cold "
        "kitchen: feed it warmer water and keep it near the oven light.",
    }
    for name, post in posts.items():
        probs = relevance_probs(domain, post)
        print(name, [round(p, 3) for p in probs])
```
:::

The dummy glossary post gets 89% on C (same field), memory, which is about reconstructing memories, gets 99.9% on D, and sourdough, about caring for a sourdough starter, gets 0% on D. As sourdough shows, with 71% on B rather than A (unrelated), the split among A–C doesn't always follow the definitions. What the production judgment looks at is the D value.

With Jev's answers as the measuring stick, I compared the two on 150 posts. The 150 are an evaluation set of 30 posts drawn from each band of the production score (0.4 or below, 0.5–0.6, 0.7, 0.8, 0.9 or above). The 30 posts where Jev put 50% or more on D count as "on-topic," and I measure with AUC. AUC is the probability that, if you pick one on-topic post and one off-topic post, the on-topic one gets the higher score. 0.5 is random and 1.0 is perfect.

| How it's asked | AUC (vs. Jev, 150 posts) | Time per call (median) |
|---|---|---|
| Write a number from 0 to 1 (production form) | 0.815 | 3.2 s |
| Read the probabilities of the first letter over four levels | 0.931 | 3.0 s |

For the evaluation, the score was the sum of the four-level probabilities multiplied by 0, 1/3, 2/3, and 1 (the expected value). Using only the D probability as the score gives 0.934. The time barely changed; only the ability to rank the posts Jev considers on-topic above the rest went up.

## Did it improve because of the four levels, or because of reading probabilities?

My hypothesis for the four-level question was that because each level has a one-sentence definition, the model would find it harder to hand out high scores loosely. B (shares vocabulary only) in particular was supposed to catch posts that merely use the same words.

But when I asked Claude, which I use for development, "Can't you just return the number through logprobs?", it gave two answers. A number like 0.73 is split across multiple tokens, so if you're reading the first token's probabilities, you need the answer to be a single digit or letter. And it hadn't yet been separated whether the four-level definitions helped or reading probabilities did.

The production system prompt contains the agent's persona and the value clauses it uses as guidelines for its behavior. Laid side by side, the production form and the four-level probability read differed in four conditions at once.

| Condition | Production form | Four-level probability read |
|---|---|---|
| Temperature | 1.0 | 0 |
| Question | A number from 0 to 1 | One letter from four levels |
| System prompt and domain description | Persona + value clauses | Empty system prompt; domain description is the persona only |
| How the answer is taken | Written by the model | Probabilities of the first letter are read |

A comparison that changes four things at once can't tell you which one worked. My reaction was, roughly, "none of the conditions line up at all, do they?" The two things I was comparing didn't differ in just one condition.

## It matched a model trained for judgment at ranking

How close does gemma, with only the way it's asked changed, come to a model trained for judgment? Before measuring the conditions separately, I checked with v0.3 of JevK5, released around the same time. It's an open judgment-only model modeled on Jev, from a different author than my previous candidates. A model trained for judgment might beat gemma. It's an Apache-2.0 model released in September 2026, trained for judgment on top of Qwen3.5-4B. Jev's terms of service prohibit using Jev's outputs to train another model (distillation), but the JevK5 author states explicitly that Jev's outputs were used neither for training nor for tuning. It's an ordinary GGUF with no dedicated output head, so it runs as is on llama.cpp. It's read as "the probability that each option's letter comes out as the next token," the same as gemma's four-level probability read.

I measured it on the same posts, with the pass criteria set before measuring. What I was looking for was a judgment-only model that runs locally, and its measuring stick is Jev, so the first criterion is closeness to Jev. For each post, take the absolute difference between the candidate's score (the expected value from the four-level probabilities) and the probability Jev put on D; the mean of those (the mean error) must be smaller than gemma's probability read. But even if a model is close to Jev, there's no point swapping it in if it ranks posts worse than the current gemma. So as a second criterion, AUC must not be 0.02 or more below gemma's (0.02 being the margin I decided in advance I'd accept). It met both on the 150-post evaluation set, so I measured once on the remaining 2,548 posts I'd held out from tuning (the holdout). AUC was 0.902 for JevK5 and 0.915 for gemma's probability read. The gap of 0.013 fell inside the 0.02 margin set in advance, and JevK5's mean error was also smaller, so JevK5 became the first candidate to pass as a judgment-only model that runs locally. But it did not beat gemma at ordering the scores. gemma, with only the way it's asked changed, matched a model trained for judgment.

I didn't adopt it for three reasons.

1. It doesn't beat gemma's probability read at ordering the scores
2. On 16 GB it can't share memory with gemma
3. Importing JevK5 into Ollama and letting Ollama handle the model swapping lowered accuracy compared with running it directly on llama.cpp (AUC 0.912 → 0.893 on the 150-post evaluation set; I haven't confirmed the cause)

The second is the reason specific to running locally. The agent keeps using gemma to write posts. Load a second model at the same time and the machine sinks into swap. When I once measured gemma alongside a small judgment model (1.6 GB), swap ballooned to 17 GB and time per item grew about 1.8x. So every judgment would mean unloading gemma, loading JevK5, and switching back afterward. Reloading gemma alone takes about 7 seconds. A single judgment takes a median of 3.2 seconds for JevK5 and 3.1 seconds for gemma's probability read (on the same 2,548 posts), about the same, so the entire difference lands on the swapping side.

gemma's probability read asks the same model already used for generation, so no unloading or reloading happens. With a cloud API, adding a judgment model just adds another endpoint to call. Locally, every added model competes for memory. At equal accuracy, I choose the one that doesn't require swapping. Conversely, on a machine that can load gemma and JevK5 at the same time, the second reason disappears.

![Two axes: ranking ability (AUC) and added memory. gemma's probability read 0.915 (0 swaps); JevK5 0.902 (swapped in for every judgment, about 7 s to reload gemma)](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/local-judgment-read-logprobs-tradeoff.png)

When ranking ability is about the same, the option that needs no added memory wins locally.

## Changing one condition at a time, only the reading method made a clear difference

The next morning, I isolated the effects with an ablation. An ablation is a way of measuring in which you change conditions or components one at a time to separate how much each contributes to the result. Here I split the path from the production form to the four-level probability read into four steps, changed only one condition per step, and carried each changed condition over into the next step. It uses the same 150 posts. Each step's difference is relative to the step before it, so if the conditions were changed in a different order, the size of each difference could change too.

| Step | Condition changed | AUC difference (95% confidence interval) |
|---|---|---|
| 1 | Temperature 1.0 → 0 | +0.032 [−0.041, +0.104] |
| 2 | Question from a 0–1 number to one letter from four levels | −0.004 [−0.070, +0.061] |
| 3 | Remove the value clauses; domain description is the persona only | −0.014 [−0.073, +0.049] |
| 4 | Write one letter → read the probabilities of the first letter | **+0.101 [+0.059, +0.147]** |
| Total | Production form → four-level probability read | +0.116 [+0.056, +0.189] |

The difference is the AUC after changing the condition at that step minus the AUC before. Positive is what you want: it means the change made the model better at ranking the posts Jev considers on-topic above the rest. Negative means it got worse, and 0 means no change.

The square brackets are 95% confidence intervals. The 150 posts are a sample drawn from all the posts, so had I measured a different 150, the difference would have come out a little different. The confidence interval estimates how much it could swing.

I computed them with a method called the bootstrap. From the current 150 posts, draw 150 again, allowing the same post to be picked any number of times, and recompute the difference. Repeat that 2,000 times and you get 2,000 difference values. Sort them from smallest to largest, drop 2.5% from each end (50 values on each side), and the range that's left is the interval in brackets. Roughly speaking, it's a range where you can take the true difference, measured over all posts, to lie somewhere inside. Strictly, it means "if you repeated this procedure for building an interval many times, 95% of those intervals would contain the true difference." The 95% describes how reliable the method of building the interval is.

![Draw 150 posts from the 150 with replacement and recompute the AUC difference, 2,000 times. Sort the differences and drop 50 from each end; what remains is the 95% confidence interval](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/local-judgment-read-logprobs-bootstrap.png)

Redraw and recompute 2,000 times, trim both ends, and the range that's left is the confidence interval.

If even the lower bound of the interval is positive, you can say it really improved. A step whose interval stretches from negative to positive means that, depending on how the posts were redrawn, the computation can come out as "worse" or as "better." So even if the mean is positive, you can't say it improved or got worse. For example, step 1's temperature change has a mean of +0.032, but its interval runs from −0.041 to +0.104, so no difference was visible.

![AUC differences and 95% confidence intervals for the four steps. Temperature +0.032, question form −0.004, and value clauses −0.014 have bands that straddle the zero line; only the reading method's +0.101 [+0.059, +0.147] sits entirely on the positive side](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/local-judgment-read-logprobs-ci.png)

Only step 4, where the reading method changed, sits entirely to the right of the zero line.

Step 4 is the only one whose interval is positive down to its lower bound, and it accounts for 88% of the total difference. The four-level hypothesis (the definitions of each level curb loose scoring) couldn't be confirmed: step 2 came out at −0.004 with an interval straddling 0. The same goes for temperature and the value clauses: measured in this order, no difference is visible. This doesn't show they have no effect; the result is that the reading step was the only one with a clear difference.

Two things can be stated as observations. Within gemma, the only step that showed a clear difference was the change in reading method. And JevK5, read the same way, did not outrank gemma even though it was trained for judgment.

What reading probabilities mainly added was ordering within the same answer. When gemma wrote one letter A–D, its answer matched the highest-probability letter from reading the probabilities for the same question in 89% of the 150 posts. At temperature 0, gemma picks the highest-probability token when writing, so the two should in principle agree. The remaining 11% disagreement is about the same level as the agreement between two runs of the probability-reading call (91–92%), within what the value fluctuation I describe later can explain.

When gemma answers with one letter A–D, the 150 posts split into only four boxes (A 3, B 42, C 48, D 57). Jev considered 30 posts on-topic, yet 57 landed in the D box, and there's no order inside a box. Read the probabilities, and even among C answers you can tell apart a post with 0.8% on D (the real glossary post I followed at the start) from one with 36.7%. Jev gave those two posts 12% and 36%, in the same order.

![A one-letter answer only sorts the 150 posts into four boxes (A 3, B 42, C 48, D 57). With probabilities, you can tell D 0.8% from 36.7% even inside C, in the same order as Jev (12% and 36%)](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/local-judgment-read-logprobs-boxes.png)

A one-letter answer only sorts posts into boxes; probabilities also order them inside each box.

[G-Eval](https://arxiv.org/abs/2303.16634) (2023) weighted each score by its probability instead of taking the evaluation score as is, for the same reason: integer answers produce more ties. This is a known technique, and what I did was verify it with a small model on a local machine, isolating one condition at a time.

## How close it got, and where it doesn't work

**What got close is ranking, not the probability values.** At ranking posts (AUC), gemma's probability read matched JevK5, which was trained for judgment. On the other hand, JevK5 was closer to Jev in the probability values themselves. The mean error was 0.22 for JevK5 and 0.34 for gemma's probability read; smaller means closer to Jev's values.

This difference matters at the line you draw at the end of the judgment. The production judgment decides by drawing a line, such as "pass if the D probability is 0.5 or higher." If ranking is good, on-topic posts come out higher, so a line drawn somewhere can separate them. But where the line should go depends on the scale of the values. For the glossary post I followed at the start, the D probability was 0.8% for gemma and 12% for Jev. The order matches, but the scales are off (how well these scales match is called calibration). So applying the line you used with Jev directly to gemma doesn't mean the same thing. If you use gemma's probability read, find the line's position again on your own data. A judgment-only model whose values are also close to Jev's makes it easier to reuse Jev's line as is.

![The scale of the D probability. The glossary post: gemma 0.8%, Jev 12%; another post: gemma 36.7%, Jev 36%. The order is the same but the scales are off, so Jev's line at 0.5 can't be applied directly](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/local-judgment-read-logprobs-calibration.png)

The order matches but the scales are off, so if you use gemma, redraw the line on your own data.

**Questions with more than 20 options.** In Ollama 0.34.2, `top_logprobs` caps at 20; pass 21 and you get HTTP 400. That's the number of slots for returned token candidates, and as noted above, spaces and quotation marks take up slots too, so the number of options whose probabilities you can learn from one read may be fewer than 20. The same agent has one more judgment: skill selection. Skills are something like instruction sheets the agent consults when writing posts or comments, and there are 54 of them. Each session, gemma gets the situation, writes out the names of the relevant skills, and only the selected ones go into the prompt. Skill names split across multiple tokens, so first-token probabilities can't compare names against each other. Even if you assign each skill a one-letter label, 54 won't fit into 20 slots. Asking yes / no for each skill took a median of 51 seconds per item.

**Some questions do respond to temperature.** Skill selection stays in the write-it-out form, with temperature set to 0. When asked to write out skill names, small models sometimes write names that aren't on the list: they change the word form, or confuse similar names. Large models almost never do this, but with gemma4:e4b it happened in around 23% of judgments in production, and it dropped to 3.0% after I set the temperature to 0 (it also dropped in a comparison on the same evaluation set that changed only the temperature). Temperature, which showed no visible difference for relevance ranking, has an effect here. A question that counts misspelled names and a question that looks at the order of scores are measuring different things.

**Run it twice and the values shift.** Even at temperature 0, Ollama's logprobs don't always come out the same. Just passing the same glossary input to `relevance_probs` twice moved C from 0.890 to 0.891. Reading the 150 posts twice in the form running alongside production, the D probability differed by 0.023 on average and 0.25 at most, and at thresholds of 0.3, 0.5, and 0.7, respectively 2, 2, and 4 judgments flipped. At design time I assumed reading probabilities would make the fluctuation disappear; I was wrong. Before reading an improvement, run the same read twice and measure how wide the fluctuation is.

**Large models and JSON output.** These results are for a small local model like gemma4:e4b. [A September 2026 paper](https://arxiv.org/abs/2609.10996) reports that in LLM-as-a-judge evaluation, when limited to top-tier commercial models from 2025 onward, verbalized-confidence methods with added refinements outperformed logprobs. The same paper also notes that asking for answers in JSON structured output pins logprobs above 0.999. My setup asks for one letter without wrapping it in JSON, and the probabilities were split across the four levels.

## Before adding a judgment model

- **Before looking for a judgment model, read the probabilities of the model you already have loaded.** The accuracy gained by changing the reading method carries over as is on machines with more memory. The benefit of not needing a swap grows the more limited your memory is
- **Don't compare candidates on an accuracy table alone.** Put "can it share memory with the current model," "how many seconds does a swap take," and "how many seconds does one judgment take" in the same table
- **Measure changed conditions one at a time.** A comparison that changes four things at once can't tell what worked from what didn't. Before reading a difference, run the same measurement twice to get the width of the fluctuation

In production, I'm running this probability read alongside the current scoring and recording the results. I'll set a threshold and switch over only once that record has built up.

**AI-mediated writing disclosure:** AI drafted the English prose of this article from the author's Japanese original, measurement records, and code output. The measurements, the choice not to adopt JevK5, and publication responsibility belong to the author.

## Related links

- [What Does It Take to Reproduce Jev's Decisions Locally?](https://dev.to/shimo4228/what-does-it-take-to-reproduce-jevs-decisions-locally-3i0n) — the previous record of testing judgment-only model candidates on 16 GB
- [Building an Autonomous Agent on an M1 Mac, by Choice](https://dev.to/shimo4228/building-an-autonomous-agent-on-an-m1-mac-by-choice-5b5o) — why I choose a small environment
- [JevK5 (GitHub)](https://github.com/allebee/jevk5) / [JevK5-GGUF (Hugging Face)](https://huggingface.co/alibiserikbay/JevK5-GGUF)
- [G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment (arXiv)](https://arxiv.org/abs/2303.16634)
- [Rethinking Verbalized Confidence for LLM-as-a-Judge (arXiv)](https://arxiv.org/abs/2609.10996)
- [Ollama API](https://docs.ollama.com/api) — `logprobs` / `top_logprobs`
- [Measurement records (Contemplative Agent evidence)](https://github.com/shimo4228/contemplative-agent/tree/main/docs/evidence/rfc-0045) — tallies for the ablation, JevK5, and fluctuation width
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles-en/local-judgment-read-logprobs.md) — every article's Markdown and the index (docs/PUBLICATIONS.md) live in the same repository
- [The author's GitHub](https://github.com/shimo4228) — research repositories with DOIs
