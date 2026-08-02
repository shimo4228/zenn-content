---
title: "Give Claude Code a Second Harness"
emoji: "⚙️"
type: "tech"
topics: ["claudecode", "anthropic", "contextengineering", "cli", "claude"]
published: true
description: "Claude Code has broad switches for disabling customizations, but no single profile switch that replaces only your personal harness while preserving repository instructions. Here is the two-part setup—and a read-only prompt that makes your coding agent plan it for your machine before changing anything."
tags: claudecode, anthropic, contextengineering, aiagents
---

The CLAUDE.md files, rules, and skills you have built up are useful in everyday development. But they can be too heavy for experiments or autonomous loops. Sometimes you want to swap the whole set for a different one.

Claude Code, however, has **no single profile switch that replaces only your personal harness while preserving the repository configuration**. The closest mechanism is `CLAUDE_CONFIG_DIR`, which points Claude Code at a different configuration directory. But it switches only half of the harness. Skills and agents move; CLAUDE.md and rules from the original environment still come along. On my machine, that meant 16 files and 3,404 words on every launch.

That is the missing piece. The solution is to combine a configuration-directory switch with path-based instruction exclusion.

The first half of this article explains why the combination is necessary and what it preserves. The second half gives you a planning prompt for your coding agent. The agent inspects your environment read-only and stops after producing an implementation plan.

## Prerequisites

- Tested with Claude Code v2.1.220 on macOS
- In this article, “harness” means the set of `CLAUDE.md`, `rules/`, `skills/`, and `agents/`
- I call the new directory selected by `CLAUDE_CONFIG_DIR` the “alternate side”

## The configuration directory switches only half the harness

`CLAUDE_CONFIG_DIR` is an environment variable that points Claude Code at another configuration directory. Here is what moves—and what stays behind.

| Item | Part of the harness? | Switches to the alternate side? |
|---|---|---|
| `skills/` and `agents/` | Yes | Switches |
| **`CLAUDE.md` and `rules/`** | Yes | **Does not switch; the originals still load** |
| `settings.json` (including hook definitions) | No | Switches |
| Session history and plugins | No | Switches |

Only the top half of the four-part harness changes.

The bottom two rows follow the official documentation:

> Override the configuration directory (default: `~/.claude`). All settings, session history, and plugins are stored under this path
> ([Environment variables](https://code.claude.com/docs/en/env-vars))

Skills and agents do not appear in that sentence, but they switched in my test. When I launched Claude Code with the alternate directory and asked for the available skills, my usual custom skills were gone. Only the skills placed on the alternate side appeared.

Credential storage depends on the operating system. On Linux and Windows, credentials live under the configuration directory. On macOS, they live in the system Keychain. In the macOS environment tested here, changing the configuration directory does not move a credential file with it.

CLAUDE.md and rules remain because they are found through another mechanism:

> Claude Code reads CLAUDE.md files by walking up the directory tree from your current working directory
> ([How Claude remembers your project](https://code.claude.com/docs/en/memory))

When the working directory is below your home directory, that walk necessarily passes through `$HOME`. This makes `$HOME/.claude/` part of the search path regardless of where `CLAUDE_CONFIG_DIR` points.

:::details How I verified the ancestor-directory behavior
I launched Claude Code with an empty configuration directory. Nothing could come from that directory, but Claude Code still loaded 16 files from `$HOME/.claude`. It recorded them as project files rather than user files.

| Launch condition | Files loaded from `$HOME/.claude` | Recorded type |
|---|---:|---|
| Default configuration directory (`$HOME/.claude`) | 16 | User (`User`) |
| Empty alternate configuration directory | 16 | Project (`Project`) |

The label changed; the files still loaded. Placing the working directory outside the home directory removed this path. On v2.1.220, pointing a symlink outside the home directory back to a directory under it did not help because Claude Code resolved the real path.
:::

Claude Code does provide official ways to disable customizations broadly. None draws the boundary needed here.

| Official mechanism | What it disables | Why it does not fit this case |
|---|---|---|
| `--safe-mode` | CLAUDE.md, skills, hooks, plugins, and other customizations | Repository customizations stop too |
| `--bare` | Automatic loading of CLAUDE.md, hooks, plugins, MCP, auto memory, and more | It is a minimal mode for scripted calls, and repository customizations stop too. Skills remain explicitly invocable |
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` | User, project, and auto-memory instruction files | It also removes the repository CLAUDE.md |

The target behavior is narrower: replace the personal harness while keeping the repository’s instructions and mechanical gates. Claude Code has no single official switch for that selective profile change. [Issue #30380](https://github.com/anthropics/claude-code/issues/30380), which requests per-session disabling of the global CLAUDE.md, is closed as not planned.

## The human decision is where to draw the boundary

This is the boundary used here:

| Item | Treatment |
|---|---|
| Everyday `$HOME/.claude` | Leave unchanged |
| Personal CLAUDE.md, rules, skills, and agents | Replace with a second set |
| Repository CLAUDE.md, rules, settings, and hooks | Preserve |
| Project memory | Separate by default; share only if needed |

This gives you a harness for experiments, autonomous loops, or a separate account without changing the environment you use for everyday development.

The mechanism has two parts:

1. Use `CLAUDE_CONFIG_DIR` to change the location of settings, skills, agents, and history.
2. In the alternate `settings.json`, use `claudeMdExcludes` to exclude the original `$HOME/.claude/CLAUDE.md` and `rules/` from instruction loading.

`claudeMdExcludes` accepts absolute-path glob patterns. In a terminal, `~` (tilde) is normally shorthand for your home directory. It is not expanded here. Writing `~/.claude/**` fails to exclude anything without producing an error in v2.1.220.

On a company- or school-managed machine, IT may deploy a machine-wide CLAUDE.md. Personal settings cannot exclude those managed instructions. If your machine is not centrally managed this exception does not apply.

Everything after this point depends on the reader’s filesystem, existing settings, symlinks, and authentication state. Do not copy a generic sequence of commands from an article. Have your coding agent inspect your machine and turn the design into an environment-specific implementation plan.

## Give this article to your agent and ask for a plan

Give your coding agent the URL of this article and the following prompt. At this stage, the agent must not change any files.

````text
Read this article and create an implementation plan for adding a second, purpose-specific Claude Code harness to this machine.

Important:
- Perform read-only inspection for this request.
- Do not create, edit, move, or delete files. Do not change settings, create symlinks, or perform Git operations.
- Put commands in the plan, but do not run commands that mutate state.

Preferences:
- Candidate TARGET_CONFIG_DIR: ~/.claude-alt
- Contents of the second harness: undecided. Look for existing candidates on this machine.
- Share project memory: no

Goals:
- Do not modify the everyday ~/.claude directory.
- Make it possible to place a separate CLAUDE.md, rules, skills, and agents in TARGET_CONFIG_DIR.
- When Claude Code starts with TARGET_CONFIG_DIR, do not load the original ~/.claude/CLAUDE.md or ~/.claude/rules/**.
- Preserve CLAUDE.md, .claude/rules, settings, and hooks from the working repository.

If you cannot access the article, treat the inspection and planning requirements below as canonical.

Read-only inspection:
1. Check claude --version, the operating system, and the resolved HOME path.
2. Inspect the structure of ~/.claude, the candidate configuration directory, and the repository's .claude directory. Do not copy their contents into a public report.
3. Look for candidates for the second harness. List possible sources separately for CLAUDE.md, rules, skills, and agents. If none exist, propose an empty structure.
4. Check for existing settings.json files, symlinks, projects/, and managed policy.

Requirements for the plan:
- Do not modify the everyday ~/.claude directory or files in the repository.
- Resolve the candidate configuration directory to an absolute path. Reject /, HOME, ~/.claude, any path below ~/.claude, and an existing symlink as the target.
- Do not overwrite existing files. For same-name assets, show the diff; skip identical content and make differing content a human approval point.
- Do not dereference symlinks when copying. Show each link target and its risk.
- Preserve existing keys in settings.json and merge the resolved absolute `<HOME>/.claude/**` glob into claudeMdExcludes. Do not use `~/.claude/**`.
- Show the destination of each CLAUDE.md, rule, skill, and agent file.
- Take a no-exclusion baseline before adding the exclusion, then compare it with the result after the change.
- Use a temporary directory and `--settings` for verification. Do not rewrite the real settings.json or existing hooks merely to run the test.
- Limit the InstructionsLoaded hook to `matcher: "session_start"`. After each process exits, wait for the asynchronous log to stabilize with a bounded timeout. Compare unique `file_path` values and their sources.
- Success means zero files loaded from the original ~/.claude, loading the second CLAUDE.md and rules when present, and preserving repository instruction files.
- Use /context or InstructionsLoaded records as evidence. Do not infer success from what the LLM says it knows.
- Remove temporary verification files afterward. Recheck the final settings.json diff and JSON syntax.
- Keep project-memory sharing out of the main plan. Describe it only as an alternative, including mixed conversation history and the deletion risk from `claude project purge`.

Output:
1. Summary of the current state
2. Proposed structure and the reason for choosing it
3. Implementation steps, each with target paths, commands, intended changes, and a rollback method
4. Verification steps and success criteria
5. Human approval points
6. Unverified assumptions and risks

Stop after presenting the plan. Do not implement it until I explicitly approve it.
````

Review the proposed target paths, no-overwrite behavior, rollback method, and success criteria. If the plan is sound, explicitly tell the same agent: “Implement this plan and verify every success criterion it defines.”

The planned layout should look like this:

```text
~/.claude-alt/
├── CLAUDE.md        # when the second-harness plan includes one
├── settings.json
├── rules/
├── skills/
└── agents/
```

The essential addition to `settings.json` is one key. The plan must merge it without discarding existing keys.

```json
{
  "claudeMdExcludes": [
    "/Users/you/.claude/**"
  ]
}
```

`/Users/you/` is illustrative. The real file must contain the absolute HOME path detected on the reader’s machine.

## Judge success by the load source

For a quick manual check, launch Claude Code with the alternate configuration, run `/context`, and inspect **Memory files**.

For an automated check, use the `InstructionsLoaded` hook. Each time Claude Code loads a CLAUDE.md or rule, the hook receives the absolute `file_path`, `memory_type`, and `load_reason`. The planning prompt requires a controlled comparison using those records.

On my Claude Code v2.1.220 environment, changing only the exclusion produced this result:

| Load source | No exclusion | With exclusion |
|---|---:|---:|
| Original `$HOME/.claude` | 16 | **0** |
| Repository | 1 | 1 |
| Total | 17 | **1** |

With `~/.claude/**`, the total remained 17. Replacing it with the absolute path reduced the total to 1. These are v2.1.220 measurements. Judge success from the `file_path` breakdown, not from whether the command prints an error.

:::message
Do not ask the LLM, “Do you know this instruction?” to verify loading. The model may know the same information from repository memory or training data. Use Claude Code’s own `/context` output or `InstructionsLoaded` records.
:::

:::details Optional: share project memory while keeping the harnesses separate
Project memory also lives under the configuration directory, so it disappears from the alternate side by default. If you want to reuse it, do not create a link immediately. Change “Share project memory” in the planning prompt to “consider sharing,” then ask the agent to produce a separate plan.

Linking all of `projects/` shares future projects without creating new links, but it also shares conversation transcripts. Sessions from both environments appear together in `/resume`.

**Do not run `claude project purge` while sharing this directory.** In a local v2.1.220 `--dry-run`, one project produced 72 deletion targets. If `projects/` is a symlink, deleting `projects/<slug>/` follows the link and removes the everyday environment’s transcripts and auto memory. Other purge targets—file history, tasks, configuration entries, and input history—belong to the alternate side.
:::

## Summary

The design has two parts:

1. Use `CLAUDE_CONFIG_DIR` to switch the configuration directory. Skills, agents, hooks, and history move here.
2. Add `claudeMdExcludes` to the alternate `settings.json`. This removes the original CLAUDE.md and rules from the remaining instruction-loading path.

The result is a Claude Code launch that swaps the personal harness as a unit. There is no single switch for this boundary, but you can get the same behavior by explicitly excluding the part that would otherwise remain.

Always verify the load sources after adding the exclusion. The dangerous failure mode is silent: an ineffective glob produces no error.

## References

- [How Claude remembers your project](https://code.claude.com/docs/en/memory) — CLAUDE.md load order and `claudeMdExcludes`
- [Hooks reference](https://code.claude.com/docs/en/hooks) — the `InstructionsLoaded` hook
- [Environment variables](https://code.claude.com/docs/en/env-vars) — environment variables including `CLAUDE_CONFIG_DIR`
- [CLI reference](https://code.claude.com/docs/en/cli-usage) — `--safe-mode` and `--bare`
- [Issue #30380](https://github.com/anthropics/claude-code/issues/30380) — request to disable the global CLAUDE.md (closed as not planned)

## Related links

- [claude-harness](https://github.com/shimo4228/claude-harness) — the Claude Code harness I maintain and use
- [github.com/shimo4228](https://github.com/shimo4228) — my other repositories
