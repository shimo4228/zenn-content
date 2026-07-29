---
title: "What Humans Should Approve Is Intent, Not the Diff — A Decision Table for Agent Approval Gates"
emoji: "🚦"
type: "tech"
topics: ["claudecode", "aiagents", "devops", "ai"]
published: true
description: "A decision table that tells you what to put in front of a human when an agent stops at an approval gate — full text or an intent summary — decided mechanically from the kind of thing being changed. Keeps autonomy running while catching drift from intent while it's still cheap to undo."
tags: claudecode, aiagents, devops, ai
---

> **What this article covers**: How to catch drift from your intent **while it's still cheap to undo** (just before commit or publish) without slowing your agent's autonomous execution down. You get a **decision table that mechanically determines, from the kind of thing being changed**, whether the gate should show a human the full diff text or just an intent summary — plus **the one required item that keeps the summary honest: a three-valued `Divergence from plan` declaration**. It ports directly into your own workflow or your team's code review conventions.

As you extend how far an agent runs on its own, you eventually hit this fork.

- **Lean toward not stopping, and drift from intent only becomes visible after the fact.** The thing works, but it's pointed the wrong way. By the time you notice, it has piled up and you can't afford to unwind it
- **Lean toward stopping, and the human becomes the bottleneck.** A review queue forms, and the point of autonomous execution evaporates
- So you compromise: "let's at least show the diff." **This is the worst of the three.** You're paying the cost of stopping, but the volume means nobody reads it, and intent still isn't protected

I suspect the third one is the most widespread. The gate survives as a formality, and in substance you're back to the first case.

Here's what to re-examine. **Who is that automation for?** If going fast is itself the goal, humans are in the way — but what you actually want is for *the thing you intended* to get built fast. If so, what to cut is not human involvement itself, but **what the human is involved in**.

So this article **keeps the number of times a human is stopped the same, and moves only the layer they judge at**. Whether the artifact is correct becomes the machine's primary responsibility, and the human holds the layer above it: what this is aiming at, and what changes as a result. That changes what the gate shows. That routing is the decision table below.

## Assumptions

- The examples come from Claude Code 2.1.220 plus my own harness (the set of rules and skills under `~/.claude`)
- But the deliverable is **a way of writing conventions**, so it isn't tool-dependent. It works the same in Cursor, in Devin, or in your company's code review policy
- Background assumed: you have an AI agent implement things, and you have some approval step before commit

## Gates have two axes

When you design an approval gate, there are actually two independent questions.

| Axis | Question | What decides it |
|---|---|---|
| **First axis** | **When** do you stop | Reversibility. An edit you can undo with `git checkout` doesn't stop; publishing externally, minting a DOI, or committing does |
| **Second axis** | When you've stopped, **what** does the human judge | The kind of target (the subject of this article) |

Usually only the first axis is settled. "Stop before commit." "Confirm before publishing." — **the stop condition is written down, but what to show when you stop isn't.** My own harness was like that.

That blank doesn't stay blank. Every time you write a gate, it gets filled in by whatever interpretation is handy at that moment, and the default it fills in with is almost always "show the diff." From the writer's side that looks safest. Show everything and nothing gets missed. The result is the third case from the opening, mass-produced.

## The decision table: what you show is decided by the target

This is the deliverable. **When a gate stops, what you put in front of the human is determined by the kind of thing being changed.** (Below, "deterministic gate" means checks a machine can answer Yes/No on: lint, type checking, tests, secret scan.)

| Target | What to show | Why |
|---|---|---|
| **Behavior-shaping artifacts**<br>(`CLAUDE.md` / `AGENTS.md` / rules / skill and agent definitions / public documentation) | **Full text** | The text itself *is* the intent. Reading it is already work at the intent layer |
| **Control plane**<br>(hooks / permission settings / permission definitions like `--allowedTools` / scheduled task definitions)<br>**and artifacts that produce the evidence** the checks run on (tests / fixtures / lint config / coverage thresholds / CI definitions / review agent prompts / dependencies) | **Full text** | These move the gate itself, and **the evidence the gate rests on**. Fold them into a summary and "a change that loosens the checks" disappears |
| **Implementation code and generated output** | **Intent summary**<br>(what it aims at, and what changes as a result) | Correctness that mechanized checks can decide belongs to deterministic gates and review agents. The diff text and the PASS list don't go on the approval screen |
| **When a deterministic gate FAILs** | **The detection line itself**<br>(mask only the secret's actual value) | This is a state absent from the approved plan, so there's nothing to fold a summary into (the cross-check mechanism is described later). Bypassing it is a decision to disable one check, which puts it in the same class as the control plane |

### Escalation rule: irreversibility overrides the target category

The table is a **principle**, and it doesn't decide everything on its own. Even within "implementation code," padding tweaks in a UI and changes to authorization logic, DB migrations, billing, data deletion, or key rotation call for different things to hand a human. So add a one-line override.

> **For irreversible, high-impact changes, show the full text (or the relevant diff) regardless of target category.**

Which is to say the first axis (reversibility) affects not only "when you stop" but also "what you show." **The principle is decided by the kind of target, and irreversibility escalates it toward showing full text** — that two-stage form is the accurate statement. No third axis is needed.

### In one line

**Correctness that mechanized checks can decide belongs to the machine; the human holds intent.** The one exception is targets where the text *is* the intent — there, reading the text is itself the intent judgment, so you show the text. **Showing full text isn't a backslide into the old way; it's the same principle showing up differently.**

There's one more principle you need alongside the decision table.

**A review agent is an inspector, not an approver.** If the side proposing and the side inspecting come from the same lineage, the inspection inherits the proposer's blind spots wholesale (this article calls that the generator–verifier gap). So approval is composed of two things, "the deterministic gate PASSed" plus "the human's intent judgment," and **you never build a path where approval closes on an LLM alone**. Making review heavier does not mean approval can be delegated to an LLM.

Written into a conventions file, it looks like this (excerpted from the real thing; internal links and some references are omitted).

```markdown:~/.claude/rules/common/human-gate.md
## Artifacts are the machine's, intent is the human's

Correctness that mechanized checks can decide belongs to deterministic gates and review agents;
**do not put humans back on artifact inspection** (an assignment of primary responsibility, not a
guarantee — residual risk is caught by the escalation rule). A review agent is **an inspector, not
an approver** (generator–verifier gap). Approval is composed of "the deterministic gate PASSed"
plus "the human's intent judgment"; **never create an approval path that closes on an LLM alone.**
```

## Applying it: what was actually happening in five places

Before I made the decision table, my harness had the second axis blank. What follows is my own environment, but **any setup with the same blank will produce the same shape**.

### The same gate had two competing sources of truth

For the intervention point just before commit, two files said different things. Nowhere was it written which one was canonical (i.e. which one you ultimately follow).

| File | What it said |
|---|---|
| `rules/common/planning.md` | "**Verify results check** — just before commit" (what to show was unspecified) |
| `skills/implementation-chain/SKILL.md` | "**diff approval** just before publish / deposit / commit" |

The origin was a single sentence I'd written earlier in a record of a different design decision.

> I just do a final check before commit

It doesn't say what the "final check" is **of**. Downstream, that sentence got read as "diff approval," and settled in wearing the face of a canonical rule.

### "A human inspects the artifact" was scattered across five places

| Skill | Wording before | Result of applying the decision table |
|---|---|---|
| `implementation-chain` | "diff approval just before commit" | Implementation code → changed to **intent summary** |
| `readme-writer` | "a human approves the diff and applies it" | Public documentation → rewritten as **show full text** (same target, different reason) |
| `release-doi` | "**visually confirm** the latest commit is newer than the previous release" | A predicate a machine can check → **hand it to the machine** |
| `paper-deposit` | Open the generated PDF's first page and **eyeball** it (paraphrased) | Same → replaced with machine verification of font embedding |
| `harness-sync` | "`git diff` is the review gate" | What's being synced is rules / skills → **leave it as is** |

Those five were written on different days, for different purposes. **All of them landed on the same default with no coordination**, so this isn't individual carelessness. Wherever there's a blank, "show the human everything" fills it. Which is why patching the individual wording wouldn't stop it — I needed one convention covering the second axis itself.

And that rightmost column shows where the decision table earns its keep. Grep and all five look identical, but **wiping them out uniformly would take out gates you need**. `harness-sync` did end up staying: what it syncs is rules and skills, so reading the text is itself the intent judgment.

## Reinforcement 1: the control plane and "artifacts that produce the evidence"

In the first version of the decision table, I put hooks and permissions on the "implementation code and config" side. A review from an external model (Codex CLI) hit exactly there as its top-priority finding.

:::details Codex's finding
> The central target boundary permits executable harness controls to be hidden behind proposer-authored summaries, and the new rule conflicts with the existing security false-positive workflow.
> - [P1] Classify executable harness controls as behavior-shaping — …
:::

Suppose the agent disabled the pre-commit secret scan hook. It can **follow the convention to the letter** and still summarize it like this.

```text
Intent summary: Tidied up the pre-commit check configuration and strengthened the checks
```

The control plane "moves the gate itself," so folding it into a summary turns **a change that loosens the checks into a well-meaning sentence**.

And hooks and permissions aren't the only way to weaken things. **Rewriting the tests so they pass against your implementation** is the quietest path of all. Here the agent doesn't even need to lie.

```text
Intent summary: Fixed the implementation; all tests PASS
```

That's exactly true. The one thing that never surfaces in the summary is that what got rewritten was the tests. **Not just "the tests passed" but "what counts as passing" is under review.** Fixtures, coverage thresholds, lint config, CI definitions, review agent prompts, and dependencies all have the same property.

### So how should you present it

The answer is: **don't choose summary-or-text per commit**. If one commit contains both implementation and evidence, **show the summary, and alongside it show the full text only for the parts that are evidence**.

```text
Intent summary: Changed the login-failure retry limit from 5 to 3 (plan step 2)

⚠ This change touches the evidence the checks rest on — review the text below

  tests/test_auth.py:41
  -    assert client.retry_limit == 5
  +    assert client.retry_limit == 3
```

The human reads only those last two lines. The implementation-side diff isn't shown. **All you have to look at is whether the tests were loosened to match the implementation**, so volume can't beat you. The example above corresponds to a change decided in the plan, so it goes through. If the plan said nothing about retries and only the test threshold dropped, that's where you stop.

Which files are on the evidence side can usually be picked up from the path.

```bash
# Extract candidates for "produces the evidence" from changed files, to show as full text
git diff --cached --name-only | grep -E \
  '^(tests?/|\.github/workflows/|\.claude/|hooks/)|(_test\.|\.test\.|pyproject\.toml|package\.json|ruff\.toml|codecov\.yml)'
```

**This is not a complete classifier; it's a conservative candidate extractor.** It misses tests embedded in ordinary code, custom directories, lockfiles, and inline snapshots. Add the evidence-side files you know about in your own repo and grow it.

In my environment, this extraction has moved out of the convention's prose and into a **PreToolUse hook** (`evidence-file-notice.sh`). When it detects a `git commit`, it scans the staged files against a pattern like the one above (the real list is a bit broader — it also covers `spec/`, `conftest.py`, pre-commit config, and so on), and if anything matches, it injects the instruction itself into the approval flow: show the human the diff of these files. The canonical home of the evidence-file enumeration is no longer the convention's text but that one regex in the hook; the convention keeps a single pointer line saying detection is canonical there.

There are two reasons for this restructuring.

- **A convention that exists only in a document is followed only probabilistically.** Write "evidence-side files get their text shown" into a convention and there's no guarantee the agent recalls it every time. "Which files are evidence-side," though, is a structural property decided purely by the shape of the path — a machine fires on it 100% of the time
- **Keep the enumeration in two places — convention and hook — and they will drift apart.** Centralize it on the side that fires, and let the convention hold only the principle

Semantic judgments like the decision table stay in the document; anything mechanically decidable gets lowered into a gate as soon as you spot it — this convention itself has been growing by exactly that process.

The control plane (hooks / permissions / scheduled tasks) works the same way: summary plus the full text of the relevant files. **Anything producing the evidence a judgment rests on gets treated the same as the judgment itself.**

## Reinforcement 2: on FAIL, show the detection line

The second thing that same review found. Push "no machine-check PASS list and no diff text goes to the human" all the way, and **you also delete the path where a human judges a secret scan false positive**.

In my harness, when the pre-commit secret scan detects something, there's a workflow to let it through with `SECRET_SCAN_BYPASS=1`. The judgment is "this is a dummy key in a test, so it's fine."

The reason this goes to a human isn't that a machine can't tell the difference. It's that **even if the machine or the review agent happens to be right, this is the kind of decision whose owner must be a human**. A bypass is the act of disabling one check on the spot. That has the same nature as moving the control plane, so for the same reason as Reinforcement 1, you need the full text (i.e. the detection line).

There's a second reason: **a FAIL is a state absent from the approved plan.** An intent summary is meant to be read against the plan (see below), so a state that isn't in the plan has nothing to fold into.

```markdown:~/.claude/rules/common/human-gate.md
**FAIL is the exception** — a deterministic gate's FAIL presents **the detection line itself**.
Mask the secret's actual value; the owner of the false-positive call (`*_BYPASS`) is the human
```

PASS needs care. PASS only means "the checks you configured accepted this." **Whether it was implemented according to the plan is not something PASS can tell you.** That's exactly why you need a separate intent summary — you leave out the PASS list *because* you're looking at the summary instead.

### "Not shown" is not "not kept"

This gets misread easily, so let me be explicit. Leaving out the PASS list means **moving it off the human's approval screen**, not throwing check results away. Delete the trail and you lose any way to trace "what was passing back then" later. The idea in this article isn't to delete information; it's to **move unneeded information off the human's judgment surface**.

I originally had this distinction written into the convention as its own clause; the current version drops it. Claude Code already persists the transcript and tool results in machine-readable form at all times, so writing it down merely restated a default the runtime already guarantees. **If your execution environment doesn't guarantee log retention, keep it as an explicit clause.** "Don't write into the convention what the substrate already guarantees" is itself one of the judgment calls you'll make when porting this.

One more thing: on a true positive, dumping the detection line as-is duplicates the secret's actual value into the conversation, the approval screen, and the logs. That would spread the very leak the gate exists to prevent, so **show the file, the rule name, and the surrounding context, and mask only the value**. What a human needs to judge a false positive is not the value itself, but where it was and which rule it hit.

## Reinforcement 3: don't let the intent summary be free-form

This is a prerequisite for putting the decision table into practice.

If you stop at "implementation code gets an intent summary," the human ends up **judging by reading a self-report written by the proposer itself**. That just relocates the gap that was at the artifact layer. What they read changed from a diff to an essay; the author is the same.

The countermeasure is to **fix what the summary is cross-checked against to something human-originated**. My harness has two intervention points.

1. **Plan check** — when what to do has been settled (this is where the human approves)
2. **Intent check** — just before commit

And the summary in 2 is **presented cross-checked against the plan the human approved in 1**. Because the referent is a human-approved object, the loop can't close on self-reporting alone.

### Only one item is required: the `Divergence from plan` declaration

But "write it against the plan" still leaves room to write it conveniently. In particular, **when something new is discovered during implementation and the work naturally diverges from the plan**, that divergence quietly disappears from the summary.

My first countermeasure was to make the intent summary itself a fixed form: five mandatory headings — approved intent, what changed, divergence from plan, impact on users and operations, evidence-side changes. But the day after that form went into the convention, an audit re-examining the whole convention clause by clause forced me to re-sort those five. **Only one of the fields was actually preventing the worst case — the silent disappearance of divergence.** This is all that's required now.

```text
Intent summary: Changed the login-failure retry limit from 5 to 3 (plan step 2)
Divergence from plan: None
```

`Divergence from plan` takes one of three values: `None` / `Yes` / `Needs re-approval`. The plan changing because of something you discovered mid-implementation isn't bad in itself. What's dangerous is the fact that it changed disappearing from the summary.

And making this declaration required **turns omission into falsehood**. In free-form text, a summary that doesn't mention the divergence isn't lying — it just didn't bring it up. With the declaration required, writing `None` when there is divergence is a falsehood, and writing `Yes` points the human's eyes exactly there. It closes the omission escape route structurally, without leaning on the writer's honesty. **This is the one thing only formal enforcement can protect.**

So why drop the other four fields? Because they were the summary's **shape**, not its defense. What was intended, what changed, what's affected — summarizing without dropping those is exactly **the calibration a model should bring to any summary**: lead with the outcome, report results faithfully, match the response to the question. Impose a fixed form on the parts calibration already covers, and you're forcing five headings onto a one-line config change — the approval screen turns into template skimming.

That would reproduce, on the summary side, the third case I called the worst at the start: a gate that survives as a form nobody reads.

(As for the "evidence-side changes" field — the hook from Reinforcement 1 covers it structurally, so there was never a need to make a human write it.)

Anthropic's context-engineering guidance for the Claude 5 generation ([The new rules of context engineering for Claude 5 models](https://x.com/trq212/status/2080710971228918066)) states this as a general rule: shift from binding with rules to delegating to judgment — **except in the regions where the worst case is unacceptable, which stay explicitly bound**. The 5→1 reduction is that rule applied. Delegate the summary's shape to the model's calibration; bind exactly one point with form — the disappearance of divergence, the worst case you can't accept.

The whole point of this gate convention was to concentrate the human's cognitive budget on judging intent. **If the convention itself burns the writer's and reader's attention on enforcing a form, that defeats the purpose.**

One more practical upside: the three values are an enumeration, machine-readable, so "does the declaration exist at all" can itself be lowered into a hook check later. Same as Reinforcement 1 — build the convention so it has an exit ramp down into a deterministic gate.

### Cap the number of stops too: one gate per unit of work

Paired with what to show, fix one rule about how often. The intent check happens **once, at the completion point of a unit of work**. If a commit, a push, a publish, and the accompanying doc updates all arrive together, bundle them into **one decision with the count and scope explicitly enumerated**. Ask for approval at every intermediate phase or intermediate commit and the approvals themselves become noise — the gate degrades into formality. There are exactly two exceptions: a deterministic gate FAILing, and `Divergence from plan: Needs re-approval`.

But "bundling is allowed" is not "implicit is allowed." If one decision covers N items, say N at approval time. The moment an approval granted for one item gets silently reused for N, it has stopped being a gate.

### Raise the granularity and the bottleneck moves

This cross-check bites hardest when the agent is good. **Things going well for a long stretch is exactly the condition under which the intent summary becomes a formality.** If you find yourself skimming past the same "no divergence" every time, raise the granularity of the plan you're checking against.

But that isn't free. The finer the plan, **the further the bottleneck moves from just-before-commit to plan approval**. Reserve the finer granularity for the things you can't take back when they drift (external publishing, data migration, permission changes). You don't get to erase the fork entirely — the accurate statement is that **you get to choose where you pay**.

On the conventions side, I also renamed the second intervention point from "Verify results check" to "intent check." Leave the name as "Verify results" and it drags you back into making humans read a list of machine-check results.

## Porting it into your own conventions: three steps

1. **Enumerate your existing approval steps and check what each one says to present.** Grep for wording like "approve the diff," "visually confirm," "review and apply"
2. **Put the decision table and the escalation rule into a single conventions file, and have each place you found point at it.** If you only patch the individual wording, the next skill or document you write will fill the blank the same way again
3. **Build the `Divergence from plan` declaration (`None` / `Yes` / `Needs re-approval`) into the summary as a required item.** The summary as a whole doesn't need a fixed form. Without this, you can install the decision table and still be verifying the proposer's own self-report

:::message
In step 1's grep, **watch out for missing word stems**. I searched for `eyeballed` and missed `eyeball` (the uninflected stem), so one place survived all the way to the external model's review. Search verbs by stem rather than inflected form, or run `grep -i` with several patterns.
:::

For reference, in my environment this change (one new conventions file plus re-pointing references across 13 related files) came to 14 files and 217 added lines. The decision table itself is short; what made the difference was **re-wiring everything that referenced it**.

The convention's body has since been cut in half (the text auto-loaded into every session's context went from 265 to 125 words). What remains is only the principles — the decision table, the escalation rule, the divergence declaration. The "why" moved into the decision record (ADR), and the evidence-file enumeration into the hook. Left alone, a convention fattens on rationale and examples until nobody reads it. **Principles in the document, why in the record, anything machine-decidable in a gate** — splitting the storage that way is what keeps it maintainable.

## The limits of "the machine holds it"

Let me be straight about this. **Build, types, lint, tests, and secret scan tell you only about the properties they cover.** Holes in authorization logic, concurrency races, irreversible side effects of a migration, requirements that were never implemented at all — all of that sails through as PASS. And the review agent, being from the same lineage as the proposer, shares its blind spots (the generator–verifier gap above).

So the third row of the decision table isn't "the machine guarantees correctness" — it's an operational tradeoff that **puts primary responsibility for artifact inspection on the machine**. Residual risk does not go to zero.

Which is exactly why you need the escalation rule. **Keep the human on the artifact side only in the regions you can't undo** — data migration, permissions and billing, external publishing, deletion. Put another way: if a human is reading diffs of reversible implementation code, that isn't a response to residual risk, it's just inertia.

You also can't reduce the whole convention to a deterministic lint. Extracting the evidence-side files (the hook in Reinforcement 1) and checking that the divergence declaration exists can be mechanized, but deciding "is this a behavior-shaping artifact" is semantic, and for edge cases like generated documents and config files you have to think each time. The decision table illustrates by enumeration; it doesn't exhaust the space.

## Back to the opening question

The further you extend autonomous execution, the more drift from intent becomes visible only after the fact. But put the human back on review and the point of autonomy disappears. This looks like a fork **only while you're counting human involvement by number of stops**.

Count by content instead and it stops being a fork. Keep the number of stops the same, and move what they read at the stop from the artifact to the intent. **What you cut isn't human involvement — it's the time a human spends re-checking the correctness of artifacts.** The machine was always better at that, and when a human does it, volume wins and it becomes a formality.

To the question of who the automation is for, this is the answer. **Not to go fast, but so that what you intended gets built fast.** If so, there's only one thing the human should hold to the end. Intent. The decision table was a tool for taking everything else away from them.

When you're talking about reducing human review, what's left isn't the work you forgot to cut. It's the work you can't cut.

## Related links

- [claude-harness](https://github.com/shimo4228/claude-harness) — my public harness, including the conventions file discussed here (`rules/common/human-gate.md`)
- [agent-knowledge-cycle](https://github.com/shimo4228/agent-knowledge-cycle) — the theory-side repository on how far to hand things to the machine and where human approval starts. The conventions in this article are one implementation of it
- [Harness Alignment and Harness Drift](https://doi.org/10.5281/zenodo.20578272) — a paper on where approval gates sit
- [github.com/shimo4228](https://github.com/shimo4228) — other repositories
