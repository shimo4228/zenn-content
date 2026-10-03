---
state: in_progress 2026-10-03
review-when: Claude Code の出力スタイルの仕様（`keep-coding-instructions` の既定値、project の `.claude/output-styles/`、`outputStyle` の設定の優先順位）が変わったとき。prose mod（下の Prior art）が system prompt の節も扱うようになったとき
---
## Summary

zenn-content 専用の出力スタイルを `.claude/output-styles/` に置き、この repo の project 設定で選ぶ。`keep-coding-instructions` は既定の `false` のままにして、Claude Code のコーディング用の指示を、この repo の執筆セッションの system prompt から外す。

## Motivation

- この repo のセッションは記事・エッセイの執筆と公開作業が中心だが、Claude Code の system prompt にはソフトウェア開発向けの指示（変更範囲の決め方、コメントの書き方、検証のしかたなど）が入ったままになっている
- 現状、この repo 用の出力スタイルは無い。どの settings にも `outputStyle` の指定が無く、Claude Code の標準の system prompt で動いている（2026-10-03 確認）
- global の harness からの流入（rules・skill 一覧・agent 一覧など）は、著者の別 repo の prose mod が扱う（Prior art）。そこでは「system prompt の節は出力スタイルに任せる」と決めた。この RFC はその受け持ちを zenn-content 側で実装する

## Guide-level explanation

- zenn-content でセッションを開くと、執筆用のスタイルが自動で選ばれる。著者が毎回選び直す必要はない
- コーディングの作業（`scripts/` の Python や公開パイプラインの修正）をこの repo でするときは、`/config` などでスタイルを切り替える。切り替え方は README か CLAUDE.md に 1 行で書く

## Reference-level explanation

- 置き場所: `.claude/output-styles/<name>.md`（project の出力スタイル。公式ドキュメント code.claude.com/docs/en/output-styles、2026-10-03 確認）
- 選び方: project の settings の `outputStyle`。公開 repo で共有するなら `.claude/settings.json`、著者の手元だけなら `.claude/settings.local.json`。project の設定は `~/.claude/settings.json` より優先される
- frontmatter: `keep-coding-instructions` を書かない（既定 `false`）
- 効く範囲: メインの会話と fork には効く。fork 以外の subagent（editor・fact-checker などの review agent）は自分の system prompt で動くので効かない

本文に書くもの・書かないもの:

- 書かない: 執筆の原理（`.claude/rules/writing-principles.md` が唯一の正本）、媒体ごとの値（`.claude/rules/publishing-channels.md`）、執筆手順（`writing-ecosystem`）。CLAUDE.md の「backbone を他所で言い直さない」規約に従う
- 書く候補: コーディング指示を外したことで抜ける、この repo に要る作業の作法（git と公開物の扱い、`npm run validate` などの機械検査の使い方）。何が抜けるかは、外す前後の system prompt を比べてから決める

## Drawbacks

- スタイルの切り替えを忘れると、`scripts/` のコーディング作業がコーディング指示なしで進む
- コーディング指示の中には、執筆作業でも効いていた作法が混ざっている可能性がある（ファイルを読んでから書き換える、など）。外すと失われる
- 本文に何かを書くと、rules との二重定義になりうる

## Rationale and alternatives

- **何もしない**: コーディング指示が執筆の判断に混ざり続ける
- **global の出力スタイルで外す**: 著者の他の repo はコーディング中心なので、global では外せない
- **prose mod の Mod で system prompt の節を外す**: prose mod の詳細設計で、v0.1 では節に触れず出力スタイルに任せると決めた
- **`force-for-plugin` 付きのスタイルを prose mod に同梱する**: plugin を有効にした repo で自動適用できるが、zenn-content 固有の作法を global の plugin に持たせることになる

## Prior art

- prose mod（著者が別 repo で設計・実装中の Mod。2026-10-03 時点で未公開）: global の harness を repo ごとに ON/OFF する Mod。system prompt の節は出力スタイルに任せると決めている
- global の出力スタイル `signal-first`（`keep-coding-instructions: true`）: 著者の応答の register を決めるスタイル。執筆用スタイルとの関係（受け継ぐか、別にするか）は未定

## Unresolved questions

- `keep-coding-instructions: false` で、実際にどの節が外れるか。外す前後で system prompt を記録して比べる（prose mod の probe が使える）
- 本文に何を書くか（上の「書く候補」）。何も書かない最小のスタイルで足りるか
- global の `signal-first` の register をこの repo でも使うか
- 選択を `settings.json`（公開）と `settings.local.json`（手元）のどちらに置くか
- コーディング作業との切り替えの手間を、どこまで許容するか

## Future possibilities

- 執筆向けスタイルの雛形を、prose mod の README で他の書き手向けに紹介する

## Status

in_progress 2026-10-03 — 外す前後を計測した。`keep-coding-instructions: false` で system prompt から外れる節は無かった。
作るかの判断待ち。

計測（Claude Code 2.1.287、prose mod の probe、zenn-content で `claude -p` に短い 1 文。plan:
[docs/plans/rfc1-replicated-lecun.md](../docs/plans/rfc1-replicated-lecun.md)）:

- C0 は出力スタイルなし。C1 は probe 同梱の計測用スタイル（`keep-coding-instructions: false`）を `--settings` で選んだ。
  plugin のスタイルは名前空間付き（`prose-probe:writing-probe`）でないと選ばれず、名前だけでは黙って Default になった
- system prompt は trait `lean` で、節は C0・C1 とも同じ 10 節。変わったのは本体（`lean_body`）の 1 行目だけ:
  「You are an agent working with the user toward their goals…」が「You are an interactive agent that helps users
  according to your "Output Style"…」になった（1,603 → 1,641 字）
- コーディング向けの文は C1 にも残った: `communication` 節の「Write code that reads like the surrounding code…」と、本体の
  「Reference code as `file_path:line_number`」。docs が例に挙げる、変更範囲・コメント・検証の指示に当たる節は、lean では
  C0 にもともと無い
- スタイルの本文はリマインダー（`output_style` 108 字、`output_style_instructions` 64 字）として足された。CLAUDE.md と rules
  （37,495 字）、skill 一覧などのリマインダーは変わらなかった

この RFC の Motivation（コーディング用の指示が執筆セッションに入ったまま）は、2.1.287 の lean な system prompt では
当てはまらない。出力スタイルにできるのは、冒頭の 1 行を「Output Style に従う」に替え、本文を足すことだけ。

## Next action

- 著者が判断する: 役割の宣言を足すためだけにスタイルを作るか、`withdrawn` で閉じるか
