---
name: article-stocktake
description: 公開済みZenn/Dev.to/note記事の実測メトリクスを収集し、内容品質ランクと実測tierの乖離をproject-localに報告する。Use when — 週1回の収集（collect）、月次または記事2〜3本ごとの受信状況を確認するとき。NOT for — テーマ候補の生成・順位付け、本文改稿、媒体共通の執筆フロー。
user-invocable: true
origin: shimo4228
---

# Article Stocktake Skill

**Purpose:** 公開後の実測データで記事 Eval ループ（AKC の Measure phase）を回す。予測ではなく読者の実際の行動（いいね・reactions・views・フォロー）を ground truth とし、**内容品質と実測読者価値の乖離**を主シグナルとして企画・配信に還流する。

予測ではなく、公開後に観測した読者行動だけを扱う。

---

## Usage

```
/article-stocktake          # 収集 → 乖離分析 → 更新提案
/article-stocktake collect  # Step 1 だけ回して止まる（週 1 回の定点観測）
```

周期は 2 つ。収集は週 1 回（定期実行してよい）。分析（Step 2 以降）は月次、または記事 2-3 本公開ごとで、人間駆動。

週 1 回にする理由: 両ダッシュボードとも記事ごとの数字は**今日時点の累計しか出さない**。記事ごとの公開直後の伸びは、累計を定点で残して差分を取る以外に再構成できない。Zenn はアカウント全体の日次推移も直近 1 か月しか遡れない（2026-09-29 確認）。

---

## Process

### Step 1: 収集（code）

```bash
cd scripts && uv run python metrics_snapshot.py
```

`scripts/metrics/snapshots.jsonl` に追記される（Zenn: liked/bookmarked/comments、Dev.to: reactions/comments/views、フォロワー総数）。API 欠損は fail-soft — 片系が死んでいても続行し、警告のみ。

続けて、ログイン済みの Chrome（Claude in Chrome）でダッシュボードを読み、同じファイルへ追記する。閲覧数は公開 API に無く、ここでしか取れない。

| source | 画面 | 読む値 |
|---|---|---|
| `zenn_dash` | `https://zenn.dev/dashboard/stats` の「投稿ごとの合計表示回数」（「もっと読み込む」を尽きるまで押す） | 記事ごとの `views`（累計）と、「表示回数」の直近 1 か月合計 |
| `note_dash` | `https://note.com/dashboard` の記事表 | 記事ごとの `impressions` / `pv` / `likes` / `comments`（累計）と、上部の過去 28 日合計 |

- 行の形（1 記事 1 行、同じ収集回は同じ `ts`）:
  - `{"ts", "source": "zenn_dash", "slug", "views", "published_at"}`
  - `{"ts", "source": "note_dash", "slug", "note_url", "status", "impressions", "pv", "likes", "comments", "published_at"}`
  - アカウント合計は `"type": "account"` と `"window"` を付けた 1 行
- `slug` は repo の slug。Zenn は表のリンク `zenn.dev/link/articles/<slug>`、note は `scripts/corpus.yml` の URL またはタイトル一致で引く。引けない行は `slug` を空にして `title` を残す
- 数字はスクリーンショットから読まず、javascript_tool で DOM から取る。Zenn は `a[href*="/link/articles/"]`、note は `a[href*="/shimo4228/n/"]` ごとに、リンクを含む行の innerText を取り出して数値化し、件数が画面の記事数と一致するか確かめる
- `-` 表示は 0 として記録する
- note のダッシュボードは background tab だと読み込みが止まる。screenshot で前面化してから読む
- どちらかにログインしていなければ、その source を飛ばして報告する（ログインは著者が行う）

### Step 2: 正規化と tier 算出

source ごとに最新 ts のレコードを読み、記事ごとに正規化する（収集回ごとに source の組が違うので、全体の最新 ts だけを読まない）:

- **主指標**: Zenn `liked / 公開後日数`（古い記事が累積で有利になるのを補正）
- **補助指標**: Dev.to views・reactions（EN 側の到達）、ブックマーク（参照価値）
- **届いたか / 刺さったかの分解**: Zenn は `liked / views`（読まれた中での反応）、note は `pv / impressions`（一覧で見えた中で開かれた割合）と `likes / pv`
- **伸び方**: `*_dash` の同じ slug を前回の収集回と差し引いた週次増分。note 転載記事は Zenn 版と並べて媒体差を見る
- 相対 tier を **上位 / 中位 / 下位** の 3 段に分ける（全公開記事内の相対評価）

**絶対スコアを出力しない**（output discipline）。「7.2/10」ではなく tier と乖離だけを提示する。

### Step 3: 乖離表の提示（主シグナル）

memory の `article-quality.md` にある内容品質ランク（A/B/C）と突合し、**乖離セルの記事のみ**列挙する:

| 乖離パターン | 示唆 | 還流先 |
|---|---|---|
| **A ランク × 実測下位** | 内容は良いが届いていない — タイトル・配信・タイミングの問題 | project-local `title-reviewer` agent / local `zenn-format` / `.claude/rules/publishing-channels.md` |
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
`title-reviewer`とlocal `zenn-format`へ個別に渡す。

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
- project-local `title-reviewer` agent; local `zenn-format`
