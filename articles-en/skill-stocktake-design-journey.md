---
title: "Offloading AI's Weak Spots to Shell Scripts — Designing, Building, and Publishing a Skill Audit Command"
emoji: "🔧"
type: "tech"
topics: ["claudecode", "ai", "shellscript", "testing"]
published: true
---

## Introduction

I built a `/skill-stocktake` command to periodically audit my Claude Code skill collection. The motivation was simple: let AI judge skill quality. But along the way, I went through four complete redesigns and stumbled into an unexpected discovery.

**When I asked AI to list files, the results were different every time.**

It forgot to pass arguments. Timestamp formats drifted. Even with the same prompt and the same set of files, the output was not reproducible. AI's judgment and mechanical accuracy turned out to be entirely separate capabilities.

This article is a record of the entire journey: the trial and error of design philosophy, the implementation that revealed the boundary between AI and deterministic code, the bugs and security holes that scripts exposed, and the realities of publishing to the ecosystem.

---

## The Problem

Claude Code skills come from diverse origins: hand-written ones, ones imported from the [Everything Claude Code](https://github.com/anthropics/claude-code) community, ones copied from external repositories, and ones auto-extracted by AI.

When 20 to 50 of these files accumulate, periodic auditing becomes necessary:

- **Still useful?** — Are the referenced APIs and tools still current?
- **Redundant?** — Are there multiple skills covering similar content?
- **Worth the cost?** — Is the context window consumption justified?

Doing this manually takes over an hour. I wanted AI to handle it. The question was how to design it.

---

## Design — Four Versions in Two Weeks

### V1-V2: Routing by Origin (Failed)

The first design used the skill's origin (`origin` field) as a routing key. "Only check Freshness for skills imported from ECC." "Delete auto-extracted skills that overlap with MEMORY.md." A rule table based on provenance.

It felt right intuitively, but two problems emerged:

1. **Origin categories keep growing.** `original`, `ECC`, `auto-extracted`, `{org/repo}`, `skill-create` — every new import pathway requires a new rule. Quality-based rules remain constant regardless of the number of origins.
2. **Origin does not predict quality.** Hand-written skills can be low quality, and externally imported skills can be the most useful ones.

Replacing the `origin` field with directory detection in V2 did not fix the structural issue: routing by origin was the wrong axis.

### Questioning Origin: Perspectives from Other Fields

After V2's failure, a fundamental question emerged: are there systems in other fields that evaluate purely by quality, ignoring origin? I researched eight fields. Two of them decisively changed the direction of the design.

**The Judgment of Paris (1976).** Nine French wine experts conducted a blind tasting, and California wines outperformed France's finest châteaux. A demonstration that knowing the origin (provenance) distorts evaluation. This became the direct basis for V3's design principle: "conduct quality evaluation blind."

**The Danger Model (2002).** Classical immunology was based on "self vs. non-self" — origin-based identification. But Polly Matzinger's Danger Model rejected this. The immune system does not respond to "non-self" but to "danger signals." It tolerates gut bacteria (non-self) and can attack its own tissue (autoimmune disease). An evolution toward a system that judges by actual danger rather than origin.

From these two analogies, the same pattern emerged: **evaluate blind; let humans with context make action decisions.** And "what is dangerous" cannot be predicted from origin. This insight resurfaced not only in the design but later in the security design of the scripts.

### V3: Four-Dimension Rubric + Two-Tier Architecture

From the analogies, I derived the principle "evaluate blind, ignore origin." V3 reflected this with two layers.

**First tier (quality evaluation).** Evaluate each skill individually in a blind assessment. No reference to other skills. Score on four dimensions:

| Dimension | Question |
|-----------|----------|
| Specificity | Does it include concrete code examples and procedures? |
| Actionability | Can you act on it immediately after reading? |
| Scope | Does it appropriately cover the target domain? |
| Coverage | Does it address the major cases? |

**Second tier (collection judgment).** On top of first-tier scores, consider overlap and usage history to determine Keep / Improve / Retire.

The rationale for dropping two dimensions from the original six matters here. **Freshness** (currency of technical references) gets absorbed into the other four when you score under the premise "in today's environment." Examples referencing outdated APIs lower Specificity; procedures for deprecated tools lower Actionability. Freshness was a correction patch needed only when scoring assumed "the environment when the skill was written."

**Non-redundancy** is a different beast. "Is this painting good?" and "Does this collection need this painting?" are separate questions. The former can be judged by looking at the piece alone; the latter requires viewing the entire collection. Placing Non-redundancy in the first tier conflated these two. So I moved it to the second tier.

V3 shrank from V1's 130 lines to 80 lines. But structural problems remained.

### The Four-Persona Review That Destroyed V3

I had four AI personas review V3 simultaneously. Receiving criticism from four perspectives at once exposes structural flaws invisible to a single reviewer.

**The psychometrician's critique.** "The correlation between Specificity and Actionability is high (estimated r=0.70–0.85). A skill with abundant code examples is by definition immediately actionable. The total score triple-counts 'concreteness and depth.'"

In other words, even after reducing to four dimensions, there was still redundancy. Seemingly independent dimensions were measuring the same latent factor. Furthermore, AI's central tendency bias compressed scores into the narrow range of 2.5–4.5. The decision threshold landed right in this cluster, causing the same skill to alternate between Keep and Improve across runs. No reproducibility.

**The minimalist's critique (the most destructive).** "The rubric is a Rube Goldberg machine. The AI reads a skill and already knows its quality. Then it decomposes that into numbers, sums them, compares against a threshold, and converts to a verdict — the AI knew the verdict from the start."

This critique rejected not just V3 but the rubric methodology itself. The fundamental problem with using rubrics for AI evaluation is that **unlike humans, AI struggles with independent scoring per dimension**. A human judge can score "Specificity: 4, Actionability: 2" independently. AI gets pulled by the overall impression. Rubrics were invented to structure human evaluation; structuring AI evaluation requires a different approach.

### V4: Checklist + AI Judgment

After all the discussion, the design's essence fit in a single sentence:

> **Force AI to complete the checks it tends to skip, and leave the judgment itself to AI.**

| Version | Dimensions | Decision rules | Instruction lines |
|---------|-----------|----------------|-------------------|
| V1 | 6 + origin routing | 12 | ~130 |
| V2 | 6 | 10 | ~130 |
| V3 | 4 + two-tier | 5 | ~80 |
| **V4** | **0 (checklist only)** | **0** | **~40** |

130 lines became 40. But this compression was not "removing information" — it was "finding the essence." All that remained in place of the rubric were four verification items:

- Checked for content overlap with other skills?
- Checked for overlap with MEMORY.md / CLAUDE.md?
- Verified the currency of technical references?
- Considered usage history?

The verdict (Keep / Improve / Update / Retire / Merge) is left entirely to AI. AI excels at holistic judgments like "Is this skill useful?" What it struggles with is "not skipping specific checks." The checklist is a design aligned with AI's strengths and weaknesses.

---

## The Turning Point — When AI Broke on Mechanical Tasks

The V4 design was finalized. Next came implementation.

The first version of V4 described Phase 1 (inventory acquisition) as "use a haiku subagent to enumerate files and retrieve mtime." The design had AI walk the filesystem and compile a skill list into JSON.

### Three Problems

**Non-deterministic.** AI forgot to pass script arguments. `scan.sh` was designed to accept the project-level skills directory as an optional argument. AI non-deterministically omitted this argument, causing project skills to be silently skipped. The fix introduced a three-stage fallback:

```bash
CWD_SKILLS_DIR="${SKILL_STOCKTAKE_PROJECT_DIR:-${1:-$PWD/.claude/skills}}"
```

Environment variable > positional argument > `$PWD` default. A design that does not depend on AI's placeholder resolution.

The mtime format also drifted. Sometimes `2026-02-15T08:30:00Z`, other times just the date portion with the time approximated as `T00:00:00Z`.

**Untestable.** Subagent output differed every time. There was no way to define expected values for automated tests.

**Wasteful.** File enumeration is a job for `find` and `date -u -r`. Spending AI tokens on it makes no sense.

### Concrete Example: The T00:00:00Z Approximation Bug

When AI generates `evaluated_at`, it sometimes uses only the date and approximates the time as `T00:00:00Z`. Quick Scan re-evaluates "only files where mtime > evaluated_at," so all changes after midnight on that day get classified as "unchanged." The test suite explicitly detects this pattern:

```jsonc
// If evaluated_at is "2026-02-15T00:00:00Z"
// A file modified at "2026-02-15T08:30:00Z" should be "changed"
// But the AI-generated midnight placeholder carries a different meaning
```

### The Decision: "Scripts Handle Mechanics, AI Handles Judgment"

Phase 1 was replaced with three shell scripts:

| Script | Role | Lines |
|--------|------|-------|
| `scan.sh` | Enumerate skill files + extract frontmatter + UTC mtime + usage frequency | ~170 |
| `quick-diff.sh` | Compare previous results with mtime, detect changed and new files | ~90 |
| `save-results.sh` | Merge evaluation results into `results.json` (preserving existing results) | ~60 |

Only Phase 2 (quality judgment) remained as AI's job: apply the checklist and issue Keep / Improve / Update / Retire / Merge verdicts for each skill. This division of labor made Phase 1's output fully reproducible.

---

## AI Output Is External Input — What the Scripts Exposed

After writing the scripts and tests and running them through code-reviewer and security-reviewer, a principle emerged:

**AI output must be treated with the same level of distrust as an external API response.**

The Danger Model analogy from the design section resurfaces here. Just as classical immunology was "self vs. non-self" (origin-based), we intuitively think "AI-generated data is trustworthy." But just as the immune system judges by "danger signals," scripts should judge by "Is this input dangerous?" — regardless of origin.

Every example below is evidence for this principle.

### Evidence 1: The is_new Bug — Undetected New Files

In the first version of `quick-diff.sh`, new files (not registered in `results.json`) also had to pass the mtime filter before being output:

```bash
# Before (buggy)
[[ "$mtime" > "$evaluated_at" ]] || continue
# is_new check came after this line — unreachable for old-mtime files
```

```bash
# After (fixed)
if echo "$known_paths" | grep -qxF "$dp"; then
  is_new="false"
  [[ "$mtime" > "$evaluated_at" ]] || continue  # Known: mtime gate
else
  is_new="true"
  # New: always emit regardless of mtime
fi
```

New files are always detection targets regardless of mtime. Only known files are filtered by mtime. Branching by the type of data, not its origin.

### Evidence 2: Three Danger Signals Found by Security Review

Running the security-reviewer agent uncovered three vulnerabilities:

**TMPDIR injection.** Using variable expansion inside double quotes with `trap "rm -rf $tmpdir" EXIT` allows shell metacharacter injection through the `TMPDIR` environment variable. Fixed by switching to a cleanup function approach:

```bash
_scan_cleanup() { rm -rf "$_scan_tmpdir"; }
trap _scan_cleanup RETURN
```

**grep substring false-positive.** `grep -qF "$path"` performs substring matching, so `python-patterns` matches `python-patterns-v2`, causing new skills to be misidentified as known. Fixed by adding `-x` (exact line match).

**Missing evaluated_at validation.** If `evaluated_at` is `null` or a malformed string, ISO 8601 string comparison produces unpredictable results. Added regex pre-validation:

```bash
if [[ ! "$evaluated_at" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
  echo "Error: invalid evaluated_at: $evaluated_at" >&2
  exit 1
fi
```

### Evidence 3: Forced Timestamp Overwrite

`save-results.sh` merges AI-generated evaluation result JSON into `results.json`. Even if AI passes a stale timestamp in `evaluated_at`, the script always overwrites it with the current UTC time. The design "overwrites" AI output rather than "trusting" it. A test verifies that "a 1999 timestamp gets overwritten with the current time."

### Preserving Design Decisions as Tests

I wrote 39 tests across four files using bats-core. Tests serve not only as specification verification but also as **records of why a particular design was chosen**.

One notable test verifies that `stat` and `date -u -r` produce different results. `stat -f "%Sm"` returns mtime in the local timezone. Since Quick Scan's mtime comparison operates in UTC, using `stat` in a JST environment introduces a 9-hour offset. This test intentionally verifies the discrepancy between the two, preserving the design decision (why `date -u -r` is used instead of `stat`) as a test.

---

## Publishing to the Ecosystem

With the skill working, I decided to publish it to the community. This is where the realities of Claude Code's skill publishing ecosystem became visible.

### anthropics/skills — A De Facto Internal Repository

I first considered submitting a PR to Anthropic's official [anthropics/skills](https://github.com/anthropics/skills) repository. But the PR history told a clear story:

- Every merged PR author was an **Anthropic employee** (klazuka, maheshmurag, mattpic-ant, etc.)
- **Over 100 PRs from the external community remain OPEN and unaddressed** (as of February 2026)
- Spam PRs mixed in ("Casino Bus Protocol skill," etc.)

The infrastructure for accepting external contributions is not in place at this time.

### Choosing a Publishing Channel

Research revealed which channels were actually functioning:

| Channel | Nature | Registration |
|---------|--------|-------------|
| **SkillsMP** | Marketplace (96,000+ skills) | Automatic (GitHub crawl, requires 2 stars) |
| **VoltAgent/awesome-agent-skills** | Awesome list (383+ skills) | PR |
| **travisvn/awesome-claude-skills** | Awesome list (strict) | PR (requires 10 stars) |
| **ECC** | Community shared repo | PR |

### Why I Chose Independent Repositories

I ultimately created an independent repository for each skill:

```text
claude-skill-stocktake/
├── .claude-plugin/
│   └── marketplace.json    # For SkillsMP auto-indexing
├── skills/
│   └── skill-stocktake/
│       ├── SKILL.md
│       └── scripts/
│           ├── scan.sh
│           ├── quick-diff.sh
│           └── save-results.sh
├── README.md
└── LICENSE (MIT)
```

Three reasons drove this choice:

1. **Discoverability.** Awesome list PRs require a repository URL. Individual skills have low discoverability inside ECC's monorepo.
2. **Auto-indexing.** SkillsMP automatically crawls and indexes GitHub repositories. An independent repo gets listed without any application.
3. **Self-containment.** Scripts, tests, and documentation live in one repo, installable directly via `/plugin marketplace add`.

---

## Takeaways

One question surfaced repeatedly throughout this article: **"How do you classify AI's capabilities, and how do you treat each category?"**

In design, I realized "it has judgment but struggles with scoring" and abandoned the rubric. In implementation, I realized "it's good at judgment but bad at accurate repetition" and separated the work into scripts. In security, I realized "AI output should be validated regardless of origin" and added input validation. The same structure every time: identify the *type* of AI capability and assign a different trust level to each type.

Here are the specific lessons:

### 1. AI's Judgment and Mechanical Accuracy Are Separate Capabilities

**What:** File enumeration, mtime comparison, and JSON merging go to deterministic scripts. Quality judgment goes to AI.
**Why:** AI excels at holistic judgments like "Is this skill useful?" but struggles with "passing the correct arguments every time." Correctly identifying which tasks AI is good at and which it is not determines the reliability of the overall system.
**Alternative considered:** A validation wrapper around AI output, but "writing a script that produces correct output from the start" was simpler than "verifying that AI output is correct."

### 2. Rubrics Are a Tool for Humans

**What:** A 6-dimension rubric (130 lines) was replaced with a 4-item checklist (40 lines).
**Why:** Rubrics were invented to structure human evaluation. Humans can score dimensions independently; AI gets pulled by the overall impression. High inter-dimension correlation (r>0.7) and central tendency bias compressed scores into a narrow range with no reproducibility. For AI, a checklist (confirmed or not confirmed — binary) works better.
**Alternative considered:** Reducing to two independent dimensions, but the minimalist's critique ("AI already knows the verdict from the start") was decisive.

### 3. Judge AI Output by Danger, Not by Origin

**What:** TMPDIR injection, grep substring false-positive, evaluated_at validation — all discovered through security review.
**Why:** The Danger Model lesson applies here. Instead of "AI-generated data is safe" (origin-based), judge by "Does this input contain a dangerous pattern?" (danger-signal-based). Scripts that process AI output need the same validation posture as code that processes user input.

### 4. The Skill Publishing Ecosystem Is Fragmented

**What:** Anthropic's official repo does not accept external PRs, while multiple community-driven channels have emerged.
**Why:** The Agent Skills specification exists, but the ecosystem is still maturing. For now, independent repos combined with parallel registration across multiple channels is the most reliable publishing strategy.

---

## Closing

"How much should we delegate to AI?" — this question extends far beyond a skill audit command. Whenever we build tools with AI, we are designing this boundary.

What this article's experience suggests is that the boundary is determined not by "the limits of AI's capabilities" but by "the types of AI's capabilities." Judgment and accuracy are separate axes. Assign to AI what AI does well; assign to machines what machines do well. Simply being conscious of this division of labor significantly changes the reliability of AI tools.

---

*skill-stocktake is published in the [claude-skill-stocktake](https://github.com/shimo4228/claude-skill-stocktake) repository.*
