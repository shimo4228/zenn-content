---
title: "Obsidian's Official CLI Is Here — No More Hacking Your Vault from the Back Door"
emoji: "⌨️"
type: "tech"
topics: ["obsidian", "cli", "claudecode", "claude", "automation"]
published: false
---

The moment I ran `mv`, 47 wikilinks broke.

I was reorganizing a 3,674-file Obsidian Vault with Claude Code, and every file move meant manually fixing broken links. I edited a plugin's `data.json` directly — Obsidian overwrote it and my changes vanished. I wrote five Python scripts to bulk-insert frontmatter, but Obsidian's index didn't notice any of it.

**Touching files from outside Obsidian was sneaking in through the back door.**

On February 27, 2026, Obsidian 1.12.4 shipped with an official CLI. The front door is now open.

> This article builds on a previous Vault reorganization effort documented in "[I Had Claude Code Clean Up My 3,674-File Obsidian Vault in a Day](https://zenn.dev/shimo4228/articles/claude-code-obsidian-vault-organization)."

---

## A "Remote Control," Not a Headless Tool

Obsidian CLI launched as early access for Catalyst members in Obsidian 1.12.0 (February 10, 2026) and became generally available to all users in v1.12.4 (February 27, 2026). It is a **built-in, official command-line interface** — no separate installation required, no Catalyst license needed for the GA release.

There is an important design principle to understand. **The CLI operates as a "remote control" for a running Obsidian app.** It is not a standalone headless tool. If Obsidian is not running when you execute a CLI command, it will launch automatically.

What this means in practice: every operation through the CLI passes through **Obsidian's internal API**. File moves automatically update wikilinks. Property changes are immediately reflected in the index. The risks that came with direct file manipulation are eliminated by design.

---

## Setup

### 1. Update Obsidian to 1.12.4 or Later

Install the latest version from [obsidian.md](https://obsidian.md).

### 2. Enable the CLI

Open Obsidian, go to **Settings → General → Command line interface**, toggle it on, and click "Register CLI."

### 3. Add to PATH

On macOS, add the following to `~/.zshrc`:

```bash
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"
```

On Windows and Linux, add the binary path to your environment variables accordingly.

### 4. Verify

```bash
obsidian version
```

If a version number appears, you are good to go.

---

## 100+ Commands in 8 Categories

Obsidian CLI commands fall into **8 categories**:

| Category | Key Commands | Purpose |
|----------|-------------|---------|
| **File Operations** | `files`, `read`, `create`, `append`, `move`, `delete` | Note CRUD |
| **Properties** | `properties`, `property:set`, `property:remove` | Frontmatter manipulation |
| **Search** | `search`, `search:context` | Full-text search |
| **Tags** | `tags`, `tag`, `tags:rename` | Tag management and bulk rename |
| **Links** | `links`, `backlinks`, `unresolved`, `orphans` | Link structure analysis |
| **Daily Notes** | `daily`, `daily:append`, `daily:read` | Daily note operations |
| **Plugins** | `plugins`, `plugin:enable`, `plugin:disable` | Plugin management |
| **Developer Tools** | `eval`, `dev:screenshot`, `devtools` | JS execution and debugging |

### Command Syntax

```bash
obsidian <command> [param=value] [flag]
```

Parameters use `key=value` format. Flags are bare words (no `--` prefix). The sole exception is `--copy` (copy to clipboard), which does use the `--` prefix.

If you have multiple Vaults, specify which one with `vault="VaultName"`:

```bash
obsidian vault="仕事" search query="TODO"
```

---

## The Days of Breaking Links with `mv` Are Over

In the previous Vault reorganization, every file move was a tense moment — will the wikilinks survive? With the CLI, that fear is gone.

### List and Read

```bash
# List all notes in the Vault
obsidian files

# Display folder structure as a tree
obsidian folders

# Read a note's content
obsidian read file="日記/2024-01-15"

# Show a note's metadata
obsidian file file="プロジェクトA"
```

### Create and Append

```bash
# Create a new note
obsidian create name="議事録/2026-03-04" content="# 定例会議"

# Create from a template
obsidian create name="読書メモ/影響力の武器" template="BookNote"

# Append to the end
obsidian append file="プロジェクトA" content="\n\n## 進捗メモ\n- タスクB完了"

# Insert after frontmatter (prepend)
obsidian prepend file="日記/2026-03-04" content="天気: 晴れ"
```

### Move and Delete

```bash
# Move (automatically updates wikilinks)
obsidian move file="Inbox/メモ" to="Archive/"

# Move to trash
obsidian delete file="不要なノート"

# Permanently delete (bypasses trash)
obsidian delete file="不要なノート" permanent
```

The `move` command **automatically rewrites wikilinks**. This is the single biggest difference from the old days of moving files with `mv`. In the previous Vault reorganization, I had to manually verify that links were not broken after every move. With the CLI, that step is gone.

---

## Manually Fixing Frontmatter Across 3,491 Files?

The most labor-intensive part of the previous Vault cleanup was bulk-inserting frontmatter into 3,491 files. I wrote a Python script called `bulk_frontmatter.py` to handle it.

With the CLI, you can set properties on individual files using `property:set`:

```bash
# Check a note's frontmatter properties
obsidian properties file="メモ"

# Set properties
obsidian property:set file="メモ" name="category" value="tech"
obsidian property:set file="メモ" name="status" value="draft"

# Remove a property
obsidian property:remove file="メモ" name="status"
```

That said, running `property:set` one by one across 3,491 files is not realistic. **For high-volume bulk operations, Python scripts are still more efficient.** The CLI's `property:set` shines for individual fixes and as a post-processing step after a script run.

```bash
# Bulk processing via shell script
obsidian files | while read -r f; do
  obsidian property:set file="$f" name="status" value="review"
done
```

---

## No More `grep -r` to Search Your Vault

```bash
# Full-text search
obsidian search query="TODO"

# Search with context (grep-like)
obsidian search:context query="ボトルネック" limit=10

# Open the GUI search panel
obsidian search:open
```

`search:context` shows surrounding lines with each match, much like `grep -C` in the terminal.

---

## Remember Renaming 77 Tags Through the GUI?

In the previous cleanup, I renamed 77 tags using the Tag Wrangler plugin. With the CLI, `tags:rename` handles bulk renaming in one shot.

```bash
# List all tags
obsidian tags

# List files with a specific tag
obsidian tag tag="#プロジェクト"

# Bulk rename a tag across the entire Vault
obsidian tags:rename old=meeting new=meetings
obsidian tags:rename old=日記 new=journal
```

`tags:rename` rewrites the tag across every file in the Vault. Far faster than clicking through Tag Wrangler's GUI.

---

## The Problem of Not Knowing Your Links Are Broken

The essence of Obsidian is a knowledge graph built on links. But Obsidian does not proactively tell you when links are broken. The CLI lets you analyze your link structure.

```bash
# Outgoing links (where this note links to)
obsidian links file="MOC-読書"

# Backlinks (what links to this note)
obsidian backlinks file="Zettelkasten"

# Unresolved links (link targets that don't exist)
obsidian unresolved

# Orphan notes (nothing links to them)
obsidian orphans
```

`orphans` and `unresolved` are Vault health checks. You can run them on a weekly cron job and generate a report — real operational monitoring for your knowledge base.

---

## Running Your Morning Routine from the Terminal

```bash
# Open today's Daily Note (creates it if it doesn't exist)
obsidian daily

# Append to today's Daily Note
obsidian daily:append content="- [ ] 記事のレビュー"

# Display today's content
obsidian daily:read

# Show the Daily Note's file path
obsidian daily:path
```

`daily:append` fits neatly into a morning routine. Hook it into a cron job or an Alfred/Raycast workflow, and you can add tasks without leaving the terminal.

---

## Lessons from Losing Settings by Editing data.json Directly

In the previous article, I learned the hard way what happens when you edit `.obsidian/plugins/{name}/data.json` by hand. The CLI provides a safe way to manage plugins.

```bash
# List installed plugins
obsidian plugins

# Enable or disable a plugin
obsidian plugin:enable id=dataview
obsidian plugin:disable id=calendar

# Hot-reload a plugin (for developers)
obsidian plugin:reload id=my-plugin
```

Theme and CSS snippet management is also covered:

```bash
# List and switch themes
obsidian themes
obsidian theme:set name="Minimal"

# Manage CSS snippets
obsidian snippets
```

---

## Reaching Into Obsidian's Internals with `eval`

The most flexible CLI command is `eval`. It gives you direct access to Obsidian's internal API (the `app` object).

```bash
# Get the number of files in the Vault
obsidian eval code="app.vault.getFiles().length"

# Get the active file's path
obsidian eval code="app.workspace.getActiveFile()?.path"

# Open DevTools
obsidian devtools

# Take a screenshot (base64 PNG)
obsidian dev:screenshot

# View console messages
obsidian dev:console

# View JS errors
obsidian dev:errors
```

`eval` provides full access to Obsidian's plugin API, so you can perform operations not covered by the standard CLI commands. However, **since it calls internal APIs directly, behavior may change across Obsidian version upgrades**. Use standard commands for stable workflows and reserve `eval` for debugging and one-off investigations.

---

## Pipe to jq, Export to Spreadsheets

Some commands like `search` support a `format=` parameter to switch output formats — essential for scripting. Check `obsidian help <command>` for supported formats per command.

| Format | Use Case |
|--------|----------|
| `json` | Pipe through jq |
| `csv` / `tsv` | Spreadsheet export |
| `md` | Markdown format |
| `paths` | File paths only (for piping) |
| `text` | Human-readable (default) |
| `tree` | Folder hierarchy |
| `yaml` | YAML format (default for properties) |

```bash
# search supports format=json
obsidian search query="TODO" format=json | jq '.[].file'

# Pipe file list to xargs
obsidian tag tag="#archive" | xargs -I{} obsidian move file="{}" to="Archive/"

# Copy to clipboard
obsidian read file="共有メモ" --copy
```

---

## Browsing Files Without the GUI — TUI Mode

Running `obsidian` with no arguments launches a **full-screen TUI (Terminal User Interface)**.

| Key | Action |
|-----|--------|
| Arrow keys | Select file |
| `/` | Filter by filename |
| `Enter` | Open in Obsidian |
| `n` | Create new note |
| `d` | Delete file |
| `r` | Rename |
| `Ctrl+R` | Search command history |
| `q` | Quit |

It also supports tab completion and command history. Handy when you want to work with your Vault without leaving the terminal.

---

## What If I Had the CLI During That 3,674-File Cleanup?

Here is the real question. The previous article used "Claude Code + Python scripts + direct file manipulation" to reorganize the Vault. With the Obsidian CLI, how would that workflow change?

### Before: Direct File Manipulation with Python

```python
# Previous approach: reading and writing files directly with Python
import os
import yaml

for root, dirs, files in os.walk(vault_path):
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            with open(path, 'r') as fh:
                content = fh.read()
            # No existing frontmatter check — a bug waiting to happen
            new_content = f"---\ncategory: tech\n---\n{content}"
            with open(path, 'w') as fh:
                fh.write(new_content)
```

**Problems:**

- Obsidian's index does not get updated
- File moves break wikilinks
- Editing while Obsidian is running causes conflicts
- NFD/NFC Unicode normalization has to be handled manually

### After: Operating Through the CLI

```bash
# Via the CLI, operations go through Obsidian's internal API
obsidian property:set file="メモ" name="category" value="tech"

# File moves automatically update links
obsidian move file="Inbox/メモ" to="Tech/"
```

**Problems solved:**

- Index updates automatically
- Wikilinks are rewritten automatically
- Safe to operate while Obsidian is running
- File path normalization is handled by Obsidian

### In Practice: Calling the CLI from Claude Code

Letting Claude Code use the Obsidian CLI dramatically improves the safety of Vault operations.

```bash
# Example instruction to Claude Code:
# "Classify notes in the Inbox folder based on their content"

# Script Claude Code would generate:
obsidian tag tag="#inbox" | while read -r note; do
  content=$(obsidian read file="$note")
  # Claude Code analyzes the content and moves to the appropriate folder
  obsidian move file="$note" to="Tech/"
  obsidian property:set file="$note" name="category" value="tech"
done
```

### When to Use What

The CLI does not solve everything. Choosing the right tool for the job matters.

| Operation | Recommended Approach | Reason |
|-----------|---------------------|--------|
| Creating/moving individual notes | **CLI** | Link preservation, index updates |
| Individual frontmatter fixes | **CLI** (`property:set`) | Safe and simple |
| Bulk processing 3,000+ files | **Python script** | CLI's sequential execution is slow |
| Bulk tag renaming | **CLI** (`tags:rename`) | One command, done |
| Detecting orphan notes | **CLI** (`orphans`) | Dedicated command exists |
| Content-based classification | **Claude Code + CLI** | AI judgment + safe operations |
| Plugin enable/disable | **CLI** (`plugin:enable/disable`) | Safe |
| Complex plugin configuration | **Direct JSON editing** (with Obsidian closed) | CLI does not cover all settings |

---

## A Tidy Vault Will Rot Again If You Ignore It

The CLI's real value is in automation. Even after a thorough cleanup, orphan files and unresolved links will accumulate as you keep adding notes. With the CLI, you can monitor Vault health through cron jobs and scripts.

```bash
#!/bin/bash
# vault-health.sh — Weekly Vault health check

echo "=== Obsidian Vault Health Report ==="
echo "Date: $(date)"
echo ""

echo "## File Statistics"
obsidian files total

echo "## Orphan Notes"
obsidian orphans

echo "## Unresolved Links"
obsidian unresolved

echo "## Tag Distribution (Top 10)"
obsidian tags
```

Run this weekly via cron and append the results to your Daily Note:

```bash
# crontab -e
0 9 * * 1 obsidian daily:append content="$(/path/to/vault-health.sh)"
```

---

## Limitations

The Obsidian CLI covers most Vault operations, but there are limitations worth knowing.

1. **Obsidian must be running**: The CLI is a remote control, not a headless tool. It auto-launches Obsidian on the first command, but you need to wait for startup to complete
2. **Desktop only**: There is no CLI on mobile (iOS / Android)
3. **Multiple Vaults**: By default, the CLI connects to the active Vault. If you use multiple Vaults, you must specify `vault="Name"` every time
4. **Sequential execution is slow at scale**: Each command communicates with the Obsidian app, so bulk processing thousands of files is not its strength. Direct Python scripting may be faster in those cases
5. **Windows Unicode issues**: Fixed in v1.12.4, but earlier versions had problems with Japanese file paths

---

## The Vault Went from "Something You Organize" to "Something You Operate"

The real significance of Obsidian getting a CLI is not that there are more commands. It is that **the Vault became a programmatically controllable system**.

Everything I was doing through the back door in the previous article can now be done through the front door. Links update automatically, the index stays intact, and settings do not conflict.

That said, bulk processing 3,000+ files is still faster with Python scripts. The CLI is not a silver bullet. "Use the CLI for safe operations, use scripts for heavy lifting" — that is the practical split.

Try running `obsidian orphans` once. The number of disconnected notes in your Vault will hit you like a cold shower.
