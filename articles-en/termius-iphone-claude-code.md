---
title: "Running Claude Code from iPhone via SSH + tmux"
emoji: "📱"
type: "tech"
topics: ["claudecode", "termius", "ssh", "tailscale"]
published: true
---

# What Lies Beyond Abandoning GUI

In [my previous article](https://zenn.dev/shimo4228/articles/cursor-to-zed-migration), I wrote about switching from Cursor to Zed. It was about resolving the discomfort of "a heavy container for light contents" by going with a lighter editor.

This time, I go one step further. **I ditched the editor entirely and built an environment to run Claude Code from a black screen on my iPhone.**

The motivation was simple. I wanted to send instructions to Claude Code while away from my desk. That's it.

## Premise: I'm a Developer Who Only Reads Code

Same premise as the previous article, but worth restating.

My development flow has exactly three steps:

1. **Read** code (review)
2. **Give instructions** to Claude Code
3. **Verify** the generated code

All I need from an editor is "display things fast." I don't use code completion or snippets.

If you follow this premise to its logical end, you arrive at one question:

**Can't I do the "reading" part on an iPhone screen too?**

---

## Chrome Remote Desktop: The First Wrong Turn

My first idea was to remote-control my Mac from my iPhone. Chrome Remote Desktop is free, after all.

I searched the App Store. Nothing came up.

I asked Gemini, and it told me Google had discontinued the native iOS app and migrated to a web app (PWA). You can supposedly use it by accessing `remotedesktop.google.com` from Safari.

Technically usable, but I paused to think. **Do I really need to stream an entire screen image just to operate Claude Code?**

Transmitting a terminal's black screen as "video" is a waste of bandwidth. Text gets blurry, input lag is noticeable. And fitting a Mac desktop onto an iPhone screen turns everything into unreadable specks.

Gemini's suggestion was this:

> "Remote desktop," which streams the screen as video, is not optimal for CLI operations. An SSH connection that sends only text data uses less than 1/100th the bandwidth, and text stays crisp.

Right. Send text, not video.

---

## The Blueprint Gemini Drew

Here's the architecture Gemini proposed:

```text
Mac (home, always on)
  ├─ Tailscale (VPN)
  ├─ SSH (remote login)
  ├─ tmux (session persistence)
  └─ Claude Code

iPhone (on the go)
  ├─ Tailscale (VPN)
  └─ Termius (SSH client)
```

**Tailscale** is a zero-config VPN. It virtually connects the iPhone and Mac with a direct LAN cable. No port forwarding needed, free.

**Termius** is an iOS SSH client. It connects the iPhone to the Mac's terminal.

**tmux** is a session persistence tool. Even if the connection drops, processes on the Mac keep running. Reconnect and the screen restores exactly where you left off.

Cost: $0/month. No VPS needed. Just use the Mac at home.

The blueprint was elegant. The problems started with the implementation.

In reality, it took a full week to arrive at this blueprint.

---

## February 7: First Attempt and Retreat

My first try with Termius was on February 7.

Connected VPN with Tailscale, SSH'd into Mac via Termius. So far so good. Launched Claude Code — "Please authenticate in your browser."

The browser doesn't open. Of course. Over SSH, the browser opens on the remote Mac. Nothing appears on my iPhone.

The screen showed `c to copy`, so I pressed `c`. "Copied," it said. I switched to Safari on my iPhone and pasted. Nothing.

I asked Gemini:

> `c to copy` copies to the remote Mac's clipboard. It doesn't sync to the iPhone clipboard.

Gemini taught me the `pbpaste` command to output the Mac clipboard contents to the terminal, but the procedure kept getting more convoluted — long-press to select the URL, and so on.

"This is too complicated," I thought.

I retreated for the day. Gemini's conclusion was clear:

> Just run `claude` once while sitting in front of the Mac and log in. After that, Termius sessions will use the authenticated state.

True, but that doesn't solve the scenario of "using it for the first time from outside."

---

## February 12-13: Second Attempt

Five days later, I tried again. This time I had Gemini draw the full blueprint first and took a systematic approach.

## Seven Stumbling Blocks

### 1. Node.js Wasn't Installed

Claude Code worked in Cursor's Extension, but typing `claude` in the terminal did nothing. Why?

I asked Gemini. The answer was straightforward:

> Cursor bundles its own internal Node.js environment. Your system terminal doesn't have Node.js installed.

Trying to run `npm install -g @anthropic-ai/claude-code` gave me `zsh: command not found: npm`. Not even npm was there.

```bash
brew install node
npm install -g @anthropic-ai/claude-code
```

This got the `claude` command working. Dependencies that had been hidden inside Cursor were now exposed in the terminal.

### 2. OAuth Authentication Can't Open a Browser

When launching Claude Code and trying to log in, it says "Please authenticate in your browser." Normally, a browser opens with the auth screen.

But this is a remote connection via Termius. The browser opens on the remote Mac. Nothing shows up on the iPhone.

I had to manually copy the URL displayed in the terminal and open it in Safari on my iPhone.

### 3. The URL Is Too Small to Copy

Here's where it got painful. The OAuth URL is a string of 100+ characters. The Termius screen on iPhone is small, and selecting it precisely with a finger was nearly impossible.

I had Gemini read the URL from a screenshot. Tapped the link to open it in Safari. Logged in.

"Invalid Auth request." Error.

Either Gemini's OCR was off by a character, or the URL had expired. OAuth URLs contain cryptographic tokens — a single wrong character causes failure.

I ended up using Termius's long-press copy feature to grab it manually, then re-issued the URL with `/login`.

> **Root fix for the auth problem**: The OAuth troubles described above are completely avoided with the "tmux approach" explained later. Log in once on the Mac side and create a tmux session. You'll never need to touch the auth flow from iPhone at all.

### 4. Tailscale Shows Green but Connection Fails

Opening the Tailscale app showed both iPhone and Mac in green — "Connected." The VPN tunnel was up.

Yet connecting from Termius gave me **"Connection timed out."**

The issue wasn't "iPhone can't find Mac on the network." It was "iPhone reached Mac's front door, but the door was locked."

The culprit was Mac's firewall. SSH (TCP 22) was being blocked.

Under `System Settings > Network > Firewall > Options`, I allowed "Remote Login (SSH)."

### 5. Mac Falls Asleep While Away

I had left before fixing the firewall settings. The MacBook lid was open, but it had gone to sleep after a while.

Gemini's last-resort suggestion:

> Send a "Play Sound" command to your Mac via the Find My app. This forces it to wake from sleep. Use that window to connect via SSH.

I gave up and went home that day.

Lessons learned after getting back:

- `System Settings > Displays > Advanced > Prevent automatic sleeping when the display is off` → **ON** (while on power adapter)
- Before leaving: Keep the Mac lid open, plug in the power cable, lock with `Ctrl + Cmd + Q`
- SSH and Tailscale work perfectly on the lock screen

> **Note on "API Usage Billing" display**: I panicked when the Claude Code startup screen showed "API Usage Billing." But this is the default text that appears even on the Max plan. Actual billing stays within the Max plan quota — running `/cost` confirmed $0.

### 6. SSH Requires Re-authentication Every Time

Connection succeeded. But a new problem appeared. Every time I launched Claude Code over SSH, it demanded OAuth login again.

I asked Gemini, and this turned out to be a macOS Keychain issue:

> Claude Code stores OAuth tokens in macOS Keychain. When logged in locally, Keychain unlocks automatically. But SSH sessions don't go through a GUI login session, so Keychain stays locked.

As a workaround, I added a Keychain-unlocking wrapper function to `.zshrc`:

```bash
claude() {
    if [ -n "$SSH_CONNECTION" ] && [ -z "$KEYCHAIN_UNLOCKED" ]; then
        security unlock-keychain ~/Library/Keychains/login.keychain-db
        export KEYCHAIN_UNLOCKED=true
    fi
    command claude "$@"
}
```

A password prompt appeared. But the cursor didn't move. No characters displayed.

This is a security feature — nothing shows on screen during password entry. I typed it anyway and pressed Enter.

`The user name or passphrase you entered is not correct.`

Maybe Termius's keyboard was inserting unintended characters. It never worked no matter how many times I tried.

### 7. tmux Solved Everything

Gemini's suggestion was a shift in perspective:

> If you launch Claude Code inside a tmux session while logged in locally on the Mac, then from iPhone you just attach to that session. No re-authentication needed.

In other words, skip Keychain unlocking entirely.

```bash
# Run once locally on the Mac
tmux new -s cc
claude

# From iPhone (any number of times)
tmux attach -t cc
```

Claude Code is already running locally. From iPhone, you're just "peeking into that window." Keychain is irrelevant.

"But what if I want to start a fresh session? Sometimes I need to reset the context."

> Use `/exit` inside tmux to quit, then run `claude` to restart. A new context session begins. tmux is just a container — you can swap the contents freely.

Makes sense. tmux is a terminal box that keeps running on the Mac. The iPhone just operates what's inside that box. It's exactly the same as working locally.

---

## "Can't I Just Launch Cursor?"

After the connection was working, I idly asked Gemini.

"Can't I launch Cursor?" Gemini replied:

> Termius can only handle text (CLI). Cursor is GUI (graphics). Even if you run `cursor .` over SSH, Cursor opens on your Mac's screen at home — nothing appears on iPhone.

Right. So how do I read code without Cursor?

> Claude Code itself serves as a file viewer. Say "show me the contents of main.swift" and it displays it. It can show diffs too.

"Well, it's the same thing in the end."

After saying that, I thought a bit more and added:

"Both are just looking at text anyway." This is the core insight of this article.

Opening a file in Cursor to read code. Asking Claude Code to "show me this file." **You're looking at the same text.** Giving instructions is the same too — typing in Cursor's sidebar terminal versus typing in an SSH terminal.

GUI is just a skin. Text is the substance.

On an iPhone's small screen, a text-only CLI actually has higher information density than a GUI that fills the screen with buttons and windows.

---

## The Final Setup

Here's the final architecture and operational rules.

### Architecture

| Layer | Tool | Role |
|-------|------|------|
| VPN | Tailscale (free) | Encrypted connection between iPhone and Mac |
| SSH Client | Termius (free) | Connect from iPhone to Mac |
| Session Management | tmux | Maintain processes across disconnects |
| Development Tool | Claude Code | Code generation, review, execution |

### Pre-departure Routine

1. Plug in the Mac's power cable
2. Lock the screen with `Ctrl + Cmd + Q`
3. **Leave the lid open** and head out

### Connecting from iPhone

```bash
# Tap "My mac" in Termius → auto tmux attach (Startup Snippet)
# If a session exists, you resume. Otherwise, a new one is created.

# New Claude Code session
/exit          # End current session
claude         # Fresh start (no re-auth needed)
```

### Termius Configuration Tips

- **Startup Snippet**: Set `tmux attach -t cc || tmux new -s cc`. Automatically enters tmux on connect.
- **Live Activities**: Recommend OFF. tmux handles persistence, so keep-alive notifications are unnecessary. Saves battery.
- **Mosh**: Start with OFF. If SSH + tmux proves insufficient, enable it later.

### Cost

| Item | Monthly |
|------|---------|
| Tailscale | $0 |
| Termius | $0 |
| VPS | Not needed ($0) |
| Claude Code | Max plan (existing) |
| **Total** | **$0** (beyond Claude Max plan) |

---

## SSH vs Mosh — SSH Is Enough for Now

I asked Gemini whether I should switch to Mosh.

Mosh is a connection-persistence protocol that auto-recovers from dropped connections and eliminates input lag through local echo. In theory, it's a strict upgrade.

However, it uses UDP ports (60000-61000), requiring additional firewall configuration. Having struggled extensively with the firewall already, I didn't want to break a working setup.

Gemini's advice was spot-on:

> Try running with SSH + tmux for a few days first. Only when you find yourself thinking "reconnecting is annoying!" or "the input lag is driving me crazy!" should you move to Mosh.

Upgrade when you feel the pain. The right call.

---

## Honest Take: iPhone Is a "Remote Control"

After a few days of use, here's my honest assessment.

**Terminal operation on iPhone is a fairly rough experience.**

The screen is too narrow to see the full picture of the code. Typing long prompts with a phone keyboard is painful.

Scrolling also needs a workaround. iPhone swipe gestures don't work inside tmux — you need to enter copy mode with `Ctrl+b → [` and navigate with arrow keys. Enabling mouse mode lets you scroll by touch, but the fundamental screen size limitation remains.

```bash
# Enable touch scrolling
echo "set -g mouse on" >> ~/.tmux.conf
tmux source-file ~/.tmux.conf
```

That said, if you accept the limited use case, it's perfectly practical:

- **Checking Claude Code's progress**
- **Pressing y at approval prompts** to let it continue
- **Sending short follow-up instructions**

Serious review waits until I'm back at the Mac. The iPhone is just a "remote control."

---

## The De-GUI Trilogy

Looking back, three articles connect along a single thread: "shedding GUI."

| Article | What was abandoned | What remained |
|---------|-------------------|---------------|
| [ECC Journey](https://zenn.dev/shimo4228/articles/ecc-journey-part1) | Coding itself | Instructions to Claude Code |
| [Cursor to Zed](https://zenn.dev/shimo4228/articles/cursor-to-zed-migration) | The heavy editor | A light editor + terminal |
| **Termius + Claude Code** (this article) | The editor's GUI | **Terminal only** |

First it was "you don't need to write code in the AI era." Then "you don't need a heavy editor." And now "you don't even need GUI."

What remains is a black background with white text on an iPhone screen. And a conversation with Claude Code.

**Both are just looking at text anyway.**

If that's the case, the optimal solution is the environment that sends and receives text most efficiently. That turned out to be SSH.

---

## Bonus: The Gemini-Assisted Journey

This entire setup was built with Gemini guiding me along the way.

Setting up Claude Code by consulting Gemini. It's a meta situation, but in practice it was the most efficient approach. Claude Code wasn't running yet, so troubleshooting the path to getting it running had to fall to a different AI.

Gemini read an OAuth URL from a screenshot and got one character wrong. It taught me the trick of waking a sleeping Mac through Find My. And it was Gemini that explained the fundamental difference between GUI and CLI in a single line:

> GUI is video (a video call). CLI is text (a phone call). CLI is optimal for iPhone + SSH because transmitting text doesn't require video.

AI helping set up AI. A scene from 2026 development.

---

## Takeaways

- To operate Claude Code on your Mac from an iPhone, the trio of **Tailscale + Termius + tmux** is all you need
- No VPS required. Use your Mac at home for $0/month
- GUI and CLI are fundamentally the same — "hand text to AI and have it rewrite things"
- Forgetting firewall and sleep settings will lock you out. Check before leaving
- Start with SSH. Upgrade to Mosh only if frustration demands it

Open the black screen on your iPhone while you're out. Send instructions to Claude Code. Your project moves forward on the train.

Strip away all the GUI decoration, and what you find is the lightest, fastest development environment.
