---
name: seo-optimizer
description: Zenn 記事のタイトル・topics・emoji を Distribution レイヤーで最適化する（内容は変えない、ADR-0001）。タイトル原則・AI slop は writing-ecosystem、文字数は zenn-writing.md が正本。
user-invocable: true
origin: shimo4228
---

# SEO Optimizer Skill

**Purpose:** Zenn 記事のタイトル・topics・emoji を最適化し、関心のある読者に記事が届くようにする。
内容の改変は行わない（[ADR-0001](../../../docs/adr/0001-content-integrity-principle.md) Content Integrity 原則）。

> **タイトル規約・AI slop の正本:** `~/.claude/skills/writing-ecosystem/SKILL.md`（Zenn 固有ルールは `.claude/rules/zenn-writing.md`）

---

## Usage

```
/seo-optimizer articles/ARTICLE_NAME.md
```

---

## Optimization Flow

### Step 1: 現状分析

記事の frontmatter と冒頭 200 文字を読み取り、以下を評価する:

| 項目 | 評価基準 |
|------|---------|
| **タイトル** | 50 文字以内（60 まで許容）、キーワード含有、具体性 |
| **Topics** | 5 個使い切り、ニッチ優先（基準は `zenn-format` の Tag guidelines） |
| **Emoji** | 記事テーマとの関連性（基準は `zenn-format` の Emoji Selection） |

### Step 2: タイトル最適化（Distribution レイヤーのみ）

タイトルの**原則・誠実さ・煽り禁止・問いの形**は `~/.claude/skills/writing-ecosystem/SKILL.md` の Title Conventions が正本、**文字数上限（50-60）**は `.claude/rules/zenn-writing.md` が正本。ここでは再掲しない。

**候補生成の技法は global skill `headline-craft` が正本** — 技法カタログ（具体性・ベネフィット前置・誠実な好奇心ギャップ）と流入経路 2 軸評価（検索/フィード）はあちらの手順に従う。本スキルはそこに Zenn 固有の入力を足すだけ:

- **主要キーワードの自然な含有**（SEO 観点。語の選び直しは可、意味は変えない）
- **自チャンネル実測の参照**: memory の `article-quality.md`（品質ランク × 実測 tier、乖離パターン）を読み、候補の 2 軸判定（検索寄せ/フィード寄せ）の参考にする
- **3 候補を提示**し、各候補に headline-craft の評価ラベル（技法・流入軸）を添え、現タイトルと比較
- 最終判断はユーザーに委ねる（内容は変えない、[ADR-0001](../../../docs/adr/0001-content-integrity-principle.md)）

### Step 3: Topics 最適化

**選定基準の正本は [zenn-format](../zenn-format/SKILL.md) の Tag guidelines**（ニッチ優先・`ai`/`llm` 単独禁止・`https://zenn.dev/topics/<tag>` で定着確認・5 個使い切り）。ここでは再掲しない。

このスキルが担うのは提案フローだけ:

1. 現タグを zenn-format の基準に照らして評価する（違反があれば指摘）
2. 差し替え候補を diff 形式（現在 → 提案）で提示し、各タグに理由を 1 行添える
3. 最終判断はユーザーに委ねる

### Step 4: Emoji 最適化

**選定基準の正本は [zenn-format](../zenn-format/SKILL.md) の Emoji Selection**。ここでは再掲しない。現 emoji が記事テーマと乖離している場合のみ、候補と理由を提示する。

---

> **Note:** 冒頭文（リード）の最適化は Content Integrity 原則により廃止。著者が自然に書いた冒頭をそのまま使う。

## Output Format

```markdown
## SEO 最適化提案

### 現状
- タイトル: "{current_title}" ({n}文字)
- Topics: {current_topics}
- Emoji: {current_emoji}

### タイトル候補
1. **"{title_1}"** ({n}文字)
   - 理由: {why}
2. **"{title_2}"** ({n}文字)
   - 理由: {why}
3. **"{title_3}"** ({n}文字)
   - 理由: {why}

### Topics 提案
- 現在: {current} → 提案: {proposed}
- 理由: {why}

### Emoji 提案
- 現在: {current} → 提案: {proposed}
- 理由: {why}
```

---

## Notes

- 最終判断は**ユーザーに委ねる**（選択肢を提示するだけ）
- SEO のためにクリックベイトにならないよう注意
- Zenn のトレンドや検索傾向は変化するため、提案は参考値として扱う
