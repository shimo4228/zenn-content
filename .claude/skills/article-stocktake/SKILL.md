---
name: article-stocktake
description: 公開済み記事の実測メトリクス（Zenn いいね / Dev.to reactions・views）を収集し、内容品質ランク（A/B/C）× 実測 tier の乖離を棚卸しして memory と ideation に還流する
user-invocable: true
origin: shimo4228
---

# Article Stocktake Skill

**Purpose:** 公開後の実測データで記事 Eval ループ（AKC の Measure phase）を回す。予測ではなく読者の実際の行動（いいね・reactions・views・フォロー）を ground truth とし、**内容品質と実測読者価値の乖離**を主シグナルとして企画・配信に還流する。

> 根拠: [ADR-0005](../../../docs/adr/0005-post-publication-eval-loop.md)（公開前の予測型エンゲージメントレビュアーは不採用）

---

## Usage

```
/article-stocktake        # 収集 → 乖離分析 → 更新提案
```

目安周期: 月次、または記事 2-3 本公開ごと。自動化はしない（人間駆動）。

---

## Process

### Step 1: 収集（code）

```bash
cd scripts && uv run python metrics_snapshot.py
```

`scripts/metrics/snapshots.jsonl` に追記される（Zenn: liked/bookmarked/comments、Dev.to: reactions/comments/views、フォロワー総数）。API 欠損は fail-soft — 片系が死んでいても続行し、警告のみ。

### Step 2: 正規化と tier 算出

最新 ts のレコードを読み、記事ごとに正規化する:

- **主指標**: Zenn `liked / 公開後日数`（古い記事が累積で有利になるのを補正）
- **補助指標**: Dev.to views・reactions（EN 側の到達）、ブックマーク（参照価値）
- 相対 tier を **上位 / 中位 / 下位** の 3 段に分ける（全公開記事内の相対評価）

**絶対スコアを出力しない**（output discipline）。「7.2/10」ではなく tier と乖離だけを提示する。

### Step 3: 乖離表の提示（主シグナル）

memory の `article-quality.md` にある内容品質ランク（A/B/C）と突合し、**乖離セルの記事のみ**列挙する:

| 乖離パターン | 示唆 | 還流先 |
|---|---|---|
| **A ランク × 実測下位** | 内容は良いが届いていない — タイトル・配信・タイミングの問題 | title-eval（タイトル）/ zenn-format（topics・emoji）/ 投稿タイミング（`.claude/rules/zenn-writing.md`「投稿ペース方針」） |
| **B/C ランク × 実測上位** | 読者需要のあるテーマ・構造 | ideation の情報源（事実として） |

一致セル（A×上位、C×下位）は正常動作なので列挙しない。各乖離記事に定性所見を 1 行添える（「タイトルが概念名のみで用途が見えない」等の具体観察）。

### Step 4: 更新提案 → 人間確認 → memory 更新

ランク・tier の更新案を提示し、**ユーザー確認後に** memory の `article-quality.md` を更新する:

- 既存の A/B/C 表に **実測 tier 列と判定日**を追加（別軸並記。ランクと混ぜない）
- 冒頭に「実測サマリ」節（届いたテーマ・構造の事実 3-5 行 + フォロワー推移 1 行）を置く — ideation Step 1 が読む前提の要約

### Step 5: 還流

- **企画へ**: ideation は Step 1 の情報源としてこのサマリを読む（推薦理由にはしない — ideation Notes の禁止条項は維持）
- **配信へ**: A×下位 記事の Distribution 改善（リタイトル等）は title-eval（タイトル判定）と zenn-format（topics・emoji）の管轄で、ユーザーが個別に判断

---

## Guardrails（Content Integrity）

- **既存記事のエンゲージメント目的リライトを提案しない**（catchify bright-line、ADR-0001）。乖離が示すのは Distribution 層（タイトル語選び・タグ・タイミング）の改善余地か、次の企画の判断材料であり、本文改変ではない
- 実測 tier を「テーマ推薦の理由」に使わない。ideation への還流は事実提示まで
- LLM による tier 判定は Step 4 の人間確認を通してのみ memory に固定される（LLM 単独の承認経路を作らない）

---

## Related

- `scripts/metrics_snapshot.py` — 収集スクリプト（raw 値のみ。正規化はこの skill の責務）
- memory `article-quality.md` — 内容ランク × 実測 tier の正本（非公開）
- `.claude/skills/ideation/SKILL.md` — 還流先（Step 1 情報源）
- `docs/adr/0005-post-publication-eval-loop.md` — 設計判断の記録
