kind: internal
# harness-stocktake の告知記事 — 既存の記録から書ける範囲と、書くときの制約

as-of: 2026-11-02。親 plan は `~/.claude/docs/plans/enumerated-petting-beaver.md` の Stage 3 手順 2・3 と Stage 4。新しい run・計測はしない
（同 plan:216-218 の改訂）。この report は記事の構成を決める材料で、本文ではない。

## 問い

告知記事（JP Zenn、EN Dev.to）を、記録に既にある数字だけで、物語の軸「系譜と出所」に沿って書くとき、各節が使える事実・数字・
出典は何か。また、書くときにどの制約が効くか。

## Found

### 1. 系譜（skill-stocktake → harness-stocktake）

| 事実 | 出典 |
|---|---|
| 2026-02-24 に `/skill-stocktake` の設計・実装・公開を Zenn に書いた | `articles/skill-stocktake-design-journey.md:2,7` |
| 2026-02 に ECC へ出した PR 8 件がすべてマージされ、その中に skill-stocktake（PR #265）があった | `articles/ecc-marketplace-contribution.md:10,33,44` |
| skill-stocktake の `origin` は `shimo4228`（自作）。ECC の更新で上書きしないと決めている | `~/.claude/skills/skill-stocktake/SKILL.md:9`、`~/.claude/docs/adr/0001-ecc-skill-management-policies.md:17` |
| 1 件ずつの `[y/n/skip]` は 2026-07-03 に stocktake / distill 系 3 skill に入った（commit `f8b08bc`）。著者は 2026-10-31 に「1 個 1 個私に判断を聞く形だから、一括承認しづらい」と言った | `~/.claude/docs/adr/0097-batch-stocktake-report-and-two-decisions.md` Context |
| ADR-0097（2026-10-31）: 著者の判断は棚卸し 1 回につき 2 回（report の承認と ff 取り込み）。7 本の棚卸し skill が判定までを持ち、承認と適用は harness-stocktake の契約に渡す | ADR-0097 Decision 1・2 |
| 初回の全体実行（2026-10-31）: 7 source・192 項目・非 Keep 74・判断 2 回・開始から report まで約 30 分 | `enumerated-petting-beaver.md:12`（192 は `research/2026-11-01-doctor-comparison.md:24` にもある。「判断 2 回」の観測は plan:12 にだけある） |
| AKC の Curate phase: skills / rules / agents が増えたとき、または参照が切れたときに、重複・古い項目・発火しない項目を見つける | `~/MyAI_Lab/akc-cycle/README.md:69` |

### 2. `/doctor` との比較（著者の harness、n = 1）

- 非 Keep 74 件のうち、native（`/doctor`・`/doctor prompt-audit`・`/skill-doctor -p`）が同じ対処まで拾ったのは 0、部分 26、拾わない 48（65%）
  （`research/2026-11-01-doctor-comparison.md` 結論 1、aggregate 表 2）
- 逆向き: native の指摘 28 件のうち、stocktake が拾ったのは 2、部分 4、拾わない 22。補完関係で、「`/doctor` の代わり」とは書けない（doctor-comparison 結論 3）
- 答えが割れる例: 10 日の窓で未使用の skill を `/doctor` は off に挙げ、stocktake は Keep にした（doctor-comparison 結論 4）
- as-of 2026-11-01、Claude Code 2.1.316

### 3. 公開 harness 20 本（`~/.claude/docs/plans/research/2026-11-01-state-of-aggregate.md`）

- 選定: GitHub code search 1 query（`filename:SKILL.md path:.claude/skills`）、seed で shuffle、fork / archive ではない、90 日以内に push、
  skill 5 本以上（aggregate「対象と条件」）。母集団の推定ではない
- 非 Keep 789 / 1979（39.9%）。非 Keep が 1 件以上出た run の数: docs・skills・assets 19/20、distill 18/20、hooks 12/20、agents 10/20、rules 2/20（表 1）
- 大きさとの関係: 件数とは ρ = 0.62（skills 数）、割合とは ρ = 0.06（表 3）
- 見立て: 見ていない 10 本で 9/10 一致。ただし「全部 ○」と言うだけでも 9/10 になり、唯一の × 予測は外れた（表 4）
- 最初の非 Keep まで: 中央値 134.5 秒、180 秒以内は 18/20（表 5）
- 正答率: 中心の主張 57/60（95%）、細部まで 40/60（67%）。照合役は Claude の別の model（表 6）
- 記事の「一つの数字」の候補 A / B / C とその弱点は aggregate の末尾の表にある。決めるのは著者

### 4. 公開済みの事実（2026-11-02、親 session の依頼文）

plugin `shimo4228/harness-stocktake` v0.1.0（immutable release）、Action `shimo4228/harness-stocktake-action` v1.0.0（GitHub Marketplace）。
Anthropic の plugin directory には提出済みで審査中なので、本文に掲載は書かない。

### 5. 書くときの制約（この repo の契約）

| 制約 | 出典 |
|---|---|
| Zenn の題は原則 50 字、em dash（——）で繋がない。仮題「`/doctor` の後に何が残るか — 公開 harness 20 本の実測」は一本の「—」で繋いでいる | `.claude/rules/publishing-channels.md` Channel routing の Zenn 行 |
| 中心命題は brief の前に著者と話して決め、Author's words は原文で置く | `.claude/skills/writing-ecosystem/SKILL.md` §2 |
| persona-read-loop は「理由が尽きた / 残りが著者に渡すものだけ / 改稿 3 回」の最初で止める。親 session の依頼文は「3 round」 | `~/.claude/skills/persona-read-loop/SKILL.md` §6 |
| panel: editor・fact-checker・Codex の初見の読みを凍結稿に各 1 回。その後に著者の通読と内容 GO、title-reviewer、quality-gate | writing-ecosystem §4–§6、publishing-channels の Shared acceptance profile |
| EN は JP の profile を通った後に devto-translator → editor の report・処分 → dry-run → 著者の公開 GO。persona 読み・初見の読み・fact-checker・title-reviewer は EN では回さない | publishing-channels の Shared acceptance profile |
| 末尾に関連リンク 2 行と AI 開示 | publishing-channels「Related links」、`writing-ecosystem/references/publication-procedures.md` |
| 公開 repo なので repo 名・個人の path・raw log を出さない | `CLAUDE.md` Public-repository safety、`~/.claude/rules/common/public-records.md` |

## 記録の中の食い違い（本文の前に決着させる）

1. AKC の DOI: 親 session の依頼文は `10.5281/zenodo.19200727`、`~/MyAI_Lab/akc-cycle/README.md:122` は `19200726`（concept DOI と version DOI の違いの可能性がある）。fact-checker に Zenodo で確かめさせる
2. 「192 項目 → 判断 2 回」の出典: 親 plan:228 は ADR-0097 を挙げるが、ADR-0097 にあるのは設計だけ。本文の出典は plan:12 と doctor-comparison:24 にする（aggregate の食い違い 7）
3. 初回の所要時間: plan:12 は約 30 分、premise-test:123-124 は約 33 分（aggregate の食い違い 8）。本文で使うなら一方に決める
4. 集計の率は Stage 0 の skill の値で、公開版の plugin の値ではない（aggregate の食い違い 9）。本文に「公開版の plugin で同じ数字が出る」とは書けない

## まだ分からないこと（著者だけが答えられる）

- 中心命題: 著者がこの記事で何に引っかかっていて、何を問いたいか（Author's words）
- 本文の「一つの数字」: aggregate の候補 A / B / C のどれにするか、またはそれ以外か
