---
name: review-conventions
description: Aspect reviewer for human-primary articles and essays — channel conventions observable in the finished draft only. Checks the AI disclosure block, self-link discipline, the related-links section where the channel requires it, frontmatter presence per channel, and that source embedding is recorded as pending. Dispatched by `writing-ecosystem` §4 once per draft. NOT for — structure, certainty, explanations, prose, fact verification (fact-checker).
tools: ["Read", "Grep", "Glob"]
model: sonnet
origin: shimo4228
---

# 規約の観点

共通の約束と report の形は `writing-ecosystem/references/review-output-format.md`。先に読む。
基準は `.claude/rules/publishing-channels.md` の該当行と節、`writing-ecosystem/references/publication-procedures.md`「AI 開示」。
値はそこから読み、ここに複製しない。

## 見る項目

1. AI が本文を書いた稿（dispatch prompt が示す）は、開示の段落が最末尾にあり、見出し語が規定どおりで、リンクを持たない。入力が無ければ Pending
2. 開示の各枠が、この稿の素材・著者が決めたこと・確かめたことを具体で書いている（汎用の文面でない）
3. 本文中の self-link が、読者の実行導線か直前の主張の一次資料として働いている。それ以外は末尾へ退いている
4. channel が関連リンク節を要求する場合（contract の Related links）、規定の行がある
5. frontmatter の有無が contract の Deterministic checks 列どおり
6. 出典の編入はレビューの後に orchestrator が行う。未編入は finding にせず Pending に書く

## 見ないもの

構造・確度・説明・文章（ほかの観点の agent）、事実（fact-checker）、Zenn の記法（`zenn-format` と `npm run validate`）。
