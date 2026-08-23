---
name: zenn-format
description: Zenn 記事の frontmatter・記法・テンプレートの正本。emoji/topics 選定、Markdown 記法、コード埋め込みのベストプラクティスを扱う。文体・執筆プロセスは扱わない（zenn-practical-writing / zenn-idea-voice を参照）。
user-invocable: true
origin: shimo4228
---

# Zenn Format Skill

**Purpose:** Zenn 記事の形式・記法・テンプレートのリファレンス。
文体・執筆プロセスは [zenn-practical-writing](../zenn-practical-writing/SKILL.md) が正本（任意の personality flavor は [zenn-idea-voice](../zenn-idea-voice/SKILL.md)）。

---

## Zenn Article Format

### Frontmatter Template

Every Zenn article MUST start with YAML frontmatter:

```markdown
---
title: "Your Article Title"  # 文字数は .claude/rules/zenn-writing.md が正本
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
| `title` | ✅ | Article title（文字数上限の正本: `.claude/rules/zenn-writing.md`「タイトル文字数上限」） | "TDD で作る pdf2anki の品質保証パイプライン" |
| `emoji` | ✅ | Single emoji representing the article | "📚", "🔬", "🤖", "⚡" |
| `type` | ✅ | Article type | `"tech"` (technical) or `"idea"` (opinion/essay) |
| `topics` | ✅ | 1-5 tags (lowercase, no spaces) | `["claude", "anki", "python", "tdd"]` |
| `published` | ✅ | Publication status | `true` (public) or `false` (draft) |
| `published_at` | **Required when `published: true`** | Scheduled publish time (Zenn-specific)。公開記事で欠けていると `scripts/generate_article_index.py` が `ValueError` を投げ索引生成が止まる（ADR-0009）。フォーマットと罠: `.claude/rules/zenn-writing.md` | `2026-04-15 07:00` (JST) |

### Emoji Selection

> emoji・topics の選定基準は**このスキルが正本**（`seo-optimizer` は提案フローのみ持ち、基準はここに defer する）。

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
- `python` - Python programming
- `tdd` - Test-Driven Development
- `cli` - Command-line tools
- `automation` - Workflow automation

**Tag guidelines:**
- **上限の5個まで使い切る**（3-4個に留めない）。5個埋まる具体性があるなら埋める
- 最も具体的なタグから優先する
- 言語・フレームワークが関係するなら含める（`python`, `typescript`）
- **定着しているか実際に確認する**（`https://zenn.dev/topics/<tag>` を確認し、記事数0や存在しないタグを弾く）
- **記事数が多すぎる汎用タグより、記事の核に近いニッチなタグを優先する**（例: 記事の主題が「ハーネスへの組み込み」なら、母数の大きい `openai`（数千記事）より的を絞った `harness`（数十〜百記事）の方が、対象読者に届きやすく埋もれにくい）。定着している（0記事ではない）ことは要件だが、記事数が多いことは優先理由にならない
- **`ai` / `llm` のような一般名すぎるタグは単独で使わない**（検索性・差別化に寄与しない）。同じ概念を指すならより具体的な語（製品名・技術名・`skills` 等の機能カテゴリ）に置き換える

---

## Article Structure Patterns

> **2026-08-23 に削除。** 記事構成の正本は `zenn-practical-writing`「実用記事の構成テンプレート」。
> 本スキルは記法・frontmatter だけを扱い、執筆プロセスには介入しない（冒頭の宣言どおり）。
> 旧 3 パターンは実用軸の既定構成（一瞬でわかる → 掴み → 緊張 → 解決 → Higher Ground）と
> 整合せず、Pattern 1 の `## 背景` は warm-up fluff として禁止されている側だった。


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

# Internal links (within Zenn) — フル URL 必須
# 相対パス（/articles/xxx）は Zenn 上で正しく解決されない（.claude/rules/zenn-writing.md 参照）
[前回の記事](https://zenn.dev/shimo4228/articles/previous-article-slug)

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

公開前チェック（レビュー→セキュリティ→frontmatter→published_at→スケジュール→クロスポスト→push）の正本は [publish-article](../publish-article/SKILL.md)。ここでは再掲しない。

---

## Related Resources

- [CLAUDE.md](../../../CLAUDE.md) - Writing guidelines and content standards
- `~/.claude/agents/editor.md` - Technical review criteria（グローバル agent。プロジェクト外のため相対リンク不可）
- [Zenn公式ドキュメント](https://zenn.dev/zenn/articles/markdown-guide) - Markdown syntax guide
