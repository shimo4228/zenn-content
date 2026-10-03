---
state: done 2026-10-03
review-when: Claude Code の出力スタイルの仕様（本文の届き方、project の `.claude/output-styles/`、`outputStyle` の優先順位）が変わったとき。Claude Code が Claude 5 系で lean でない system prompt を使うようになったとき。スタイルの項目に反する著者の指摘が続いたとき
---
## Summary

zenn-content 専用の出力スタイル `zenn-writing` を `.claude/output-styles/` に置き、`.claude/settings.json` で選ぶ。中身は著者との会話の規約（問いへの答え方、判断の渡し方、命題の扱い、報告、通読の渡し方、説明のしかた）で、記事の文章の規約は持たない。

## Motivation

- この repo のセッションは記事・エッセイの執筆と公開作業が中心だが、著者との会話のしかたを決めた場所が無かった。どの settings にも `outputStyle` が無く、Claude Code の Default で動いていた（2026-10-03 確認。global の `signal-first` は ADR-0079 で著者が無効のままを選んでいる）
- 過去セッション（2026-07〜10、119 本）の著者の発言には、応答のしかたへの同じ反応が繰り返し出ていた: 問いに改稿で返された、選ぶ材料が実物でない、Claude の案の枠が命題に残った、「できない」が確かめずに出た、通読する稿が手元で開けない
- 起票時は「コーディング用の指示を system prompt から外す」ことが目的だった。計測でこの目的は Claude 5 系では成り立たないと分かり（Status）、著者の判断（2026-10-03）で会話の規約を書くことに改めた

## Guide-level explanation

- zenn-content でセッションを開くと `zenn-writing` が選ばれる。著者が選び直す必要はない
- `scripts/` などのコーディング作業では `.claude/settings.local.json` に `"outputStyle": "default"` を置く（local が project の settings.json より優先）。CLI では `/output-style default`。CLAUDE.md に 1 行で書いた

## Reference-level explanation

- 置き場所: `.claude/output-styles/zenn-writing.md`。選択: `.claude/settings.json` の `"outputStyle": "zenn-writing"`（公開 repo で選択を共有する）
- frontmatter に `keep-coding-instructions` は書かない（既定 `false`）
- 本文は system prompt の節ではなく、リマインダー（`output_style_instructions`、555 字）として最初のターンに届く。2 ターン目以降に新しく差し込まれるのは `output_style`（95 字、スタイル名の念押し）だけ（2.1.288 の probe、2026-10-03）。1 ターン目の本文が履歴に残るかは測っていない（公式 docs は "sends the active style's instructions with every request" と書く）。効くのはメインの会話と fork だけで、review agent には効かない
- 記事の本文もメインの会話が起草するので、本文の冒頭で「記事・brief・訳文の文章は writing-principles と channel contract に従う」と範囲を切った
- 項目は 7 つ。どれも過去セッションの著者の発言（複数 session）を根拠にし、外部の研究・編集実務で補った。選ぶ場面で推奨を添える項目と、中心命題では案より先に著者の考えを聞く項目を分けたのは、AI の提案が書き手の意見と構想を寄せる実証（Jakesch et al., CHI 2023 / Bhat et al., CHI 2026）と、履歴で Claude の案の枠が命題に残った例（6 session）による

## Drawbacks

- コーディング作業で切り替えを忘れると、Claude 5 系の system prompt の冒頭 1 行（「自分の判断で」）が「Output Style に従う」に替わったまま進む
- 項目は 8 月の摩擦を多く含む。Claude 5 系で既に出なくなったものがあるかは測っていない
- 指示は保証ではない。守られたかを測る計器は無い

## Rationale and alternatives

- **何もしない**: 会話の規約を決めた場所が無いまま、同じ摩擦が著者の言い直しで直される
- **global の signal-first を使う**: 著者が ADR-0079 で無効を選んでいる。執筆特有の項目（命題の扱い・通読の渡し方）も無い
- **workflow が出した 14 項目の草稿**: 1 項目 100〜150 字、計約 5,400 字。手順（reviewer への中継、対の言語版への波及、削除前の退避）が混ざり、Claude 5 系向けの指針（短い指示で足り、規定しすぎは質を下げうる）にも反する。応答の型だけを 7 項目に絞った
- **rules に書く**: rules は毎セッションの CLAUDE.md 層に載り、会話の規約と記事の規約の境目が見えにくくなる。出力スタイルは「応答の型」を持つ公式の置き場

## Prior art

- harness-scope（旧 prose mod。著者の別 repo）: global の harness を repo ごとに ON/OFF する Mod。system prompt の節は出力スタイルに任せると決めている。計測の probe（`tools/probe/`）はこの repo のもの
- global の出力スタイル `signal-first`（ADR-0073、ADR-0079 で無効）: 結論先頭・1 問 1 観点・推奨を添える。`zenn-writing` の項目 2 は同じ向き
- 公開されている執筆用スタイル（DawnEver/Academic ほか 10 本、2026-10-03 調査）: 300〜830 語が中心。返信の形式と成果物の形式を分けて書く例（jakecadams/writing-style）がある

## Status

done 2026-10-03 — `zenn-writing` を置いて project で選んだ。plan: [docs/plans/rfc1-replicated-lecun.md](../docs/plans/rfc1-replicated-lecun.md)

計測 1: `keep-coding-instructions` で何が外れるか（Claude Code 2.1.287、harness-scope の probe、zenn-content で `claude -p` に短い 1 文）。C0 は出力スタイルなし、C1 は `keep-coding-instructions: false` の計測用スタイル。

| モデル | trait | C0 の節の合計 | C1 で外れた節 |
|---|---|---|---|
| Haiku 4.5 / Opus 4.6 / Sonnet 4.6 | `lean` なし | 28,108 字 | `doing_tasks` 3,319 字（Haiku で確認） |
| Sonnet 5.5 / Opus 5.5 | `lean` | 6,557 字 | なし |
| Fable 5.1 | `lean` | 12,621 字 | （C1 は未計測。`doing_tasks` は C0 に無い） |

- Claude 5 系の lean な system prompt には `doing_tasks`（依頼をソフトウェア開発として解釈する、既存ファイルの編集を優先する、頼まれていない抽象を足さない、など）がもともと無い。スタイルを選ぶと、`keep-coding-instructions` が true でも false でも、本体の 1 行目が「You are an agent working with the user toward their goals, using your own judgment along the way.」から「…helps users according to your "Output Style"…」に替わるだけ
- plugin のスタイルは名前空間付き（`prose-probe:writing-probe`）でないと選ばれず、名前だけでは黙って Default になった

調査: 項目は workflow（agent 78 本）で決めた。過去セッション 119 本から著者の発言 1,017 件を直前の応答と対で読み、外部調査（出力スタイルの実例、共同執筆の研究、編集実務）と既存の規約の地図を合わせ、候補ごとに証拠・二重定義・記事への漏れの 3 視点で反証した。草稿の 14 項目を、応答の型だけの 7 項目に絞った。

計測 2: 導入後（Opus 5.5）。`.claude/settings.json` だけで `zenn-writing` が選ばれ、本文が `output_style_instructions`（555 字）で届いた。`.claude/settings.local.json` に `"outputStyle": "default"` を置くと外れ、冒頭 1 行も元に戻った。Desktop app での表示は未確認。

## Next action

- Desktop app で zenn-content の新しいセッションを開き、`/output-style` で `zenn-writing` が選ばれていることを確かめる
