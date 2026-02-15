---
title: "15 Days of Skill Sprawl in Claude Code — Lessons from 3 Audits"
emoji: "🗃️"
type: "tech"
topics: ["claude", "ai", "claudecode", "devtools"]
published: true
---

## Introduction

In [Part 1](https://qiita.com/shimo4228/items/06d48f19bde5e6401a85), I wrote about my first 10 days of real development in an ECC environment. In [Part 2](https://qiita.com/shimo4228/items/743f2b43f63b2bbe2dba), I covered the 6 pitfalls I hit while building pdf2anki with the Claude API.

This time, I'll talk about what was quietly growing behind the scenes: **skills**.

Over 15 days with ECC, my skills grew from 16 to 48. Learned skills alone — patterns that Claude Code automatically extracts from development sessions — reached 40. While I was working on 6 projects in parallel, all of them piled up in the same global folder.

Swift DI patterns, Python immutable dataclasses, Zenn textlint workarounds. All dumped into the same `~/.claude/skills/learned/`.

One audit wasn't enough. I did 3 in 15 days. And on the third, I finally realized: skill management never ends.

This article covers how skills spiraled out of control, what I did in each of the 3 audits, and the shocking reality of continuous-learning-v2.

---

## How Skills Work — A 3-Minute Overview

Claude Code loads skills in 3 stages.

| Stage | What's Loaded | Cost |
|-------|---------------|------|
| Discovery | name + description only | 30–50 tokens/skill |
| Activation | Full SKILL.md for task-relevant skills | Hundreds to thousands of tokens |
| Deep refs | Referenced files loaded on demand | Variable |

The critical constraint is the **Character Budget** at the Discovery stage. The space available for displaying the skill list is limited to roughly 2% of the context window (~16,000 characters). There's a reported case where only 42 out of 63 skills were displayed ([GitHub #13099](https://github.com/anthropics/claude-code/issues/13099)).

In other words, **if you have too many skills, they get silently truncated.** More is not better.

Skills can be placed in 3 locations.

| Location | Purpose | Shareable |
|----------|---------|-----------|
| `~/.claude/skills/` | Global, all projects | No |
| `<project>/.claude/skills/` | Project-specific | Yes, via git |
| `~/.claude/skills/learned/` | Auto-extracted from sessions | No |

This question of "where to put them" became a major problem later.

---

## The Day I Installed ECC (1/31) — It All Started with a Misplacement

On January 31, 2026, I downloaded Everything Claude Code (ECC) as a ZIP from GitHub and placed the files manually.

I made a critical mistake. As I wrote in Part 1, I put files that belong in `~/.claude/` (personal settings) into `MyAI_Lab/.claude/` (workspace) instead.

```text
MyAI_Lab/.claude/
├── rules/     ← Should have been in ~/.claude/
├── skills/    ← 16 skills + 23 legacy commands
├── agents/    ← Should have been in ~/.claude/
├── README.md  ← GitHub file left as-is
└── LICENSE    ← Same
```

I developed 6 projects in parallel for 8 days with this misconfiguration.

| Project | Stack | Commits |
|---------|-------|---------|
| baki-quiz-app | Python/Streamlit | 4 |
| baki-quiz-ios | Swift/SwiftUI | 50+ |
| xmetrics-web | Next.js/Supabase | 15 |
| hanma-db-ios | Swift/SwiftUI | 2 |
| XMetricsTracker | Swift/SPM | 1 |
| pdf2anki | Python | 20 |

Over 90 commits in 8 days. During that time, the first learned skills started appearing.

- `protocol-di-testing` — Swift Protocol-based DI pattern
- `immutable-model-updates` — Swift immutable model updates
- `swift-actor-persistence` — Actor-based state management

All mixed together in `MyAI_Lab/.claude/skills/learned/`. Swift skills and Python skills, same folder.

---

## Reinstallation and the Skill Explosion (2/8–2/9)

On February 8, I finally migrated to `~/.claude/`.

**What the migration involved:**

1. Placed 10 ECC skills in `~/.claude/skills/`
2. Deleted rules/skills/agents from `MyAI_Lab/.claude/`
3. Removed unnecessary GitHub files (README, LICENSE)
4. Archived 5 unused commands to `~/.claude/commands-archive/`

At the same time, pdf2anki development accelerated. And learned skills surged.

| Date | Skill | Origin |
|------|-------|--------|
| 2/8 | cost-aware-llm-pipeline | pdf2anki |
| 2/9 | long-document-llm-pipeline | pdf2anki |
| 2/9 | backward-compatible-frozen-extension | pdf2anki |
| 2/9 | ai-era-architecture-principles | General |
| 2/9 | root-cause-challenge-pattern | General |
| 2/9 | python-immutable-accumulator | General |
| 2/9 | skill-stocktaking-process | Meta (the audit procedure itself) |

By February 9, the learned directory contained **14 files**. pdf2anki's pipeline patterns and baki-quiz-ios's Swift patterns all coexisted in global `~/.claude/skills/learned/`.

Every time I opened a Swift project, pdf2anki's LLM pipeline skills appeared in Discovery. In Python projects, Swift Actor patterns showed up. Wasting Character Budget.

---

## First Audit (2/10) — The Birth of a 3-Layer Structure

**Trigger:** Learned skills hit 14, and I thought "this is getting out of hand."

I set rules for the audit.

1. **Is this skill used in only one project?** → Move to that project
2. **Used across multiple projects?** → Keep it global
3. **Can it be re-derived with a one-liner?** → Retire (delete)

The result was the first establishment of a 3-layer structure.

| Layer | Count | Contents |
|-------|-------|----------|
| Global (`~/.claude/skills/learned/`) | 7 | Cross-project patterns |
| pdf2anki (`.claude/skills/learned/`) | 10 | LLM pipeline-specific |
| baki-quiz-ios (`.claude/skills/learned/`) | 5 | Swift/iOS-specific |

**The 7 skills kept global:**

| Skill | Why Global |
|-------|-----------|
| ai-era-architecture-principles | Design principles applicable to all projects |
| root-cause-challenge-pattern | ROI evaluation framework for feature requests |
| python-immutable-accumulator | Frozen dataclass pattern used across all Python projects |
| python-module-to-package-refactor | Patch target updates during refactoring |
| skill-stocktaking-process | The audit procedure itself (meta-skill) |
| claude-code-tool-patterns | Write/Edit tool gotchas |
| tech-writing-patterns | Tone adjustments for Zenn/Qiita posts |

### Mass Disabling of ECC Standard Skills

ECC ships with standard skills for Django, Spring Boot, Go, ClickHouse, and more. Unused skills still consume Character Budget during Discovery.

I added `disable-model-invocation: true` to the top of SKILL.md for 19 unused skills, disabling model invocation.

```yaml
# Added to top of SKILL.md
disable-model-invocation: true
```

No more Django or Spring Boot showing up in Discovery when I never use them.

---

## They Grew Back (2/11–2/13)

One day after the audit, they were already growing again.

I ran a small second audit on February 11.

| Action | Skill | Reason |
|--------|-------|--------|
| Retire | `pbpaste-secret-to-env` | One-liner trick, easily re-derived |
| Promote | `python-optional-dependencies` → global | Not pdf2anki-specific, general pattern |
| New | `mock-friendly-api-layering` | Preventing internal parameter leakage from public APIs |

Result: Global 7 → 9 / pdf2anki 10 → 9.

But on that same day, **7 new learned skills** were generated. Skills continued accumulating in the days that followed.

ECC's Wave 2 update (2/12) added 5 standard skills. In zenn-content, skills like `prh-hyphen-regex-escape` and `zenn-markdownlint-config` kept piling up as learned entries.

No matter how many times I audited, skills kept growing as long as development continued.

---

## The continuous-learning-v2 Shock (2/14)

Before the third audit, I investigated the actual state of ECC's learning system.

ECC has 2 learning systems.

**v1 (continuous-learning):** At session end, a Stop hook extracts patterns and generates skill files in `learned/`. You can also run it explicitly with `/learn`.

**v2 (continuous-learning-v2):** PreToolUse/PostToolUse hooks record all tool invocations. An observer extracts instincts from observations, and `/evolve` is supposed to refine instincts into skills.

v2 looked more sophisticated. I investigated.

```bash
$ wc -l ~/.claude/homunculus/observations.jsonl
10557 observations.jsonl    # 6.5 MB of raw logs

$ ls ~/.claude/homunculus/instincts/personal/
(empty)

$ ls ~/.claude/homunculus/instincts/inherited/
(empty)

$ ls ~/.claude/homunculus/evolved/
(empty)
```

**10,557 lines of logs accumulated, but 0 instincts.**

I traced the architecture.

```text
observe.sh (hooks)          ← Implemented, running
    ↓ writes
observations.jsonl          ← 10,557 lines accumulated
    ↓ ??? observer reads
instincts/personal/         ← Empty ← THIS IS UNIMPLEMENTED
    ↓ /evolve clusters
evolved/                    ← Empty
```

`observer.md` is a "specification document," not "executable code." There is **no executable code** (daemon, cron, script) to transform observations into instincts.

`observe.sh` tries to send SIGUSR1 to a pid in `.observer.pid`, but there's no process that creates that pid. There's no code that reads `config.json`'s `"observer": { "enabled": true }` and launches anything.

**v2 was "recording everything but learning nothing."**

The design is excellent. The pipeline idea of observations → instincts → evolved skills is brilliant. But the middle layer's implementation is missing.

Meanwhile, v1's `/learn` works correctly, and all 40 of my learned skills were generated by v1.

**Current conclusion:** Until v2 starts working, using v1's `/learn` regularly is the most practical option.

---

## Third Audit (2/14) — 9 Moved, 2 Merged

### Searching for External Tools

Manual auditing is tedious. I looked for automation tools.

| Tool | Purpose | Result |
|------|---------|--------|
| skill-audit (npm) | Quality/security audit | CLI not registered, didn't work. Immature |
| CCPI | Skill marketplace | Worth considering after cleanup |
| OpenSkills | Multi-agent support | Overkill for individual use |
| CraftDesk | Package manager | Registry under development. Too early |

**External tools aren't mature yet; manual auditing is the most reliable approach.** That's the reality as of February 2026.

### Immediate Disabling of ECC Wave 3

That same day, ECC Wave 3 added 14 skills. Django 4, Spring Boot 4, Java 2, Go 2, ClickHouse 1, project-guidelines-example 1.

**I disabled all 14 immediately.** Disable unused skills the moment they're added. That's the lesson from the first audit.

### Executing the Sort

Global learned had re-expanded to 17. The sorting rules were the same as the first audit.

**Moved to projects (9 skills):**

| Skill | Destination | Reason |
|-------|-------------|--------|
| baki-ocr-text-normalization | baki-quiz-ios | OCR normalization regex for martial arts encyclopedia |
| xcode-pbxproj-file-registration | baki-quiz-ios | Xcode-specific operation |
| swift-codable-decode-diagnosis | baki-quiz-ios | Swift Codable diagnostics |
| tech-writing-patterns | zenn-content | Zenn/Qiita tone adjustments |
| zenn-qiita-crosspost-workflow | zenn-content | Cross-posting procedure |
| zenn-markdownlint-config | zenn-content | Zenn-specific lint config |
| zenn-context-driven-writing | zenn-content | Article writing process |
| zenn-textlint-workarounds | zenn-content | textlint false-positive workarounds |
| prh-hyphen-regex-escape | zenn-content | prh hyphen escaping issue |

**Merged (absorbed into parent skills, 2 skills):**

| Absorbed | Into | Reason |
|----------|------|--------|
| mock-patch-target-migration | python-module-to-package-refactor | Patch target updates are part of refactoring |
| llm-batch-json-key-normalization | parallel-subagent-batch-merge | Key normalization is a quality check step in batch merging |

By asking "Is this skill independent knowledge, or part of another skill?", I corrected the granularity.

---

## The Numbers Over 15 Days

### Learned Skills Over Time

| Point in Time | Global | pdf2anki | baki-quiz-ios | zenn-content | Total |
|---------------|--------|----------|---------------|-------------|-------|
| 2/9 (unsorted) | 14 | — | — | — | 14 |
| 2/10 post-audit | 7 | 10 | 5 | — | 22 |
| 2/11 post-audit | 9 | 9 | 5 | — | 23 |
| 2/14 pre-audit | 17+ | 9 | 5 | — | 31+ |
| 2/14 post-audit | 17 | 9 | 8 | 6 | 40 |

### ECC Standard Skills Over Time

| Point in Time | Active | Disabled | Event |
|---------------|--------|----------|-------|
| 1/31 | 16 | 0 | Initial install |
| 2/8 | 10 | 0 | Migration to `~/.claude/` |
| 2/10 | 10 | 19 | Mass disabling in first audit |
| 2/12 | 15 | 19 | Wave 2 adds 5 |
| 2/14 | 15 | 33 | Wave 3 adds 14 → immediately disabled |

---

## What I Learned

### 1. Auditing Is Not a One-Time Event — It's Recurring

I audited 3 times in 15 days. The day after the first audit, when I thought "that's clean now," new skills were already accumulating.

As long as you keep developing, skills keep growing. So auditing has to be recurring too.

**My trigger: audit when any single layer exceeds 10 skills.** The threshold adjusts by project scale, but the important thing is having a defined number that triggers action.

### 2. Where You Place Skills Matters More Than How You Write Them

There are plenty of articles about how to write skills and skill templates. But where you put them after writing determines their value.

- A Swift Protocol pattern showing up in Discovery for a Python project is just noise
- Zenn textlint workarounds sitting in global are useless for other projects
- Conversely, the frozen dataclass pattern is used in every Python project, so global is correct

The sorting criterion is simple: "Is this skill used in only one project?"

Yes → move to that project. No → keep it global. If unsure, leave it global and revisit at the next audit.

### 3. Be Aware of the Character Budget Constraint

When skills grow too numerous, Discovery truncation kicks in. Skills you carefully created become invisible to Claude.

Two countermeasures. Disable unused skills with `disable-model-invocation: true`. And don't put project-specific skills in global.

Both are "reduction" strategies. Preventing unnecessary skills from appearing is more important than adding more skills.

### 4. Don't Fear Merging and Retiring

I executed 2 merges (absorbing into parent skills) and 1 retirement (`pbpaste-secret-to-env`).

Retirement criterion: **"Can it be re-derived with a one-liner?"** If yes, delete it without worry. If you need it again, just run `/learn`.

Merge criterion: **"Is this independent knowledge, or part of another skill?"** The patch target update procedure is just one step in module-to-package refactoring. It didn't need to be a standalone skill.

### 5. Use v1's /learn Regularly Until v2 Works

The continuous-learning-v2 instinct system is brilliant in design. Automatically extracting patterns from observations, refining with confidence scoring, and distilling into skills.

But as of February 2026, the middle layer implementation doesn't exist. 10,557 lines of logs accumulated, 0 instincts.

v1's `/learn` works reliably. Just run it manually at the end of a session, and useful patterns get saved as learned skills. All 40 of my learned skills were born this way.

---

## Conclusion

Adding skills is easy. Develop with Claude Code, and they accumulate naturally.

Management is the hard part. Where to put them. When to clean up. What to discard.

Here's where I stand after 3 audits over 15 days.

| Location | Learned | Custom | ECC Standard | Total |
|----------|---------|--------|-------------|-------|
| Global | 17 | 3 | 15 (active) | 35 |
| pdf2anki | 9 | — | — | 9 |
| baki-quiz-ios | 8 | — | — | 8 |
| zenn-content | 6 | 5 | — | 11 |
| ECC (disabled) | — | — | 33 | — |

Active skills total: **roughly 63 (33 of which are disabled). 48 effectively in use.**

The "number" of skills has no value. Value comes from having **the right skills, at the right granularity, in the right place**.

And this state won't last. Start a new project, and learned skills will grow again, and another audit will be needed.

Auditing never ends. But that's fine. As long as development continues, learning continues too.

---

## References

### Official Documentation

- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

### ECC / continuous-learning

- [everything-claude-code (GitHub)](https://github.com/affaan-m/everything-claude-code)
- [humanplane/homunculus (GitHub)](https://github.com/humanplane/homunculus)

### Related Articles

- [Decoding everything-claude-code](https://zenn.dev/ttks/articles/a54c7520f827be)
- [Design Philosophy of everything-claude-code](https://zenn.dev/tmasuyama1114/articles/everything-claude-code-concepts)
- [Complete Guide to Claude Code Skills](https://zenn.dev/ino_h/articles/2025-10-23-claude-code-skills-guide)
- [Summary of Claude Code Skills in Early 2026](https://zenn.dev/nanahiryu/articles/claude-code-skills-202601)
- [How to Distinguish Claude Code's Proliferating Features](https://zenn.dev/notahotel/articles/a175aa95629d0b)

### Series

- Part 1: [A Beginner's First 10 Days of Real Development with Everything Claude Code](https://qiita.com/shimo4228/items/06d48f19bde5e6401a85)
- Part 2: [Never Trust LLM Output — 6 Defenses from Building a PDF-to-Anki CLI with the Claude API](https://qiita.com/shimo4228/items/743f2b43f63b2bbe2dba)
