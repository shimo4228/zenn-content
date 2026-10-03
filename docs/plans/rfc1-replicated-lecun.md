# RFC-0001 実装 plan: zenn-content 用の出力スタイル

RFC: [rfcs/0001-writing-output-style.md](../../rfcs/0001-writing-output-style.md)

## Context

RFC-0001 は、`keep-coding-instructions` を書かない（既定 `false`）出力スタイルを zenn-content の project 設定で選び、
Claude Code のコーディング用の指示を執筆セッションから外す提案。Next action は「外す前後の system prompt を記録して比べる」。

着手前に分かったこと（2026-10-03、Claude Code 2.1.287）:

- prose mod（`~/MyAI_Lab/claude-prose-mod`）の Phase 0 は C0（今のまま）と C2（ネイティブ設定）だけを記録した。
  C1（`keep-coding-instructions` なしのスタイル）は plan にあるが未実行。probe に計測用スタイル
  `tools/probe/output-styles/writing-probe.md` は同梱済み
- C0 の system prompt は trait `lean` で、節の合計 6,557 字。コーディング向けに読める文は `communication` 節の
  「Write code that reads like the surrounding code…」（94 字）と `lean_body` の「Reference code as `file_path:line_number`」程度。
  公式 docs の例示（変更範囲・コメント・検証）に当たる長い節は、lean ではもともと見当たらない
- つまり外れる量は小さい可能性が高い。手順 1 の計測で確かめてから、作るかを著者が決める
- 公式 docs（code.claude.com/docs/en/output-styles、2026-10-03 確認）: project の `.claude/output-styles/` を読む。
  `outputStyle` は project の settings が `~/.claude/settings.json` より優先。`/output-style` とメニューは
  `.claude/settings.local.json` に書く。Desktop app では settings ファイルの `outputStyle` で選ぶ。fork 以外の subagent には効かない
- global の `~/.claude/settings.json` に `outputStyle` は無い。`signal-first` はどの settings からも選ばれておらず、
  今のセッションにも効いていない（RFC の「signal-first を使うか」は、今は回帰の心配が無い）

## 手順

| # | 内容 | 終了条件 |
|---|---|---|
| 0 | `claims.py claim RFC-0001 --label "出力スタイルの計測と実装"`、RFC の state を `in_progress 2026-10-03` に。この plan を単独 commit（`docs(plan): rfc1-replicated-lecun`） | commit 済み |
| 1 | C1 を計測（下）し、C0 と節ごとに diff | 外れた節・文の一覧ができる |
| 2 | 結果を RFC の Status に書き、著者に「作る / 作らずに RFC を閉じる」を聞く | 著者の判断 |
| 3 | （作る場合）スタイル本体と project 設定を置く | 下の Verification が通る |
| 4 | Doc Sync: CLAUDE.md に切り替え方を 1 行、RFC の Status と state | `npm run validate` / `npm run check:index` 緑 |

### 手順 1: C1 の計測

C0 と同じ条件（zenn-content を cwd、短い 1 文、`claude -p`）。zenn-content のファイルは変えない。

```bash
PROSE_PROBE_OUT=~/MyAI_Lab/claude-prose-mod/tools/probe/out/c1.jsonl claude -p --plugin-dir ~/MyAI_Lab/claude-prose-mod/tools/probe --settings '{"outputStyle":"writing-probe"}' "こんにちは"
```

- 記録の `compose.outputStyle` が null なら選択が効いていない。plugin の名前空間付き（`prose-probe:writing-probe`）で
  やり直す
- 比べるもの: `compose.sections` の id 集合と各 `text`（`tools/probe/out/c0.jsonl` と diff）。attachments（`instructions`・
  `skill_listing`）の字数が変わらないことも確かめる（スタイルは system prompt の節だけに効くはず）
- 生の記録は prose mod の gitignore 下に置く。prose mod の計測記録（`docs/measurements/2026-10-03-phase0.md`）へ C1 を
  足すかは別 repo の作業なので、完了報告で著者に渡す

### 手順 2: 判断材料

RFC の Status に、外れた文の全文と字数、スタイル本体として足す字数を書く。推奨はこう置く:

- 外れるのが上の 2 文程度なら、効果は「コーディング役の 1 文を外し、執筆役であることを 1 文で伝える」だけ。
  コストも設定 1 行とファイル 1 つで小さいので、作る側を推奨する。ただし RFC の Drawbacks（切り替え忘れ）は残る
- 想定外に大きい節（検証・変更範囲の指示など）が外れていたら、RFC どおり作り、本文に要る作法を足すかを検討する

### 手順 3: 実装（作る場合）

- `.claude/output-styles/zenn-writing.md`
  - frontmatter: `name: zenn-writing`、`description`、`origin: shimo4228`。`keep-coding-instructions` は書かない
  - 本文: 役割の宣言と、規約の置き場所へのポインタだけ（例: この repo のセッションは記事・エッセイの執筆と公開作業。
    執筆の原理は `.claude/rules/writing-principles.md`、媒体の値は `.claude/rules/publishing-channels.md`、手順は
    `writing-ecosystem`）。原理・値・手順の言い直しは書かない（CLAUDE.md の規約）。手順 1 で外れた文のうち執筆にも要る
    ものがあれば、ここに 1 行ずつ足す
- `.claude/settings.json` を新設し `{"outputStyle": "zenn-writing"}`。公開 repo で選択を記録として共有する
  （`settings.local.json` は gitignore 済みで、手元の切り替え用に空けておく）
- 切り替え: コーディング作業では `.claude/settings.local.json` に `"outputStyle": "default"`（local が project の
  settings.json より優先）、CLI なら `/output-style default`。これを CLAUDE.md に 1 行で書く

## Verification

- 選択が効く: `--settings` なしで手順 1 のコマンドを流し（出力先は `c3.jsonl`）、`compose.outputStyle` が `zenn-writing`、
  sections が C1 と同じ diff になり、スタイル本文が載っている
- Desktop app: zenn-content で新しいセッションを開き、`/output-style`（引数なし）で現在のスタイルが `zenn-writing` と
  表示される
- 切り替え: `settings.local.json` に `"outputStyle": "default"` を入れて同じ計測をし、C0 と一致する。確認後に戻す
- 機械検査: `npm run validate`、`npm run check:index`。public-safety（個人 path なし。plan と RFC の path は `~/` で書く）

## Commits

1. `docs(plan): rfc1-replicated-lecun`（この plan だけ）
2. `docs(rfc): RFC-0001 に C1 の計測結果を書く`（Status と state。本文に `Plan:` 行）
3. （作る場合）`feat(claude): 執筆用の出力スタイル zenn-writing を project で選ぶ` — スタイル・settings.json・CLAUDE.md の 1 行。
   本文に `Context:` / `Decision:` / `Review-when:`（RFC の review-when と同じ条件）と `Plan:` 行
4. RFC の state を終端に（作った: `done`、作らない: `withdrawn`）、`claims.py release --outcome done`

push は著者の指示を待つ（記事・schedule の変更ではないので Zenn / Dev.to の予定には影響しない）。
