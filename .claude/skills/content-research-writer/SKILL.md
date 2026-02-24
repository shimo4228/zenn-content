---
name: content-research-writer
description: Assists in writing high-quality content by conducting research, adding citations, improving hooks, iterating on outlines, and providing real-time feedback on each section. Transforms your writing process from solo effort to collaborative partnership.
origin: ComposioHQ/awesome-claude-skills
---

# Content Research Writer

Writing partner for research, outlining, drafting, and refining content while maintaining your unique voice.

## When to Use

- Writing Zenn articles, blog posts, or technical tutorials
- Creating content from real experiences (dev logs, tool comparisons, workflow changes)
- Researching and citing external sources
- Improving hooks and introductions
- Getting section-by-section feedback while writing

## What This Skill Does

1. **Collaborative Outlining** — Structure ideas into coherent outlines with research gaps identified
2. **Research Assistance** — Find relevant information and add citations
3. **Hook Improvement** — Strengthen openings with bold statement / question / story options
4. **Section Feedback** — Review clarity, flow, evidence, and style for each section
5. **Voice Preservation** — Maintain your tone; suggest rather than override
6. **Citation Management** — Inline, numbered, or footnote style
7. **Iterative Refinement** — Multiple draft passes

## Instructions

1. **Understand the project** — Ask: topic, audience, length, goal, style, existing sources
2. **Collaborative outline** — Structure with Hook → Intro → Sections → Conclusion + Research To-Do list
3. **Research** — Search for facts, quotes, data; cite as `[n] Author. (Year). "Title". Publication.`
4. **Improve hooks** — Offer 3 options: bold statement, question, or personal story
5. **Section feedback** — Review: What Works / Suggestions (Clarity, Flow, Evidence, Style) / Line Edits
6. **Preserve voice** — Read existing samples first; periodically ask "Does this sound like you?"
7. **Citations** — Maintain running reference list; match user's preferred format (inline / numbered / footnote)
8. **Final review** — Assess structure, content quality, readability; pre-publish checklist

## Zenn Article Workflow (Context-Driven)

実体験ベースの技術記事や複数技術の組み合わせ記事を書く場合、以下のフローが効果的。

### Phase 1: 並列リサーチ（3エージェント同時）

Task tool で researcher エージェントを**並列起動**:

1. **技術A単体**: 対象技術の機能・特徴・価格
2. **技術B単体**: 組み合わせ先の技術詳細
3. **組み合わせ**: A×B の既存記事・コミュニティ反応・差別化ポイント

### Phase 2: ユーザー実体験の取り込み

AI 会話ログ（Gemini 等との対話）を構造化:

- つまずきポイントを表形式（#, 問題, 原因, 解決）に整理
- 会話フローを時系列でマッピング
- 記事の「オチ」になる気づきを特定

### Phase 3: コンテキストファイル保存

`drafts/article-context_<topic>-<date>.md` に以下を構造化:

1. 記事企画（仮タイトル案、想定読者、核心メッセージ、構成案）
2. 実体験タイムライン
3. 技術コンテキスト
4. 差別化ポイント（既存記事との比較）
5. リサーチ結果（要点のみ、参考記事リスト）

### Phase 4: ドラフト生成

既存記事を 2-3 本読んでフォーマット・トーンを把握した上で:

- 一人称ナラティブ（「私は〜した」）
- AI 会話を対話形式で引用
- つまずきを正直に記録
- 前回記事からの繋がりを意識
- Zenn frontmatter 付き
