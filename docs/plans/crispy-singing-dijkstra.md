# レビュー体制の非収束 — 前提検証と設計パケット

起票元: `.notes/handoff-review-panel-nonconvergence.md` / 検証日: 2026-08-27

**スコープ: 執筆レビュー chain のみ**（editor / prose-clarity / fact-checker / title-reviewer / codex のパネルと処分規律）。コーディング chain は ADR-0055 で /code-review 1 本に縮約済みで本件の対象外。Anthropic 一次(コーディング文書)の引用は、パケット検証項目 (b) =「著者の記憶の一次確認」のためであり、その推奨方向(本数削減でなく処分規律)を執筆パネルへの類推根拠として使う。

## Context

引き継ぎパケットは「レビュー体制が分厚すぎて収束しない」を報告し、対策の前に前提 3 点の反証を要求した。本 plan は前提検証の結果と、成立した分だけの最小設計を提示する。判定器の解体（8/23、-1151 行、判定器 0 本）と project harness 縮約（8/23 45eb8fe）は実施済みであり、本件の残余は **reviewer の本数と指摘の処分規律** に限定する。

## 前提検証の結果

### (a) n=1 問題 — 「収束しない」は部分的に成立、主因は別

`~/.claude/metrics/agent-usage.jsonl`（960 行、zenn-content 分を日別集計）の実測:

| 日付 | パターン | 帰結 |
|---|---|---|
| 07-27 | editor+clarity+fact の round が 18 分間に 3 回 | 当日中に収束 |
| 08-02 | フルパネル 3 round / 約 1 時間 | 当日公開（b8256f4 21:25） |
| 08-12〜13 | article-judge ×5 + panel（判定器時代） | 翌日公開 |
| 08-20 | judge ×2 + panel ×1 | 当日公開（8aa570b 19:20） |
| 08-23 | editor ×4 / fact ×4 | ハーネス改修の検証プローブ（d0a9b68）— 記事レビューではない |

**判定: 「2〜3 round の再レビュー」は常態だが、ほぼ全記事が当日〜翌日で収束・公開している。** 「収束しない」（4 日滞留・修正連鎖・却下 CRITICAL の複合）が実測されたのは 8/27 の 1 本のみ = **n=1**。よってパケットの主訴のうち「体制全体が収束しない」は不成立。ただし下記 FM-1 だけは n≥2 かつ機構的に再現が確定しており、これは対処する。

### (b) Anthropic 一次ソース — 記述は実在（2 箇所）

1. **[Best practices](https://code.claude.com/docs/en/best-practices)**（旧 anthropic.com/engineering から 308 redirect）"Add an adversarial review step" の Callout:
   > "A reviewer prompted to find gaps will usually report some, even when the work is sound, because that is what it was asked to do. Chasing every finding leads to over-engineering […] Tell the reviewer to flag only gaps that affect correctness or the stated requirements, and treat the rest as optional."
2. **[Code Review docs](https://code.claude.com/docs/en/code-review)** REVIEW.md 節に **"Re-review convergence"** が項目として実在:
   > "tell Claude how to behave when a PR has already been reviewed. A rule like 'after the first review, suppress new nits and post Important findings only' stops a one-line fix from reaching round seven on style alone."

**判定: 著者の記憶は正確。かつ一次ソースの推奨解はどちらも「本数削減」ではなく「flag 範囲の制約 + 残りは optional 扱い + 再レビュー時の指摘抑制」= 処分規律。**（as-of 2026-08-27）

### (c) パス数削減 vs 処分規律 — 処分規律が解

(a) で本数由来の非収束は実測されず、(b) の一次ソースも処分規律を指す。**reviewer 本数は変えない。**

## 失敗モード同定（producer→sink。成立した分のみ）

**FM-1: 規約 vs 実態の CRITICAL が構造的に再発する（成立、n≥2、決定論的）**
- producer: `zenn-content/.claude/rules/publishing-channels.md:29`（AI-mediated 行に Zenn 適用外が無い）+ `~/.claude/skills/writing-ecosystem/SKILL.md:327`（global canon「記事末に開示ブロックを置く」）
- 経路: `~/.claude/agents/editor.md:140-141` は「exemption は supplied channel contract が確立した場合のみ not applicable」と明記 → contract に免除が無い限り毎回 CRITICAL
- sink: editor CRITICAL → 著者が毎回却下
- 根本原因: 8/23 の著者判断が **memory `feedback_zenn-no-ai-disclosure` に書かれた**が、fresh-context reviewer は memory を読まない。さらに同 memory の How-to-apply は quality-gate 経由を指示するが、`quality-gate/SKILL.md:60` は「memory を受け入れ条件として読まない」— 免除が誰にも届かない死文
- 同型の副検出: zenn memory `feedback_dual-review`（editor+essay 常時両方）は 8/23 の channel routing（9039376）と矛盾する陳腐化 memory

**FM-2: 修正が次の指摘を生む連鎖** — n=1。機構は設計通りに機能した（title-reviewer は「最後の構造変更後」に走る契約で、正当に検出した）。対策は新機構でなく処分規律の再レビュー規律 1 行で受ける。

**FM-3: 台帳照合の偽陽性** — n=1（codex 3 件）。台帳機構は変えない。処分規律に「blocking 指摘は一次ソース引用を要す」1 行のみ（弱い前提として失効条件付き）。

**FM-4: レビューが対象より遅い（4 日滞留）** — **前提不成立として報告**。主因は著者 GO 待ちの人間レイテンシ + 滞留中のハーネス側変更で、reviewer 本数・処分規律と独立。対策なし。

**FM-5: 並行セッション衝突** — n=1、task-tracking 領域。本件スコープ外。対策なし。

## 目的

同じ却下を著者が繰り返さないこと。指摘の採否既定・severity の意味・規約 vs 実態の裁定者を 1 箇所に決め、裁定結果が reviewer に届く層へ書き戻されること。

## 採用案（最小 3 手 + 削除 1 手）

### 1. FM-1 の値の修正 — local contract 1 行（Delete 型の fix）
`publishing-channels.md` shared acceptance profile の AI-mediated 行を更新:
「Zenn (`articles/*.md`) は適用外（2026-08-23 著者判断）。note / Substack / Dev.to は従来通り適用可否を記録」。editor.md:140-141 の既存機構がそのまま免除を拾う。**新機構ゼロ。**

### 2. 指摘の処分規律 — global `writing-ecosystem` §4 に 1 小節（〜6 行）
意味論は global、値は local という既存の分担に従い、§4「Freeze, title, and review」末尾へ:
- **severity の意味**: CRITICAL = 読者への約束・事実・中心命題を壊すもののみ。規約と運用実態の衝突は CRITICAL でなく「裁定要求」として報告し、裁定者は著者
- **裁定の書き戻し**: 裁定結果は memory でなく channel contract に書く（fresh-context reviewer に届く唯一の層）。著者が同種指摘を 2 回却下したら、その場で contract の該当行を更新または削除する
- **再レビュー規律**: 2 round 目以降は CRITICAL と変更部分の regression のみを blocking とし、新規 MEDIUM/MINOR は集計のみ（Anthropic "Re-review convergence" pattern、as-of 2026-08-27）
- **blocking の根拠水準**: blocking 指摘は一次ソースの引用を要す。台帳のみを根拠とする指摘は advisory

### 3. 陳腐化 memory の削除 2 件
- `feedback_zenn-no-ai-disclosure.md` — 値を contract へ移送後に削除（死文の解消）
- `feedback_dual-review.md` — 8/23 channel routing と矛盾。削除

### harness-boundary 分類
```
Classification        : 手 1 = Values/Policy の値（local contract）。手 2 = Values/Policy の意味論（global skill 内の責任境界記述）。手 3 = Data/Memory の負債削除
Keep outside model because : 裁定既定と severity 契約は著者の責任境界であり、モデル推論に任せると記事ごとに揺れる（実測: 同一指摘の再発）
Portability           : runtime 非依存の prose 規約。Claude Code → 他 runtime でも残る
Obsolescence risk     : Low〜Medium（下の失効条件）
Recommendation        : Simplify（機構追加ゼロ、正味は削除超過 — memory 2 件削除 + 数行の規約）
```

### 捨てた案
- **reviewer 本数の削減**: (a)(b) とも支持しない。パネルは常態で 2〜3 round 収束
- **codex-review の writing profile からの除外**: 誤検出は n=1、有効指摘 10 件が同居。ADR-0055 も writing chain を意図的に対象外とした
- **severity 語彙の新 rule / 新 hook / 却下台帳の新設**: harness-boundary の「強く疑う対象」（policy を encode する新機構）。既存文書への数行で足りる
- **GO 待ち滞留の機構的対策**（自動 re-validate 等）: FM-4 は n=1 かつ人間レイテンシが主因
- **並行セッション locking**: スコープ外（task-tracking 領域）

## 失効条件

- 本規律適用後の 5 本で、規約 vs 実態型 CRITICAL が再発、または 4 round 以上が 2 本以上 → 処分規律では不足。本数削減を再検討（そのとき初めて）
- Anthropic の該当 2 記述（best-practices Callout / Re-review convergence）が改訂されたら as-of を更新し規律を再照合
- FM-3 の 1 行は次の 3 記事で偽陽性が観測されなければ根拠 n=1 のまま — 削除候補として扱う

## 実装時の変更ファイル

1. `~/MyAI_Lab/zenn-content/.claude/rules/publishing-channels.md` — AI-mediated 行の更新（+ 必要なら処分規律の local 参照 1 行）
2. `~/.claude/skills/writing-ecosystem/SKILL.md` §4 — 処分規律 小節（〜6 行）
3. `~/.claude/projects/-Users-<user>-MyAI-Lab-zenn-content/memory/feedback_zenn-no-ai-disclosure.md` / `feedback_dual-review.md` — 削除（MEMORY.md の index 行も）
4. global 側変更は skill: `harness-sync` で公開 repo へ同期

## Verification

- editor agent を fresh context で現行公開稿（judge-degrades-into-reviewer.md）+ 更新後 contract に対して 1 回走らせ、AI 開示 CRITICAL が "Not applicable（contract exemption）" に落ちることを確認
- `quality-gate` の手順が memory 非参照のまま成立していること（変更なしで通る）を照合
- 次の実記事 1 本で round 数と CRITICAL 却下数を観測（適用後ベースライン）
