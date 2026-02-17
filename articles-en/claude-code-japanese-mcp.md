---
title: "Using a Japanese Text Analysis MCP Server with Claude Code -- kuromoji.js"
emoji: "🇯🇵"
type: "tech"
topics: ["claudecode", "mcp", "nlp", "japanese"]
published: true
---

## The Problem

I asked Claude Code "how many characters is this article?" and got back "about 2,800 characters." The actual count was 3,200. LLMs cannot accurately handle Japanese token boundaries, so the answer is always an estimate.

When writing Zenn articles with Claude Code, I frequently need accurate character counts and readability metrics. In English, you can just count words. Japanese has no spaces between words, so morphological analysis is required.

By connecting a Japanese text analysis tool as an MCP (Model Context Protocol) server, you can run text analysis directly from within a Claude Code conversation.

## MCP Server Configuration

Add a key to `mcpServers` in `~/.claude.json`.

:::message
`~/.claude.json` is a file managed automatically by Claude Code. **Do not overwrite the entire file.** Edit it by adding a key to the existing `mcpServers` object while preserving the rest of the content.
<!-- textlint-disable ja-technical-writing/ja-no-mixed-period -->
:::
<!-- textlint-enable ja-technical-writing/ja-no-mixed-period -->

```json
{
  "mcpServers": {
    "JapaneseTextAnalyzer": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "github:Mistizz/mcp-JapaneseTextAnalyzer"]
    }
  }
}
```

The npm package is downloaded automatically on first launch. kuromoji.js (the morphological analysis engine) is bundled, so no additional dictionary installation is needed.

:::message
Because it installs directly from a GitHub repository, `npm audit` security checks do not apply. For production use, pinning to a specific commit hash is recommended.
<!-- textlint-disable ja-technical-writing/ja-no-mixed-period -->
:::
<!-- textlint-enable ja-technical-writing/ja-no-mixed-period -->

## What It Can Do

The tools fall into two categories. **File-based tools** (`count_chars`, `count_words`, `analyze_file`) take a file path and analyze it. **Inline text tools** (`count_clipboard_chars`, `count_clipboard_words`, `analyze_text`) take text directly.

> The output examples below are illustrative. Actual values will vary depending on the article content.

### Character Count

Measures the character count of a file or text. The count excludes spaces and newlines.

```text
me: How many characters is this article?
Claude Code: [runs JapaneseTextAnalyzer.count_chars]
→ 2,556 characters (excluding newlines and spaces)
```

### Word Count

Measures word count using morphological analysis via kuromoji.js.

```text
me: What's the word count of this article?
Claude Code: [runs JapaneseTextAnalyzer.count_words]
→ 850 words
```

### Text Analysis

Quantitatively evaluates part-of-speech ratios, vocabulary diversity, and sentence complexity.

```text
me: Analyze the readability of this paragraph.
Claude Code: [runs JapaneseTextAnalyzer.analyze_text]
→ Nouns: 35%, Verbs: 18%, Particles: 25%
→ Average sentence length: 45 characters
→ Vocabulary diversity: 0.72
```

## Practical Use Cases

### Checking Character Count While Writing

Zenn articles read best in the 2,000 to 4,000 character range. You can check the count mid-writing to adjust the length.

```text
me: Check the character count of articles/claude-code-auto-memory.md
Claude Code: 2,556 characters. That's a good length.
```

### Pre-Publication Quality Check

Use `analyze_text` to check sentence complexity and part-of-speech balance. If nouns dominate, the explanation may be lacking -- add more verbs to provide concrete steps.

### Analyzing Clipboard Text

You can also analyze text that has not been saved to a file. Pass it directly to `count_clipboard_chars` or `analyze_text`.

## Why an MCP Server?

Claude Code itself can count characters, but morphological analysis of Japanese is not something LLMs do well. kuromoji.js with its dictionary-based analysis is more accurate.

The benefits of connecting it as an MCP server:

- Analyze text without leaving the Claude Code conversation flow
- Just pass a file path and it reads and analyzes the file automatically
- Claude Code can interpret the morphological analysis results and offer improvement suggestions

## Setup Tips

**Put it in the global config**: Adding it to `~/.claude.json` makes it available across all projects. Japanese text analysis is not project-specific, so there is no reason to confine it to a single project's config.

**First launch takes time**: `npx -y` triggers package download and kuromoji.js dictionary loading on the first run. This can take 10 to 15 seconds depending on your environment. Subsequent runs use the cache and respond in a few seconds.

## Summary

- Connect kuromoji.js Japanese text analysis to Claude Code via an MCP server
- Character count, word count, part-of-speech analysis, and readability evaluation all happen within the conversation
- Just add the config to `~/.claude.json` and it is available from every project
- Get accurate, dictionary-based analysis results instead of relying on LLM estimation

As a next step, try building a workflow where Claude Code takes the analysis results and generates improvement suggestions for the article.
