---
title: "Claude Code's CLAUDE.md Hierarchy — Lessons from 10 Days of Misconfiguration"
emoji: "📂"
type: "tech"
topics: ["claudecode", "ai", "devtools", "configuration"]
published: true
---

## 10 Days of Misplaced Config

When I set up [Everything Claude Code (ECC)](https://github.com/affaan-m/everything-claude-code), I downloaded the ZIP from GitHub. I dropped the entire collection of rules, skills, and agents templates into `MyAI_Lab/.claude/` — and that was where things went wrong.

```text
MyAI_Lab/.claude/       ← Workspace level
├── rules/
├── skills/
├── agents/
├── README.md
├── LICENSE
└── .gitignore
```

I worked on 6 projects in this state for 10 days. All projects were forcibly sharing the same rules, skills, and agents. Problems gradually surfaced: "Zenn article-writing skills are loading in an iOS app project," "Python-specific rules are being applied to a Swift project."

## Claude Code's 3-Layer Structure

After re-reading the official documentation, I understood that the `.claude/` directory has three hierarchical levels.

```text
~/.claude/                    ← User level (shared across all projects)
├── rules/                      Universal rules
├── skills/                     Universal skills
├── agents/                     Universal agents
├── commands/                   Universal commands
└── settings.json               Global settings

MyAI_Lab/.claude/             ← Workspace level
└── settings.local.json         Workspace-specific settings only

MyAI_Lab/zenn-content/.claude/ ← Project level
├── skills/                     Project-specific skills
├── agents/                     Project-specific agents
└── settings.local.json         Project-specific settings
```

For settings values (`settings.json`), the lower level (project) takes precedence when the same key exists. On the other hand, `rules/`, `agents/`, and `skills/` are **additively merged** across all levels.

## Role of Each Layer

### User Level (`~/.claude/`)

This is where you place settings shared across all projects. In my environment, it contains:

- `rules/common/` — Language-agnostic rules for coding style, Git workflow, testing policies, etc.
- `rules/typescript/`, `rules/python/` — Language-specific extension rules
- `agents/` — 14 universal agents including planner, code-reviewer, tdd-guide, etc.

These are referenced regardless of which project you open.

### Workspace Level (`MyAI_Lab/.claude/`)

Settings for monorepos or workspaces that bundle multiple projects. After the fix, I kept only `settings.local.json` here. The key point: **do not place** rules, skills, or agents at this level.

### Project Level (`zenn-content/.claude/`)

Settings specific to that project. For zenn-content, the main contents are:

- `skills/zenn-writer/` — Zenn article format guide
- `skills/seo-optimizer/` — Title and tag optimization
- `skills/publish-article/` — Publishing checklist
- `agents/editor.md` — Tough-love review agent

These are not loaded for the iOS app project. Only what's needed per project is active.

## Where to Place CLAUDE.md

Separately from the `.claude/` directory, `CLAUDE.md` files also have a hierarchical structure.

```text
~/CLAUDE.md                   ← User level (personal global instructions)
MyAI_Lab/CLAUDE.md            ← Workspace level (tracked by Git)
zenn-content/CLAUDE.md        ← Project level (tracked by Git)
```

`CLAUDE.md` is a **Git-tracked file** placed at the project root. You write team-shared rules and conventions here. In contrast, settings inside the `.claude/` directory are confined to your personal environment.

Claude Code **traverses parent directories upward** from the directory where it was launched, looking for `CLAUDE.md` files. When started in `zenn-content/`, it loads `zenn-content/CLAUDE.md` → `MyAI_Lab/CLAUDE.md` → `~/CLAUDE.md` in order, merging all of them.

Note: The user-level `CLAUDE.md` works at either `~/CLAUDE.md` or `~/.claude/CLAUDE.md`. If you manage rules via `~/.claude/rules/` in split files, neither is necessary.

## What I Did to Fix It

```text
1. Removed rules/skills/agents from MyAI_Lab/.claude/
2. Moved rules/agents to ~/.claude/ (shared across all projects)
3. Placed project-specific skills/agents in zenn-content/.claude/
4. Kept only settings.local.json at each level
5. Deleted unnecessary files like README and LICENSE
```

After the fix, each project had its own independent settings, and context cross-contamination was eliminated.

## Decision Criteria

When unsure about which layer to place something in, use these criteria:

| Location | Criteria | Examples |
|---------|---------|---------|
| `~/.claude/` | Used in every project | Coding rules, universal agents |
| `workspace/.claude/` | Workspace-specific settings only | settings.local.json |
| `project/.claude/` | Used only in that project | Zenn writing skills, iOS test skills |
| `project/CLAUDE.md` | Rules to share with the team | Project conventions, testing policies |

The 10 days of misconfiguration ultimately became an opportunity to understand this hierarchy. The tricky part is that "everything works even if you put it all in the same place — you just lose flexibility." No errors are thrown, so it's hard to notice.

Specifically, I realized the cross-contamination when Claude Code flagged a "Zenn article textlint rule violation" while I was debugging an iOS app. The rule itself was correct — it was just being applied to the wrong target. This was a placement problem, not a rule problem.

If you have a growing number of projects and feel like "settings are getting tangled," revisit the 3-layer structure.
