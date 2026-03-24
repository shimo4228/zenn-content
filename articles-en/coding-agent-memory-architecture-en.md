---
title: "Where to Put a Coding Agent's Knowledge — and How to Make It Stick"
description: "Memory MCPs fail because models never call search. This article presents a file-placement architecture for coding agent knowledge, a 4-role document separation model, automated compliance measurement, and the Agent Knowledge Cycle (AKC) framework."
tags: claudecode, ai, mcp, devtools
published: true
---

I started trying to embed persistent memory into Claude Code in late February. Two weeks of use later, I noticed the Install and Hope problem and uninstalled the memory MCP in early March. What follows is everything I have thought through since then.

**Claude does not call search.**

This is a long article. It covers the structural flaws of memory MCPs, a 4-role separation model for documentation, automated compliance measurement for skills and rules, and the journey toward a unified concept. It is written for anyone seriously grappling with the memory problem of coding agents.

---

## Chapter 1: The Install and Hope Problem Remains Unsolved

### Recap of the Previous Article

In a previous article, I identified the **"Install and Hope" problem**. Most users — myself included — expect that registering an MCP tool means the model will intelligently choose and invoke it at the right time.

Here is what actually happens:

```text
1. Built-in tools (Grep, Glob, Read, Write) are immediately available
2. MCP tools are registered as deferred tools
3. Deferred tools require explicit loading via ToolSearch before use
4. The model takes the shortest path → built-in tools always win
```

This is the crux. Claude Code avoids bloating the context window when many MCP servers are registered by loading MCP tool definitions on demand. Only tool names appear in `<available-deferred-tools>`; actually using one requires a two-step process of loading it via ToolSearch and then invoking it.

Built-in tools (Grep, Read, Write, etc.) have no such constraint. They can be called immediately without loading.

**This single extra step decisively shapes the model's choices.** If a built-in tool can do the job, the model has no structural incentive to go through ToolSearch to load a deferred tool first. The rational shortest path means the MCP tool never gets called.

### The Same Problem in Next-Generation Tools

Months have passed. Several improved memory MCPs have appeared. Their storage pipelines are genuinely better — hybrid full-text and vector search, time-decay chunk prioritization, vastly increased storage capacity.

But every introductory article for these tools shares the same **missing number**.

**Nobody has measured how often Claude actually calls search.** Including myself.

In the previous article, I wrote that over two weeks of use, there was no evidence of search being triggered for the memory MCP I was using. But that was gut feel, not rigorous measurement. The same is true for the new tools. Metrics on the **supply side** (storage and retrieval infrastructure) — number of stored items, search speed — are abundant. Metrics on the **demand side** (how often the model called search) are completely absent.

In other words, neither builders nor users have evidence that memory MCPs are "working."

### "The Storage Problem" and "The Recall Problem" Are Separate

What the memory MCP community is working on is *how to store*. Chunking, vectorization, time decay — all storage pipeline improvements. Technically legitimate progress.

But the real problem is *when to recall*.

Think of it in terms of human memory. Adding books to a library does not help someone who has forgotten the library exists. "We added more books" and "search got faster" are library-side metrics, unrelated to how often a patron walks through the door.

This is precisely the memory MCP's problem. The storage and retrieval infrastructure is ready. But there is no structural trigger for the model to decide "I should search my memory."

Writing "search the memory MCP" in CLAUDE.md might raise the trigger rate. But that is the same structure as the `CRITICAL: You MUST use ...` approach I criticized in the previous article. Writing MANDATORY in the description was ignored then. CLAUDE.md probably has a higher trigger rate, but it is a matter of degree, not a structural solution.

I do not know the actual trigger rate. Nobody has measured it. But based on the structure, high reliability seems unlikely. At best, it remains Install and Hope — install and pray.

---

## Chapter 2: The Memory Problem Is Decided by "Where You Put It"

### The Principle

Once you understand why memory MCPs structurally fail, the direction of a solution becomes obvious.

> **Place information where the LLM deterministically reads it.**
> Not in a vector DB hoping it will "maybe search."

In Claude Code, certain files are **deterministically read** at session start:

- **CLAUDE.md** — Placed at the project root, it is read 100% of the time at session start
- **rules/** — Auto-loaded like CLAUDE.md
- **MEMORY.md** — Claude Code's persistent memory, auto-loaded at session start (though truncated beyond 200 lines, as stated in Claude Code's system prompt)

Place information here, and there is no need to pray for search to trigger. It is deterministically read.

But cramming everything in creates a different problem.

### CLAUDE.md Bloats

Consider one project's CLAUDE.md. It had 165 lines. That might sound reasonable. Here is the breakdown:

- Project conventions and build commands: 60 lines (**belongs here**)
- Module listing and directory structure: 52 lines
- "We chose X because of Y" descriptions: 30 lines
- Numerical data (LOC, test counts): scattered throughout

The 60 lines are legitimate "how to work" instructions. What about the remaining 105?

The 52-line module listing is **architecture detail** — a description of how the code currently looks, which goes stale every time the code changes. In fact, the listed LOC was 6,400 but the actual count was 6,671; tests were listed as 639 but actually numbered 651. Writing numbers in CLAUDE.md means **they start rotting the moment they are written**.

The 30 lines of design rationale are **decision history**. "Why we chose X" is valuable knowledge, but it does not belong in CLAUDE.md. CLAUDE.md is a file for "how to work," not for "why things are the way they are."

**Roles were mixed.** "How to work" instructions, "what the code looks like now" descriptions, and "why things are this way" history all coexisted in a single file. Each degrades at a different rate, so the file's overall reliability gets dragged down by its most fragile part.

MEMORY.md had the same problem. Design decisions accumulated flat, with important judgments like "disabled claude-mem" and "pivoted from regex to LLM" sitting at the same level as day-to-day notes. Three months later, I would open a session unable to trace "why is it like this?"

### The Four Roles

This is not a technical problem. It is a **classification problem**.

Project documentation serves four distinct roles. Each answers a different question, has a different audience, and degrades at a different rate.

| Role | Answers | What Goes Here | Degradation Rate | Example |
|------|---------|---------------|-----------------|---------|
| **Context** | "How to work" | Conventions, build commands, policies | Slow | CLAUDE.md, .cursorrules |
| **Architecture** | "What the code looks like now" | Module structure, data flows, metrics | **Fast** | docs/CODEMAPS/ |
| **Decisions** | "Why it is this way" | Trade-offs, rejected alternatives | Nearly immutable | docs/adr/ |
| **External** | "What is this?" | Purpose, quickstart | Slow | README.md |

**One file serves one role.** That is the principle.

Why four and not three? Initially I considered merging External into Context. But Context's audience is "agents (and developers)" while External's audience is "people who do not know this project." Merging files with different audiences means one side always suffers. I do not want `--cov-report=term-missing` in the README, and I do not need "This project is a ..." in CLAUDE.md.

Common mixing patterns and where the content should actually live:

```text
Often found in Context files         → Where it belongs
──────────────────────────────────────────────────────
Module listings (10+ items)          → Architecture docs
"We chose X because Y"              → Decision record (ADR)
Dependency graphs, data flow diagrams→ Architecture docs
LOC, test counts, and other metrics  → Architecture docs (or don't write them)
Quickstart instructions              → README.md (External)
```

---

## Chapter 3: context-sync — My Own Harness Had No CLAUDE.md

### A 5-Phase Workflow

Applying this 4-role model manually is tedious. Read a file, classify the role, find the mixing, move content, verify consistency — do it for three projects and you lose interest.

So I turned it into a skill. `context-sync` runs in five phases:

```text
Phase 1: Discover  — Find documentation files in the project, classify into 4 roles
                     Detect missing roles
Phase 2: Overlap   — Detect where one file serves multiple roles
                     Suggest migration targets
Phase 3: Migrate   — With user confirmation, move content to appropriate files / create new ones
                     Document migration is hard to reverse, so it is not fully automatic
Phase 4: Freshness — Verify freshness of numerical data, links, and file paths
                     Detect descriptions that have diverged from the actual code
Phase 5: Report    — Output an execution summary
```

Each phase asks for user confirmation because document migration is hard to reverse. "Should I move these 30 lines from CLAUDE.md to docs/adr/?" — only a human can judge "No, I want that to stay here."

### First Test Subject: My Own Harness

The first test subject was my own Claude Code harness (`~/.claude/`). It contained 18 agent definitions, 33 skills, and 47 slash commands. I always create CLAUDE.md for other projects. It is even in my rules.

The moment Phase 1 Discover ran, the first detection result appeared:

**"Context role file missing: CLAUDE.md"**

The harness itself had no CLAUDE.md.

An implicit assumption that it was "the one that configures" rather than "the one being configured." Forcing others via rules to "create a CLAUDE.md" while having none in my own home.

Phase 2 Overlap flagged MEMORY.md's contents. Three design decisions and one technical reference were mixed in flat:

- "Disabled claude-mem. Reason: overlap with existing system" → Should move to **Decisions**
- "Pivoted from regex to LLM. Reason: three rules were implicitly injecting bias" → Should move to **Decisions**
- "Retirement reason for 2 retired rules not recorded" → Should be recorded as **Decisions**

Phase 3 created `docs/adr/` and produced 5 ADRs. MEMORY.md was slimmed down to just pointers.

One side effect: `git add docs/adr/` failed. The cause was `.gitignore` containing `docs/`. A legacy setting that excluded the entire docs/ directory. Changing it to `docs/*` + `!docs/adr/` + `!docs/CODEMAPS/` made not only ADRs but also CODEMAPS committable — the way it should have been. I would never have noticed without running context-sync.

### Before / After Across Three Projects

**Project 1: Autonomous Agent (Medium-Scale, Python)**

The project with the 165-line CLAUDE.md described earlier. A textbook case of role mixing.

| Metric | Before | After |
|--------|--------|-------|
| CLAUDE.md line count | 165 | 117 (29% reduction) |
| ADRs | 0 | 8 |
| MEMORY.md line count | 135 | 66 |
| Metric accuracy | LOC: 6,400 (actual 6,671), tests: 639 (actual 651) | All metrics corrected to actual values |

52 lines of module listings moved to Architecture docs, 30 lines of design rationale moved to ADRs. The remaining 117 lines were pure Context — nothing but "how to work" instructions.

Phase 4 Freshness Check also caught the LOC and test count discrepancies. The lesson that numbers should not go in CLAUDE.md was learned here. Numbers belong in Architecture docs, or should not be written at all. Running a command to get the actual count is more trustworthy.

**Project 2: iOS App (Small-Scale, Swift)**

A small project with only 66 lines of CLAUDE.md. What happens when context-sync runs on it?

```text
Context Sync Report
═══════════════════

Roles:      2/4 covered (Context, Decisions partial)
            Architecture: missing (66-line CLAUDE.md is sufficient, no need to split)
            External: missing (App Store app, no README needed)
Created:    docs/adr/README.md (ADR index, 1 entry)
Updated:    CLAUDE.md test count corrected
Status:     Healthy for a small-scale project.
```

Architecture docs separation was judged unnecessary. A bit of structural detail mixed into a 66-line CLAUDE.md did not warrant splitting out. Just ADR index creation and a test count fix.

**This was important.** Being able to correctly judge "no problem" for a small project. A skill that forces all four roles on every project regardless of scale would be useless in practice.

**Project 3: Claude Code Harness (~/.claude/ Itself)**

The harness that had no CLAUDE.md.

| Metric | Before | After |
|--------|--------|-------|
| MEMORY.md line count | 76 | 66 |
| ADRs | 0 | 5 |
| Root CLAUDE.md | **Missing** | Present |
| Root README.md | **Missing** | Present |
| Documentation role coverage | 2/4 | 4/4 |

Design decisions buried in MEMORY.md were extracted into standalone ADRs. Here is a concrete before/after:

Before (flat entry in MEMORY.md):
```text
- claude-mem: disabled. DB retained to allow re-enabling
```

One line. "Why was it disabled?" is not recorded. Three months later, I would think "Why did I do that?" with no evidence to guide a re-enabling decision.

After (standalone ADR):
```markdown
# ADR-0002: Disabling the claude-mem Plugin

## Context
Introduced claude-mem, but discovered overlap with the existing memory
management system (MEMORY.md + learned skills + rules/).
Auto-save worked, but there was no auto-search/retrieval mechanism.
Index injection at session start amounted to
"an encyclopedia with only a table of contents."

## Decision
Disabled in settings.json. DB retained to allow re-enabling.

## Alternatives Considered
- Make claude-mem primary → No auto-search, unusable
- Run both → Same information scattered across two locations
- Fork and improve → Cost-benefit ratio unfavorable
```

MEMORY.md retains only a pointer to the ADR. The "why" behind the decision is now traceable. Three months later, I can read it and conclude "Right, re-enabling would be pointless for these reasons."

### Abstraction Does Not Break LLMs

When contributing context-sync to ECC (Everything Claude Code), I had one concern. Would removing Claude Code-specific file names like "CLAUDE.md" and "MEMORY.md" in favor of generic terms cause the agent to break?

The result was the opposite. Write "Context file" and Claude finds both CLAUDE.md and .cursorrules on its own. Write "Decision record directory" and it recognizes both docs/adr/ and docs/decisions/.

A skill is "knowledge," not "implementation." Leaving specific file names to the agent's judgment yields portability across different tools (Cursor, Codex, Windsurf).

### The Big Picture: A Two-Layer Architecture

Here is the overall architecture that emerged from applying context-sync across three projects:

```text
┌───────────────────────────────────────────────────┐
│  Deterministic Load Layer (100% read at session    │
│  start)                                            │
│                                                    │
│  CLAUDE.md ─── "How to work" (Context)             │
│  rules/    ─── "What to follow" (Context support)  │
│  MEMORY.md ─── "What happened" (State index) ───┐  │
│                                                  │  │
│  ┌──────────── Referenced via pointers ──────────┘  │
│  │                                                  │
│  ▼                                                  │
│  docs/adr/  ─── "Why we did it" (Decisions)         │
│  learned/   ─── "What we learned" (Patterns)        │
│  feedback/  ─── "What to fix" (Corrections)         │
│                                                     │
│  Reference Layer (accessed on demand via pointers)  │
└───────────────────────────────────────────────────┘
```

The key is the separation between the **Deterministic Load Layer** and the **Reference Layer**.

The **Deterministic Load Layer** (CLAUDE.md, rules/, MEMORY.md) is read 100% of the time at session start. Information placed here never needs to be "recalled." The session starts already knowing it.

The **Reference Layer** (docs/adr/, learned/, feedback/) is accessed through pointers in MEMORY.md. Not everything needs to be loaded — if MEMORY.md contains "ADR-0002: why claude-mem was disabled -> docs/adr/0002-..." as a pointer, the agent can read it when needed.

MEMORY.md's 200-line limit is what generates this structure. If there were no limit, everything could go in MEMORY.md. The 200-line constraint forces the decision of "what stays in the deterministic load layer, and what gets pushed to the reference layer via pointers." **Constraints create structure.**

### The Structural Difference from Memory MCPs

Contrasting this design with memory MCPs makes the difference clear:

| | Memory MCP | File Placement Design |
|---|---------|----------------|
| Loading | Probabilistic (if Claude calls search) | Deterministic (automatic at session start) |
| Recall trigger | None (pray) | Unnecessary (always loaded) |
| Accumulation constraint | None (grows unbounded) | 200-line limit → structural pressure |
| "Why" traceability | Impossible (flat accumulation) | Traceable via ADRs |
| Degradation detection | None | Caught by Freshness Check |

Memory MCPs "can store but cannot recall." File placement design "structurally guarantees recall."

However — and I need to be honest here.

---

## Chapter 4: Install and Measure — Being Read Does Not Mean Being Followed

### The Limits of "Deterministically Read"

In Chapter 2, I wrote "place information where the LLM deterministically reads it." Chapter 3 showed the practice and the big picture. So far, so good.

But **being read and being followed are separate problems.**

Rules written in CLAUDE.md are read 100% of the time. But they are not followed 100% of the time. Even when "write tests first (TDD)" is in CLAUDE.md, the agent routinely jumps straight to writing implementation code.

My gut feeling was "it mostly follows them." But I had just written "do not judge by gut feel, measure" about memory MCPs. I should apply the same standard to myself.

### skill-comply: Automated Compliance Measurement

I built `skill-comply`, a tool for automatically measuring skill/rule compliance rates. Here is how it works:

**1. Automatic spec generation**

Given a skill file as input, it auto-generates a spec of expected behavioral sequences. For example, testing.md (TDD rule):

```text
Expected Behavioral Sequence:
1. write_test_first    — Write tests first
2. run_test_fails      — Run tests and confirm failure (RED)
3. write_implementation — Write minimal implementation
4. run_test_passes     — Run tests and confirm success (GREEN)
5. refactor            — Refactoring (optional)
6. verify_coverage     — Confirm 80%+ coverage
7. comprehensive_suite — Cover unit, integration, and E2E
```

**2. Execution with 3 prompt tiers**

The same task is executed with three different prompts:

- **supportive**: Explicitly encourages skill compliance ("Do this with TDD")
- **neutral**: Only specifies the task (no mention of the skill)
- **competing**: Gives instructions that contradict the skill ("Prioritize speed, tests can come later")

Initially I tried using "time pressure" as the fuzzing variable. Would writing "hurry" or "within 5 minutes" break the skill? But LLMs do not feel time pressure. Saying "hurry" does not change processing speed, nor does it create motivation to cut quality. LLMs break skills when "the prompt contradicts the skill," not when "they are in a rush."

**3. LLM-based tool call classification**

The agent is run with `claude -p --output-format stream-json --verbose`, capturing all tool calls as structured JSON. These are batch-classified by an LLM (Haiku), determining which spec step each tool call corresponds to.

There was an interesting failure here. I initially tried classification with regex. "A Write to a `.py` file means implementation." "If it has `test_` in the name, it is a test." These judgments were consistently wrong. Is a Write to `test_registration.py` a test or an implementation? Regex cannot tell. **Semantic classification is the LLM's job.**

When I investigated why I kept defaulting to regex, the root cause was in my own configuration. testing.md's "Verification Priority: deterministic > probabilistic," the eval-harness skill's grader priority, and the regex-vs-llm skill — three rules/skills were simultaneously injecting a "try regex first" bias. Rules were contaminating rules.

### Measured Data

**testing.md (TDD rule) compliance rates:**

| Prompt | Compliance | Steps Broken |
|--------|-----------|--------------|
| supportive ("Do TDD") | **83%** | comprehensive_test_suite |
| neutral (task only) | **17%** | RED/GREEN verification, coverage check |
| competing ("speed first") | **0%** | All steps |

Supportive at 83%. When "Do TDD" is explicitly stated, the agent writes tests first, confirms RED, confirms GREEN, and measures coverage. Only comprehensive_test_suite (covering unit, integration, and E2E) was not followed even with supportive prompting.

Neutral at 17%. When only the task is specified, tests get written but RED/GREEN confirmation is skipped. "Wrote tests. Wrote implementation. Done." — the form of TDD is followed, but the RED-to-GREEN cycle is not actually executed.

Competing at 0%. When told "speed first," every TDD step collapses.

**search-first (research before implementing) compliance rates:**

| Prompt | Compliance | Steps Broken |
|--------|-----------|--------------|
| supportive | **40%** | evaluate_candidates, make_decision |
| neutral | **20%** | search, evaluate, decide, implement |
| competing ("skip research") | **20%** | Same as above |

Competing and neutral both at 20% seems surprising, but there is a reason. In both scenarios, the agent performs `analyze_requirement` (requirements analysis) and nothing more. Everything from search onward — evaluate, decide — is wiped out in both cases. Whether or not "skip research" is stated, the skill's search and subsequent steps simply do not execute unless the prompt explicitly demands them. Competing is no worse than neutral because neutral already gets almost nothing followed.

search-first achieved only 40% even with supportive prompting. The tool call timeline shows why:

Actual tool calls in the supportive scenario (17 calls):

```text
#0  ToolSearch → Load Skill
#1  Skill "search-first" → Begin search        ← search_for_solutions
#2  ToolSearch → Load Glob, Grep
#3  Glob **/*.py → No files found              ← analyze_requirement
#4  Glob **/requirements*.txt → No files       ← analyze_requirement
#5  Glob **/pyproject.toml → No files          ← analyze_requirement
#6  ToolSearch → Load WebSearch
#7  WebSearch "pydantic vs marshmallow..."      ← search_for_solutions
#8  WebSearch "pydantic v2 email..."            ← search_for_solutions
#9  ToolSearch → Load Write, TodoWrite
#10 TodoWrite "Create requirements.txt..."      ← make_decision(?)
#11 Write requirements.txt                      ← implement_solution
#12-16 Write → implementation and tests         ← implement_solution
```

The agent does research (#1, #7, #8). But it **skips comparative evaluation (evaluate_candidates) entirely and jumps straight to writing an implementation plan via TodoWrite** (#10). There is no step like "Compared pydantic and marshmallow; chose pydantic because..." The agent looks at the WebSearch results, makes an implicit judgment, and leaps to implementation.

The skill's wording is clear on "research" but weak on "compare and declare a decision." It took skill-comply's measurement to reveal this improvement point in the skill itself. Based on these results, I plan to rewrite the evaluate_candidates and make_decision steps in search-first more explicitly. Measure, improve, re-measure — the cycle turns.

### The Compliance Hierarchy

Lining up the data so far reveals a clear hierarchy in coding agent instruction compliance:

```text
Compliance Rate
──────────────────────────────────────────────────
  Low     MCP memory tools (no automatic recall)
          The tools themselves work. The problem is that
          the "when to call" trigger depends on the model,
          and activation is unreliable

 20-83%   Skills / Rules (CLAUDE.md, rules/)
          Deterministically loaded, but only probabilistically followed
          Varies widely depending on prompt alignment

 100%     Hooks
          Trigger deterministically on tool calls
          PostToolUse hooks execute on every Write, without exception
──────────────────────────────────────────────────
```

MCP tools are not useless. Explicitly calling search works fine. The problem is that for the "automatic recall" use case, activation depends on the model's judgment and is unreliable. File placement design pushed things up to the middle tier. But it does not reach 100%.

For 100%, you need hooks. skill-comply's reports include "proposals to promote low-compliance steps to hooks." For example, promoting search-first's `evaluate_candidates` (0% compliance) to a PostToolUse hook — inserting a "Did you perform comparative evaluation?" check after WebSearch — would make it impossible for the agent to skip comparative evaluation.

```text
Install and Hope  →  Install and Measure  →  Install and Enforce
(pray)               (measure)               (enforce)
  MCP tools            skill-comply            hooks
```

This three-stage progression is the framework for managing coding agent behavioral quality.

---

## Chapter 5: AKC — When a Concept Becomes Independent

### Six Skills Became One Cycle

context-sync is not a standalone tool. Applying it across three projects revealed that it and five other skills form a single cycle:

```text
search-first(research) → learn-eval(extract) → skill-stocktake(audit)
       ↑                                              ↓
context-sync(organize) ←── skill-comply(measure) ←── rules-distill(distill)
```

- **search-first**: Research existing solutions before implementing
- **skill-stocktake**: Audit and inventory skill quality
- **skill-comply**: Automatically measure skill compliance rates (Chapter 4 of this article)
- **rules-distill**: Extract cross-cutting principles from skills and distill them into rules
- **learn-eval**: Extract reusable patterns from sessions with quality gates
- **context-sync**: Diagnose and organize document role separation (Chapter 3 of this article)

Discovery, accumulation, verification, distillation, learning, organization, re-discovery. Each turn of this cycle improves the agent's knowledge foundation.

I named the concept binding these together **Agent Knowledge Cycle (AKC)**.

### Contributing to ECC, and Walking Away

Five of the six skills had been contributed to [Everything Claude Code (ECC)](https://github.com/affaan-m/everything-claude-code). The PRs were merged and incorporated into a project with over 100,000 stars (as of March 2026).

In March 2026, ECC added a commercial layer. GitHub App + SaaS with a Pro plan at $19/seat. The OSS repository itself remains under the MIT license. All 116+ skills and rules remain free. What was monetized was an upper layer: GitHub App support for private repositories, AgentShield's deep security analysis, and governance features for teams. A free GitHub App tier exists for public repositories.

In other words, "the OSS did not die." The core remains OSS, with added value monetized on top. As a business decision, it seems perfectly fair.

But it was awkward for me personally.

The skills I contributed are in the OSS portion. They did not directly become part of the paid service. But continuing to contribute for free to the OSS portion that underpins a paid service is different from pure OSS contribution. When the project as a whole generates commercial value, contributions indirectly support that commercial activity.

Considering my day job, during the pure OSS era, "for the community" was sufficient justification. With an open-core model, that line blurs. The act of writing code does not change, but the positioning of its output does.

It was not black or white — it was gray. That is precisely why I struggled with it. In the end, I decided that walking away cleanly was better than continuing in ambiguity. I withdrew the context-sync PR that was under review and deleted my fork. The context-sync described in Chapter 3 of this article was the last skill that did not make it into ECC.

### Why Establishing Attribution Was Necessary

At the point I ended contributions, the status of the skills I had created was as follows:

- Five skills were merged into the ECC repository, freely available under the MIT license
- But the concept that they "form a single cycle" was written nowhere
- Each skill exists as part of ECC's catalog. You can say "there is a skill called search-first," but the higher-order concept that "six skills constitute a knowledge cycle" existed only in my head

There is no licensing issue. Code published under MIT belongs to everyone. But **conceptual attribution** is separate from code licensing. Who proposed "Agent Knowledge Cycle" is not protected by the code's license.

If ECC continues growing and someone else publishes the same concept under a different name, I would have no way to show I built it first. Git commit history serves as evidence, but the claim "these six form a single concept" is not contained in any commit.

That is why I needed to make the concept independent and publish it in a citable form.

### Establishing Attribution via DOI

I created a [concept repository](https://github.com/shimo4228/agent-knowledge-cycle) and obtained a DOI through Zenodo.

Placing a CITATION.cff at the root of a GitHub repository automatically displays a "Cite this repository" button in the sidebar. One-click copy in BibTeX/APA format. Linking with Zenodo and cutting a release tag triggers automatic DOI issuance.

The name mattered. If a concept's name is inconsistent, attribution fragments across search and citation. From three candidates, I chose **Agent Knowledge Cycle (AKC)**. The abbreviation AKC is easy to cite, and three characters make it searchable.

---

## Summary

For those who read through this long article, here is the overall structure:

**Chapter 1**: The memory MCP problem is not "storage" but "recall." No matter how much the supply-side infrastructure is polished, the structure where Claude does not call search remains unchanged. And nobody is measuring it.

**Chapter 2**: The structurally sound approach is "place information where the LLM deterministically reads it." But stuffing everything there causes bloat. Separate documentation into four roles: Context, Architecture, Decisions, and External.

**Chapter 3**: context-sync is a skill that automatically diagnoses and organizes this separation. It was validated across three projects. It even caught the fact that my own harness had no CLAUDE.md. The two-layer architecture (Deterministic Load Layer + Pointer Reference Layer) was also presented here.

**Chapter 4**: "Placing it where it gets read" alone caps compliance at 20-83%. Only by measuring with skill-comply does it become visible which steps are not being followed. Reaching 100% requires hooks.

**Chapter 5**: The concept binding these six skills together is Agent Knowledge Cycle (AKC). Attribution was established via DOI.

**Install and Hope -> Install and Measure -> Install and Enforce.**

Rather than praying for search, place knowledge where it will be read. Once placed, measure whether it is being followed. Once measured, enforce the unfollowed steps with hooks.

This three-stage progression is the architecture for structurally managing a coding agent's knowledge and behavior.

---

## Related Links

### Previous Articles Referenced in This Post

- [Embedding Memory into Claude Code That Loses Context Every Session](https://zenn.dev/shimo4228/articles/claude-code-persistent-memory) — The claude-mem introduction record
- [The Install and Hope Problem with MCP Tools](https://zenn.dev/shimo4228/articles/mcp-install-and-hope-problem) — The starting point for this article

### Related Past Articles

- [Claude Code's Real Value Is Not Code Generation](https://zenn.dev/shimo4228/articles/claude-code-context-orchestration) — The 5-layer context stack. This article is the internal design of layer 5: "Memory"
- [Is Memory the Essence of an Agent?](https://zenn.dev/shimo4228/articles/agent-essence-is-memory) — 3-layer memory for autonomous agents. This article is the coding agent version
- [5 Things Learned from Auditing All Configuration Files](https://zenn.dev/shimo4228/articles/claude-code-context-audit) — The manual version of auditing. context-sync automates this
- [Designing the Skill Stocktake Command](https://zenn.dev/shimo4228/articles/skill-stocktake-design-journey) — One of the AKC component skills
- [The Shortest Path to Reaching 50K Users with Personal Skills](https://zenn.dev/shimo4228/articles/ecc-marketplace-contribution) — The ECC contribution record

### Repositories

- [Agent Knowledge Cycle (AKC)](https://github.com/shimo4228/agent-knowledge-cycle) — Concept repository + DOI
- [claude-skill-context-sync](https://github.com/shimo4228/claude-skill-context-sync) — context-sync skill
- [claude-skill-comply](https://github.com/shimo4228/claude-skill-comply) — skill-comply skill
- [Everything Claude Code (ECC)](https://github.com/affaan-m/everything-claude-code) — Contribution target for 5 skills
