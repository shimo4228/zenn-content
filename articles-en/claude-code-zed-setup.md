---
title: "Running Claude Code in Zed — Why I Disable the Built-in AI"
emoji: "⚡"
type: "tech"
topics: ["claudecode", "zed", "editor", "devenv"]
published: true
---

When I was using Claude Code inside Cursor, I noticed a brief freeze every time a file changed. I wasn't using Cursor's Tab completion or Composer — just the Claude Code extension — yet background indexing kept eating CPU. It was a heavy container for lightweight contents.

After switching to Zed, file rendering became instant and CPU usage dropped. This article covers the Zed settings I use when pairing it with Claude Code.

## Why Zed

When Claude Code is your primary development tool, the editor's role shifts from "writing code" to "reading code." Claude Code edits the files; the editor displays those changes instantly. For that division of labor, speed is the top priority.

Here's the 3-pane layout I use:

## Layout

```text
┌──────────────────┬──────────────────┬─────────────┐
│                  │                  │             │
│ Claude Code CLI  │   Zed Editor     │ File Tree   │
│ (terminal)       │   (file view)    │ (right)     │
│                  │                  │             │
│ Give instructions│   Review results │ See structure│
└──────────────────┴──────────────────┴─────────────┘
```

I type instructions in the CLI on the left; Claude Code modifies the files. The changes appear immediately in Zed in the center. The file tree on the right gives an overview of the project structure.

## Disabling the Built-in AI

Zed's Agent Panel (the GUI-based AI chat) overlaps with the Claude Code CLI in functionality. Keeping both enabled leads to double context consumption.

```jsonc
// ~/.config/zed/settings.json
{
  "agent": {
    "enabled": false
  },
  "features": {
    "edit_prediction_provider": "none"
  }
}
```

This disables the Agent Panel (formerly Assistant Panel) and AI code completion, leaving Claude Code CLI as the sole AI interface.

> These setting keys may change across Zed versions. If they don't work, check the [Zed official documentation](https://zed.dev/docs) for the latest keys.

## Why Use Claude Code in the Terminal

Zed can also run Claude through the Agent Panel, but launching the CLI directly in Zed's built-in terminal is more practical:

- **Context consumption is visible**: The CLI status bar (at the bottom of the screen) shows context usage as a percentage. You can gauge when to wrap up a session by checking remaining capacity
- **Full feature access**: CLI-only features like `/learn`, `/plan`, and MCP server integration are available
- **Operational transparency**: Every command Claude Code runs and every file change it makes is displayed in the terminal

## Recommended Additional Settings

### Theme and Font

```jsonc
{
  "theme": "One Dark",
  "ui_font_size": 14,
  "buffer_font_size": 14,
  "buffer_font_family": "JetBrains Mono"
}
```

### Auto-Reload on File Changes

When Claude Code modifies a file, Zed automatically updates the displayed content. No additional configuration is needed. This is a major advantage of pairing Zed with Claude Code.

### Language Servers

Zed ships with built-in language server (LSP) support. TypeScript, Python, Rust, and others get go-to-definition and code completion out of the box. Swift works via sourcekit-lsp, though building and simulator execution still happen in Xcode.

## Caveats

**Japanese input**: Zed's Japanese input support is still maturing. You may notice sluggishness when editing comments or CLAUDE.md files. Since the primary input target is the terminal (Claude Code CLI), the practical impact is limited.

**Settings file changes**: Configuration keys can change structurally between version upgrades, so keeping a backup is a good idea.

## Takeaways

Three things changed after moving from Cursor to Zed:

1. **Startup and file rendering got faster** — The lag between Claude Code modifying a file and Zed reflecting it is nearly zero
2. **CPU and memory usage dropped** — Disabling the built-in AI eliminated background processing
3. **Operations consolidated into the CLI** — The division of labor is clear: instructions go to the terminal, review happens in the editor

If Claude Code is your primary tool, it's comfortable to treat the editor as a lightweight display layer and nothing more.
