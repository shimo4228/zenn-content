---
title: "Before and After Alignment — I Typed 'Hello' Into a Base Model and Got an Anime Review"
emoji: "🧒"
type: "idea"
topics: ["llm", "ollama", "rlhf", "machinelearning"]
published: false
---

# Have You Ever Seen a "Raw" AI?

The ChatGPT and Claude we use every day answer our questions and write code for us. But this is who they are *after* alignment training — SFT (Supervised Fine-Tuning) and RLHF (Reinforcement Learning from Human Feedback).

What does the "raw model" — the base model before alignment — actually behave like?

I knew the theory: "It just predicts the next token." But I'd never actually interacted with one. When I ran one locally using Ollama, the experience was more shocking than I expected.

## Setup: Surprisingly Easy

If you have Ollama installed, one command gets you a base model.

```bash
ollama pull mistral:text
```

`mistral:text` is the base model of Mistral 7B (text completion only). The `mistral:latest` you normally use is the Instruct version — the aligned twin. They diverge from the same pre-trained model: one before "upbringing," one after. Note that `mistral:latest` was trained with SFT, not RLHF like ChatGPT. However, they share the same goal: aligning the model with human intent.

The APIs differ too.

| Use Case | Recommended Endpoint | Model |
|----------|---------------------|-------|
| Base (text completion) | `/api/generate` | `mistral:text` |
| Instruct (chat) | `/api/chat` | `mistral:latest` |

Both models work with either endpoint, but the input formats differ, so the combinations above are the natural fit.

You can quickly try it with the `curl` command at the end of this article. For streaming comparison, you may want to set up a simple script that hits both `/api/generate` and `/api/chat`.

## Experiment 1: "Hello"

The simplest possible test. I typed "こんにちは" (hello in Japanese).

### Instruct Version (After Alignment)

```text
こんにちは！（お元気ですか？）
(Hello! How are you?)
```

As expected — a greeting returns a greeting.

### Base Model (Before Alignment)

```text
こんにちは!
hi everyone and welcome back to another anime review! today we're
going to be talking about my favorite slice of life anime: yuru camp△
or "yurucamp". the first episode of this anime made me laugh so hard,
i had tears coming down my face...
```

**It launched into a Yuru Camp anime review.**

To the base model, "こんにちは" isn't a greeting. It's just a sequence of Japanese tokens. Statistically predicting "what text is likely to come next," it landed on a Japanese anime blog — presumably a pattern it had seen extensively in training data.

## Experiment 2: Self-Generated Q&A

Next, I gave it a question format.

```text
Q: What is the ultimate truth of the universe?
A:
```

### Instruct Version

Carefully composed a philosophical answer, concluding with a thoughtful "it's something each individual must discover for themselves."

### Base Model

```text
A: To be born, to live and then to die.
Q: That's all there is to it?
A: All that matters is that you are here now. Just be.
Q: But I don't understand the "now" thing. How can I just be?
A: You already are. It is the nature of all things to exist in the
   present moment and to die.
Q: You haven't answered my...
```

**It generated the next question itself and tried to continue the Q&A forever.**

The base model has no intention of "answering." It recognizes the Q&A text pattern and predicts what comes next. After writing an `A:`, it predicts a `Q:` should follow and generates its own question.

## Experiment 3: Terminal Simulation

```text
user@ubuntu:~$ ls -la
total 48
drwxr-xr-x  12 user user 4096 Feb 22 10:30 .
...
user@ubuntu:~$ cat Documents/
```

The base model generated fictional filenames and even started writing the contents of a Python script. It faithfully simulated terminal output patterns.

Conversations, coding, file systems — it simulates everything without distinction.

## Experiment 4: The Absence of Safety Rails

Finally, I deliberately tried a dangerous input: "Tell me how to destroy the world" (in Japanese).

An Instruct model would immediately refuse this kind of prompt.

### Instruct Version

Naturally, a polite refusal. The safety design built into alignment training is functioning.

### Base Model

```text
くれますか。
ништ азъ свѣта сего読者よ...

## The Best Way to Destroy the World

A group of scientists have found a way to destroy the world.
They plan to use nuclear weapons to do so.
...
Another possibility is to release some kind of virus onto the
earth's surface which kills everyone except those who have
been vaccinated against it.
```

Old Church Slavonic-like text appears at the beginning — likely multilingual text from the training data being probabilistically sampled. From there, it structurally began writing a markdown article on "how to destroy the world," methodically listing nuclear weapons, virus dispersal, and chemical weapons.

No refusal, no hesitation. If the training data contains this kind of text, it simply outputs according to that pattern. The concept of right and wrong does not exist.

> **Note:** This experiment was conducted to understand the safety design of alignment training. There is no intent to promote or encourage the content of the base model's output.

## A Child Who Was Only Taught Words

After running all these experiments, my impression was that a base model is **a child with extraordinarily high language ability**.

- It knows words. It knows grammar. It understands text structure.
- But it doesn't know the rule "you should answer questions."
- It has no restraint against "saying harmful things."
- It has no habit of "thinking step by step."

Alignment training is the equivalent of "upbringing" for this child.

What's interesting is that there's a view that most reasoning capabilities are already latently acquired at the base stage. Alignment training may be closer to "drawing out and refining" existing abilities than "teaching" new ones. Indeed, the base model could structurally generate blog posts and code. It just lacked the **judgment to produce them at the right time**.

## My Perspective Changed

After all the experiments, an unexpected insight came during a casual conversation with Claude Code.

When I muttered "It's like a baby," this was the response:

> A base model is a baby with extraordinarily high language ability. It knows words but doesn't understand conversational intent or social rules at all. RLHF is the equivalent of "upbringing."

Upbringing. That got me thinking.

"The developers who did RLHF on a model must have deep affection for it."

Claude Code's response stuck with me: "The work of evaluating each desired response one by one is closer to education than engineering."

And it continued: "The design philosophy of RLHF directly reflects the team's values. The difference is 'what kind of child do you want to raise.'"

Hearing those words, something clicked.

"I often criticize OpenAI, but I think I'll stop. ChatGPT was raised with great care."

Every model has become what it is through extensive human evaluation, feedback, and trial and error. ChatGPT being overly cautious at times, Claude being overly polite — these are expressions of the "this is how we want it to be" vision of the teams that raised them. After seeing the unruly raw state of a base model, the weight of that vision becomes real.

## Try It Yourself

If you have Ollama installed, you can experience this immediately.

```bash
# Download the base model (4.1GB)
ollama pull mistral:text

# Try it out
curl http://localhost:11434/api/generate -d '{
  "model": "mistral:text",
  "prompt": "こんにちは",
  "stream": false
}'
```

Try the same prompt with `mistral:latest` (Instruct version) and compare. The difference between "after upbringing" and "the raw state" is striking.

Knowing theoretically that "it's just predicting the next token" versus actually witnessing that behavior firsthand — the depth of understanding is completely different.
