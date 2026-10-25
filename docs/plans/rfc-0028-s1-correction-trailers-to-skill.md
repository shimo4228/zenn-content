# Kickoff packet — S1: harness RFC-0028（試行 rule「著者の指摘を commit に残す」を writing-ecosystem の処分規律へ移す）

あなたは task-triage loop の **build 役**です。
cwd は `zenn-content` の git worktree（branch `task/rfc-0028-s1`）。成果は branch 上の commit で返し、
判断役が検収して main へ ff-only 取り込みます。境界（人間に渡す操作 / とってよいリスク / 止まる
条件）は rule `boundary.md` — build は task branch まで。packet に無いことは harness の規約が既定。

最初に読む: harness の `rfcs/0028-correction-commit-trailers.md`（`~/.claude/rfcs/`、特に Status の
2026-10-18 著者判断）、この repo の `.claude/rules/correction-trailers.md`、
`.claude/skills/writing-ecosystem/SKILL.md` の「#### 指摘の処分規律」節、同 skill の `MAINTENANCE.md`、
`docs/adr/0014-writing-backbone-in-resident-rules.md` の 88 行目付近。

Effort: low — 文面の移設で、仕様が細かい docs 変更

## 進め方
- 入力が要らない step は止まらずに続ける。止まるのは Phase 0 の反証、time cap、この packet の外の操作が要るときだけ
- 確かめられなかったことには「未確認」と印を付け、どこを見たかを書く
- 方針を選んだ箇所は、その理由を 3 文で Report の Fix に書く

## Goal（決定可能な受入条件）
1. `.claude/rules/correction-trailers.md` が存在しない（`test ! -e .claude/rules/correction-trailers.md`）
2. `writing-ecosystem/SKILL.md` の「指摘の処分規律」に、積む（`drafts/<slug>.corrections.md` の 1 件の形）・
   写す（commit 本文の `指摘:` / `Trigger:` / `Expect:` ブロックと、写す前の Public-repository safety の適用）・
   撤回の扱いの 3 つが、現行規則として書かれている。試行の日付・「試行」の語・撤退条件は SKILL.md に書かない
   （経緯は git と RFC が持つ）。長い雛形は `references/` に置いて SKILL.md から 1 行で指してよい
3. 試行の読み（数えた値と著者の「続ける」判断の所在 = harness RFC-0028）は `MAINTENANCE.md` に経緯として 1 節で残す
4. `grep -rn 'correction-trailers' .claude CLAUDE.md docs/adr` が、ADR の注記と MAINTENANCE.md の経緯以外で 0 件。
   ADR-0014 の該当行は本文を書き換えず、`> **注記（2026-10-25, commit「<この commit の subject>」）**` 形式の注記で
   移設先を示す
5. `npm run validate` が exit 0

## Phase 0 — 前提の再照合（反証されたら実装せず止めて報告）
- `.claude/rules/correction-trailers.md` が存在し、末尾に「続けるなら writing-ecosystem の処分規律へ移し、この rule は消す」とある
- `writing-ecosystem/SKILL.md` の「指摘の処分規律」節に、著者の指摘を commit 本文へ写す規則がまだ無い
- harness RFC-0028 の Status に「2026-10-18 著者判断: 続ける」がある

## Build（順序）
1. rule の「積む」「写す」の内容を処分規律へ移す。rule 側の `origin` / `rationale` / `review-when` の注釈は skill では
   frontmatter の規約に従う（SKILL.md 本文に HTML 注釈を持ち込まない）
2. 肯定形で書く（「するな」は書かず、すべきことを書く）
3. rule ファイルを `git rm`、ADR-0014 に注記、MAINTENANCE.md に経緯
4. verify: `npm run validate` exit 0

## Review
- 種別: chore（docs のみ）。chain は skill `implementation-chain` の Chain Matrix に従う
- **packet に書いていないことは harness の規約が既定**。省略・読み替えは可だが、報告に「逸脱: 何を・なぜ」と**必ず名指し**する
- diff 外の気づきは `rfcs/` にも台帳にも書かない。再現手順を書けるものは Report の `Proposed tasks`（最大 2 件）に、
  書けないものは `Out-of-diff findings` に 1 行ずつ

## Must-not（境界）
- 変えてよいのは `.claude/rules/correction-trailers.md`（削除）、`.claude/skills/writing-ecosystem/`、`docs/adr/0014-*.md`（注記の追記のみ）だけ
- `articles/`・`drafts/`・`.github/`・`.claude/settings.json` を変えない
- `git add -A` を使わない ; harness の `rfcs/` の state は判断役が書く
- この packet のファイルを編集しない — dispatch 時点で凍結した契約
- main に merge・push しない
- 45 分を超えたら打ち切って、そこまでの diff で報告

## Report（最終 commit の message 本文）
refactor(writing): <summary> (harness RFC-0028)

Packet: S1
Plan: docs/plans/rfc-0028-s1-correction-trailers-to-skill.md
Needs from judge: <… / none>
Model: <この session のモデル名>
Effort: <実際に走った effort。分からなければ「未確認」>
Premise: <再照合の結果>
Fix: <what and why>
Verify: <npm run validate の結果・日時>
Review: <回した reviewer と結果> / Deviations: <none か名指し>
Risk: <戻し方>
Proposed tasks (for the judge, 最大 2 件): <none か各件>
Out-of-diff findings (for the judge): <none か 1 行ずつ>

最後のメッセージは「判断役に要るもの」から始め、commit SHA・verify の結果・所要時間を報告して終了してください。
