---
title: "Building Zed as an Observation Window for Claude Code — Japanese Typography with IBM Plex"
emoji: "🪟"
type: "tech"
topics: ["zed", "ai", "font", "typography"]
published: true
description: "How I configured Zed as a read-only observation window for Claude Code CLI, resolved dual-formatter conflicts, trimmed visual noise, and arrived at an IBM Plex font stack for Japanese typography — only to discover Zed's defaults were IBM Plex all along."
tags: zed, ai, font, typography
---

# Making Zed an Observation Window: A Design Record of Fonts and Cognitive Resources

In [the previous article](https://zenn.dev/shimo4228/articles/cursor-to-zed-migration), I wrote about migrating from Cursor to Zed. The gist: Cursor felt like a heavy container for lightweight content, so I switched to Zed and settled on a development workflow centered around the Claude Code CLI.

Two months later. Nothing has gone wrong with Zed.

Nothing wrong, but three things kept nagging at me:

1. **Opening a file somehow changes its formatting**
2. **The left dock is cluttered with panels I never use**
3. **Japanese fonts have an unnameable wrongness to them**

This article documents fixing all three in a single day. But it is not just a settings walkthrough. Tracing the "why" behind each setting led to **three design principles** and an **unexpected rediscovery**.

![Before: Zed initial state — SF Mono + unorganized dock](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/zed-observation-window-01-initial.png)
*Before: Zed at session start. SF Mono, unorganized dock, stock UI.*

## Defining the Role: Observation Window

First, the premise. I develop with the Claude Code CLI. Writing code, running tests, git operations — all handled in the terminal by Claude Code.

So what is Zed doing?

**Zed is an observation window.** A window where I pull information that the CLI pushes — file changes, test results, commit logs — to review it as a human. Not a tool for writing. A tool for reading.

Once you recognize this role, the requirements for an editor shift.

| Feature | As a writing tool | As an observation window |
|---------|------------------|------------------------|
| Code completion | Essential | Unnecessary |
| Formatter | Essential | Gets in the way (CLI handles it) |
| Debugger | Essential | Unnecessary |
| File tree | Essential | Essential (locating changes) |
| Git diff view | Nice to have | Essential (seeing what changed) |
| Font quality | Nice to have | **Essential** (reading for long periods) |

The priorities for "writing" and "reading" are entirely different. With this premise, I worked through the three nagging issues in order.

## Cutting Dual Control — format_on_save: off

### Symptom

"Opening a file somehow changes the formatting."

At first I thought I was imagining it. But every time I opened a file, indentation shifted subtly. Diffs appeared. Code written by Claude Code produced diffs just from being opened.

### Diagnosis

The cause was **dual formatting**.

1. Claude Code's PostToolUse hook formats with `black` / `ruff`
2. Zed's `autosave: on_focus_change` + `format_on_save: on` reformats via Zed's LSP formatter
3. The two formatters had slightly different rule configurations, producing diffs

In other words, **two formatters were alternately rewriting the same file under different rules**.

### Fix

```jsonc
// Claude hooks own formatting, so turn this off
"format_on_save": "off",
```

One line. In [the previous article](https://zenn.dev/shimo4228/articles/cursor-to-zed-migration), I actually had `format_on_save: on`. Right after the migration, Claude Code's hook system was not fully set up yet, so having Zed handle formatting made sense. But once PostToolUse hooks with `black` / `ruff` were in full operation, dual formatting became a problem. When the environment changes, settings change with it.

This single line contains a principle important for observation windows.

> **Principle 1: Prioritize the primary channel; do not replicate in the secondary.**
>
> If the Claude Code CLI is the primary channel carrying information, Zed (secondary) should not duplicate the same function. Formatting responsibility is consolidated in the CLI. Duplicating information does not improve observability — it wastes cognitive resources.

![Settings editing — adjusting format_on_save and dock](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/zed-observation-window-02.png)
*The editing process. Working through settings.json in conversation.*

## Trimming Visual Noise — The button: false Approach

### The Left Dock Problem

Before cleanup, the left dock had Terminal, Agent Panel, Debugger, Outline, and Git — panels I never use. As an observation window, I only use Terminal, yet icons for everything else stay in view.

Unused things in your field of vision are noise.

### button: false as a Solution

Zed has a `button: false` setting. It **hides just the button (icon) while keeping the feature alive**.

```jsonc
// Hide buttons for unused panels without killing functionality
"debugger": { "dock": "left", "button": false },
"agent": { "enabled": true, "dock": "left", "button": false },
"outline_panel": { "button": false },
"collaboration_panel": { "button": false },
"diagnostics": { "button": false },
"notification_panel": { "button": false },
"search": { "button": false },
```

You could use `enabled: false` to kill the feature entirely, but I deliberately did not. The Agent Panel may be needed for ACP (Agent Control Protocol) integration. **Do not touch the function; touch the visuals.**

### The Deprecated Key Trap

During this work, Zed warned: "Your settings file uses deprecated settings."

Two causes:

- `collab_panel` — correct key is `collaboration_panel` (renamed)
- `chat_panel` — no longer exists as an independent panel (merged into collaboration)

Old keys still work but produce persistent warnings. I updated to the canonical key names.

### The Notifications Connect Misconception

The right dock's Notifications panel had a "Connect" button. I expected it to show GitHub PR reviews, CI lint errors, deploy failures — all within Zed.

![Right-side Notifications panel with Connect button](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/zed-observation-window-05.png)
*"Connect to view notifications." — I assumed GitHub integration.*

**The reality was different.** Checking Zed's official documentation, this "Connect" is for **Zed's own collaboration feature** (Zed Channels). It uses GitHub OAuth but the scope is `read:user` only — no repository access whatsoever.

There is no official Zed feature for integrating GitHub repository notifications.

I did not connect. The expected feature was absent, and the available feature (collaboration) was one I would not use. Zero value on both sides.

**Lesson: Do not infer functionality from a UI label alone ("Connect").** Especially for connections involving authentication, verify what you are actually connecting to before clicking.

### The "Guessed Value That Did Not Work" Incident

Wanting to empty the status bar, I wrote `active_encoding_button` as `"never"` — thinking of it like CSS `display: none`.

> **Invalid user settings file:** unknown variant 'never', expected one of 'enabled', 'disabled', 'non_utf8'

Zed's settings file uses **type-safe JSONC with schema validation**. Invalid values do not fail silently — they return an immediate error. Better yet, the error message lists the valid values.

The same class of mistake happened three times during this session:

1. `collab_panel` (deprecated; correct: `collaboration_panel`)
2. `font-moralerspace-nf` (discontinued; correct: `font-moralerspace`)
3. `"never"` (does not exist; correct: `"disabled"`)

The common pattern: **guessing a plausible-sounding name**. Verify before guessing. Settings values come from official sources, not intuition.

### The Decision to Keep LSP

For an observation window, the core features of Language Servers (Pyright, tsserver, etc.) — autocomplete, hover, diagnostics — go entirely unused. Why not turn them off?

![LSP diagnostics panel showing empty state](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/zed-observation-window-04.png)
*"No problems in workspace" — LSP is running but has nothing to say.*

Conclusion: **Keep them.** Three reasons:

1. On Apple Silicon with ample memory, the perceived overhead from LSP is near zero
2. JSON schema hints (completions when editing settings.json) turned out to be surprisingly useful — proven during this very session
3. Switching cost (adding config + losing features) > cognitive resources saved (nearly zero)

**"Could be removed" and "should be removed" are different judgments.** If there is no actual harm to cognitive resources, leaving things alone is also a form of optimization.

> **Principle 2: Do not touch the function; touch the visuals (hide, don't delete).**
>
> Hide unused features visually with `button: false`. Killing features risks side effects.
>
> **Principle 3: Trim visible noise; tolerate invisible background processes.**
>
> Dock icons and status bar items consume cognitive resources, so trim them. Background processes like LSP stay out of sight, so tolerate them.

## The Long Font Journey — From SF Mono to PlemolJP Console NF

Here is where the real story begins. Of the three nagging issues, fonts consumed the most time.

### SF Mono Has No Japanese Glyphs

I was using SF Mono as the default (technically macOS's default). Japanese "just appeared." But **SF Mono contains only Latin characters**.

So where was the Japanese coming from?

The answer was **CJK fallback**. macOS's font rendering detected that SF Mono lacked Japanese glyphs and drew them using system fallback fonts like Hiragino Sans or PingFang SC.

The problem was metrics. The fallback font's baseline, character width, and line spacing were subtly misaligned with SF Mono, producing a **"something feels off" jitteriness**. Hard to articulate, but definitely there.

The solution was clear: a **CJK-unified font** — one where Latin and Japanese glyphs coexist in the same font file with metrics unified from the start.

### Moralerspace Argon: Too Bold

The first candidate was [Moralerspace](https://github.com/yuru7/moralerspace). A CJK-unified font by the same author as UDEV Gothic (yuru7), synthesizing Monaspace + IBM Plex Sans JP. I chose the Argon variant.

```bash
brew install --cask font-moralerspace
```

> :warning: `font-moralerspace-nf` (the Nerd Font-only cask) was discontinued on 2025-07-29. Nerd Fonts are shifting from "patched font files" to a "symbols overlay" approach, and the base `font-moralerspace` is the successor.

Result: **It felt bold.** Even at Regular weight, the strokes had too much presence. Modern and refined design, but for an observation window meant for long reading sessions, I wanted something more restrained.

### PlemolJP Console NF: Light Was Too Thin, Regular Landed

Next up was [PlemolJP](https://github.com/yuru7/PlemolJP). A CJK-unified font synthesizing IBM Plex Mono + IBM Plex Sans JP. I chose the Console NF variant (monospace + Nerd Font symbols).

```bash
brew install --cask font-plemol-jp-nf
```

First I tried Light (weight 300). **Too thin.** Characters dissolved into the background, requiring subtle effort to read.

Regular (weight 400). **Landed.** Classic strokes inherited from Plex Mono — less assertive than Moralerspace, more present than Light. The sweet spot.

#### Getting the Exact Font Family Name

Right after `brew install`, I tried to write the font name in Zed's settings.json. **The exact family name was unclear.**

If macOS's Spotlight index has not updated, `mdls` returns empty. The reliable method is `system_profiler`:

```bash
system_profiler SPFontsDataType 2>/dev/null | \
  grep -B 1 -A 4 "PlemolJPConsoleNF-Regular:" | head -20

# Result:
#   Full Name: PlemolJP Console NF Regular
#   Family: PlemolJP Console NF
#   Style: レギュラー
```

`Family: PlemolJP Console NF` — this is the value for settings.json.

### Unifying All Layers Failed: The Pain of Reading Prose in Monospace

With PlemolJP Console NF, the Buffer and Terminal felt great. Riding that momentum, I **applied the same font to the UI**. All layers unified — beautiful.

![UI with PlemolJP showing prose monospace problem](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/zed-observation-window-03.png)
*The monospace-UI failure. Japanese prose forced into a grid feels wrong.*

**Something was off.** Panel labels, Insight block text, Japanese segments in file paths — they all looked like "a sequence of square boxes."

Thinking about the cause, it clicked. **Monospace fonts assume a fixed-width grid.** ASCII characters look natural aligned to a grid, but Japanese prose is naturally read in proportional spacing (varying width per character).

This connects to the history of type:

- **Monospace**: Originated from typewriters. Each physical type slug had to be the same width or the carriage would not advance. Code culture adopted the grid as standard
- **Proportional**: Since movable type printing, prose has been set in proportional spacing. Varying character widths create a smoother reading flow

UI is primarily prose-like labels. Applying monospace to prose was like typesetting a novel on a typewriter.

### IBM Plex Sans JP: Returning Just the UI to Proportional

Revert the UI to proportional. But instead of reverting to the system default, I chose from **within the same IBM Plex family as PlemolJP**.

```bash
brew install --cask font-ibm-plex-sans-jp
```

IBM Plex Sans JP is the Japanese extension of IBM Plex Sans — PlemolJP's "proportional sibling." The design language is unified, so there is no jarring disconnect between Buffer (monospace) and UI (proportional).

```jsonc
{
  // UI: proportional (suited for prose)
  "ui_font_family": "IBM Plex Sans JP",
  "ui_font_size": 16.0,
  "ui_font_weight": 400,

  // Buffer: monospace (suited for code)
  "buffer_font_family": "PlemolJP Console NF",
  "buffer_font_size": 15.0,
  "buffer_font_weight": 400,

  // Terminal: monospace (suited for CLI output)
  "terminal": {
    "font_family": "PlemolJP Console NF",
    "font_weight": 400,
    "font_size": 14,
    "line_height": "comfortable"
  }
}
```

Each of the three layers gets the appropriate font type.

| Layer | Purpose | Font Type | Font | Size |
|-------|---------|-----------|------|------|
| UI | Panel labels, menus | Proportional | IBM Plex Sans JP | 16pt |
| Buffer | Code display | Monospace | PlemolJP Console NF | 15pt |
| Terminal | CLI output | Monospace | PlemolJP Console NF | 14pt |

Buffer is for "reading"; Terminal is for "scanning." Font size steps down by 1pt according to information density.

## Rediscovery — Zed's Default Was IBM Plex All Along

I was satisfied with the setup when I idly looked up Zed's default font.

Zed uses aliases called `.ZedSans` and `.ZedMono`. Their underlying fonts:

- **`.ZedSans`** = **IBM Plex Sans**
- **`.ZedMono`** = **Lilex** (a fork of IBM Plex Mono with ligatures)

Zed's default font is the **IBM Plex family**.

In other words, what happened was this:

> **SF Mono -> Moralerspace (did not fit) -> landed on PlemolJP (IBM Plex Mono-based) -> applied IBM Plex Sans JP to UI -> ended up building a Japanese-optimized version of Zed's own defaults**

Arriving independently at the IBM Plex family was not a coincidence. The Zed development team chose IBM Plex too. More accurately, I naturally arrived at this point along the extension of Zed's design philosophy.

![Zed final UI — IBM Plex Sans JP + PlemolJP Console NF](https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/zed-observation-window-final-ui.png)
*After: Left dock is Terminal only, Buffer uses PlemolJP Console NF, UI uses IBM Plex Sans JP. File tree on the right dock.*

## Closing — settings.json Is a Record of Design Decisions

Today's work produced a 140-line settings.json. Each item maps to one of the three principles.

| Principle | Corresponding Settings |
|-----------|----------------------|
| **Primary channel first** | `format_on_save: "off"`, `edit_predictions.provider: "none"` |
| **Do not touch the function; touch the visuals** | Various `button: false`, `agent.enabled: true` (kept alive but hidden) |
| **Trim visible noise; tolerate invisible background** | All `status_bar` items off, `show_whitespaces: "none"`, LSP retained |

This settings.json is not a list of preferences. **It is a record of design decisions for protecting cognitive resources.**

"Changing" and "optimizing" are different things. Understanding Zed's default design, then adapting it to my usage pattern (observation window) and environment (Japanese mixed content). Not breaking it — localizing it.

In the previous article, I wrote "I switched from Cursor to Zed." Now I can say it more precisely.

**I built Zed as an observation window for Claude Code.**

<details><summary>Full settings.json</summary>

```jsonc
{
    "diagnostics": { "button": false },
    "calls": { "share_on_join": true, "mute_on_join": true },
    "notification_panel": { "button": false },
    "pane_split_direction_vertical": "right",
    "active_pane_modifiers": { "inactive_opacity": 1.0 },
    "use_system_window_tabs": false,
    "bottom_dock_layout": "contained",
    "tabs": { "file_icons": false, "git_status": false },
    "tab_bar": {
        "show_pinned_tabs_in_separate_row": false,
        "show_nav_history_buttons": true,
        "show": true
    },
    "title_bar": {
        "show_user_picture": false,
        "show_sign_in": true,
        "show_project_items": true,
        "show_branch_name": true
    },
    "status_bar": {
        "active_encoding_button": "disabled",
        "show_active_file": false,
        "active_language_button": false,
        "cursor_position_button": false
    },
    "search": { "button": false },
    "agent_servers": { "claude-acp": { "type": "registry" } },
    "debugger": { "dock": "left", "button": false },
    "icon_theme": "Zed (Default)",
    "edit_predictions": { "provider": "none" },
    "agent": { "enabled": true, "dock": "left" },
    "session": { "trust_all_worktrees": true },
    "theme": {
        "mode": "system",
        "light": "Tokyo Night Light",
        "dark": "Tokyo Night"
    },
    "vim_mode": false,
    "soft_wrap": "editor_width",
    "ui_font_family": "IBM Plex Sans JP",
    "ui_font_size": 16.0,
    "ui_font_weight": 400,
    "buffer_font_family": "PlemolJP Console NF",
    "buffer_font_size": 15.0,
    "buffer_font_weight": 400,
    "autosave": "on_focus_change",
    "show_whitespaces": "none",
    "terminal": {
        "flexible": true,
        "show_count_badge": false,
        "dock": "left",
        "font_family": "PlemolJP Console NF",
        "font_weight": 400,
        "font_size": 14,
        "line_height": "comfortable",
        "working_directory": "current_project_directory"
    },
    "tab_size": 4,
    "format_on_save": "off",
    "indent_guides": { "enabled": true, "coloring": "indent_aware" },
    "inlay_hints": { "enabled": true },
    "scrollbar": { "show": "auto" },
    "git": {
        "disable_git": false,
        "inline_blame": { "enabled": true }
    },
    "project_panel": {
        "file_icons": true,
        "hide_gitignore": false,
        "hide_root": false,
        "git_status_indicator": true,
        "bold_folder_labels": false,
        "entry_spacing": "comfortable",
        "button": true,
        "auto_reveal_entries": true,
        "dock": "right"
    },
    "git_panel": {
        "show_count_badge": false,
        "tree_view": true,
        "file_icons": true,
        "dock": "right"
    },
    "outline_panel": { "button": false },
    "collaboration_panel": { "button": false },
    "languages": {
        "Swift": { "tab_size": 4 },
        "JSON": { "tab_size": 2, "soft_wrap": "editor_width" },
        "Python": { "tab_size": 4 }
    }
}
```

</details>

<details><summary>Font installation commands</summary>

```bash
# Buffer / Terminal (IBM Plex Mono + IBM Plex Sans JP synthesis)
brew install --cask font-plemol-jp-nf

# UI (proportional, Japanese support)
brew install --cask font-ibm-plex-sans-jp

# Reliable way to get the exact font family name
system_profiler SPFontsDataType 2>/dev/null | \
  grep -B 1 -A 4 "PlemolJPConsoleNF-Regular:"
```

</details>
