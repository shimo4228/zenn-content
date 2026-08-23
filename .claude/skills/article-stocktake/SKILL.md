---
name: article-stocktake
description: 公開済みZenn/Dev.to記事の実測メトリクスを収集し、内容品質ランクと実測tierの乖離をproject-localに報告する。Use when — 月次または記事2〜3本ごとの受信状況を確認するとき。NOT for — テーマ候補の生成・順位付け、本文改稿、媒体共通の執筆フロー。
user-invocable: true
origin: shimo4228
---

# Article Stocktake Skill

**Purpose:** 公開後の実測データで記事 Eval ループ（AKC の Measure phase）を回す。予測ではなく読者の実際の行動（いいね・reactions・views・フォロー）を ground truth とし、**内容品質と実測読者価値の乖離**を主シグナルとして企画・配信に還流する。

予測ではなく、公開後に観測した読者行動だけを扱う。

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
| **A ランク × 実測下位** | 内容は良いが届いていない — タイトル・配信・タイミングの問題 | global `title-eval` / local `zenn-format` / `.claude/rules/publishing-channels.md` |
| **B/C ランク × 実測上位** | 読者需要を示す観測 | 著者のnext-move reviewへ事実として提示 |

一致セル（A×上位、C×下位）は正常動作なので列挙しない。各乖離記事に定性所見を 1 行添える（「タイトルが概念名のみで用途が見えない」等の具体観察）。

### Step 4: 更新提案 → 人間確認 → memory 更新

ランク・tier の更新案を提示し、**ユーザー確認後に** memory の `article-quality.md` を更新する:

- 既存の A/B/C 表に **実測 tier 列と判定日**を追加（別軸並記。ランクと混ぜない）
- 冒頭に「実測サマリ」節（届いたテーマ・構造の事実3〜5行 + follower推移1行）を置く

### Step 5: Report and stop

乖離表と実測サマリを著者へ提示して止まる。`session-theme-mining`を自動起動せず、候補の順位や
推薦を作らない。著者は受信指標を「何を書くか・cadence・language placement」の判断に使えるが、
既存の中心命題や本文を数字へ合わせて変形しない。A×下位のdistribution見直しはglobal
`title-eval`とlocal `zenn-format`へ個別に渡す。

---

## Guardrails（Content Integrity）

- **既存記事のエンゲージメント目的リライトを提案しない**。乖離が示すのはdistributionの改善余地か、著者が次に何を書くかを考えるための観測である
- 実測tierから自動でテーマを推薦・順位付けしない
- LLM による tier 判定は Step 4 の人間確認を通してのみ memory に固定される（LLM 単独の承認経路を作らない）

---

## Related

- `scripts/metrics_snapshot.py` — raw値の収集
- `scripts/metrics/snapshots.jsonl` — project-local observation record
- memory `article-quality.md` — 内容ランクと実測tierのprivate working record
- global `title-eval`; local `zenn-format`
