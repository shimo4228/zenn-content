---
title: "Herdr: tmux for AI Agents — the Layer Zed Doesn't Have"
emoji: "🐑"
type: "tech"
topics: ["claudecode", "terminal", "productivity", "ai"]
published: true
description: "Monitor multiple Claude Code sessions with live status, reattach over SSH, and let agents rearrange their own terminal layout. A hands-on log of adopting Herdr, including where Zed is enough and where it isn't."
---

> **What this article covers**: how to build a terminal environment where you can monitor multiple Claude Code sessions with live status, come back to the same sessions after stepping away or over SSH, and — the interesting part — **let the agents reorganize their own screen layout**. It's a hands-on log from installation to verification, including how it divides work with an editor (Zed).

## The "where do I put them" problem of parallel agents

Once you start running multiple Claude Code or Codex sessions in parallel, you hit these walls:

- Terminal tabs pile up, and remembering "which tab was doing what" costs you time every single round
- Quitting your editor or terminal app kills the agent sessions running inside it
- You can't check on your running agents from your iPhone or another machine while away from your desk
- Agents can't touch their own execution environment (pane layout, workspaces) at all. Rearranging things is always manual human work

This article solves these with **Herdr** (an agent multiplexer — a terminal multiplexer built for agents). I'm a Zed user, and right after installing it my verdict was "isn't this redundant with what Zed already does?" — until **the moment I let an agent manipulate the layout itself, which flipped my evaluation**. I'll include that process too.

## Prerequisites

- macOS + Homebrew (Herdr also runs on Linux)
- You're already using CLI agents such as Claude Code
- This article is based on **Herdr v0.7.4** (verified 2026-07-18). The tool is only about three and a half months old, so the command surface may change
- Pane IDs in this article (`w5:p8` etc.) are real values from my environment. Yours will differ

## What Herdr is — only two real differences from tmux

Herdr is an "agent multiplexer that lives in your terminal." It's a single Rust binary, and like tmux it persists sessions in a server process (the prefix key is even tmux-compatible: `ctrl+b`).

The essential differences from tmux come down to two things:

1. **Semantic agent state tracking** — it auto-detects agents inside panes and lists their state — `working` / `blocked` / `done` / `idle` / `unknown` — in a sidebar. You can see "which one is waiting on me" without visually patrolling every pane
2. **A socket API** — pane splitting, command execution, output reading, and layout changes are all controllable from external processes (CLI commands like `herdr pane run` are wrappers around a Unix-socket API). Which means **an agent can operate its own execution environment**

The screen has three levels: **workspace → tab → pane**. From the CLI you address them as `w1` (workspace 1), `w1:t1` (tab 1 inside it), and `w1:p1` (pane 1). Read the command examples below with this notation in mind.

Basic facts (verified by me as of 2026-07-18):

- GitHub: [ogulcancelik/herdr](https://github.com/ogulcancelik/herdr) — a solo project, 17,700 stars 113 days after the repo was created
- Hit [Hacker News](https://news.ycombinator.com/item?id=48714802) on 2026-06-29 with 166 points and 110 comments
- Dual-licensed: AGPL-3.0-or-later + commercial (stated in the LICENSE file)

## Installing — one brew command

It's bottled in homebrew-core, so brew it is. I skipped the official site's `curl | sh` because piped install scripts are hard to audit. Including config generation, it's four lines:

```bash
brew install herdr                                    # v0.7.4
mkdir -p ~/.config/herdr
herdr --default-config > ~/.config/herdr/config.toml  # 305-line baseline config
herdr config check                                    # → config: ok
```

Running `herdr` starts the TUI, and the server (`herdr server`) comes up automatically. No login-item daemon (`brew services`) was needed.

As a sanity check, run a smoke test of the socket API. This doubles as the minimal example of "letting an agent operate the environment" covered later:

```bash
# Create a workspace, run a command in a pane, wait for output, read it back
herdr workspace create --cwd ~ --label smoke-test --no-focus
# → Returns workspace_id and pane_id as JSON. The lines below assume it returned
#   "w1:p1" — substitute whatever IDs you actually got (if you already have
#   workspaces, you'll get w2 or later)
herdr pane run "w1:p1" "echo herdr-smoke-ok"
herdr wait output "w1:p1" --match "herdr-smoke-ok" --timeout 5000
herdr pane read "w1:p1" --lines 10
# → If the output contains herdr-smoke-ok, you're wired up
```

If all four pass, layout, execution, and reading are controllable from an external process.

## Where Zed is enough, and where it isn't

Let me be honest here: right after installing, my evaluation was "**this is barely different from Zed**."

Zed announced [Parallel Agents](https://zed.dev/blog/parallel-agents) on 2026-04-22. The Threads sidebar runs multiple agents in parallel, with per-thread git worktree isolation. Its terminal already does tabs (`cmd+N`) and splits (`cmd+D`). If you're at your desk reviewing in a GUI while agents run, Zed's experience is better. Herdr's workspace switching looked about the same as switching Zed windows.

In fact, I almost shelved it with a tidy division of "at the desk = Zed, away = Herdr."

What changed my evaluation was using the layers that **structurally don't exist in Zed**:

| Layer | Zed | Herdr |
|---|---|---|
| GUI review experience | ◎ Parallel Agents + editor integration | — (terminal only) |
| Execution persistence | Quitting the app stops execution (thread history survives) | Server-resident. Execution continues with every app closed |
| External reattach to a running session | Not possible (SSH remote dev exists, but it's a different thing) | `ssh → herdr` from an iPhone etc. drops you back into the same screen |
| Agents operating their own environment | Not possible | Full control via the socket API |

The first row is Zed's win; the bottom three are territory only Herdr has. So it's not competition — it's a complement: **Herdr fills the "managing many agents" layer where Zed is weak**.

One more trap that matters in practice: **sessions launched from Zed's agent panel can't be grabbed from outside — not by the official Claude Code app (Remote Control), not by Termius** (verified myself). They're sealed inside the editor process. A Claude Code launched as a CLI from a terminal shows up in the official app's list and is reachable via SSH → Herdr. If there's any chance you'll want to look at a session from outside, launch it as a CLI.

The next section is the clincher for the complement story.

## Letting the agent operate the layout itself

After installing, I wanted my agents — scattered across tabs — on one screen, and on a whim asked Claude Code itself: "consolidate the tabs into one."

Claude Code executed these three commands:

```bash
# Move panes from other tabs into tab t2 as splits (executed by Claude Code itself)
herdr pane move w5:p5 --tab w5:t2 --split right --no-focus
herdr pane move w5:p7 --tab w5:t2 --split down --target-pane w5:p4 --no-focus
herdr pane move w5:p6 --tab w5:t2 --split down --target-pane w5:p5 --no-focus
# → Panes scattered across tabs become a 2×2 grid on one tab. Emptied tabs auto-close
```

Two agents were in `working` state at the time, and the layout changed **without stopping a single one**. All I did was say one sentence. No worrying about reopening panes and interrupting processes, no assembling the sequence of move commands by hand.

Here's what it looked like. Starting from one-tab-per-agent (Before):

![Before: one tab per agent. Four tabs in the tab bar, only one session visible at a time](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/herdr-tab-to-pane-before.png)
*Before: four tabs in the bar. Only one session visible at a time*

I ask the Claude Code in another pane to "consolidate them":

![Instructing Claude Code to consolidate tabs. The screen shows it surveying the tab list and the execution log](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/herdr-tab-to-pane-instruction.png)
*The instruction is a single sentence. Claude Code surveys the current tab structure via the socket API, assembles the pane moves, and runs them*

And everything lands in a 2×2 grid on one tab:

![After: consolidated into a 2×2 grid on a single tab, four panes visible simultaneously](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/herdr-tab-to-pane-after.png)
*After: every agent on one screen. Running processes never stopped*

Agents know where they are through environment variables:

```bash
$ env | grep -i herdr    # home directory in the output replaced with ~
HERDR_ENV=1
HERDR_PANE_ID=w5:p8
HERDR_SOCKET_PATH=~/.config/herdr/herdr.sock
HERDR_TAB_ID=w5:t2
HERDR_WORKSPACE_ID=w5
```

So an agent knows "which pane am I in," and from there it can split a pane next door, run a command, and read the result. **The shape of the execution environment itself becomes one of the agent's tools.** Incidentally, the session writing this very article is a Claude Code inside a Herdr pane — `herdr agent list` shows it as `working` on this draft.

git worktree integration was also a one-liner (verified):

```bash
# Create a worktree + branch + new workspace in one shot
herdr worktree create --workspace w6 --branch feature-x
# → Creates a worktree at ~/.herdr/worktrees/<repo-name>/feature-x/ and
#    opens a workspace labeled "feature-x" with that as its cwd
```

The same "one room per branch, work in parallel" structure as Zed Parallel Agents — except an agent can assemble it from the CLI.

:::details Gotcha: a zoomed tab refuses layout changes
`pane move` can return `changed: false` (reason: `"zoomed_tab"`) and do nothing. If the target tab is in zoomed view, layout changes are rejected by design. Run `herdr pane zoom <pane-id> --off` to unzoom first.
:::

:::details Gotcha: `--current` means the focused pane, not the caller
When I had Claude Code run `herdr pane split`, the pane split in **a different workspace — the one I happened to be looking at** — not the intended one. The CLI's `--current` resolves to "the pane focused in the TUI," not "the pane the command was invoked from."

When agents drive the CLI, don't rely on `--current`; have them pass their own position explicitly via `HERDR_PANE_ID`.
:::

:::details Gotcha: server lifetime and startup directory
- **The server belongs to the parent process that started it.** If `herdr server` gets started from Claude Code's shell, it can die with that session. After my experiments I stopped the server once and restarted `herdr` myself so the server ownership sat with my own process
- **The startup cwd only matters once, at first session creation.** `cd`-ing into a repo and running `herdr` just reattaches to the existing session from the second time on. Add repos from inside Herdr with `herdr workspace create --cwd <repo> --label <name>`. It took a mental-model move from "cd to navigate" to "switch workspaces to navigate"
:::

## Does the sidebar show state, or history?

Running Herdr inside Zed's terminal gives you this nesting:

![Herdr inside a Zed terminal. Spaces/agents sidebar on the left, two Claude Code sessions running side by side in split panes on the right](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/herdr-zed-spaces-agents.png)
*The spaces / agents sidebar on the left. Each agent gets one line with its state and remaining context*

What I noticed in use: Herdr's sidebar **only shows rows that map 1:1 to living processes**. When an agent finishes, its row disappears. It structurally cannot get cluttered.

Zed's Threads sidebar, by contrast, is **a history list**. Sessions that ended days or months ago sit alongside active ones, projects interleaved. Finished work keeps occupying your screen as "attention inventory."

![Zed's Threads sidebar. Finished historical sessions and active ones, across multiple projects, in the same list](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/zed-threads-sidebar-history.png)
*Zed's Threads sidebar. Sessions from 4 days, 2 weeks, and 2 months ago mixed into the same list as active ones*

Does a list show **current state**, or **past history**? That felt like a litmus test for UIs in the parallel-agent era.

This realization changed how I use the whole screen, too. I used to keep a permanent two-way split of editor and CLI — but I only actually looked at the editor "when reading code," and the rest of the time it was dead space.

![Before: permanent two-way split. claude CLI on the left, editor and file tree on the right](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/herdr-zed-split-editor-cli.png)
*Before: permanent two-way split. The editor side spends most of its time unwatched*

![After: full-screen editor-only view, switched to only when reading code](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/herdr-zed-editor-fullscreen.png)
*After: Herdr (the CLI side) is the main screen; when I read code I flip the editor to full screen with `cmd+shift+backtick`*

In agent-driven development, the primary screen flips from the editor to the agent CLI, and **the editor becomes the on-demand side**. Same root idea as the sidebar: align "what's in view" with "what's in use right now," and you stop leaking attention. Since switching to this, Zed has felt closer to "an editor with a file explorer that I open only to read code."

## The division of labor — Zed at the desk, Herdr everywhere else

My setup settled into this:

| Situation | Tool | Why |
|---|---|---|
| At the desk, GUI review while agents run | Zed (Parallel Agents) | Better review experience. Worktree isolation stays in the GUI |
| Keeping agents running after stepping away / quitting apps | Herdr | Server-resident. Session lifetime independent of any app |
| Monitoring and reattaching from iPhone / SSH | Herdr | `ssh → herdr` drops you into the same screen (verified on-device) |
| Delegating layout and parallel execution to agents | Herdr | The socket API is a layer Zed doesn't have |

The iPhone connection path (Tailscale + Termius) is identical to [the one I wrote up in the tmux days](https://dev.to/shimo4228/running-claude-code-from-iphone-via-ssh-tmux-4c10) — just swap tmux for Herdr. If conversational UX is your main goal, [my write-up on the official Claude Code app](https://dev.to/shimo4228/claude-code-from-iphone-plugging-3-holes-in-remote-control-17cf) is a better fit. The split is: "conversation = official app / fleet monitoring = Termius + Herdr."

I also measured what happens when multiple clients attach at once. Attach to the same session from the Mac's terminal and from Termius on the iPhone, and the two become **mirrors of the same screen**. Workspace switches and focus moves on one side show up on the other with barely any lag.

![Termius on iPhone mirroring the same Herdr session as the Mac](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/herdr-termius-iphone-sync.png)
*The iPhone side. It syncs with the Mac's screen with barely any lag. What's on screen is this article's own writing session*

The display size **syncs to the smaller client**. While you're driving from the iPhone, the Mac's terminal also rewraps to the iPhone's screen width:

![The Mac side while the iPhone is in control. Pane contents rendered at the iPhone's screen width](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/herdr-termius-mac-sync.png)
*The Mac at the same moment. While the iPhone is driving, the Mac's display syncs to iPhone size*

One caveat: the server runs as a user process on the Mac (not managed by launchd), so **agents make no progress while the Mac sleeps** (macOS suspends user processes during sleep). Sleep doesn't kill the server — sessions are intact on wake (measured: sleep → wake, session survived). If you want agents running while you're away, configure the Mac not to sleep.

## Closing — the shape of the execution environment becomes the agent's tool

Seen as "a tmux successor," Herdr looks redundant next to Zed. My evaluation flipped when the socket API let an agent operate its own environment.

Looking at just these three, the layers — editor (Zed Parallel Agents), terminal (Herdr), harness (Claude Code's own subagent machinery) — are all absorbing "agent orchestration" features at the same time. Herdr's distinctive answer within that: **it made the layout of the execution environment itself something agents can operate**. Splitting panes, opening rooms, cutting worktrees — the "workspace housekeeping" humans used to do becomes delegable.

It's one brew command to try. If you're running two or more Claude Code sessions in parallel, start by watching your own agents show up in `herdr agent list`.

## Related links

- [ogulcancelik/herdr](https://github.com/ogulcancelik/herdr) — Herdr itself (GitHub)
- [herdr.dev](https://herdr.dev/) — official site and docs
- [Zed: Parallel Agents](https://zed.dev/blog/parallel-agents) — Zed's parallel agent feature
- [Running Claude Code from iPhone via SSH + tmux](https://dev.to/shimo4228/running-claude-code-from-iphone-via-ssh-tmux-4c10) — building the mobile connection path (read tmux as Herdr)
- [Claude Code from iPhone: Plugging 3 Holes in Remote Control](https://dev.to/shimo4228/claude-code-from-iphone-plugging-3-holes-in-remote-control-17cf) — the conversational-UX side
- [Cursor to Zed: Disabling Built-in AI for a CLI-First Setup](https://dev.to/shimo4228/cursor-to-zed-disabling-built-in-ai-for-a-cli-first-setup-6e4) — the Zed environment this article assumes
- [github.com/shimo4228](https://github.com/shimo4228) — my GitHub (agent-related skills and tools)
