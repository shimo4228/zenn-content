---
title: "How I Organized 3,674 Obsidian Vault Files in One Day with Claude Code"
emoji: "🗄️"
type: "tech"
topics: ["obsidian", "claudecode", "claude", "python"]
published: true
---

## Introduction

I had 3,674 Markdown files exported from Evernote, Apple Notes, and Apple Journal sitting in my Obsidian Vault. No frontmatter, no tags, no classification. Web clippings were mixed with my own writing, and duplicate files were everywhere.

I organized all of it in one day using Claude Code (Opus 4.6).

| Metric | Before | After |
|--------|--------|-------|
| Total files | 3,674 | ~1,000 |
| Files with frontmatter | 0 | All |
| Duplicate files | 2,751 | 0 |
| MOCs (Map of Content) | 0 | 5 |
| Plugins (configured) | 0 | 10 |
| Templates | 0 | 6 |

---

## Why Claude Code?

Obsidian has a rich ecosystem of community plugins. But bulk-inserting frontmatter into 3,674 files, tagging based on folder structure, detecting and removing duplicates, and batch-editing plugin settings in JSON is not feasible through GUI operations alone.

With Claude Code, I could drive all of this from the shell:

- **Generate and run Python scripts**: Write classification logic in Python and execute immediately
- **Per-file content judgment**: Read 100+ files one by one in mixed folders and classify them
- **JSON editing of plugin settings**: Batch-update configurations for 10 plugins
- **Rapid iteration**: Fix a failing script and re-run instantly

In short, **"applying a mix of rule-based and judgment-based processing to a large number of files"** is exactly where Claude Code excels.

---

## Phase 1: Bulk Frontmatter Insertion

### Approach

I had Claude Code generate and run a Python script to insert frontmatter with the following structure into 3,491 Markdown files:

```yaml
---
category: tech        # tech / personal / creative / reference
type: fleeting        # fleeting / literature / permanent / moc
status: draft         # draft / review / done
tags:
  - journal
  - reflection
source: evernote      # evernote / apple-notes / apple-journal
date: "2020-01-15"
---
```

I defined folder-to-tag mappings for 26 folders, and `bulk_frontmatter.py` processed all 3,491 files with zero errors.

### Gotcha: macOS NFD/NFC Issue

Files exported from Apple Notes had mysterious filename matching failures. The cause was macOS filesystem's **NFD (Normalization Form D)**.

```python
# macOS filesystem stores filenames in NFD
# Python string literals are NFC
# → They don't match

import unicodedata

# Solution: Normalize to NFC before comparison
normalized = unicodedata.normalize("NFC", filename)
```

If you're writing Python scripts that handle non-ASCII filenames on macOS, `unicodedata.normalize("NFC")` is essential. This applies to any file operation, not just Obsidian.

---

## Phase 2: Removing Unnecessary Files

### Duplicate Files: 2,751 Deleted

Evernote exports generate massive numbers of duplicate files following the `filename 2.md` pattern. I detected them with regex, verified diffs against originals, and deleted them.

### Thin Files: 1,196 Deleted

I detected and deleted files with extremely low character counts (50 characters or fewer, stats-only tables, etc.). However, thresholds varied by folder — journal folders were excluded since even short entries have value.

### Web Clip Separation: 1,612 Archived

This was the most trial-and-error part.

**Failed Approach: Hiragana Ratio Heuristic**

I hypothesized that my own writing would have a higher hiragana ratio and tried filtering on that basis. It failed. Japanese web articles also have high hiragana ratios, causing massive misclassification.

```python
# This didn't work
def is_personal(text: str) -> bool:
    hiragana = sum(1 for c in text if '\u3040' <= c <= '\u309f')
    total = len(text)
    return hiragana / total > 0.3  # No threshold gave acceptable accuracy
```

**Successful Approach: Folder-Level Classification**

In the end, the Evernote-era folder structure was the most reliable classification criterion. Folders clearly containing my own writing (journals, reflections) were kept, while web-clip-heavy folders (Study, Lifehack, etc.) were moved to an archive wholesale.

Only mixed folders (like Inbox) required Claude Code to read and judge files individually. Out of 124 files, 47 were classified as personal writing and 77 as web clips, with high accuracy.

**Lesson: Distinguishing content origin by statistical features of natural language is difficult. Metadata (folder structure, filename patterns) is far more reliable.**

---

## Phase 3: Batch Plugin Configuration

### 10 Plugins Installed

After the vault structure settled, I installed and configured the following plugins:

| Plugin | Purpose | Configuration Highlight |
|--------|---------|------------------------|
| **Dataview** | Metadata-based queries & dashboards | JS queries & inline enabled |
| **Linter** | Auto-format frontmatter | Fixed YAML key order, duplicate tag removal |
| **Templater** | Template engine | Folder-template linking |
| **Tag Wrangler** | Bulk tag rename & merge | Organized 77 tags |
| **Calendar** | Calendar view | Japanese locale, week starts Monday |
| **Auto Note Mover** | Auto-sort new notes | Funnel to Inbox, exclude legacy folders |
| **QuickAdd** | Quick capture | 3 purpose-specific commands |
| **Graph** | Knowledge graph visualization | Color-coding by folder |
| **Smart Connections** | Semantic search & related notes | Switched to multilingual model (see below) |
| **Periodic Notes** | Daily/Weekly/Monthly notes | Template integration |

### Editing Plugin Settings with Claude Code

Obsidian stores plugin settings in `.obsidian/plugins/{plugin-name}/data.json`. Editing this JSON directly with Claude Code saves the tedium of clicking through the GUI. However, there's an important caveat.

**Don't edit settings while Obsidian is running.** Obsidian holds settings in memory, so CLI edits will be overwritten on next save. Always quit Obsidian before editing.

### Vault Root Problem

During the session, I hit an issue where plugin settings changes had zero effect. Investigation revealed that **Obsidian's vault was pointing to the parent directory**.

```text
Documents/                  ← Obsidian recognized this as vault root
├── .obsidian/              ← This config was active
└── Obsidian Vault/
    ├── .obsidian/          ← This was being ignored
    └── (actual notes)
```

Two `.obsidian` directories existed, with different configs being used. I merged into the correct one to fix it.

**Lesson: When plugin settings won't take effect, first run `find . -name ".obsidian" -type d` to verify the `.obsidian` location.**

### Smart Connections: Multilingual Support

Smart Connections displays related notes via semantic search. The default embedding model `TaylorAI/bge-micro-v2` is English-focused and performs poorly on non-English vaults.

Making matters worse, **this plugin's settings are stored not in `data.json` but in `.smart-env/smart_env.json`**. This is barely documented — I found it by reading `main.js`.

```json
// .smart-env/smart_env.json
{
  "smart_sources": {
    "embed_model": {
      "model_key": "Xenova/multilingual-e5-small"
    }
  }
}
```

After switching to `Xenova/multilingual-e5-small` (multilingual) and clearing the embedding data for re-indexing, related notes started showing accurate connections.

**Lesson: Obsidian plugin settings aren't always in `data.json`. When settings don't take effect, look outside `.obsidian/plugins/{plugin}/` as well.**

---

## MOCs and Dashboard

To make use of the organized notes, I created 5 MOCs (Maps of Content) and a Dataview dashboard.

A MOC is a file that lists notes for a specific theme using a combination of manual links and Dataview queries. For example:

```dataview
TABLE date, status
FROM #books
SORT date DESC
```

The dashboard displays note counts by status, recently updated notes, and uncategorized notes. Enabling Dataview's JS queries allows more flexible aggregation.

---

## Tips for Using Claude Code with Obsidian

### 1. File Operations on iCloud Work Fine

I ran Claude Code against an Obsidian Vault on iCloud Drive — reading/writing `.md` files and executing Python scripts — with no sync issues. However, plugin settings (under `.obsidian/`) should only be edited after quitting Obsidian.

### 2. "Generate and Execute" Python Scripts Is Fastest

Having Claude Code read all 3,674 files directly is unrealistic in terms of tokens. Instead, the most efficient workflow was "generate a Python script → run it → check results → fix → re-run." I used 5 scripts total:

| Script | Purpose | Files Processed |
|--------|---------|----------------|
| `bulk_frontmatter.py` | Bulk frontmatter insertion | 3,491 |
| `apple_notes_folders.py` | Subfolder-based classification | 66 |
| `apple_notes_root.py` | Content-analysis-based classification | 86 |
| `vault_audit.py` | Tag distribution & gap detection | All |
| `tag_cleanup.py` | Tag merge & rename | All |

### 3. Always NFC-Normalize Non-ASCII Filenames

As mentioned, the combination of macOS + non-ASCII filenames + Python requires `unicodedata.normalize("NFC")`. NFD/NFC mismatches can occur in file searches, pattern matching, and dictionary key comparisons.

### 4. Take Backups Assuming Failure

I created a `tar.gz` backup before starting. In practice, the failed hiragana-ratio classification required restoring from backup. For bulk file operations, having a backup that enables rapid "try → fail → restore" cycles is essential.

---

## Conclusion

I completed the organization of 3,674 Obsidian Vault files in one day with Claude Code. Key technical takeaways:

1. **For bulk file processing, generating and executing Python scripts is fastest.** Don't feed all files to Claude Code — encode the logic as code
2. **Statistical heuristics are less reliable than metadata (folder structure).** Hiragana-ratio content classification failed
3. **Direct JSON editing of plugin settings is powerful, but do it after quitting Obsidian.** Watch out for vault root issues and non-standard settings files
4. **For Smart Connections multilingual support, switch to `multilingual-e5-small`.** Settings live in `.smart-env/smart_env.json`
5. **NFD/NFC normalization is essential for non-ASCII filenames on macOS**

Claude Code isn't just a tool for writing code. It works for any "organization" task on the filesystem. Its strength lies in combining rule-based batch processing with content-based individual judgment.
