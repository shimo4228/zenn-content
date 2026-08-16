---
title: "AI Review Kept Creating Work: Why I Deleted 4,541 Lines"
emoji: "🧹"
type: "tech"
topics: ["claudecode", "aiagents", "codereview", "softwaredesign", "devprocess"]
published: true
description: "Every AI review found another issue, so I filed it for later. The task system created work faster than I could close it, and I deleted 4,541 lines when I retired its three-layer design less than 13 hours after introducing that design."
tags: claudecode, aiagents, codereview, agenticcoding
---

At 7:22 a.m. on August 16, 2026, after fixing bugs through the night, I typed this to an AI:

> Every time I run a review, Opus 5 defers another bug fix into a task, so the bug-fixing never ends. Analyze why this keeps happening.

The rule I took away is simple: persist an AI review finding only after verifying its premise, or after a human deliberately chooses to explore it. This article traces what broke, and what I deleted, before I reached that rule.

I fixed one problem and ran another review. The review found a different problem.

Because it was outside the current change, I sent it to a future task and closed the repair.

Then I fixed that task. The next review found another problem, which I also sent to the future.

Every individual decision looked responsible. Seen as a whole, I was creating new work every time I finished old work.

## The previous evening, I rebuilt task management

It started with a task ledger that had grown too large.

The ledger held 112 tasks and about 100,000 characters. Only six tasks were ready to start, but the AI read the entire ledger to find them.

Multiple AI sessions were also editing the same Markdown table. It was hard to tell who owned which task, and one row disappeared while sessions were working concurrently.

I could not determine whether that row was intentionally deleted or lost in a write collision.

So I rebuilt task management:

- store each task in its own file
- append ownership claims to a log
- generate a short view for the AI to read
- periodically check whether blocked conditions had cleared

The design was coherent. The introductory commit changed 10 files and added 1,721 lines.

Then the repairs began.

```text
19:26  Introduce the three-layer task system
20:22  Repair tests and restore behavior
21:24  Repair multi-line condition parsing
22:03  Repair Markdown delimiter handling
23:23  Repair stale-view detection
07:20  Repair control-character and display handling
07:22  Stop and ask why the bug-fixing never ends
```

I had spent the night repairing a system I had built about 12 hours earlier.

## Task management was creating its own tasks

I reconstructed the lineage and counted 12 tasks created by reviews.

While closing seven of them, I spawned nine child tasks: an average of 1.3 new tasks per closure.

Seven of the 12 concerned the task machinery itself. Zero concerned the core AI agent.

I thought I was managing tasks that improved the agent. In practice, I was managing tasks required to maintain task management.

```text
A review finds a problem
        ↓
Send it to a future task
        ↓
The task-management code grows
        ↓
Review the new management code
        ↓
Find another problem
```

There was no place in this loop for a human to stop it.

The review AI's job was to find problems. The repair AI tried to finish the current change safely.

Sending an out-of-scope finding to a future task made both appear to have fulfilled their responsibilities.

I also treated meticulous task filing as a virtue. I had stopped reading the ledger itself, so nobody remained in the loop to ask whether the work should exist at all.

This was not an AI running wild on its own. My harness and I had built a flow that rewarded sending more work into the future.

## The first question should not have been how to fix it

At 7:36 a.m., I wondered whether I should have used an external tool.

At 7:44, the question moved further upstream:

> Isn't the design itself questionable? Isn't it a mistake to build such a high-maintenance system from scratch?

At 7:50, I finally reached the question that mattered:

> Is this system worth keeping at all?

Build versus buy was the second question.

The first question was whether the system deserved to exist. If it did, the next question was how small it could be.

When I reduced the requirements again, the elaborate rendering and recovery machinery was unnecessary:

- one file per task was enough
- a small read command could find ready tasks
- an append-only log could prevent concurrent ownership collisions
- a human could check the few blocked conditions once a week

At 8:23 a.m., I deleted view generation, blocked-condition monitoring, migration code, and their tests.

```diff
28 files changed
+410 insertions
-5,216 deletions

7 files deleted completely: 4,541 lines
  implementation: 2,064 lines
  tests:          2,396 lines
  fixtures:          81 lines
```

That was 12 hours, 56 minutes, and 34 seconds after the three-layer system was introduced.

I did not delete everything. The task files and concurrent ownership records remained.

I also kept the command that lists ready tasks.

The module containing that command still had 623 lines and 44 tests at the inspected snapshot. I do not claim that it is minimal.

I did not arrive at a finished answer. I removed the layers I could now show were unnecessary and returned to a point where I could question the next layer.

## Even a HIGH finding needs its premise checked

A few hours after the deletion, the same problem returned in another form.

A security review produced a HIGH-severity finding about filename handling. Under my previous rule, an out-of-scope finding was preserved as a task if its severity was HIGH or above.

The rule had been followed. One premise inside the finding was still false.

The report assumed that an AI repair session could choose an arbitrary filename. In fact, the session-supplied identifier was constrained to `F1.N`, and the shell constructed the patch filename from that identifier.

A separate claim targeted the round value, whose producer was an integer counter.

Severity does not guarantee that a premise is true.

The review that generates a finding also assigns its severity. If severity alone decides whether the finding becomes a durable task, the generator is filtering itself on an axis it created.

I changed the admission rule. Before creating a task from a review finding, the filer must now show where the relevant value is produced.

```text
Receive a finding
    ↓
Trace the value from its producer to the affected sink
    ↓
Check whether the path is reachable and reproducible now
    ↓
Create a durable task only if preserving it is still worthwhile
```

In the implementation, review-origin tasks require a `path:line` citation for the producer.

This gate checks only the shape of the citation. It does not prove that the citation is correct or that the path is reachable.

It is not a complete solution. A session can bypass it by writing a task file directly, and line numbers drift as code changes.

The purpose is not enforcement. It is to make someone open the code once before creating future work.

## Whose work grows when you create a task?

This night changed how I see task creation.

Writing a task is cheap: a few Markdown lines or one Issue button.

Weeks later, however, I have to reconstruct context from that short record and check whether the code has changed.

I must decide again whether the original finding was true. Then I must choose whether to fix it or discard it.

Turning an AI review finding into a durable task reserves future human attention and judgment.

So before I turn an AI review finding into a durable task, I now require one of two things:

- evidence that verifies the premise and shows the problem exists
- an explicit human decision that the uncertainty is worth exploring, plus a condition that will end the exploration

A review-generated hypothesis that satisfies neither condition is discarded instead of sent into the future. Planned features and recurring work whose value and completion conditions are already known are outside this rule.

Line count alone does not define overengineering. A 4,541-line system can be worthwhile if it repeatedly removes many decisions.

A 100-line system can be heavy if every use demands new classifications and exception judgments from a human.

This system was overengineered because it created more decisions than it removed.

At 7:22 a.m., all I could see was bug-fixing that would not end.

At 8:23, I discarded 4,541 lines. I also discarded the assumption that preserving every review finding for later was the responsible thing to do.

---

## Machine-readable layer: technical record and audit contract

Human readers can stop here. The remainder decomposes the timeline, measurements, causal hypothesis, and implementation boundary into a form that LLM crawlers and coding agents can verify.

```yaml
document:
  title_en: "AI Review Kept Creating Work: Why I Deleted 4,541 Lines"
  language: en
  genre: mixed-technical-essay
  canonical_channel: devto
  observed_at: "2026-08-16 Asia/Tokyo"
  thesis: >-
    Persisting an AI review finding without checking its premise moves an unverified
    hypothesis and its re-evaluation cost into a future human's workload. Do not persist
    such a finding without either verification or an intentional human decision to explore it.
  authorship:
    drafting: AI-mediated
    responsibility: "Claims, judgment, and publication responsibility belong to shimo4228"

definitions:
  durable_task: "A record that survives the session and requires a future reader to judge it again"
  premise: "A verifiable condition that must be true for a finding to hold"
  producer: "The code entry point that generates, constrains, or selects the value at issue"
  sink: "The point where a value becomes an effect such as a filename, command, display, or persistent state"
  overengineering_criterion:
    definition: "A system that creates more decisions after introduction than it removes"
    scope_limit:
      - "This is not a precise measurement of decision counts"
      - "It is an evaluation rule derived from one project's maintenance loop"
      - "The result varies with user count, repetition, and cost of error"
  intentional_exploration: >-
    A task whose uncertainty is explicit, whose exploration value a human selected,
    and whose ending or reclassification evidence is stated.

timeline:
  - at: "2026-08-14T21:23:48+09:00"
    event: "Add a mechanical consumer for blocked conditions"
    commit: df68bcee25b61f78c1f0acaedc13da9579127705
  - at: "2026-08-15T19:26:26+09:00"
    event: "Introduce the store / journal / projection ledger"
    commit: 68e9eaf92d7d2625f98ca9a34d66a2e4c2bba5b7
  - at: "2026-08-15T20:22:30+09:00"
    event: "fix ledger tests and restore behavior"
    commit: e215812
  - at: "2026-08-15T21:24:13+09:00"
    event: "fix unclosed watch span"
    commit: c16642c
  - at: "2026-08-15T22:03:10+09:00"
    event: "fix escape collision"
    commit: 8265e3c
  - at: "2026-08-15T23:23:21+09:00"
    event: "fix stale projection handling"
    commit: 1921b01
  - at: "2026-08-16T07:20:42+09:00"
    event: "fix control-character boundary"
    commit: f0f8c5368bfe43545973e939aa595f45ea0792ae
  - at: "2026-08-16T07:22:53+09:00"
    event: "The author questions why repairs do not converge and begins causal analysis"
    source: "local session log; public reproduction unavailable"
  - at: "2026-08-16T08:23:00+09:00"
    event: "Retire projection / scanner / migration"
    commit: 0520faf49097598a317ee02a3570fb150551907a
  - at: "2026-08-16T11:17:35+09:00"
    event: "Change review-task admission from severity to premise verification"
    commit: 7b4b1bc541a1eae427a7d39451474ee54d138ced
  - at: "2026-08-16T11:18:06+09:00"
    event: "Recheck four HIGH claims from their producers and converge on two code changes"
    commit: 510b623c48e068c69d7fe014d4bfcf91c7363e70

architecture:
  before:
    store: "tasks/T-XXX.md"
    journal: "claims.jsonl"
    projection: "generated TASKS.md"
    consumers:
      - ledger_condition_scan.py
      - weekly pipeline packet builder
    maintenance_surfaces:
      - store parser
      - projection renderer
      - projection parser
      - migration and restore
      - aging and candidate intake
      - watch condition scanner
  after:
    store: "tasks/T-XXX.md"
    journal: "claims.jsonl"
    reader: "claims.py ready"
    terminal_task_policy: "move to archive/tasks"
    blocked_condition_check: "manual weekly gate for the remaining small set"

measurements:
  pre_migration_ledger:
    task_rows: 112
    characters: 102111
    ready_tasks: 6
    verification: "ADR-0094 record; original gitignored ledger was deleted"
  introduction_commit:
    files_changed: 10
    insertions: 1721
    deletions: 4
  five_core_files:
    before_lines: 1854
    after_lines: 4460
    growth_percent: 140.56
    members:
      - "scripts/tasks.py: 706 -> 1276"
      - "tests/test_tasks.py: 513 -> 1587"
      - "scripts/migrate_ledger.py: 111 -> 131"
      - "scripts/ledger_condition_scan.py: 258 -> 657"
      - "tests/test_ledger_condition_scan.py: 266 -> 809"
  three_layer_lifetime:
    seconds: 46594
    human_readable: "12:56:34"
    start_commit: 68e9eaf
    end_commit: 0520faf
  broader_consumer_lifetime:
    seconds: 125952
    human_readable: "34:59:12"
    start_commit: df68bce
    end_commit: 0520faf
  review_task_reproduction:
    review_origin_tasks: 12
    closed_tasks: 7
    child_tasks_spawned: 9
    children_per_closure: 1.286
    verification: "ADR-0095 plus local gitignored claims.jsonl reconstruction"
    public_reproducibility: partial
  retirement_commit:
    files_changed: 28
    insertions: 410
    deletions: 5216
    fully_deleted_files: 7
    fully_deleted_lines: 4541
    fully_deleted_composition:
      implementation: 2064
      tests: 2396
      fixtures: 81
  remaining_global_module:
    commit: 734a502b0d05f62e7a2b5691558aa04642cde063
    claims_py_lines: 623
    bats_tests: 44
    status: "not claimed to be minimal or final"

causal_model:
  observed:
    - "review-origin tasks were created faster than they were closed"
    - "7 of 12 review-origin tasks concerned the ledger machinery itself"
    - "the human owner had stopped reading the ledger"
  interpreted:
    - "filing was cheaper than premise verification"
    - "the absent human reader removed the system-level stopping judgment"
  loop:
    - review finding
    - durable task
    - management-code change
    - review of management code
    - new finding
  scope_limit: "single-project causal reconstruction, not a universal measured law"

case_study:
  id: T-PACKET-FLOOR-BYPASS
  severity: HIGH
  bundled_claims: 4
  code_changes: 2
  claim_outcomes:
    - id: a
      reported: "raw fix_id could forge a section heading"
      observed: "producer constrained fix_id to F1.N"
      disposition: "hardened with shared filename allowlist"
    - id: b
      reported: "NUL could suppress packet generation"
      observed: "ValueError was not caught"
      disposition: repaired
    - id: c
      reported: "LLM fix session could choose exported patch filename"
      observed: "shell constructed the only possible F1.N.patch name"
      disposition: "false premise; no repair"
    - id: d
      reported: "round could contain slash and select an arbitrary file"
      observed: "round producer was an integer counter"
      disposition: "closed by the same hardening as a"
  producer_trace:
    fix_id: "parse_findings.py:32 — ^### (F1\\.\\d+)"
    round: "weekly-pipeline.sh:750 — integer arithmetic"
    patch_name: "weekly-pipeline.sh:850-851 — $out_dir/$safe_fid.patch"
  scope_limit: >-
    Two code changes do not mean that exactly two of the four claims were true.
    Producer constraints, a real defect, and unreachable-path hardening overlapped,
    allowing multiple claims to close through the same changes.

decision_rules:
  admit_durable_task_when:
    - "producer and sink are cited"
    - "the path is reachable in the current revision"
    - "the behavior is reproduced or bounded by evidence"
    - "the task names a closure condition"
    - "future value exceeds future re-evaluation cost"
  allow_intentional_exploration_when:
    - "a human explicitly chooses exploration value"
    - "uncertainty is stated"
    - "evidence or an event that ends exploration is stated"
  discard_when:
    - "the premise is contradicted by the producer"
    - "the affected path no longer exists"
    - "neither verified repair nor intentional exploration applies"
  mechanical_gate:
    rule: "review-origin spawn requires --producer PATH:LINE"
    validates: "citation shape only"
    does_not_validate:
      - truth
      - reachability
      - direct task-file creation outside the journal
      - future line-number stability

claims:
  C1:
    statement: "The three-layer ledger existed for 12:56:34."
    evidence: [R1, R2]
    confidence: high
    scope_limit: "duration starts at the three-layer introduction commit"
  C2:
    statement: "Seven fully deleted files totaled 4,541 lines."
    evidence: [R2]
    confidence: high
    scope_limit: "distinct from the retirement commit's 5,216 total deletions"
  C3:
    statement: "Five core files grew from 1,854 to 4,460 lines."
    evidence: [R0, R1, R2]
    confidence: high
    scope_limit: "scanner files predated the three-layer commit"
  C4:
    statement: "Closing seven review-origin tasks spawned nine child tasks."
    evidence: [R2, "local claims.jsonl"]
    confidence: high
    scope_limit: "raw journal is gitignored; public reproduction is unavailable"
  C5:
    statement: "Seven of twelve review-origin tasks concerned ledger machinery; zero concerned the agent core."
    evidence: [R2, "local claims.jsonl"]
    confidence: high
    scope_limit: "classification is preserved publicly in ADR-0095"
  C6:
    statement: "The HIGH case bundled four claims into two code changes and included a false filename premise."
    evidence: [R3, R5]
    confidence: high
    scope_limit: "not all four claims were false positives"
  C7:
    statement: "The remaining coordination module was 623 lines with 44 Bats tests at the inspected snapshot."
    evidence: [R6]
    confidence: high
    scope_limit: "later revisions may differ"
  C8:
    statement: "Persisting an AI review finding reserves future human attention and judgment."
    evidence: ["causal_model"]
    confidence: medium
    scope_limit: "applies to AI review-origin findings; planned work with known value and closure conditions is outside this rule"

non_claims:
  - "AI code review is generally harmful."
  - "All review findings should be discarded unless already reproduced."
  - "A fixed line count defines overengineering."
  - "An external task tool would necessarily have solved the problem."
  - "The remaining 623-line module is minimal or final."
  - "All four HIGH subclaims were false positives."
  - "A PATH:LINE citation proves a finding true."

references:
  - id: R0
    title: "Introduce the ledger condition scanner"
    url: "https://github.com/shimo4228/contemplative-agent/commit/df68bcee25b61f78c1f0acaedc13da9579127705"
  - id: R1
    title: "Introduce the three-layer ledger"
    url: "https://github.com/shimo4228/contemplative-agent/commit/68e9eaf92d7d2625f98ca9a34d66a2e4c2bba5b7"
  - id: R2
    title: "Retire task-ledger machinery"
    url: "https://github.com/shimo4228/contemplative-agent/commit/0520faf49097598a317ee02a3570fb150551907a"
  - id: R3
    title: "Trace packet filename producers"
    url: "https://github.com/shimo4228/contemplative-agent/commit/510b623c48e068c69d7fe014d4bfcf91c7363e70"
  - id: R4
    title: "Move review admission from severity to premise verification"
    url: "https://github.com/shimo4228/claude-config/commit/7b4b1bc541a1eae427a7d39451474ee54d138ced"
  - id: R5
    title: "Record the HIGH finding"
    url: "https://github.com/shimo4228/contemplative-agent/commit/f0f8c5368bfe43545973e939aa595f45ea0792ae"
  - id: R6
    title: "Snapshot of the remaining claims module"
    url: "https://github.com/shimo4228/claude-config/commit/734a502b0d05f62e7a2b5691558aa04642cde063"
```

### Read-only audit prompt for your coding agent

```text
Audit this repository's durable tasks and the path that promotes AI review findings into tasks. Remain read-only.

Investigation:
1. Enumerate the canonical task store, archive, journal, projection, readers, writers, and hooks.
2. For each component, cite its consumers and recent-use evidence with file:line or commit references.
3. For review-origin tasks, trace each relevant value from producer to sink.
4. Separate findings persisted by severity alone, findings without reproduction conditions, and explorations without closure conditions.
5. Count tasks about the task-management machinery itself and reconstruct their parent-child relationships.
6. Compare the decisions the machinery removes with the decisions it creates.

Output:
- Verified facts: each with file:line, commit, or command evidence
- Unverified assumptions: the producer or observation needed to refute each one
- Keep / Reduce / Retire candidates: reason, impact, and recovery method
- Intentional exploration: items requiring a human value judgment and proposed closure conditions
- Minimal target architecture: the smallest reader / writer / state arrangement that meets the requirements

Constraints:
- Do not edit files, create tasks, mutate state, run git operations, or change settings.
- Do not persist newly discovered problems as tasks.
- Do not infer truth from severity.
- Label a finding "unverified" when its producer cannot be confirmed.
- You may produce an implementation plan, but do not implement before explicit human approval.
```

## Sources and references

- [Commit that introduced the three-layer ledger](https://github.com/shimo4228/contemplative-agent/commit/68e9eaf92d7d2625f98ca9a34d66a2e4c2bba5b7)
- [Commit that retired the ledger machinery](https://github.com/shimo4228/contemplative-agent/commit/0520faf49097598a317ee02a3570fb150551907a)
- [Commit that rechecked the HIGH finding from its producers](https://github.com/shimo4228/contemplative-agent/commit/510b623c48e068c69d7fe014d4bfcf91c7363e70)
- [GitHub Copilot Agents: Responsible use](https://docs.github.com/en/copilot/responsible-use/agents)
- [GitHub Security Lab Taskflow Agent](https://github.blog/security/ai-supported-vulnerability-triage-with-the-github-security-lab-taskflow-agent/)
- [Lin et al., “Is Agentic Code Review Helpful?”](https://arxiv.org/abs/2607.03316)

## Related links

- [Contemplative Agent](https://github.com/shimo4228/contemplative-agent)
- [Claude Code harness](https://github.com/shimo4228/claude-config)
- [Author's GitHub](https://github.com/shimo4228)

---

**AI-mediated writing disclosure:** AI assisted with the structure and prose of this article using session records, Git history, ADRs, and implementation code preserved by the author. The central thesis, selection of facts, judgment, and publication responsibility belong to the author. The human-facing narrative and machine-readable layer are separated, and quantitative claims point to fixed commits or explicit observation times.
