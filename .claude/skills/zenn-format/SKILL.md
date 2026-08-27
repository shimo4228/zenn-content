---
name: zenn-format
description: Zenn記事のfrontmatter、emoji/topics、Zenn固有Markdown記法の正本。Use when — Zenn原稿を作成・検証するとき、本文凍結後にtopics/emoji候補を提示するとき。NOT for — 執筆構成・voice・タイトル判定・公開可否・Dev.to/note/Substack形式。
user-invocable: true
origin: shimo4228
---

# Zenn Format Skill

文体と執筆プロセスはglobal `writing-ecosystem`、titleはglobal `title-reviewer`、channel値は
`.claude/rules/publishing-channels.md`、公開操作は`publish-article`が持つ。

## Frontmatter

draft template:

```markdown
---
title: "Your Article Title"
emoji: "📚"
type: "tech"
topics: ["claude", "ai", "python"]
published: false
---

## 最初の見出し
```

本文見出しはH2から始める。公開時は`published: true`と`published_at`を設定する。

| Field | Requirement |
|---|---|
| `title` | required。文字数はchannel contract |
| `emoji` | required、single emoji |
| `type` | required、`tech`または`idea`。voice分岐には使わない |
| `topics` | required、lowercase 1〜5件 |
| `published` | required、boolean |
| `published_at` | `published: true`でrequired。`YYYY-MM-DD HH:MM` JST |

## Emoji and topics

emojiは記事の主対象を示す一つを選ぶ。

| Theme | Candidates |
|---|---|
| AI / LLM | 🤖, 🧠, 💬 |
| Learning | 📚, 🎓, 📝 |
| Testing | 🔬, ✅, 🧪 |
| Development | ⚙️, 🛠️, 💻 |
| Performance | ⚡, 📊 |
| Architecture | 🏛️, 🧩, 🌐 |

topics:

- 1〜5件。具体性があるなら5件まで使う
- 主題に最も近い製品名・技術名を優先する
- `ai` / `llm`のような一般語だけで埋めない
- `https://zenn.dev/topics/<tag>`で実在と現在の使用を確認する
- 記事数の多さだけで選ばず、対象読者との一致を優先する

本文凍結とtitle選択の後、現在値と候補をdiffで提示する。topics / emojiはdistributionだけを
変え、本文・中心命題・見出しを書き換えない。最終選択は著者が行う。

## Zenn Markdown

### Code blocks

languageを必ず指定し、必要なら先頭commentでpathを示す。

````markdown
```python
# src/auth/session.py:88
def rotate_token(session: Session) -> Token:
    ...
```
````

### Images

```markdown
![Tokenization flow](/images/tokenization-flow.png)
```

descriptive filenameを使い、個人path・key・credentialをsanitiseする。

### Links

Zenn内部記事もfull URLを使う。

```markdown
[前回の記事](https://zenn.dev/shimo4228/articles/previous-slug)
```

### Blocks

```markdown
:::message
補足
:::

:::message alert
警告
:::

:::details 詳細
補助情報
:::
```

`details`は中心命題から外れた論点の退避先ではない。補助情報だけに使う。

## Validation and handoff

**Step 0 — 数える検査はscriptに任せる。**

```bash
npm run evidence -- articles/<slug>.md      # 構造・書式・実在・一致
npm run evidence -- articles/ --text        # 全数
npm run validate                            # Zenn frontmatter（一覧表示のみ）
```

`deviations`をfindingsへそのまま転記する。**目視で数え直さない。** `grandfathered`は検査導入前に
公開済みの記事の逸脱なので、その稿を改稿するときだけ扱う。`signals`は判定ではなく解釈の材料
（register混在、self-linkの位置、段落密度）。

検査項目の正本は`scripts/zenn_evidence.py`のmodule docstringと各`check_*`関数。ここに複製しない。
公開直前は`--online`を足して外部URLの生死も見る（既定はoffline完結）。

validation後の公開処理は`publish-article`へ渡す。

## Related

- `.claude/rules/publishing-channels.md`
- global `writing-ecosystem` / `title-reviewer`
- local `publish-article`
- [Zenn Markdown Guide](https://zenn.dev/zenn/articles/markdown-guide)
