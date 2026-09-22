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

### Tables

比較にだけ使う。列は3〜4まで、行頭の列に読者が探す語を置く。並列は箇条書き、因果は散文
（使い分けの正本は`writing-ecosystem`の「認知負荷の設計」）。

### Figures

図は内容GOの後、`writing-ecosystem`のFigure planに沿って起こす。Zennが受けるのは`/images`直下の
`.png .jpg .jpeg .gif .webp`、3MB以内。SVGは不可（Zenn公式 deploy-github-images、as-of 2026-09-22）。

1. `/eli5 <その節の主張1文>` に、形（対比 / 流れ / 階層 / 2軸）と制約を添えて呼ぶ: 1600×900の1画面、
   要素6個以内、文字は名詞句、色は2色+灰、フォントは`"Hiragino Sans", system-ui`。読者の既知物との
   比喩を持つのはhero図だけで、他の図は構造だけを描く。出力HTMLを `figures/<slug>-<what>.html` に
   保存する（共通styleは`figures/_base.css`。artifactとして公開しない）
2. repo rootで `python3 -m http.server 8765 --bind 127.0.0.1 --directory figures &` を起動し、Playwright
   MCPで `browser_resize` 1600×900 → `browser_navigate` `http://127.0.0.1:8765/<slug>-<what>.html`
   → `browser_take_screenshot`（scale css、type png、filename `images/<slug>-<what>.png`。repo root
   からの相対path）。`file:`直開きはブロックされる。撮ったら`Read`で目視し、はみ出し・重なり・
   折り返しを直して撮り直す。`ls -la images/<slug>-*.png` で3MB以内を確かめ、`pkill -f "http.server 8765"`
   でserverを止める
3. 記事側は `![<図が示すこと1文>](/images/<slug>-<what>.png)` を、その節の発見が出そろった段落の後に
   置き、直後に「この図が示すこと」を1文書く。alt textは図の文字（数値・モデル名）を含める
4. 本文を直したらHTMLを直して撮り直す。図の文字と本文の差分は`fact-checker`に渡す

mermaidは流れ図でeli5図を補うときだけ。nodeは8個まで。生成画像（ChatGPT等）を使うときは
同じ`images/`規約で、生成promptを`figures/<slug>-<what>.prompt.md`に残す。

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
