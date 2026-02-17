---
title: "5 Things I Learned from Auditing All My Claude Code Config Files"
emoji: "🔍"
type: "tech"
topics: ["claudecode", "ai", "devtools", "productivity"]
published: true
---

## What Triggered the Audit

One day I launched Claude Code in a project and discovered it had forgotten a gotcha I'd taught it in a previous session. "I saved that to memory — why doesn't it know?"

After investigating, I found that I had been working on that project from the workspace root, so the memory was saved under a different directory. This discovery prompted a two-day, full audit of `CLAUDE.md` files, `rules/`, and `auto memory` across all 6 projects.

## Environment

```text
MyAI_Lab/                    ← Workspace root (not a git repo)
├── swift-app-a/            # Swift 6.0 / SwiftUI
├── swift-app-b/        # Swift 6.0 / SwiftUI
├── nextjs-app/            # TypeScript / Next.js
├── python-cli/                # Python / uv
├── python-tool/             # Python / uv
└── zenn-content/            # Markdown / Zenn CLI
```

Claude Code's configuration is divided into 3 layers:

```text
~/.claude/                   ← User level (shared across all projects)
├── rules/common/            #   Language-agnostic rules
├── rules/python/            #   Python-specific rules
├── rules/typescript/        #   TypeScript-specific rules
├── settings.json            #   Permissions & hook settings
└── projects/{path}/memory/  #   Per-project auto memory (path-encoded)

MyAI_Lab/CLAUDE.md           ← Workspace level
MyAI_Lab/python-cli/CLAUDE.md  ← Project level (each project)
```

## 1. Every Project Should Have a CLAUDE.md

Before the audit: only zenn-content had a CLAUDE.md. The other 5 projects had none.

Without a CLAUDE.md, Claude Code doesn't know the project's tech stack or build commands. Explaining "this is a Swift project with..." every session is wasted effort.

I deployed CLAUDE.md to all 5 projects at once. Here's the template I used for each:

```markdown
# {project-name}

{One-line summary}

## Tech Stack
- Language, framework, key dependencies

## Directory Structure
(Main folders only)

## Build / Test / Run
(Copy-pasteable commands)

## Conventions
(Project-specific rules)

## Status
(Current development state)
```

Each file is around 65-89 lines. Keep it to "information needed to work on this project" and nothing more. Workspace-level information (checkpoint rules, etc.) goes in the parent `MyAI_Lab/CLAUDE.md` — no duplication.

## 2. Put "Rules for Rules" in the Workspace CLAUDE.md

When you mass-produce per-project CLAUDE.md files, quality varies. I added "rules for new project creation" to the workspace-level `MyAI_Lab/CLAUDE.md`:

```markdown
## Rules for New Project Creation

When creating a new project folder, always create a CLAUDE.md at the same time.

### Required Sections
- Project overview (1 line)
- Tech Stack
- Directory Structure
- Build / Test / Run
- Conventions
- Status
```

With this in place, the next time I add a project, I just request "create a CLAUDE.md" and Claude Code generates one following the template.

## 3. Global Rules Language Waste Is Negligible

Rule files placed in `~/.claude/rules/` are **loaded in every session regardless of language**. There is no filtering mechanism.

While working on a Swift project, Python and TypeScript rules are loaded needlessly — this bothered me enough to run the numbers.

```text
~/.claude/rules/
├── README.md          3,030 bytes  ← Installation guide
├── common/           10,544 bytes  ← Language-agnostic (10 files)
├── python/            2,843 bytes  ← Python-specific (5 files)
└── typescript/        3,288 bytes  ← TS-specific (5 files)
                      ──────────
                      19,705 bytes  Total: 21 files
```

I calculated the waste for a Swift project:

| Unnecessary rules | bytes | tokens (approx.) |
|-------------------|------:|------------------:|
| python/ | 2,843 | ~900 |
| typescript/ | 3,288 | ~1,000 |
| README.md | 3,030 | ~900 |
| **Total** | **9,161** | **~2,800** |

Against a 200K token context window, that's **about 1.4%** (estimated at ~3-4 bytes per token). However, early in a session when context is sparse, this percentage feels larger in practice.

I considered moving language-specific rules to the project level, but the management overhead of maintaining rules across 6 projects per language isn't worth it. **Keeping the status quo is the optimal choice.**

> README.md is purely an installation guide and has no value during a session. You could delete it if it bothers you, but at ~900 tokens the priority is low.

## 4. Not Having ~/.claude/CLAUDE.md Is Fine

"Is it a misconfiguration that there's no CLAUDE.md at the user level?" I briefly panicked, but it's fine.

User-level instructions can be provided in two ways:

| Approach | Path | Characteristics |
|----------|------|-----------------|
| Single file | `~/.claude/CLAUDE.md` | Everything in one file |
| Split rules | `~/.claude/rules/*.md` | Split by topic |

**Either one is sufficient.** Technically you can use both, but having the same instructions in two places creates risk of update misses and contradictions.

If you're managing rules via `~/.claude/rules/` split into common / python / typescript, you don't need `~/.claude/CLAUDE.md`.

## 5. Working from the Workspace Root Starves Your Memory

**This was the biggest finding.**

Auto memory is saved using a **key derived from the absolute path** of the directory where the session was opened. `/` characters are converted to hyphens, producing flat directory names.

```text
~/.claude/projects/
├── -Users-me-MyAI-Lab/memory/              ← Workspace root
├── -Users-me-MyAI-Lab-python-cli/memory/   ← Per-project
├── -Users-me-MyAI-Lab-swift-app-a/memory/
└── ...
```

I checked whether MEMORY.md existed for each of the 6 projects:

| Project | Stack | MEMORY.md |
|:--------|:------|:---------:|
| swift-app-a | Swift | Yes |
| swift-app-b | Swift | No |
| nextjs-app | TypeScript | No |
| python-cli | Python | Yes |
| python-tool | Python | No |
| zenn-content | Markdown | Yes |

**Half of the projects — 3 out of 6 — had no MEMORY.md.**

The cause was clear: I had been working on those projects from the workspace root (`MyAI_Lab/`). When you open a session at the root, the following happens:

- Memory is associated with `MyAI_Lab/`
- Project-specific knowledge (gotchas, design decisions, toolchain details) doesn't accumulate in that project's memory
- Next time you open from the project directory, you start with a blank slate

```bash
# NG: Working from workspace root
cd ~/MyAI_Lab && claude
# → Memory accumulates under MyAI_Lab/. Project memory stays empty.

# OK: Launch from project directory
cd ~/MyAI_Lab/swift-app-b && claude
# → Memory accumulates under swift-app-b/
```

**Fix: Always launch Claude Code from within the project directory.**

Reserve workspace root sessions for cross-project planning and research only.

## Summary

| # | Finding | Impact | Action |
|---|---------|:------:|--------|
| 1 | Most projects lack CLAUDE.md | High | Deploy to all projects |
| 2 | No creation rules leads to inconsistency | Medium | Define template in workspace CLAUDE.md |
| 3 | Global rules language waste | Low (~1.4%) | None needed |
| 4 | No ~/.claude/CLAUDE.md | None | Not needed if rules/ exists |
| 5 | Workspace root usage causes memory loss | **High** | Launch from project directory |

The rules waste I was worried about (#3) turned out to be far less impactful than **missing CLAUDE.md files (#1) and session launch location (#5)**.

Rather than adding more configuration, **using existing mechanisms from the right location** is what actually makes a difference.
