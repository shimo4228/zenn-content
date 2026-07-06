---
title: "Claude Code from iPhone: Plugging 3 Holes in Remote Control"
emoji: "📱"
type: "tech"
topics: ["claudecode", "tmux", "mobile", "github"]
published: false
description: "Running Claude Code from the official Claude iPhone app hits three walls: you can't spawn new sessions, expired auth can't be fixed remotely, and git push fails with 'Device not configured'. Here is how I plugged all three — a tmux one-liner, a brief VNC hop, and GitHub's device flow with --insecure-storage."
tags: claudecode, tmux, mobile, github
---

> **What this article covers**: the three holes you are likely to hit when you make the official Claude iPhone app (Remote Control) your main way of driving Claude Code from outside — and how to plug each one.

A while back, I wrote about [building an iPhone setup for Claude Code with Termius + Tailscale + tmux](https://dev.to/shimo4228/running-claude-code-from-iphone-via-ssh-tmux-4c10). That approach connects straight to a black SSH screen.

Since then, Claude's official mobile app gained **Remote Control** — a feature that lets you operate the Claude Code instance running on your Mac, remotely, as-is (available since Claude Code v2.1.51, added a few months ago). The UI is well done, and it is now my main setup. Approval prompts and progress are dramatically easier to read than on an SSH terminal.

But once the official app becomes your main interface, you run into three holes. And none of them can be plugged from an iPhone alone while you are out.

| Hole | Symptom | Fix |
|---|---|---|
| **#1** Can't start a new session | The app only connects to existing sessions | Spawn one with a tmux one-liner |
| **#2** Claude auth expires | The login browser opens on the Mac's side | Hop into the screen via VNC just for the auth moment |
| **#3** git push fails | Dies with `Device not configured` | GitHub's device flow + `--insecure-storage` |

## Prerequisites

This article assumes the following are already in place. For the environment setup itself, see the earlier Termius article.

- **Remote Control is enabled in the official Claude app**, and you can already operate Claude Code on your Mac remotely. Remote Control connects through Claude's service, so the iPhone and the Mac do not need to be on the same network
- **Your Mac at home stays on** (plugged in, lid open, sleep disabled)
- `tmux` is installed on the Mac (if not: `brew install tmux`)
- You push to GitHub via **HTTPS + `gh auth login`** (if you push with SSH keys, hole #3 does not apply to you)
- For the VNC re-authentication in the second half, you need a separate **route from the iPhone to the Mac's Screen Sharing**. This is a different channel from Remote Control — set it up over your home LAN or a VPN like Tailscale (see the [previous article](https://dev.to/shimo4228/running-claude-code-from-iphone-via-ssh-tmux-4c10) for setup)

## Hole #1: You can't start a new session from mobile

The official Remote Control has one clear limitation: **the mobile app itself cannot start a new session.** All it can do is list sessions already running on the Mac and connect to them. Any session you want in that list has to be started somewhere, in advance.

This bites in a quiet way. You are driving project A from your iPhone and think "I want a parallel session for project B" — but you cannot trigger that launch from mobile. Your only option is to walk back to the Mac and type `claude`, which means you are stuck whenever you are out.

:::message
Having multiple sessions on one Mac is itself fine. Launch several named `claude --remote-control` instances and they all show up in the list. The problem is that the *launching* cannot be triggered from the iPhone.
:::

:::details Why not the first-party alternatives (server mode / Dispatch)?
Anthropic ships two first-party alternatives ([official docs](https://code.claude.com/docs/en/remote-control)).

**server mode (`claude remote-control`)** keeps one "receptionist" process running, and it spawns new sessions on demand from the mobile side (up to `--capacity N`). But the spawned sessions are **tied to the directory where the receptionist was started (or worktrees of the same repository)**, so it does not fit the use case of spinning up sessions across multiple separate repositories.

**Dispatch** (the Desktop integration), in my hands-on testing (as of July 2026), still felt experimental:

- The execution environment appears to follow a different substrate (Cowork — Claude's agent work environment) rather than Claude Code itself, so custom skills built for Claude Code are unavailable
- Session startup auto-injects boilerplate instructions like "check git status, recent commits, and the layout, then report" — so every conversation opens with a long status report nobody asked for

For now, the spawn approach in this article is my main method.
:::

### Have a live session launch another session

The idea behind the workaround is simple: **have the session that is currently alive (the one you can operate from the iPhone) run a Bash command, and let that session launch another Claude Code on the Mac.**

When Claude Code starts with `--remote-control`, it registers itself with Claude's service as a Remote Control session. Registered live sessions appear in the mobile app's list. So if you launch a new `claude --remote-control` inside tmux, detached (in the background), the list simply gains one more entry. That is the whole trick.

Here is the flow as a diagram:

```text
iPhone (official app / Remote Control)
   │  "Start a new session"
   ▼
Currently live session (on the Mac, RC-connected)
   │  runs the command below via Bash
   ▼
tmux (detached, holds the pty → survives disconnects)
   │  claude --remote-control "AKC"
   ▼
New Claude process → registers itself as RC → "AKC" appears in the app's list
```

From Remote Control on the iPhone, I ask the Claude I am currently driving: "Start a new Remote Control session in `~/MyAI_Lab/agent-knowledge-cycle`." Claude then runs this command on the Mac:

```bash
# 新しい Remote Control セッションを tmux で detached 起動する
tmux new-session -d -s cc-AKC \
  "exec $SHELL -lc 'cd ~/MyAI_Lab/agent-knowledge-cycle && exec claude --remote-control \"AKC\"'"
```

Three points matter here:

- **`-d` (detached)** — launches in the background. It does not hijack the calling session
- **Login shell `-lc`** — loads the PATH for `node` / `claude` before launching. Without this, it dies instantly with "claude not found"
- **tmux holds the pty (pseudo-terminal)** — so even if SSH or the network drops, or the calling session closes, the launched Claude keeps running

A few seconds later, open the app on the iPhone and "AKC" has appeared in the session list. **I never touched the Mac.**

Here is the actual session list. Both `zenn-content` (where this article is being written) and `AKC` below it were spawned this way. (The previous Termius article also had a "new session" section, but that was a different move: typing `/exit` → `claude` inside the single tmux session `cc` to *swap out* its contents. You could only hold one at a time — no parallel projects. This spawn approach lines up multiple named sessions side by side.)

![Session list in the official app, showing zenn-content and AKC, both launched via spawn](/images/iphone-claude-code-remote-control-session-list.png)
*Sessions spawned from the phone show up in the list. Filters for "awaiting input" and "awaiting review" work too*

### Typing this by hand every time is unrealistic, so I made it a launch script

Typing that one-liner by hand every time — on an iPhone keyboard, no less — is not realistic. So I wrapped it in a launch script, `spawn.sh`, that takes just a project name, and made it callable from a Claude Code **skill** (Agent Skills — Claude Code's mechanism for scripting a specific task and invoking it as a `/command`).

From the iPhone, all I say is "Spin up an AKC session." The skill resolves "AKC" → `agent-knowledge-cycle` and passes it to the script below. The skill is published as [spawn-session](https://github.com/shimo4228/claude-harness/blob/main/skills/spawn-session/SKILL.md) (you can borrow the skill-definition style along with it).

:::details spawn.sh in full (copy-paste ready)

```bash
#!/usr/bin/env bash
# spawn.sh — 新しい Claude Code (Remote Control) セッションを tmux で detached 起動する。
# Usage: spawn.sh <project-dir> [display-name]
# 動作条件: tmux 3.2+（new-session の -e オプションを使うため）
set -euo pipefail

PROJECT="${1:?usage: spawn.sh <project-dir> [display-name]}"
PROJECT="${PROJECT/#\~/$HOME}"                       # 先頭 ~ を展開
[[ -d "$PROJECT" ]] || { printf 'spawn.sh: no such directory: %s\n' "$PROJECT" >&2; exit 1; }

NAME="${2:-$(basename "$PROJECT")}"                  # 省略時はディレクトリ名
SESSION="cc-${NAME// /-}-$(date +%H%M%S)"            # tmux セッション名（空白は -）

# tmux を探す。PATH に無くても Homebrew の既定パス（Apple Silicon / Intel 両方）を拾う
TMUX_BIN=""
for candidate in "$(command -v tmux 2>/dev/null || true)" /opt/homebrew/bin/tmux /usr/local/bin/tmux; do
  [[ -n "$candidate" && -x "$candidate" ]] && { TMUX_BIN="$candidate"; break; }
done
[[ -n "$TMUX_BIN" ]] || { printf 'spawn.sh: tmux not found (install: brew install tmux)\n' >&2; exit 1; }

LOGIN_SHELL="${SHELL:-/bin/zsh}"

# tmux -e で値を環境変数として渡す（クォート地獄を回避）。
"$TMUX_BIN" new-session -d -s "$SESSION" -e "CCDIR=$PROJECT" -e "CCNAME=$NAME" \
  "exec $LOGIN_SHELL -lc 'cd \"\$CCDIR\" && exec claude --remote-control \"\$CCNAME\"'"

printf '✅ Remote Control session started: "%s"\n' "$NAME"
printf '   tmux: %s\n' "$SESSION"
printf '   dir:  %s\n' "$PROJECT"

# 起動直後に落ちていないかの簡易チェック（あくまで早期検知。成功保証ではない）
sleep 1
if "$TMUX_BIN" has-session -t "$SESSION" 2>/dev/null; then
  printf '   (tmux session live ✓ — アプリ一覧に出たか最終確認してください)\n'
else
  printf '   ⚠️  起動直後に tmux セッションが消えました（auth 切れ / claude が PATH に無い等）\n' >&2
  exit 1
fi
```

(Comments are in Japanese; the logic reads top to bottom: expand `~`, validate the directory, derive the session name, locate tmux even off-PATH via Homebrew's default paths, pass values as environment variables with `tmux -e` to avoid quoting hell, then a 1-second early liveness check.)

The alias table ("AKC" → actual directory) is deliberately *not* baked into the script; the calling skill owns it. The script stays a pure launcher that receives an already-resolved directory and name.
:::

Running it returns this:

```text
✅ Remote Control session started: "AKC"
   tmux: cc-AKC-143512
   dir:  /Users/you/MyAI_Lab/agent-knowledge-cycle
   (tmux session live ✓ — アプリ一覧に出たか最終確認してください)
```

(The last line says: tmux session live ✓ — do a final check that it appeared in the app's list.)

That `✓` is only an early check meaning "the tmux pane is still alive one second later." **The real confirmation of success is the app's session list.**

:::details When ✓ and the actual outcome disagree (troubleshooting)
- **`✓` appeared but the session is not in the list** — if `claude` is stuck on an auth prompt or a trust confirmation, the pane stays alive (`✓`) but the session never registers
- **It died without a `✓`** — expired auth is the most likely cause, but a wrong PATH or a wrong flag dies the same way

In either case, the reliable move is to peek into the tmux pane first (`tmux attach -t cc-AKC-143512`) and see what actually happened.
:::

:::message
This workaround depends on "at least one session is alive." Only right after a Mac reboot, when nothing is running, do you need to start the first one by hand at the Mac. Then again, if the Mac is off you can't do anything from the iPhone anyway, so in practice this is a non-issue.
:::

## Hole #2: When Claude's auth expires, you can't re-log-in from where you are

Run this setup from mobile for a few days and Claude Code's OAuth occasionally expires. Spawn in that state and it dies right at startup:

```text
   ⚠️  起動直後に tmux セッションが消えました（auth 切れ / claude が PATH に無い等）
```

(Translation: the tmux session vanished right after launch — expired auth, or claude missing from PATH, etc.)

If it was an auth expiry, the real problem starts here. To re-authenticate, the login URL that Claude Code prints has to be opened in a browser. **That browser opens on the home Mac — the machine being remote-controlled.** Nothing shows up on the iPhone in your hand. `/login` is an operation that completes in the CLI on the Mac, and Remote Control does not proxy that browser login to your device.

### Hop into the Mac's screen over VNC, just for the auth

So, **only when authenticating**, I go look at the Mac's actual screen. I use a VNC viewer with a free tier (RealVNC Viewer).

The whole procedure:

1. Connect to the home Mac with RealVNC Viewer on the iPhone
2. Complete the Claude Code browser auth that is open on the Mac, with your finger, on the iPhone
3. Once auth passes, close VNC and return to Remote Control in the official app

VNC streams the entire screen as video, so using it as a daily driver on a small iPhone screen is painful. But for **the single moment of "tap the login button and let auth through,"** it is plenty. Once authenticated, you go back to the far more usable official app.

:::details The conditions for "free to use" (RealVNC licensing)
Whether it is actually free depends on the VNC server on the Mac side. If you install RealVNC Server's Lite plan (free, non-commercial) on the Mac and connect to that, the whole path stays free. If instead you connect to macOS's built-in Screen Sharing, RealVNC's current licensing treats it as a "third-party VNC server," which requires a paid plan on the Viewer side. If you want to stay free, matching RealVNC on the server side is the safe bet.
:::

> ⚠️ **Security note: treat VNC with care.** Exposing remote access to your Mac's screen directly on a shared network like café Wi-Fi is dangerous. **Restrict the Mac's Screen Sharing (VNC) service so it is reachable only from your home LAN or over a VPN such as Tailscale.** The official app's Remote Control connects via Claude's service — a separate path — so keep it mentally separate from the VNC route ("Remote Control works, therefore VNC is safe" does not follow). And always enable a strong password and encryption on VNC.

### Keep auth from expiring in the first place

VNC is the recovery tool for when auth has already expired. Better to not let it expire. One thing works:

**Log in once while you are physically at the Mac, and keep that session alive in tmux.** Same idea as the tmux approach in the previous article. If sessions are launched from a locally logged-in state, the number of times you touch the auth flow at all goes down. Spawn is built on top of this "live session" too — the longer the root session lives, the less often re-authentication comes up.

## Hole #3: git push stops working

After a few days of operating remotely, `git push` stopped going through. The work is done, and the final push dies like this:

```text
fatal: could not read Username for 'https://github.com': Device not configured
```

`gh auth status` says "The token in default is invalid." Looks like the token expired. Here is the trap: **often the token is alive — it just can't be read.**

### The cause: SSH/tmux sessions cannot read the Keychain

gh (the GitHub CLI) stores its token in the macOS Keychain. The login Keychain gets unlocked at **GUI login**. A session over SSH, or a tmux session started by spawn, can neither unlock a locked Keychain nor display the access-permission dialog. The read fails with a "no interaction allowed" error (exit 36), gh cannot read the token and misreports it as "invalid," and git push falls over with no credentials.

The [previous article](https://dev.to/shimo4228/running-claude-code-from-iphone-via-ssh-tmux-4c10)'s issue — Claude Code's OAuth expiring on every SSH connection — had the same root cause. In remote operation, **every tool that depends on the Keychain hits this wall.**

Diagnosing it is copy-paste:

```bash
# Keychain の gh トークンが読めるか（ロック中は exit 36 で失敗する）
security find-generic-password -s "gh:github.com" -w >/dev/null; echo "exit=$?"

# SSH 経由のセッションかどうか
echo "SSH_TTY=${SSH_TTY:-unset}"
```

If you get `exit=36` and `SSH_TTY` is set, it is a Keychain access problem. Conversely, if `exit=0` (the token *is* readable) and gh still says invalid, the token really has expired — and the fix is the same as the next section either way.

### The fix: have Claude itself run the device flow

Unlike Claude Code's OAuth (hole #2), GitHub has a **device flow** — you type a one-time code into a browser on any other device to complete auth. That means **no VNC required**.

I ask the Claude in the session: "Re-authenticate gh using the device flow and tell me the one-time code." What Claude runs boils down to this:

```bash
# バックグラウンドで認証フローを起動し、ワンタイムコードをログから読む
printf '\n' | gh auth login -h github.com --git-protocol https --web --insecure-storage \
  > /tmp/gh-login.log 2>&1 &
sleep 3 && cat /tmp/gh-login.log
```

```text
! First copy your one-time code: XXXX-XXXX
Open this URL to continue in your web browser: https://github.com/login/device
```

Then, **in the browser on the iPhone in your hand**, open `github.com/login/device`, enter the code, and approve. Once approved, the auth process on the Mac side completes, and `git push` goes straight through.

I never entered the Mac's screen. Hole #2's Claude OAuth needed VNC because "where the browser opens" is pinned to the Mac; the device flow lets **the browser open on any device, as long as the code matches**. That difference is what makes this work.

### Is `--insecure-storage` actually OK?

The `--insecure-storage` flag in the command above stores the new token not in the Keychain but in `~/.config/gh/hosts.yml` (a plaintext file with 0600 permissions). This is the permanent fix: **the Keychain is out of the loop, so from then on `git push` works from SSH and tmux alike.**

Let's be precise about what "insecure" means here. Exactly one thing gets weaker: "any process running with your user privileges can read it."

| Threat | Keychain storage | hosts.yml plaintext |
|---|---|---|
| Theft / disk read by another user | Protected | Effectively protected by 0600 + FileVault (when powered off) |
| Malicious process running as you | Some barrier via per-app ACLs | **Readable (this is the "insecure" part)** |
| Leaking into backups / dotfiles sync | The Keychain file itself is encrypted | **Can ride along in plaintext with `~/.config`** |
| Usable from SSH/tmux sessions | No (our original problem) | Yes |

So the protection drops in two scenarios: "after you have already allowed arbitrary code execution on the machine," and "if `~/.config` is included in backups or dotfiles sync." Even then, it is the same level as plaintext API keys in `~/.aws/credentials` or `.env` — a standard storage method for CLI tools. If you suspect a leak, you can revoke immediately from GitHub's [Applications settings](https://github.com/settings/applications).

More than hardening the storage location, **narrowing the token's permission scope is what actually limits the damage of a leak**. The narrowing options are folded below.

:::details If you want to narrow the blast radius further (fine-grained PAT)
One option is switching to a fine-grained PAT (an access token you can scope to specific repositories with an expiry). Note that gh recommends passing fine-grained PATs via the `GH_TOKEN` environment variable rather than registering them with `--with-token`, since the latter can confuse the behavior of some commands. This is the narrowing move for the "all I need is push" case.
:::

## The finished setup

My mobile operation has settled into this shape:

| Device / tool | Role | Path |
|---|---|---|
| Official Claude app (Remote Control) | Main UI. Progress checks, approvals, giving instructions | Via Claude's service |
| spawn (tmux one-liner / skill) | Start new sessions without touching the Mac | Bash inside a live session above |
| RealVNC Viewer | Only when Claude's auth expires: complete the Mac-side browser login from the iPhone | LAN / Tailscale (VNC only) |
| Device flow (`gh auth login --web`) | Recover git push auth using nothing but the iPhone's browser | Via GitHub's service |

The daily loop looks like this:

1. Operate as usual from the official app on the iPhone
2. Need another project? "Spin up a session for X" → spawn, then confirm it appeared in the app's list
3. `⚠️ session vanished` = expired auth is the prime suspect → pass auth via VNC, return to the official app
4. `git push` dies with `Device not configured` → have Claude run the device flow, approve in the iPhone's browser (make it permanent with `--insecure-storage` and it stops happening)

To be honest, the iPhone is still, as before, a "remote control." Serious reviews happen back at the Mac. But **starting sessions without touching the Mac, recovering from auth expiry from outside, and completing the push** — with those three holes plugged, the situations where I am stuck while out have all but disappeared.

## Summary

- The official app's Remote Control has a good UI and suits mobile-first operation. But it has three holes: "you can't start a new session from mobile," "you can't fix Claude's expired auth from where you are," and "git push auth fails"
- **The new-session problem**: have a live session run `tmux new-session -d ... claude --remote-control`. The new process registers its own Remote Control session and appears in the app's list (`✓` is an early check; the app's list is the real confirmation)
- **Claude auth expiry**: enter the Mac's screen via VNC only for the auth moment, and complete the browser login from the iPhone. Keep the VNC (Screen Sharing) route restricted to LAN/VPN, and treat it as separate from Remote Control
- **git push auth**: the cause is the Keychain (unreadable from SSH/tmux). Have Claude run gh's device flow, approve in the iPhone's browser, and use `--insecure-storage` to remove the Keychain dependency for good
- Environment setup (Tailscale etc.) stays in the earlier Termius article; this one focused on day-to-day operation with the official app at the center

I abandoned the editor, passed through even the black SSH screen, and now I start sessions and finish pushes from the official app in my pocket, without touching the Mac. The remaining holes each got plugged: a tmux one-liner, VNC, and the device flow.

## Related articles

That's it for the tooling. One level deeper — agent design itself:

- [Where ReAct Agents Are Actually Needed in Business](https://dev.to/shimo4228/where-react-agents-are-actually-needed-in-business-33do)
- [I Built a Skill for Easy Codex Reviews from Claude Code](https://dev.to/shimo4228/i-built-a-skill-for-easy-codex-reviews-from-claude-code-4h89)

The previous mobile-setup article:

- [Running Claude Code from iPhone via SSH + tmux](https://dev.to/shimo4228/running-claude-code-from-iphone-via-ssh-tmux-4c10)

The skill used in this article:

- [spawn-session skill (claude-harness)](https://github.com/shimo4228/claude-harness/blob/main/skills/spawn-session/SKILL.md) — the spawn approach from this article, packaged as a skill

Research artifacts (with DOIs) live at [github.com/shimo4228](https://github.com/shimo4228).
