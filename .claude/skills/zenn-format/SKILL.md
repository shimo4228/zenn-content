---
name: zenn-format
description: Zenn 記事の frontmatter・記法・テンプレートの正本。emoji/topics の選定基準と、公開直前の topics・emoji 提案フロー（Distribution 層のみ、内容は変えない）、Zenn 固有の Markdown 記法（コードブロックの diff/ファイル名指定・`:::message`・埋め込み・内部リンク）を扱う。汎用の Markdown 作法は持たない。文体・執筆プロセスは扱わない（zenn-practical-writing / zenn-idea-voice を参照）。
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

> emoji・topics は**基準も提案フローもこのスキルが正本**（2026-08-23 に `seo-optimizer` を Retire し、
> 分かれていた提案フローをここへ統合 — 基準の唯一の消費者だったため。提案フローは下記「Topics / Emoji の提案フロー」）。

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

### Topics / Emoji の提案フロー

公開直前（本文凍結後、`title-eval` でタイトルを確定した後）に、既存記事の topics・emoji を
見直すときの手順。**Distribution レイヤーのみ** — 本文・冒頭文は変えない（ADR-0001、
`.claude/rules/content-integrity.md`）。

1. 現在の topics / emoji を、上の Tag guidelines と Emoji Selection に照らして評価する（違反は指摘）
2. 差し替え候補を **diff 形式**（現在 → 提案）で提示し、各項目に理由を 1 行添える
3. **最終判断は著者に委ねる** — 選択肢を提示するだけで、確定はしない

```markdown
### Topics 提案
- 現在: {current} → 提案: {proposed}
- 理由: {why}

### Emoji 提案
- 現在: {current} → 提案: {proposed}
- 理由: {why}
```

- SEO を理由にクリックベイトへ寄せない（誠実さ規約は `writing-ecosystem` の Title Conventions）
- Zenn のトレンドは変化するので、提案は参考値として扱う（`https://zenn.dev/topics/<tag>` の実地確認が優先）

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

# Internal links (within Zenn) — 規則の正本は .claude/rules/zenn-writing.md「内部リンク」
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

> **汎用の Markdown / コード埋め込み作法はここに持たない**（2026-08-23 削除）。
> 表の書き方・最小コードスニペット・前後比較の見せ方は、Claude が prompt なしで
> 適用する一般作法で、Zenn 固有の情報ではなかった。記事としての見せ方の判断は
> `zenn-practical-writing`（実用軸・低認知負荷）が正本。

## Publishing Workflow

公開前チェック（レビュー→セキュリティ→frontmatter→published_at→スケジュール→クロスポスト→push）の正本は [publish-article](../publish-article/SKILL.md)。ここでは再掲しない。

---

## Related Resources

- [CLAUDE.md](../../../CLAUDE.md) - Writing guidelines and content standards
- `~/.claude/agents/editor.md` - Technical review criteria（グローバル agent。プロジェクト外のため相対リンク不可）
- [Zenn公式ドキュメント](https://zenn.dev/zenn/articles/markdown-guide) - Markdown syntax guide
