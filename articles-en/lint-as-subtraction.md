---
title: "After Cutting My AI Reviews, I Put a Complexity Ceiling in Ruff"
emoji: "📏"
type: "tech"
topics: ["claudecode", "aiagents", "staticanalysis", "codereview"]
published: false
description: "A review's job is to return findings, so every stage you add creates standing work. Lint returns only defined violations, so with no violations it adds nothing. That asymmetry is why I cut my AI review chain and, the next morning, added a complexity ceiling with Ruff's C901 — measured across 7 repos and 442 Python files, with all 13 existing violations drained the same day."
tags: claudecode, aiagents, staticanalysis, codereview
---

When you have AI agents writing your code, reviews keep piling up.

I spent several weeks cutting mine back. And the morning after I cut them, I added a lint rule that puts a ceiling on complexity.

That looks like subtracting and adding at the same time, but there is no contradiction. **Reviews and lint differ in what they add when you add them.**

A review's job is to return findings. Asked about sound code, it will still return something. So every stage you add adds that much more judgment work. What decides the volume is not the state of the code but the disposition of the reviewer.

Lint is different. It returns only defined violations. No violations, no output. Adding it adds work only in proportion to the violations that actually exist.

Because of that difference, I cut one and grew the other. **When you are unsure whether to add or remove a check, look at what decides its output volume: the rule, or the reviewer's disposition.** What a rule decides does not add work when you add it.

This article covers what it took to actually measure and install a complexity ceiling, and what I found along the way that cannot be handed to a machine. All I used was one Ruff rule, `C901`. I built nothing of my own.

## The morning after cutting reviews, I added lint

On August 27, 2026, I cut my pre-commit reviews from 6 stages to 1. The reason was volume, not accuracy. A reviewer returns something even against sound work, so the more stages I ran, the more decisions I accumulated about whether to fix things. I wrote up how that went in [the previous article](https://dev.to/shimo4228/i-cut-my-ai-review-chain-from-6-stages-to-1-breaking-the-loop-that-never-hits-zero-findings-1moi). This one is the sequel: **what I put in its place**.

The next morning, on the 28th, I saw a discussion on X about "automated lint rules that are too strict for humans but work on agents." Put a ceiling on function complexity. Put a ceiling on file length. The moment I read it, I wanted it.

### What decides how much gets added

I had just gone from 6 stages to 1 the day before. Did adding a check today make any sense?

| | What decides the output volume | What gets added |
|---|---|---|
| LLM review | The reviewer's disposition | Standing judgment work |
| A lint rule with a ceiling | The rule, plus measured values from the code | Only the violations that actually exist |

Enabling one `C901` rule adds one line to a config file. It runs inside the linter I already have, so no new process appears. What comes back is the count of functions over the threshold, and if nothing is over, it is zero.

So the two do not sit on the same scale. Cut reviews. Grow lint where it works, and leave it out where it does not.

This was not the first decision of this shape. On August 15 I had also demoted TDD on new features from mandatory to conditional. What I removed was only **the forced RED→GREEN ordering**; the coverage floor stayed, still enforced by machine. Drop the procedure the agent has to follow; keep the floor the machine hits. Same operation.

## Left alone, LLM-written code gets complex

This part is my working hypothesis. I want to say that up front.

The codebase I have had agents write (Contemplative Agent, the LLM agent I develop — 4,580 Python functions) had this complexity distribution before I added any lint.

```text
p50 = 1  /  p90 = 3  /  p95 = 5  /  p99 = 10  /  max = 35
```

First, how to read those numbers.

`p50 = 1` means that if you line up every function by complexity, the middle one is 1. `p90 = 3` means the top 10% starts at 3, and `p99 = 10` means the top 1% starts at 10. `max` is the largest value among them.

So what does the complexity number itself count? Ruff's `C901` (McCabe cyclomatic complexity) **starts a branchless function at 1 and adds 1 for every branch**. Here is what I actually measured with ruff 0.16.1 (McCabe complexity counts different things in different implementations; the following is Ruff's behavior and will not necessarily match the mccabe package or radon).

| Code | Complexity |
|---|---|
| No branches (straight through, top to bottom) | 1 |
| One `if` | 2 |
| `if` + `elif` | 3 |
| One `for` | 2 |
| Two `except` clauses | 3 |
| An `if` inside an `if` (2 levels of nesting) | 3 |
| `for` / `if` / `for` / `if`, 4 levels of nesting | 5 |

Some things are not counted. `else`, `and` / `or`, the ternary operator, an `if` inside a comprehension, and `with` all leave complexity untouched. **Nesting depth is not counted either.** Two levels of nesting and two sequential `if`s are both 3.

Reading the distribution back with those rules: the median of 1 means "a function with no branches at all." p90 at 3 means "roughly two `if`s." p99 at 10 means "nine branches." And the maximum of 35 meant **34 branches in a single function**.

Functions above 15: 13 of them. 0.3% of the total.

I have not proven that those 13 exist *because* an LLM wrote them. I have not compared against a human-written codebase, and I have not measured whether they are increasing over time. All I measured was the shape of the distribution.

I decided to put a ceiling on it anyway, because I believe this 0.3% is the side that grows one branch at a time with every edit. "Just one more branch" looks reasonable every single time it comes up in review. With a ceiling, that one branch becomes something to argue about. Without one, it gets merged.

The point of the discussion I saw on X was not the threshold value either, but the direction of the operation. **When you hit the ceiling, you drain it — you do not raise the threshold.** One way only.

## I measured what I had not pushed down to the machine

Saying "push down to the machine whatever can be pushed down" is easy. So how much had I actually not pushed down?

I counted the lint and build configs across all of my repositories: 82 repos, 104 configs. Then I searched for the terms that set ceilings on complexity or size (`C901` / `mccabe` / `max-complexity` / `PLR09*` / `max-lines` / `radon` / `lizard`, and so on).

**Zero hits.**

Here is a re-run with a narrower target, done while writing this article (August 28, 2026).

```bash
python3 - <<'PY'
import os,glob,re
roots=[os.path.expanduser("~/MyAI_Lab"),os.path.expanduser("~/.claude")]
repos={d for r in roots for d in glob.glob(os.path.join(r,"*"))
       if os.path.isdir(os.path.join(d,".git"))}
repos |= {r for r in roots if os.path.isdir(os.path.join(r,".git"))}
names=["pyproject.toml","setup.cfg",".flake8","ruff.toml",".ruff.toml",
       "eslint.config.mjs",".eslintrc.json",".eslintrc.js",".swiftlint.yml",
       "tox.ini",".pylintrc"]
pat=re.compile(r"C901|mccabe|max-complexity|PLR09|max-lines|max-module-lines"
               r"|size-limit|radon|lizard|cyclomatic_complexity|file_length",re.I)
cfgs=0;hits=[]
for repo in sorted(repos):
    for n in names:
        p=os.path.join(repo,n)
        if os.path.isfile(p):
            cfgs+=1
            t=open(p,encoding="utf-8",errors="replace").read()
            if pat.search(t):
                hits.append((os.path.basename(repo),n,sorted(set(pat.findall(t)))))
print(f"repos: {len(repos)}  configs: {cfgs}  hits: {len(hits)}")
for h in hits: print("  ",h)
PY
```

```text
repos: 76  configs: 20  hits: 1
   ('contemplative-agent', 'pyproject.toml', ['C901', 'max-complexity', 'mccabe'])
```

The single hit is the one I added that same day, as part of the work described in this article. Before that it was zero.

### Why "maximum strict" still let this through

My own conventions say "lint should be at maximum strict by default." I had been following that, and I still had zero.

The reason is that ceiling rules are not in the default sets of the major linters.

- Ruff expanded its default rules from 59 to 413 in 0.16.0, but `C90` (complexity) and the `PLR09*` subset of `PLR` (too-many-branches / too-many-arguments / too-many-statements and other ceiling rules) remain outside the defaults
- **Ruff has no rule equivalent to a file line-count ceiling.** In the Pylint-compatibility tracking issue [astral-sh/ruff#970](https://github.com/astral-sh/ruff/issues/970), the corresponding `too-many-lines` entry carries the note "not compatible with the formatter" and is unimplemented
- Cognitive complexity has been sitting as [astral-sh/ruff#2418](https://github.com/astral-sh/ruff/issues/2418), open since January 2023

So even if you follow "make the default rule set strict" faithfully, the ceiling rules fall through structurally. It was not that I forgot to write the setting — **my convention was written somewhere it could not reach**.

The contrast was in the Swift repositories I have. SwiftLint enables `cyclomatic_complexity` (warning 10 / error 20) and `file_length` (warning 400 / error 1000) **by default**. Without a single line in `.swiftlint.yml`, they were in force.

And there, the ceiling was actually working as a cutting force. The largest Swift file was 397 lines. Three lines short of the 400-line warning threshold.

Whether your toolchain ships ceilings by default completely changes what the same "maximum strict" convention produces. This is not a discipline problem. It is a tool-defaults problem.

## You cannot set the threshold globally

So what number do you pick? My first plan was to settle on one number shared across all repositories.

I could not.

Tip the threshold to 0 and Ruff prints the measured value for every function. That gets you the whole distribution in a single run.

```bash
uvx ruff@0.16.1 check --isolated --no-cache --output-format json \
  --select C901 --config "lint.mccabe.max-complexity=0" -- <files>
```

Measurements across my 7 public repositories, 442 Python files (as of August 28, 2026; `~/.claude` is my personal collection of Claude Code operations scripts, and the Contemplative Agent row shows values after the cutting described below).

| repo | functions | p50 | p90 | p99 | max | >10 | >15 |
|---|---|---|---|---|---|---|---|
| ~/.claude | 949 | 1 | 6 | 12 | 28 | 15 | 3 |
| contemplative-agent | 4,746 | 1 | 3 | 10 | 20 | 33 | 2 |
| pdf2anki | 954 | 1 | 2 | 8 | 14 | 5 | 0 |
| tiny-lm-lab | 111 | 1 | 2 | 6 | 6 | 0 | 0 |
| daily-quest-generator | 50 | 1 | 4 | 26 | 27 | 2 | 2 |
| active-inference-viz | 111 | 1 | 3 | 5 | 5 | 0 | 0 |
| einstein-arena | 261 | 1 | 4 | 10 | 14 | 3 | 0 |

p99 ranges from 5 to 26 — a spread of more than 5x. File line counts measured the same day had a p90 spread from 184 lines to 901.

What happens if you paste `C901 = 10` across all of them? In tiny-lm-lab nothing trips, and it protects nothing. In daily-quest-generator the existing code goes red immediately and work stops. It becomes **a number that matches the reality of neither repository**.

I once retired a fixed checklist that did not match the reality of the repositories it ran against. I was about to rebuild the same thing in the shape of a threshold.

What I did instead: **measure that repository's distribution, then place the threshold where only the current outliers go red**. Thresholds are allowed to differ per repository. The only thing decided globally is the procedure.

## Some things cannot be pushed down

The same measurements told me one more thing. **A complexity ceiling and a file line-count ceiling behave in opposite ways.**

| | C901 > 15 | File LOC > 500 |
|---|---|---|
| Count | 7 | 83 |
| Of which test code | **0** | **43 (52%)** |

All 7 functions over complexity 15 were production code. Not one test.

Open the largest test file in Contemplative Agent and the reason is obvious. `tests/test_agent.py` is 4,028 lines with 209 `def test_`s. Measuring the 233 functions in it, helpers and fixtures included, **224 (96%) had complexity 1** — zero branches. The maximum was 4. It is long not because it is tangled, but because independent cases are lined up next to each other.

File line counts went the other way: a majority of the 83 files over 500 lines were tests.

### Whether to split tests is genuinely contested

I wanted to conclude "so tests don't need splitting," but when I looked into it, the consensus was not that simple.

- **The "no need to split" side**: Google's [DAMP principle](https://testing.googleblog.com/2019/12/testing-on-toilet-tests-too-dry-make.html) argues that because tests do not have tests of their own, it matters that a human can verify their correctness by eye — worth paying some code duplication for. If you prioritize each test being readable on its own, the length of the whole file is not a burden
- **The "same standard" side**: the claim that [test code should be treated as production code](https://www.ontestautomation.com/on-treating-your-test-code-like-production-code/) also exists. That position says lint should be applied to test automation code too

SonarQube sits between the two, and it is telling. The [official documentation](https://docs.sonarsource.com/sonarqube-server/instance-administration/analysis-functions/analysis-scope/exclude-from-coverage-duplication) provides **the configuration steps** for excluding tests from duplication analysis, but they are not excluded by default. The **rationale** — "test duplication is intentional, so it should be excluded" — is not in the official documentation; it lives in the [community forum](https://community.sonarsource.com/t/duplicated-lines-of-code-in-tests/137785). The tool goes as far as offering the option, and the judgment is left to each repository.

The position I took is: apply lint to tests too, but decide rule by rule. Writing **forbidden in production, allowed in tests** with ESLint overrides or Ruff per-file-ignores is an officially intended use. Complexity does not go red in tests, so it stays applied. Line count would require designing exemptions, so I put it on hold.

Which is to say: if you naively add a file line-count ceiling, **most of the resulting work becomes "splitting test files."** The reason I wanted a ceiling was to cut down unreadable code the agents had grown. Splitting tests has nothing to do with that intent.

That is where I noticed one more thing to check. **Does what the machine flags match what I actually want cut?**

For a complexity ceiling it matches. What goes red is the same thing I wanted cut in the first place. For a line-count ceiling it does not. You cannot install it without first deciding how to treat tests.

**Even among "ceilings," some can be pushed down to the machine and some cannot.** I installed only complexity and put the line-count ceiling on hold.

## I installed it and drained it the same day

I set `max-complexity = 15` in Contemplative Agent.

I run `ruff check` before every commit and block the commit on errors. Add a new rule there and every existing violation becomes an error from that instant.

At install time there were 13 violations. Left as-is, commits would break in the middle of changes that have nothing to do with complexity. When that happens, the agent either goes off to fix violations unrelated to the work in front of it, or it learns the procedure for skipping the check. Both are outcomes I want to avoid.

So I wrote those 13 into `per-file-ignores` as a **backlog to drain**, and **started from zero errors**.

Then I **drained all 13 the same day**. The largest was the 35 in `never_selected_metrics.py`; I split it and the other 12 into helpers at or below 15. I confirmed behavior was unchanged by running the same inputs through the old and new code and comparing outputs across 4,767 test cases (zero mismatches). The backlog was empty.

### The backlog that empties, and the exemption that does not

That said, exemptions did not go to zero. I ran into this in my own environment while writing.

The `ruff check` I run before commits targets four directories: `src tests scripts evals`. Outside them, under `docs/evidence/`, two functions with complexity 16 and 20 were still sitting there.

I thought about whether to cut them, and decided not to. Those two are verbatim records from verifying a past rewrite, and one of them is the baseline the outputs were compared against. Split them up for readability and they stop working as evidence.

The problem was that leaving them meant **the next session to touch those files would eat an error with no warning**. Even outside the full-scan target, the pre-commit check looks at every staged `.py`. An undeclared exemption is not an exemption, it is a landmine.

So I added it to the existing exclusion line as a permanent exemption with a reason.

```toml
# Promoted one-off measurement scripts — the progress and readout prints are the UI.
# C901 is permanently exempt here too: these are frozen verbatim records (including
# the baseline values used for output comparison), and cutting them destroys their
# value as evidence. This is not a backlog to drain
"docs/evidence/**" = ["T20", "C901"]
```

The important part is **not to mix the two kinds of exemption**.

| | Backlog to drain | Permanent exemption with a reason |
|---|---|---|
| Contents | Existing code that was over the ceiling at install time | Things that must not be cut |
| Goal | Empty it | Never empty it |
| Additions | Not allowed (a new violation is a design problem) | Allowed, with a written reason |

Mix those two into one list and you can no longer tell whether anything is left to cut by asking "is the exemption list empty?" Keep them separate and the backlog can be operated as "keep it empty."

### Detection goes to the machine, the cutting goes to the LLM

The cutting work did not need the judgment of a frontier model. The machine had already finished the detection, and what remained was fixing the places the machine pointed at. In fact, what I considered before starting was "which model is enough," not "where is it complex."

Adding lint did not make the LLM unnecessary. What actually happened is that **the LLM's role moved from "judge where it is complex" to "cut down where the machine pointed."**

I put a comment on the threshold line.

```toml
[tool.ruff.lint.mccabe]
# Budget rule: drain, do not raise — any change to this number needs a dated
# reason in .claude/verify.md
# Distribution as-of 2026-08-28 (4,580 functions):
# p50=1 / p90=3 / p95=5 / p99=10 / max=35.
# 10 was rejected as the threshold: it would have put 24 files on the
# exemption list, blinding the modules that see the most editing.
max-complexity = 15
```

`.claude/verify.md` is where I record verification procedures and decisions in my environment. If you do the same, read that as wherever you keep your own decision records.

You can write the convention in some other document, but no session goes back to read it at the moment lint throws an error. What is in front of you then is the lint output and the config. **If you want "drain, do not raise" to land, the delivery address is that very line.**

## When this reasoning does not apply

Let me be honest about the limits.

**"Drain, do not raise" is not machine-enforced.** It is an operating convention carried by a comment. If someone raises the threshold to get around it, I cannot detect that. I rejected the idea of building something new to detect it, precisely because that would add another thing that runs — the thing I had decided to cut the day before. If I observe one real instance of the workaround, I will think about it then.

**If what goes red does not match what you want cut, this axis does not work.** The machine can decide in an instant, but if it points at the wrong things, you get more work without moving the intent. That is what I nearly walked into with the file line-count ceiling. Before "machine or LLM," look at what that machine will point at.

**Check what your lint command actually covers before you pick a threshold.** A ceiling only works out to the directories that command looks at. I carried two violations outside that range for a while without noticing.

**I have not measured the effect of installing it.** What I can observe stops at "13 violations, drained the same day." Whether the bug rate dropped, whether readability improved, whether the agents' generation tendencies changed — I cannot say anything about any of it yet.

## Porting this to your own setup

Four steps.

**1. List what you currently have LLM reviews doing.** Write it out by concern, not by stage name. Like "naming," "duplication," "complexity," "error handling," "security."

**2. Sort each item into three buckets.** Three, not two.

| Bucket | Input to the decision | Destination |
|---|---|---|
| Deterministic | Structure, format, existence, matching (complexity, circular imports, dead code, naming conventions) | Machine |
| Semantic | Intent, soundness, two-sidedness (whether a design is right, alignment with requirements, post-hoc justification) | Leave with the LLM |
| Mixed | The machine counts, the LLM interprets (distribution of term usage, the denominator behind a number) | Machine produces the value, LLM reads it |

And **when in doubt, tip the item toward semantic**. An item you mechanized by mistake passes false negatives wearing the face of "checked." The worst outcome is that misses quietly increase in exchange for the relief of one fewer stage.

For every item you assigned to the machine, one more question. **Does what it flags match what you want cut?** For things that do not match — like file line counts — the rule may decide the output volume, but what comes back will be things you did not want cut.

**3. Set the threshold from the measured distribution.** Do not pick the number first. Tip the ceiling to 0, take the distribution for everything, and place the threshold where only your current outliers go red. In Python, one line gets you there.

```bash
uvx ruff@0.16.1 check --isolated --no-cache --output-format json \
  --select C901 --config "lint.mccabe.max-complexity=0" -- <files>
```

**4. Start from zero errors the moment you add it.** Adding a new rule turns every existing violation into an error on the spot. If you run lint before commits or in CI, changes unrelated to this will stop passing. What happens then is one of two things: the agent goes off to fix violations unrelated to the work in front of it, or the habit of skipping the check sets in. Write the existing violations into an exemption list and start from a state that passes. **If you see errors on day one, what is wrong is not the threshold — it is how you wrote the exemptions.**

Then decide the plan for removing those exemptions. When you do, write the backlog to drain and the permanent exemptions with reasons as separate groups.

And one comment on that threshold line. **When you go over, drain it — do not raise it.**

These four steps are a summary of the procedure I normally use. The original ([review-to-lint](https://github.com/shimo4228/claude-harness/blob/main/skills/review-to-lint/SKILL.md)) is written as "pull the mechanically decidable items out of the reviewer's checklist, and thin the reviewer down to semantic checks only." The division of labor is one line: **code decides whether it is there, and the LLM decides whether it is sound.** What I did this time was the version where the machine side is handled by one off-the-shelf lint rule instead of a script of my own.

The way to pick a threshold and the "drain, do not raise" convention itself went into the skill that builds per-repository verification procedures ([verify-bootstrap](https://github.com/shimo4228/claude-harness/blob/main/skills/verify-bootstrap/SKILL.md)) as a 20-line proviso. No new skill, no new hook, no new script.

When I am unsure whether to add or remove a check, I look at two things.

One is what I opened with: **what decides the output volume**. What the reviewer's disposition decides adds standing work when you add it. What a rule plus measured values from the code decides adds nothing when there are no violations.

The other is what I noticed along the way: **whether what goes red matches what you want cut**. That is where the file line-count ceiling caught me.

Anything that satisfies both, I want more of.

## Sources and references

- [Ruff — Default Rules](https://docs.astral.sh/ruff/default-rules/) (retrieved 2026-08-28; `C901` is not in the default list)
- [Ruff v0.16.0 release notes](https://github.com/astral-sh/ruff/releases/tag/0.16.0) (retrieved 2026-08-28; defaults went from 59 rules to 413)
- [astral-sh/ruff#970 — "Implement Pylint"](https://github.com/astral-sh/ruff/issues/970) (retrieved 2026-08-28; the Pylint-compatibility tracking issue. The `too-many-lines` entry, the equivalent of a file line-count ceiling, carries a "not compatible with the formatter" note and is unimplemented)
- [astral-sh/ruff#2418 — "Implement flake8-cognitive-complexity"](https://github.com/astral-sh/ruff/issues/2418) (retrieved 2026-08-28; opened 2023-01-31 and open ever since)
- [Ruff documentation — mccabe (C90)](https://docs.astral.sh/ruff/rules/#mccabe-c90) (retrieved 2026-08-28)
- [claude-harness — review-to-lint / verify-bootstrap](https://github.com/shimo4228/claude-harness/tree/main/skills) (the source of record for the procedures in this article, as of 2026-08-28)
- [SwiftLint — Rule Directory](https://realm.github.io/SwiftLint/rule-directory.html) (retrieved 2026-08-28; `cyclomatic_complexity` / `file_length` are enabled by default)
- [Google Testing Blog — Tests Too DRY? Make Them DAMP!](https://testing.googleblog.com/2019/12/testing-on-toilet-tests-too-dry-make.html) (retrieved 2026-08-28; test readability takes priority over duplication)
- [SonarQube — Excluding from coverage or duplication](https://docs.sonarsource.com/sonarqube-server/instance-administration/analysis-functions/analysis-scope/exclude-from-coverage-duplication) (retrieved 2026-08-28; the configuration steps for exclusion. Not excluded by default)
- [Sonar Community — Duplicated lines of code in tests](https://community.sonarsource.com/t/duplicated-lines-of-code-in-tests/137785) (retrieved 2026-08-28; the discussion treating test duplication as intentional. Not official documentation)
- [ESLint — max-lines](https://eslint.org/docs/latest/rules/max-lines) / [Ruff — Settings (per-file-ignores)](https://docs.astral.sh/ruff/settings/) (retrieved 2026-08-28; rule selection per file type)

## Related links

- [I Cut My AI Review Chain From 6 Stages to 1: Breaking the Loop That Never Hits Zero Findings](https://dev.to/shimo4228/i-cut-my-ai-review-chain-from-6-stages-to-1-breaking-the-loop-that-never-hits-zero-findings-1moi) — the previous article: how I cut reviews back, and what I measured
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles/lint-as-subtraction.md) — the Markdown for every article, plus the index (docs/PUBLICATIONS.md), lives in the same repository
- [My GitHub](https://github.com/shimo4228) — my research repositories, with DOIs
