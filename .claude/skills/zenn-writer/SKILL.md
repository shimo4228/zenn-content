---
name: zenn-writer
description: 声のルーター（歴史的参照 path 維持用）。Zenn/Dev.to の記事は tech/idea 問わず zenn-practical-writing（実用軸・ですます）で書く。genuine な思索エッセイは Substack corpus（writing-ecosystem）へ。新規に書くなら zenn-practical-writing を直接使う。
origin: original
---

# zenn-writer — 声のルーター

**このファイルは voice の入口（router）。既存の参照パスを壊さないため path だけ維持している。**

かつて zenn-writer はタイトル・Voice・AI-slop・research を自前で抱えていたが、それらは再配置された。振り分け先は以下。

## 振り分け

| 書くもの | 使うスキル |
|---|---|
| **Zenn/Dev.to の記事**（tech / idea 問わず全て） | [zenn-practical-writing](../zenn-practical-writing/SKILL.md) — 実用軸（ですます・即実用・実コード/図・低認知負荷） |
| **genuine な思索エッセイ**（だ/である × 発見調） | essay corpus（Substack）へ。`~/.claude/skills/writing-ecosystem/SKILL.md` + `substack-publishing` skill |

**Zenn/Dev.to は type（tech/idea）で声を分けない。** すべて実用軸。毒humor/刃牙 の personality は話題が合えば任意で足せる（[zenn-idea-voice](../zenn-idea-voice/SKILL.md)）。

## 共通

- **AI-slop 禁止・タイトル誠実さ・ネタ 3 軸** → `~/.claude/skills/writing-ecosystem/SKILL.md`（正本）
- **frontmatter・記法・emoji・topics** → [zenn-format](../zenn-format/SKILL.md)（正本）
- **Zenn プラットフォーム固有ルール**（文字数・:::message・投稿ペース・文体） → `.claude/rules/zenn-writing.md`

## 執筆は本体が直接行う

記事の執筆はサブエージェントに委譲せず、Claude Code 本体が `zenn-practical-writing` を参照して直接書く。

## なぜ router に縮小したか

根拠: `.claude/docs/adr/0003-zenn-practical-channel-axis.md`。Zenn/Dev.to は「読者が即座に何かわかり、すぐ手に取って使える」実用軸を独自の声として確立し、essay（Substack）や paper（`paper-ecosystem`）とチャンネル単位で分離した。
