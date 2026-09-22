---
title: "What Does It Take to Reproduce Jev's Decisions Locally?"
emoji: "📏"
type: "tech"
topics: ["localllm", "aiagents", "llm", "benchmarking"]
published: false
description: "Four local model candidates — qwen3:8b, Laya, kev-0.8b, and AFM 3 Core — replayed the same 150 skill selections Jev solves in 0.3 seconds. All four failed, each for a different reason. The failures reveal 3 conditions a local decision model needs: calibrated probabilities, prefix-cache-friendly attention, and context length that is both sufficient and trained at that length."
tags: localllm, aiagents, llm, benchmarking
---

| Model | Method | Agreement with Opus ceiling | Time per row | Result |
|-------|--------|---------------------------|-------------|--------|
| Jev (hosted) | choice+noul | 0.346 | 0.3 s | ✓ Baseline |
| gemma4:e4b | logits x 54 questions | 0.162 | 51 s | Existing baseline |
| **qwen3:8b** | logits x 54 questions | — (stopped at 4 rows) | 43–74 s | ❌ Too slow |
| **Laya** | noul | 0.075 | 39 s | ❌ Random-level |
| **kev-0.8b** | choice | — (stopped at 25 rows) | 6.9 s | ❌ Out of memory |
| **AFM 3 Core** | verbalized | — (20 rows only) | 20.7 s | ❌ Context too short |

*"Agreement with Opus ceiling" = Jaccard index measuring how much each model's selections overlap with those of Opus 5, treated as the upper bound. Details in "Measuring with 150-row replays." Random expectation: 0.056. Method descriptions follow in the next section. AFM = Apple Foundation Models (the on-device model in macOS 27). Its context length (the maximum text a model can process at once) is only 4,096 tokens — too short for the full prompt — so it was tested on just 20 rows with the catalog cut in half; AUC was 0.443. Jev's numbers are from [the previous article](https://dev.to/shimo4228/how-close-to-opus-does-jev-a-model-that-writes-no-text-get-at-skill-selection-in-03-seconds-1nfj).*

I tried to reproduce the skill-selection judgment that TypeSafe's decision model Jev solves in 0.3 seconds, using four candidates that run locally. As the table shows, all four failed. But the causes of failure split into three, and they reveal the conditions to evaluate next time a local decision model is on the table.

## 30+ open alternatives and 3 approaches

In [the previous article](https://dev.to/shimo4228/how-close-to-opus-does-jev-a-model-that-writes-no-text-get-at-skill-selection-in-03-seconds-1nfj), Jev reached about half the agreement ceiling — using Opus 5's picks as the upper bound — in 0.3 seconds per row for skill selection in an autonomous agent. But Jev is a closed API. As of September 2026, there are no open weights and no self-hosting path.

Within a week of Jev's launch, over 30 open alternatives appeared (a catalog is at [systemonemodels.org](https://systemonemodels.org/examples/alternatives/)). None of the trained decision-only models (kev, von, Laya, etc.) run on Ollama, though. Ollama requires GGUF-format weight files, and none of the decision-only models ship GGUF. On top of that, these models replace the standard text-generation output layer with a custom head that returns only select/don't-select probabilities — Ollama's general-purpose inference engine cannot handle that.

The approaches you can try fall into three categories.

![Three approaches to local decision models](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/local-decision-approaches.png)

1. **Logits method** — Ask a general-purpose LLM "Should we select this skill?" as a yes/no question and read the yes and no probabilities (log-probabilities = logits) via Ollama's `logprobs` option. No fine-tuning needed, but you pay 54 calls for 54 skills
2. **Typed-decisions method** — Use a classifier trained specifically for decision tasks. Pass all 54 skills and the situation at once, and receive the "should select" probability for each skill in a single response. Instead of generating text like a general-purpose LLM, it outputs only an array of probabilities
3. **Specialized decoder method** — Replace the "text-generation part" of a general-purpose LLM with a "decision-only output part" and run the resulting small model through a dedicated server

I picked one from each category. qwen3:8b is the smallest Ollama-compatible general-purpose LLM where prefix cache (explained below) works. Laya is the only decision-only model with a public Python API. kev-0.8b is the highest-profile project aiming to reimplement Jev. I also added Apple's on-device model (AFM 3 Core, Apple Foundation Models) available through the FoundationModels framework in macOS 27. AFM is not open, but it ships with macOS and requires no extra installation.

## Measuring with 150-row replays

The measurement method is the same as last time. I fed 150 rows of actual skill-selection logs from an autonomous agent into each model and compared the agreement with Opus 5's picks. The test environment is Apple Silicon M1 (16 GB) using MPS (Metal Performance Shaders — Apple's GPU compute framework, analogous to NVIDIA's CUDA), running Ollama 0.34.2.

Three metrics:

- **Jaccard@topk** — The overlap between the skill sets Opus picked and the model picked. Calculated as "skills both picked / skills either picked." If Opus picked {A, B, C} and the model picked {A, B, D}, the overlap is {A, B} = 2, the union is {A, B, C, D} = 4, so Jaccard = 2/4 = 0.5. 1.0 means perfect agreement, 0 means zero overlap
- **AUC** — Higher when the skills the model assigned high probabilities to are the ones Opus also picked. Measures ranking quality: 0.5 equals random, 1.0 means perfect ranking
- **ECE (calibration error)** — How well a model's stated confidence matches its actual hit rate. When a model says "80% confident this should be selected," does it actually get it right 80% of the time? Calibration is the property of a model's probabilities matching real-world accuracy. ECE of 0 means perfectly calibrated. High ECE means you cannot trust the probability numbers for decision-making

The skill-selection prompt runs about 12,000 characters (skill catalog ~9,600 characters + situation description median 1,537 characters). The maximum text a model can process at once is called its context length. This prompt size matters later.

## qwen3:8b — 54 questions pile up

First, the logits method. Ollama 0.34.2 returns the top-20 token probabilities with `logprobs: true`.

```bash
curl -s http://localhost:11434/api/generate \
  -d '{"model":"qwen3:8b","prompt":"...Should we select this skill? Answer yes or no:","stream":false,"logprobs":true,"top_logprobs":5,"options":{"num_predict":1,"temperature":0}}'
```

For each of the 54 skills, ask "Should we select this skill?" and read the yes log-probability.

The 54 prompts share a common prefix — "skill catalog + situation description" (~12,000 characters) — with only the trailing "Should we select this skill?" part changing per question. Prefix cache holds the processing result of this shared part in memory so that from the second question onward, only the changed tail gets processed.

![How prefix cache works](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/local-decision-prefix-cache.png)

I first tried qwen3.5:9b, but even though the 54 prompts share a common prefix, every question after the first still took over 5 seconds. Prefix cache was not working. Switching to qwen3:8b, the second question with a different suffix returned in 0.4 seconds.

```text
qwen3.5:9b — same prompt resent: 0.3 s / different suffix: 7–12 s (full reprocessing)
qwen3:8b   — same prompt resent: 0.3 s / different suffix: 0.4 s (prefix cache active)
```

LLMs compute relationships between tokens using an attention mechanism. Standard Transformer attention examines every pair of tokens, which is expensive, but the intermediate results (the KV cache) can be saved and reused. The hybrid linear attention that qwen3.5 uses trades cheaper computation for what I suspect is an inability to reuse KV cache from just the shared prefix. I switched to qwen3:8b, which uses standard Transformer attention.

With cache active, the first question took 14.2 seconds; the rest had a median of 0.63 seconds. Per row: 43-74 seconds. The gemma enum method from the previous round passes all 54 skills at once in a single call and gets an answer in ~13 seconds per row; the logits method runs 54 serial calls, making it 3-5x slower. I cut it off at 4 rows.

The serial execution of 54 calls is the fundamental bottleneck of the logits method. Even with prefix cache, 0.63 s x 54 = 34 seconds is the floor.

> **How to tell if prefix cache is working:** The `prompt_eval_count` (input token count) in Ollama's response reports the original full token count whether or not the cache is active, so that number alone does not reveal cache status. If `prompt_eval_duration` (time to process the input) drops significantly, the cache is working.

## Laya — the wall called calibration

Calibration, as explained in the previous section, is the property of a model's stated probabilities matching actual hit rates. "70% confident" means it really hits 7 out of 10 — that is what being calibrated means. Laya hit a wall here.

![What calibration means](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/local-decision-calibration.png)

Laya is a typed-decisions model based on mmBERT-base (322M params), available on [HuggingFace](https://huggingface.co/convaiinnovations/laya). I used two question formats:

- **noul** — Returns yes/no probabilities per skill
- **choice** — Picks the best from a set of options, returning each option's probability

Results over 150 rows:

| Metric | Laya (noul) | Laya (choice) | gemma (logits) | Random |
|--------|-------------|---------------|----------------|--------|
| Jaccard@topk | 0.075 [0.062, 0.089] | 0.051 [0.041, 0.061] | 0.162 [0.141, 0.182] | 0.056 |
| AUC | 0.587 [0.561, 0.611] | 0.477 [0.455, 0.499] | 0.728 [0.704, 0.750] | 0.500 |
| ECE | 0.469 | — | — | — |

*Brackets show 95% confidence intervals.*

Noul's Jaccard of 0.075 barely exceeds random (0.056). Choice's confidence interval includes random — indistinguishable.

The core problem is calibration. Breaking down ECE 0.469: of 8,207 total judgments, 6,382 (78%) fell in the 0.5-0.7 probability band, where the actual hit rate was 10-14%. "60% confident this should be selected" actually hits 1 in 10.

Laya prints this warning at startup:

```text
laya: this checkpoint ships temperatures outside [0.5, 5]
which would distort confidence; clamping choice:11+=0.1006.
Treat confidence from the affected buckets as uncalibrated.
```

What this means: Laya uses an internal temperature parameter (which adjusts the sharpness of the output probability distribution) to compute probabilities. In this checkpoint, cases with 11 or more options (bucket = group by number of options) have temperatures outside the normal range, so the probability values are force-corrected (clamped). Selecting from 54 skills falls into the 11+ range, so the returned probabilities are not calibrated.

I also checked latency. The model card cites 33 ms per question (7 ms batched) on an NVIDIA T4 GPU, but my test environment uses Apple Silicon (MPS). Different hardware, so a direct comparison is not meaningful, but the measured values in this environment were: noul median 39.4 seconds per row (54 questions), minimum 6.8 seconds; choice 10.5 seconds, minimum 1.7 seconds.

Laya's problem is quality, not speed. When probabilities cannot ground decisions, you cannot run a policy like "delegate only the high-confidence rows to Jev's replacement."

## kev-0.8b — 0.8B devours 12 GB

Last, the specialized decoder kev-0.8b. It mounts a decision head on Qwen3.5-0.8B-Base and runs through a dedicated server.

Sending one request as designed (~6,000 tokens, choice + noul for 54 skills) immediately ran out of memory.

```text
RuntimeError: MPS backend out of memory
(MPS allocated: 12.50 GiB, other allocations: 7.02 GiB,
 max allowed: 20.13 GiB).
Tried to allocate 880.00 MiB on private pool.
```

Splitting works. Choice alone (2,432 tokens) takes 8.6 seconds; noul split into batches of 14 takes 7-27 seconds. But running choice alone continuously, the MPS memory allocator failed to allocate even 16 KB after processing 17 rows. The server does not release GPU memory between requests.

Two constraints are at play:

- **Inference kernel** (the program that executes the model's computation on the GPU): kev's `flash-linear-attention` implementation targets NVIDIA (CUDA) and AMD (ROCm) GPUs and does not support Apple Silicon's MPS. It falls back automatically to the unoptimized reference implementation, printing a `"much slower"` warning at server startup
- **Input length**: Training was done at 384 tokens or fewer. The serving config can set `num_ctx` to 8,192, but the gap from the 12,000-character prompt to the training input length remains large

I cut it at 25 rows, taking only the choice-alone results. Working around the allocator issue would require periodic server restarts, and I could not see a path to completing the full 150 rows.

## AFM 3 Core — context length falls short

macOS 27 made the FoundationModels framework available. On the M1 (16 GB), the model that arrives is `AFM 3 Core` (3B) with a 4,096-token context length. Too small a window for text generation, but a decision model's input and output are short, so I tried it on the off chance. The larger `AFM 3 Core Advanced` (20B sparse) has no model-selection API in the SDK and does not come down to M1.

The first wall is context length. The skill-selection prompt is about 12,000 characters, but AFM's context length is only 4,096 tokens. I cut the catalog in half and measured on just the first 20 rows.

`fm serve` provides an OpenAI-compatible endpoint, but it silently ignores `logprobs`. Using a verbalized approach (asking the model to state probabilities as numbers), AUC was 0.443 at temperature 0. The same 20 rows with gemma's logprobs scored 0.736. Five of the 20 rows hit a guardrail `RefusalError`, leaving half the catalog unscored.

The one advantage is co-residency. In-flight memory is about 2 GB, and it coexists with Ollama models without increasing swap. But if the prompt does not fit the window, it is not a candidate.

## 3 conditions a local decision model needs

Line up the reasons each candidate dropped out, and three conditions for practical local decision models emerge.

![Three conditions for a decision model](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/local-decision-conditions.png)

**1. Calibrated probabilities**

Laya returns probabilities, but you cannot split decisions by those numbers. ECE 0.469 means the probabilities are decorative. As the gap between Laya's typed-decisions benchmark (0.766) and its score on this task (0.075) shows, calibration depends on the task and the prompt structure.

**2. An attention mechanism that supports prefix cache**

The 54 skills share a common prefix. Without cache, every question reprocesses 12,000 characters from scratch. qwen3.5's hybrid linear attention cannot do this reuse; kev's flash-linear-attention targets CUDA/ROCm and does not run on Apple Silicon. Both the kind of attention mechanism and the inference environment are conditions.

**3. Context length of 12,000 characters — and training at that length**

kev was trained at 384 tokens or fewer. Stretching `num_ctx` at serving time does not guarantee quality when the gap from training is that wide. AFM's context length is physically 4,096 tokens — the 12,000-character prompt does not fit. Input length must not only be "accepted by the config" but also "trained at that length," and the window must be wide enough.

---

In response to these results, I introduced a seam called `DecisionBackend` on the agent side. Setting the environment variable `DECISION_MODEL` switches the decision surface to a local model — ready to swap in a model that meets the conditions.

Looking back, Jev's performance is in a different league. Calibrated probabilities, context length that absorbs long inputs, an attention mechanism that supports prefix cache — it meets all three conditions, and on top of that returns 0.3 seconds per row at half the Opus ceiling. The fact that the four candidates each dropped out at a different condition throws into relief what Jev accomplishes at that price and speed.

Four triggers would reopen the evaluation: kev implements an MLX backend, Laya gets fine-tuned on this task's data, Jev itself publishes open weights, or AFM's context length is extended. The moment any one of those moves, I re-measure with the same 150 rows.

**AI-mediated writing disclosure:** AI drafted the English prose of this article from the author's Japanese original, measurement records, and terminal output. The measurements, the synthesis into three conditions, and publication responsibility belong to the author.

## Related links

- [Previous article: How Close to Opus Does Jev, a Model That Writes No Text, Get at Skill Selection in 0.3 Seconds?](https://dev.to/shimo4228/how-close-to-opus-does-jev-a-model-that-writes-no-text-get-at-skill-selection-in-03-seconds-1nfj)
- [systemonemodels.org — Catalog of open alternatives](https://systemonemodels.org/examples/alternatives/)
- [kev (GitHub)](https://github.com/jaredpalmon/kev) / [Laya (HuggingFace)](https://huggingface.co/convaiinnovations/laya) / [Laya (GitHub)](https://github.com/NandhaKishorM/laya)
- [Apple Foundation Models — Third Generation](https://machinelearning.apple.com/research/introducing-third-generation-of-apple-foundation-models) / [apple-fm-sdk (PyPI)](https://pypi.org/project/apple-fm-sdk/)
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles-en/local-decision-model-conditions.md) — every article's Markdown and the index (docs/PUBLICATIONS.md) live in the same repository
- [The author's GitHub](https://github.com/shimo4228) — research repositories with DOIs
