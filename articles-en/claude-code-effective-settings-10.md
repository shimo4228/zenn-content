---
title: "Stop Using Default Settings — 10 Claude Code Configs That Actually Work"
emoji: "⚙️"
type: "tech"
topics: ["claudecode", "ai", "cli", "devtools"]
published: false
---

After a month with Claude Code, I had racked up over 270 sessions. My `.claude/` directory was rewritten countless times along the way. "That setting I thought was essential turned out to be useless." "That one-liner I almost ignored has prevented disasters multiple times." What survived this natural selection are these 10 configurations.

If you are using Claude Code with default settings, you are almost certainly suffering from **approval dialog fatigue** and **sudden context window death**. This article addresses both.

:::message
<!-- textlint-disable -->
This article is based on Claude Code (CLI version) settings as of March 2026. Specifications may change with future updates.
<!-- textlint-enable -->
:::

## Prerequisites

A quick overview of my Claude Code environment.

- **Primary use cases**: Python CLI development, Zenn article writing, iOS app development
- **Policy**: Claude writes the code. Humans focus on design and decisions.

For the full configuration file structure, see [5 Things I Learned from Auditing All My Claude Code Config Files](https://zenn.dev/shimo4228/articles/claude-code-context-audit). This article goes further, focusing on specific settings that have proven effective in real-world use.

---

## 1. Visualize Context Window Remaining Capacity with the Status Line

**Impact**: Prevents context window sudden death.

The biggest trap in Claude Code is that the context window fills up silently. By the time you notice, it is past 90%, and auto-compact wipes out your entire working context.

Setting a status line in `~/.claude/settings.json` displays it permanently at the bottom of your terminal.

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline-command.sh"
  }
}
```

Display script (`~/.claude/statusline-command.sh`):

```bash
#!/bin/bash
input=$(cat)
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
model_name=$(echo "$input" | jq -r '.model.display_name // "Claude"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // ""')

status_parts=()
status_parts+=("$model_name")
[ -n "$cwd" ] && status_parts+=("$(basename "$cwd")")

if [ -n "$used_pct" ]; then
  used_int=$(printf "%.0f" "$used_pct")
  bar_width=20
  filled=$(( used_int * bar_width / 100 ))
  empty=$(( bar_width - filled ))
  bar=""
  for ((i=0; i<filled; i++)); do bar+="█"; done
  for ((i=0; i<empty; i++)); do bar+="░"; done
  status_parts+=("[${bar}] ${used_int}%")
fi

printf "%s" "${status_parts[0]}"
for ((i=1; i<${#status_parts[@]}; i++)); do
  printf " | %s" "${status_parts[$i]}"
done
printf "\n"
```

The output looks like this:

```text
Claude Opus 4.6 | zenn-content | [████████░░░░░░░░░░░░] 40%
```

I enforce a personal rule: **stop and checkpoint at 80%**. This alone eliminated "sudden context loss" entirely.

---

## 2. Kill Approval Dialogs with a Permission Allow List

**Impact**: Eliminates several approval dialogs per session.

Default Claude Code asks "Allow?" every time it runs a Bash command. Allow for `git status`. Allow for `ls`. Allow for `python`. This happens dozens of times per session.

List safe commands in `settings.json` under `permissions.allow`.

```json
{
  "permissions": {
    "allow": [
      "Bash(git:*)",
      "Bash(python:*)",
      "Bash(npm:*)",
      "Bash(ls:*)",
      "Bash(grep:*)",
      "Bash(jq:*)",
      "Bash(curl:*)",
      "Bash(ruff:*)",
      "Bash(black:*)",
      "Bash(pytest:*)",
      "Read",
      "WebFetch",
      "WebSearch"
    ]
  }
}
```

The syntax is `"Bash(command:*)"`, where `*` permits all arguments. In my environment, I have **88 Bash commands** and **over 30 MCP tools** pre-approved.

The key is **not including `rm`**. File deletion is the one thing I always want to confirm. Similarly, `sudo`, `dd`, `mkfs`, and other destructive commands are intentionally excluded.

---

## 3. bypassPermissions + Hook Validation as a Two-Layer Safety Net

**Impact**: Full automation while reliably blocking destructive operations.

Taking setting #2 further: setting `defaultMode` to `bypassPermissions` auto-approves everything, including commands **not** on the allow list.

```json
{
  "permissions": {
    "defaultMode": "bypassPermissions"
  }
}
```

"That sounds dangerous." Correct. That is exactly why you combine it with a **PreToolUse hook** as a safety valve.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/validate-bash.sh"
          }
        ]
      }
    ]
  }
}
```

Here is `validate-bash.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
[[ -z "$COMMAND" ]] && exit 0

block() {
  echo "{\"decision\": \"block\", \"reason\": \"$1\"}"
  exit 0
}

# rm -rf /
echo "$COMMAND" | grep -qE 'rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|(-[a-zA-Z]*f[a-zA-Z]*r))\s+/(\s|$|\*)' \
  && block "rm -rf / is blocked for safety"

# git push --force
echo "$COMMAND" | grep -qE 'git\s+push\s+.*(-f|--force)' \
  && block "git push --force is blocked. Use --force-with-lease"

# git add -A / git add .
echo "$COMMAND" | grep -qE 'git\s+add\s+(-A|--all|\.)(\s|$)' \
  && block "git add -A is blocked. Stage specific files instead"

# sudo
echo "$COMMAND" | grep -qE '(^|[;&|]\s*)sudo\s' \
  && block "sudo is blocked in automated mode"

exit 0
```

The mechanism is simple. A script runs **immediately before** a Bash tool execution and checks the command string with regex. If it matches a dangerous pattern, it returns `{"decision": "block"}` to prevent execution. If no match, it passes through silently.

**Keep the block list minimal.** If you block too many things, the hook just becomes a replacement for the approval dialog. I block exactly 6 patterns:

1. `rm -rf /` (system destruction)
2. `git push --force` (history destruction)
3. `git add -A` / `git add .` (unintended file staging)
4. `sudo` (privilege escalation)
5. `dd` / `mkfs` (disk operations)
6. Writes to `/dev/` (device file protection; `/dev/null` etc. are allowed)

In practice, the block that fires most often is `git add .`. Claude tends to reach for convenient commands, so this one pulls its weight the most.

---

## 4. Auto-Run Tests After Every Edit with PostToolUse Hooks

**Impact**: Tests run automatically right after shell script edits.

PostToolUse hooks fire **immediately after** Claude edits a file, triggering automatic actions.

What I have configured is auto-testing specifically for `.sh` files.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/bats-autorun.sh"
          }
        ]
      }
    ]
  }
}
```

`bats-autorun.sh` only runs bats tests when the edited file ends in `.sh` and a `tests/` directory exists nearby. When tests fail, it returns `{"decision": "block"}`, telling Claude "tests broke, fix them." Below is a simplified version highlighting the key logic (the actual script includes JSON escaping and other handling):

```bash
#!/usr/bin/env bash
set -euo pipefail
INPUT=$(cat)
filepath=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')

# Ignore non-.sh files
[[ "$filepath" == *.sh ]] || exit 0

# Ignore if no tests/ directory
dir=$(dirname "$filepath")
[[ -d "$dir/../tests" ]] || exit 0

cd "$dir/.."
result=$(bats tests/ 2>&1) || true

if echo "$result" | grep -q "^not ok"; then
  printf '{"decision":"block","reason":"bats tests failed after editing %s"}' \
    "$(basename "$filepath")"
else
  printf '{"systemMessage":"[bats] all tests passed for %s"}' \
    "$(basename "$filepath")"
fi
```

This creates a loop of **"edit -> tests fail -> Claude auto-fixes -> tests re-run"** without human intervention. It is essentially a mechanism that forces TDD on Claude.

For Python, the textlint / markdownlint auto-execution described in [my Zenn writing environment article](https://zenn.dev/shimo4228/articles/claude-code-zenn-writing-env) serves the same role.

---

## 5. Run Final Checks at Session End with Stop Hooks

**Impact**: Catches documentation structure violations before the session ends.

In addition to PreToolUse (before execution) and PostToolUse (after execution), **Stop** (at session end) is the third layer of hooks.

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/driftcheck.sh"
          }
        ]
      }
    ]
  }
}
```

My `driftcheck.sh` validates the `docs/` directory structure. Specifically:

- Does `docs/README.md` exist?
- Are there any unauthorized files at the root level?
- Do files in `records/` follow the `YYYY-MM-DD_` prefix convention?
- Has `.DS_Store` crept in?

The idea is **"clean up the mess you made during the session before it ends."** It is similar to a CI/CD pre-commit hook.

Here is an overview of the three hook layers:

| Hook | Timing | Role | Example |
|------|--------|------|---------|
| **PreToolUse** | Before execution | Block destructive operations | `rm -rf /`, `git push --force` |
| **PostToolUse** | After execution | Quality checks, auto-testing | bats tests, lint |
| **Stop** | At session end | Final consistency verification | Documentation structure checks |

---

## 6. Hierarchical Rules: Write Each Principle Once

**Impact**: Prevents rule duplication and contradictions across multi-language projects.

Claude Code rule files (`~/.claude/rules/`) support directory-based scoping.

```text
~/.claude/rules/
├── common/           # Language-agnostic principles
│   ├── coding-style.md
│   ├── testing.md
│   ├── security.md
│   └── git-workflow.md
├── python/           # Python-specific rules
│   ├── coding-style.md   ← extends common/coding-style.md
│   └── testing.md        ← extends common/testing.md
└── typescript/       # TypeScript-specific rules
    ├── coding-style.md
    └── testing.md
```

In `common/coding-style.md`, write "Prefer immutability."

In `python/coding-style.md`, reference `common/coding-style.md` at the top and specify using `@dataclass(frozen=True)`.

In `typescript/coding-style.md`, concretize the same principle with the spread syntax `{...obj, field: value}`.

**Writing "prefer immutability" once gives you consistent behavior in both Python and TypeScript.** Now that my rules have grown to 13 files and roughly 1,000 lines, contradictions would be inevitable without this structure.

---

## 7. Separate Project Skills from Global Skills

**Impact**: Prevents skill contamination and preserves per-project specialization.

Skills (`.claude/skills/`) have two scopes.

| Scope | Path | When loaded |
|-------|------|-------------|
| **Global** | `~/.claude/skills/` | Always |
| **Project** | `{repo}/.claude/skills/` | Only within that project |

In my case:

- **Global** (22 skills): `python-patterns`, `security-review`, `backend-patterns` — general-purpose skills
- **Project** (7 skills): `zenn-writer`, `publish-article`, `seo-optimizer` — Zenn-specific

There is no reason to load `zenn-writer` during iOS development, and `security-review` should be available in every project. Being deliberate about this split reduces wasted context sent to Claude.

In my experience, once you exceed about 20 skills, **"irrelevant skills getting in the way"** starts happening. When Claude cited Zenn textlint rules in the middle of an iOS app build, I knew it was time to separate them.

---

## 8. Teach Agents When to Activate Themselves

**Impact**: Quality checks run automatically.

Claude Code agents (`~/.claude/agents/`) can be configured so that **Claude itself decides "I should use this agent now."**

In my rules file (`~/.claude/rules/common/agents.md`), I have:

```markdown
## Immediate Agent Usage

No user prompt needed:
1. Complex feature requests → Use **planner** agent
2. Code just written/modified → Use **code-reviewer** agent
3. Bug fix or new feature → Use **tdd-guide** agent
4. Architectural decision → Use **architect** agent
```

In other words, I **define trigger conditions in rules**: "After writing code, invoke code-reviewer." "For bug fixes, use tdd-guide."

This achieves:

- Complex feature implementation -> planner auto-activates to create a plan before coding begins
- After code changes -> code-reviewer automatically reviews
- When tests are needed -> tdd-guide enforces the RED -> GREEN -> REFACTOR cycle

I no longer need to say "review this" every time. Claude will do anything you ask, but it will do nothing you don't ask. Writing "do this without being asked" in advance is the essence of this approach.

---

## 9. What to Write (and Not Write) in MEMORY.md

**Impact**: Retains context across sessions.

MEMORY.md (`~/.claude/projects/{project}/memory/MEMORY.md`) is persistent memory that loads automatically at session start. It survives context compaction. I covered the mechanism in detail in [my article on embedded memory](https://zenn.dev/shimo4228/articles/claude-code-persistent-memory). Here I will focus only on the inclusion/exclusion criteria I discovered through real use.

**What to write** (= information referenced repeatedly):

- Project toolchain (linter settings, how to run tests)
- Past gotchas and their solutions (Key Gotchas)
- Writing style conventions and branding guidelines
- External service constraints (API rate limits, character limits)
- Status of in-progress tasks

**What not to write** (= information that goes stale quickly):

- Session-specific work logs
- One-off research findings
- Content that duplicates CLAUDE.md
- Unverified hypotheses

**200 lines** is the practical limit. Beyond that, content gets truncated. My MEMORY.md is currently around 180 lines, organized by topic in a semantic structure. When a topic threatens to grow too long, I extract it into a separate file and link from MEMORY.md.

---

## 10. Selectively Enable Plugins

**Impact**: Load only the features you need, reduce noise.

Claude Code has a plugin system (`enabledPlugins`). Disabling unused plugins reduces the context that gets loaded.

```json
{
  "enabledPlugins": {
    "pyright-lsp@claude-plugins-official": true,
    "github@claude-plugins-official": false,
    "swift-lsp@claude-plugins-official": true,
    "hookify@claude-plugins-official": true,
    "claude-mem@thedotmack-claude-mem": true,
    "everything-claude-code@everything-claude-code": true
  }
}
```

In my case, I disabled the `github` plugin because the `gh` CLI is sufficient. Conversely, `pyright-lsp` (Python type checking) and `swift-lsp` (Swift LSP) are always enabled.

Key points about plugins:

- **LSP plugins** (pyright, swift-lsp): Let Claude reference type information in real time. Directly contributes to early type error detection.
- **hookify**: Provides a management UI for hooks. Essential once your hooks start multiplying.
- **claude-mem**: Persistent memory across sessions. Functions as a searchable database that complements MEMORY.md.
- **everything-claude-code**: A package of agents, skills, and commands. Forms the foundation of my environment.

**Do not enable everything.** More plugins means slower startup and, more critically, a bloated context that eats into your token budget.

---

## Full settings.json Overview

Combining all the settings above, the skeleton of `~/.claude/settings.json` looks like this (excerpt of settings covered in this article):

```json
{
  "permissions": {
    "allow": [
      "Bash(git:*)",
      "Bash(python:*)",
      "Bash(npm:*)",
      "Bash(ls:*)",
      "Bash(grep:*)",
      "Read",
      "WebFetch",
      "WebSearch"
    ],
    "defaultMode": "bypassPermissions"
  },
  "model": "opus",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "bash ~/.claude/hooks/validate-bash.sh"
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "bash ~/.claude/hooks/bats-autorun.sh"
        }]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "bash ~/.claude/hooks/driftcheck.sh"
        }]
      }
    ]
  },
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline-command.sh"
  },
  "enabledPlugins": {
    "pyright-lsp@claude-plugins-official": true,
    "swift-lsp@claude-plugins-official": true,
    "hookify@claude-plugins-official": true,
    "claude-mem@thedotmack-claude-mem": true,
    "everything-claude-code@everything-claude-code": true
  }
}
```

---

## Conclusion: Settings Should Be Invisible Infrastructure

What all 10 settings share is that they **work without you thinking about them**.

- Glance at the status line and you know your remaining context budget
- The allow list means no dialogs to click through
- Hooks mean dangerous operations get blocked automatically
- Rules mean you never repeat the same instructions
- Skills mean you never have to teach Claude the same workflow twice

The most important principle of Claude Code configuration is **building systems that prevent problems before they happen, rather than reacting after they occur.** Using default settings is like driving on the highway without a seatbelt.

For more on the three-layer config file structure and how to write CLAUDE.md, see [5 Things I Learned from Auditing All My Claude Code Config Files](https://zenn.dev/shimo4228/articles/claude-code-context-audit).
