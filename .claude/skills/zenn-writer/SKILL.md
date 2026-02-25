<!-- origin: original -->
# Zenn Writer Skill

**Purpose:** Provide knowledge and templates for writing high-quality Zenn articles following pdf2anki ecosystem conventions.

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

### Title Guidelines

#### 基本ルール

- **Length:** メインタイトル40文字以内。サブタイトルは ── で区切って別途
- **Be specific:** "Claude-Native 設計で PDF から Anki カードを自動生成" (good) vs "AI でカード作成" (too vague)
- **Include key terms:** Mention main technologies (Claude, Anki, TDD, etc.)
- **Avoid empty clickbait:** No "必見！", "超簡単！", "たった3分で"（根拠のない煽りはNG）
- **Use natural Japanese:** Avoid overly formal or unnatural phrasing
- **感情語はOK:** 「地獄」「壊す」「棄却」など、記事内容に裏付けのある感情語は積極的に使う

#### タイトル設計7つのルール

1. **感情を動かす動詞を入れる** — 「〜した」→「〜したら」「〜が壊れた」「〜を捨てた」
2. **具体的な数値を1つ入れる** — **身近な単位**で驚きを伝える（9倍 > 900%、0行 > 不要）
3. **メインタイトル40文字以内** — サブタイトルは ── で区切る
4. **2パターン以上を複合する** — 下記9パターンから選択
5. **数字を前置し感情語と組み合わせる** — 「3,674ファイルのObsidian地獄」
6. **学びの要素を残す** — 数字だけが主役にならないよう注意。「棄却」「教訓」など
7. **タイトル案を3つ出して比較する** — 必ず複数案を検討してから決定

#### タイトル9パターン

| # | パターン | テンプレート | 例 |
|---|---------|-------------|-----|
| 1 | 挑発/断定型 | 「〇〇の真価は△△ではない」 | Claude Code の真価はコード生成ではない |
| 2 | 網羅型 | 「〇〇 N選」「完全ガイド」 | Claude Code 設定10選 |
| 3 | チェックリスト型 | 「〇〇する前に確認すべきこと」 | LLM出力を信じる前のチェックリスト |
| 4 | 数値型 | 「N倍」「N件」「0行で」 | 最強モデルで9倍遅くなった |
| 5 | 仮定/結果型 | 「〇〇したら△△になった」 | 片付けさせたら1日で終わった |
| 6 | 内幕公開型 | 「〇〇の裏側」「全貌」 | 執筆環境の全貌 |
| 7 | フロー追跡型 | 「N日間の記録」「1ヶ月の試行錯誤」 | 2日間壊し続けた記録 |
| 8 | OSS公開型 | 「〇〇を作って公開した」 | 〇〇をOSSで公開した |
| 9 | 暗黙知言語化型 | 「〇〇が無意識にやっていること」 | LLMの出力は信用するな |

**複合の例:**
- 数値型 + 仮定/結果型: 「最強モデルで司令塔を組んだら9倍遅くなった」
- 網羅型 + フロー追跡型: 「Claude Code 1ヶ月で効いた設定10選」
- 挑発/断定型 + 内幕公開型: 「Claude Code の真価はコード生成ではない」

#### タイトル作成フロー

1. 記事の核心（一番伝えたいこと）を1文で書く
2. 9パターンから2つ以上を選び、組み合わせ候補を3つ作る
3. 各候補を以下でチェック:
   - [ ] 40文字以内か
   - [ ] 数値が1つ以上入っているか
   - [ ] 感情を動かす動詞があるか
   - [ ] 記事内容の裏付けがあるか（空の煽りでないか）
4. 最も「クリックしたら何が得られるか」が明確な案を選ぶ

**Good examples:**
- "3,674ファイルのObsidian地獄をClaude Codeに1日で片付けさせた"
- "最強モデルで司令塔を組んだら9倍遅くなった"
- "Pythonコード0行でAIリサーチを毎朝自動化した"

**Bad examples:**
- "AI で Anki カード作成" (too vague, no emotion, no number)
- "必見！Claude を使った最強の自動化ツール" (empty clickbait, no evidence)
- "Claude Code で Obsidian Vault 3,674ファイルを一括整理した" (事実描写型のみ、感情なし)

### Emoji Selection

Choose emojis that represent the article's main theme:

| Theme | Recommended Emojis |
|-------|-------------------|
| AI/LLM | 🤖, 🧠, 💬, ✨ |
| Anki/Learning | 📚, 🎓, 🔖, 📝 |
| Testing/Quality | 🔬, ✅, 🧪, 🎯 |
| Development | ⚙️, 🛠️, 💻, 🏗️ |
| Performance | ⚡, 🚀, 📊, 🔥 |
| Architecture | 🏛️, 🗺️, 🧩, 🌐 |

### Topics (Tags)

Use consistent, lowercase tags across articles:

**Common tags for pdf2anki ecosystem:**
- `claude` - Claude AI / Claude Code
- `anki` - Anki flashcard system
- `ai` - General AI topics
- `python` - Python programming
- `tdd` - Test-Driven Development
- `cli` - Command-line tools
- `automation` - Workflow automation
- `pdf` - PDF processing
- `nlp` - Natural Language Processing
- `testing` - Software testing

**Tag guidelines:**
- Use 3-5 tags per article (3-4 optimal)
- Start with most specific tags
- Include language/framework if relevant (`python`, `typescript`)
- Use established tags when possible (check Zenn for popular tags)

---

## Article Structure Patterns

### Pattern 1: Problem-Solution (Technical Deep Dive)

Use this pattern for explaining technical challenges and solutions.

```markdown
---
title: "日本語トークン化の落とし穴と CJK バイグラム実装"
emoji: "🔬"
type: "tech"
topics: ["python", "nlp", "testing", "tdd"]
published: true
---

# 問題: 日本語テキストの重複検出が機能しない

[Hook: Specific problem that occurred]

## 背景: なぜトークン化が重要か

[Context: Why this problem matters]

## 実装: CJK バイグラムによる解決

[Solution: How you solved it with code examples]

### テストファースト (TDD)

[Show the test-first approach]

### 実装詳細

[Implementation details with code]

## 結果: 精度が 30% から 92% に改善

[Results: Measurable impact]

## 学び: 言語特性を考慮した設計の重要性

[Lessons learned: Personal insights]

## まとめ

[Conclusion: Key takeaways and next steps]
```

### Pattern 2: Design Philosophy (Architectural)

Use this pattern for explaining design decisions and architecture.

```markdown
---
title: "Claude-Native 設計で実現する半自動開発フロー"
emoji: "🏛️"
type: "tech"
topics: ["claude", "architecture", "ai", "automation"]
published: true
---

# なぜ Claude-Native か

[Hook: The "why" behind the design choice]

## 従来のアプローチとその限界

[Context: What alternatives exist and why they fall short]

## Claude-Native とは何か

[Definition: Explain the concept clearly]

### 原則 1: Immutability (不変性)

[Principle explanation with examples]

### 原則 2: CLI-First (コマンドライン優先)

[Principle explanation with examples]

### 原則 3: Test-Driven Development

[Principle explanation with examples]

## 実装例: pdf2anki のアーキテクチャ

[Concrete implementation in the actual project]

## トレードオフと代替案

[Honest discussion of trade-offs]

## 結論: いつ Claude-Native を選ぶべきか

[Conclusion: When to use this approach]
```

### Pattern 3: Development Journey (SpecStory-based)

Use this pattern for narrative-driven articles based on real development sessions.

```markdown
---
title: "TDD で品質パイプラインを構築した 3 日間の記録"
emoji: "📝"
type: "tech"
topics: ["tdd", "python", "claude", "testing"]
published: true
---

# Day 1: テスト設計と RED フェーズ

[Narrative: What happened on day 1]

## 失敗から学ぶ: 最初のアプローチが機能しなかった理由

[Honest account of failures]

# Day 2: GREEN フェーズと実装

[Narrative: Implementation journey]

## 予期せぬ問題: 日本語トークン化の落とし穴

[Challenges encountered]

# Day 3: IMPROVE フェーズとリファクタリング

[Narrative: Refinement]

## 結果: カバレッジ 85%、品質スコア平均 0.82

[Results with data]

## 振り返り: 3 日間で得た 5 つの教訓

[Personal insights and lessons]
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
| Data 4   | Data 5   | Data 6   |
```

---

## SEO Best Practices

### Title Optimization

- Include primary keyword (Claude, Anki, TDD, etc.)
- Use natural Japanese phrasing
- 50-60 characters optimal for search results display

### Topic Selection

- Use 3-5 topics (tags)
- Include at least one high-traffic tag (`python`, `ai`, `claude`)
- Include specific tags for targeting (`anki`, `tdd`)

### Introduction (First 200 characters)

- Hook reader with a specific problem or insight
- Include main keywords naturally
- Set clear expectations for the article

**Good example:**
> "pdf2anki の開発で日本語テキストの重複検出が全く機能しない問題に直面しました。原因は、スペースのない日本語テキストを想定していないトークン化ロジックでした。この記事では、CJK バイグラム実装による解決方法を TDD アプローチで紹介します。"

**Bad example:**
> "今回は Anki カード作成の自動化について書きます。便利なツールを作りました。"

### Internal Linking

- Link to related articles when publishing multiple articles
- Use descriptive anchor text (not "こちら")

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
import re
from typing import Any
import anthropic
from pydantic import BaseModel, ValidationError
...
# 100+ lines of irrelevant code
```

### Include Context

Add comments for clarity:

```python
# BAD: No context
tokens = re.split(r"[\s　、。？?！!,.\-:：]+", text)

# GOOD: With context
# Split on whitespace and common Japanese/English punctuation
tokens = re.split(r"[\s　、。？?！!,.\-:：]+", text)
```

### Show Before/After

For refactoring or improvements, show both versions:

```python
# Before: Simple word splitting (fails for Japanese)
def _tokenize(text: str) -> set[str]:
    tokens = re.split(r"[\s]+", text)
    return set(tokens)

# After: CJK bigrams (works for Japanese)
def _tokenize(text: str) -> set[str]:
    tokens = re.split(r"[\s　、。？?！!,.\-:：]+", text)
    result = {t for t in tokens if len(t) >= 2}

    cjk_chars = _CJK_RE.findall(text)
    if len(cjk_chars) >= 2:
        for i in range(len(cjk_chars) - 1):
            result.add(cjk_chars[i] + cjk_chars[i + 1])

    return result
```

---

## Common Mistakes to Avoid

### 1. Overly Long Titles

❌ "PDF ファイルから Anki カードを自動生成する Claude ベースのツールを作った話"
✅ "Claude-Native 設計で PDF から Anki カードを自動生成"

### 2. Generic Introductions

❌ "AI 技術の発展により、様々なタスクの自動化が可能になってきました。"
✅ "pdf2anki の開発で、日本語テキストの重複検出が 30% の精度しかない問題に直面しました。"

### 3. Missing Code Context

❌ Showing code without explanation
✅ Show code with file path, explanation of what it does, and why it matters

### 4. No Personal Insights

❌ "テストは重要です。TDD を使いましょう。"
✅ "最初はテストなしで実装を進めましたが、リファクタリング時に予期せぬバグが多発。TDD に切り替えたところ、バグ発生率が 70% 減少しました。"

### 5. Unsanitized Screenshots

❌ Screenshots with `/Users/shimomoto/MyAI_Lab/` visible
✅ Screenshots with paths anonymized or cropped out

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
- [Security Checklist](../../../Anki-QA/docs/security-checklist.md) - Pre-publication security checks

---

**Quick Reference Card:**

```
✅ DO:
- Use 50-60 char titles
- Include file paths in code snippets
- Show before/after for refactoring
- Add personal insights
- Be specific and concrete
- Flag AI slop

❌ DON'T:
- Use clickbait titles
- Show code without context
- Use generic AI phrases
- Skip security checks
- Over-explain basics
- Leak personal info
```
