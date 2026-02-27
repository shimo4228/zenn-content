<!-- origin: original -->
# Zenn Format Skill

**Purpose:** Zenn 記事の形式・記法・テンプレートのリファレンス。
文体・タイトル設計は [zenn-writer](../zenn-writer/SKILL.md) を参照。

---

## Zenn Article Format

### Frontmatter Template

Every Zenn article MUST start with YAML frontmatter:

```markdown
---
title: "Your Article Title (50-60 characters optimal)"
emoji: "📚"
type: "tech"  # "tech" or "idea"
topics: ["claude", "anki", "ai", "python", "tdd"]  # 1-5 tags, lowercase
published: true  # false for draft
---

# Article content starts here
```

### Frontmatter Fields

| Field | Required | Description | Examples |
|-------|----------|-------------|----------|
| `title` | ✅ | Article title (50-60 chars optimal, 60 max) | "TDD で作る pdf2anki の品質保証パイプライン" |
| `emoji` | ✅ | Single emoji representing the article | "📚", "🔬", "🤖", "⚡" |
| `type` | ✅ | Article type | `"tech"` (technical) or `"idea"` (opinion/essay) |
| `topics` | ✅ | 1-5 tags (lowercase, no spaces) | `["claude", "anki", "python", "tdd"]` |
| `published` | ✅ | Publication status | `true` (public) or `false` (draft) |

### Emoji Selection

| Theme | Recommended Emojis |
|-------|-------------------|
| AI/LLM | 🤖, 🧠, 💬, ✨ |
| Anki/Learning | 📚, 🎓, 🔖, 📝 |
| Testing/Quality | 🔬, ✅, 🧪, 🎯 |
| Development | ⚙️, 🛠️, 💻, 🏗️ |
| Performance | ⚡, 🚀, 📊, 🔥 |
| Architecture | 🏛️, 🗺️, 🧩, 🌐 |

### Topics (Tags)

**Common tags:**
- `claude` - Claude AI / Claude Code
- `anki` - Anki flashcard system
- `ai` - General AI topics
- `python` - Python programming
- `tdd` - Test-Driven Development
- `cli` - Command-line tools
- `automation` - Workflow automation

**Tag guidelines:**
- Use 3-5 tags per article (3-4 optimal)
- Start with most specific tags
- Include language/framework if relevant (`python`, `typescript`)
- Use established tags when possible (check Zenn for popular tags)

---

## Article Structure Patterns

### Pattern 1: Problem-Solution (Technical Deep Dive)

```markdown
# 問題: [具体的な問題]
## 背景: なぜこれが重要か
## 実装: [解決策]
### テストファースト (TDD)
### 実装詳細
## 結果: [数値で示す改善]
## 学び: [個人的な洞察]
## まとめ
```

### Pattern 2: Design Philosophy (Architectural)

```markdown
# なぜ [設計方針] か
## 従来のアプローチとその限界
## [設計方針] とは何か
### 原則 1-3
## 実装例
## トレードオフと代替案
## 結論: いつこのアプローチを選ぶべきか
```

### Pattern 3: Development Journey (SpecStory-based)

```markdown
# Day 1: [フェーズ 1]
## 失敗から学ぶ
# Day 2: [フェーズ 2]
## 予期せぬ問題
# Day 3: [フェーズ 3]
## 結果: [数値データ]
## 振り返り: N つの教訓
```

---

## Zenn Markdown Syntax

### Code Blocks

Always specify language for syntax highlighting:

````markdown
```python
def _tokenize(text: str) -> set[str]:
    """Tokenize text for similarity comparison."""
    tokens = re.split(r"[\s　、。？?！!,.\-:：]+", text)
    return {t for t in tokens if len(t) >= 2}
```
````

Supported languages: `python`, `typescript`, `javascript`, `bash`, `json`, `yaml`, `markdown`, `diff`

### File Path References

Include file paths for code snippets:

```markdown
```python
# src/pdf2anki/quality.py:322-329
def _tokenize(text: str) -> set[str]:
    ...
```
```

### Images

Store images in `/images/` directory:

```markdown
![Tokenization flow diagram](/images/tokenization-flow.png)
```

**Image guidelines:**
- Use descriptive filenames: `architecture-diagram.png` not `img1.png`
- Sanitize screenshots: no personal paths, no API keys
- Optimize for web: compress images, use PNG for diagrams, JPG for photos

### Links

```markdown
# External links
[Anki公式サイト](https://apps.ankiweb.net/)

# Internal links (within Zenn)
[前回の記事](/articles/previous-article-slug)

# Footnotes
テキスト[^1]

[^1]: 補足説明
```

### Message Boxes

```markdown
:::message
重要な情報やヒント
:::

:::message alert
警告や注意事項
:::

:::details 折りたたみ可能なセクション
詳細情報をここに
:::
```

### Tables

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
```

---

## Code Embedding Best Practices

### Minimal Code Snippets

Show **only what's needed** to illustrate the point:

**Good:**
```python
# Show only the relevant function
def _tokenize(text: str) -> set[str]:
    tokens = re.split(r"[\s　、。？?！!,.\-:：]+", text)
    return {t for t in tokens if len(t) >= 2}
```

**Bad:**
```python
# Showing entire file including unrelated imports and functions
from __future__ import annotations
import json
import logging
# ... 100+ lines of irrelevant code
```

### Include Context

```python
# BAD: No context
tokens = re.split(r"[\s　、。？?！!,.\-:：]+", text)

# GOOD: With context
# Split on whitespace and common Japanese/English punctuation
tokens = re.split(r"[\s　、。？?！!,.\-:：]+", text)
```

### Show Before/After

For refactoring or improvements, show both versions side by side.

---

## Publishing Workflow

1. **Draft** article in `articles/` directory
2. **Preview** locally: `npm run preview`
3. **Lint** for style: `npm run lint`
4. **Review** with editor agent
5. **Human polish** - Add personal insights
6. **Security check** - No API keys, no personal paths
7. **Publish** - Set `published: true` and push to GitHub
8. **Sync** with Zenn (automatic via GitHub integration)

---

## Related Resources

- [CLAUDE.md](../../CLAUDE.md) - Writing guidelines and content standards
- [Editor Agent](../../.claude/agents/editor.md) - Technical review criteria
- [Zenn公式ドキュメント](https://zenn.dev/zenn/articles/markdown-guide) - Markdown syntax guide
