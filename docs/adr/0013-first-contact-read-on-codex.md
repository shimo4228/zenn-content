# ADR-0013: 初見の読みを Codex に移し、cross-model review を兼ねさせる

## Status

Accepted

## Date

2026-09-27

本 ADR は [ADR-0004](./0004-zenn-clarity-reviewer-addition.md) Decision 1 のうち「初見読者の明瞭性を Claude の agent が
読む」部分と、[ADR-0011](./0011-dismantle-the-eval-layer.md) Decision 2 の panel 構成に含まれる `codex-review` を部分
supersede する。両 ADR の該当節に日付つき注記を置く。同じ日の harness 側の決定（harness ADR-0084、global `codex-review`
skill の退役）と対になる。

## Context

2026-09-27 の Zenn 稿 `articles/local-judgment-read-logprobs.md` で、凍結稿に Claude の panel を 1 回ずつ回した。
`editor` は NO BLOCKERS、`prose-clarity-reviewer` は PASS、`fact-checker` の訂正は 1 件だった。その後、人間の著者の通読で、
初見読者に伝わらない箇所が 5 つ見つかった（書き出しの呼びかけが狭い、「手元」が何を指すか分からない、実例の投稿の
出どころが無い、「関心そのもの」が何か分からない、表のどの行が gemma か分からない）。どれも panel の指摘には無かった。

反映後の稿を、Codex（`gpt-5.6-sol`）に `prose-clarity-reviewer` の checklist で初見読者として 1 回読ませると、verdict は
FAIL で、Claude の panel が挙げなかった指摘が 7 件出た（plugin の job `task-muj5vgk6-npmo76`）。うち 3 件は本文の中の
矛盾や混同で、凍結稿の時点から本文にあった — 「変わったのは答えでなく順番」と「1 文字と確率最大の段の一致は
150 件中 89%」の矛盾、`top_logprobs` の上限 20（token 候補の枠）と選択肢数の混同、単一条件の比較が無いまま温度に効果を帰属した箇所。
指摘ごとの処分は `drafts/review-disposition_local-judgment-read-logprobs_2026-09-27.md`（gitignored、公開しない）に残した。

比較の条件はそろっていない。Claude の panel は凍結稿を、Codex は著者の 5 箇所を直した後の稿を読んだ。だから Codex が
著者の 5 箇所を先取りできたかは観測していない。この観察が支えるのは「凍結稿にあった本文の矛盾 3 件を、Claude の panel は
拾わず、Codex は拾った」までで、orchestrator（Claude）と同じ系統の reviewer は orchestrator と同じ所を読み飛ばす、という
読みは記事 1 本からの仮説である。

同じ日、cross-model review を担っていた global skill `codex-review` は、Codex 側のモデル固定（`~/.codex/config.toml` の
`gpt-6-luna`）が ChatGPT アカウントで HTTP 400 になり動かなかった。原因は skill でなく config にあり、config は
`gpt-5.6-sol` に固定し直した。harness 側はこの機に、Codex CLI の変化へ追従し続ける自作 wrapper を持たないと決め、skill を
退役して OpenAI 公式の Claude Code 用 plugin（openai/codex-plugin-cc、v1.0.6）に接点を移した（harness ADR-0084）。
plugin の `/codex:adversarial-review` は `disable-model-invocation: true` で人間しか起動できず、prompt はソフトウェアの
変更（認証・データ破損・競合状態）を攻める前提で書かれている。model から起動できるのは `codex:codex-rescue` agent で、
companion script の `task` を 1 回呼ぶ中継役である。試行では Codex 側が 2 分 38 秒で完了したのに（companion の `status`
表示）、中継役が 10 分以上返らなかった。

## Decision

1. **初見の読みの実行者を Codex にする。** plugin の `codex:codex-rescue` agent を background で起動し、prompt の先頭に
   「Read-only review. Do not edit files (no --write).」と書く（書かないと rescue は書き込み可で走る）。渡すのは
   checklist（`.claude/agents/prose-clarity-reviewer.md`）・channel contract・原稿の path だけで、central thesis や成功
   基準は渡さない
2. **この 1 回で cross-model review を兼ねる。** prompt に「本文から弁護できるカテゴリのすり替え・事実の矛盾・帰属の誤り」
   を加える。`.claude/rules/publishing-channels.md` の Shared acceptance profile から `codex-review` の行を消し、初見の読み
   の行に統合する
3. **plugin が使えないときは Claude の `prose-clarity-reviewer` agent で代替し、理由を処分記録に残す**
4. **中継役が返らないときは Codex 側の結果を直接取り出す** — companion script の `status` → `result <job-id>`
5. **`/codex:adversarial-review` は使わない** — 人間しか起動できず、prompt がコード前提で prose に合わない
6. **cross-model 指摘の裁定表は `writing-ecosystem` に置く**（退役した global `codex-review` の Prose 裁定基準から移した）

## Review-when

- 3 本続けて、Codex の初見の読みが人間の著者の通読の指摘を 1 件も先取りできない — 系統を分けた利得が無いので、Claude の
  agent に戻すか panel から外す。3 本の間は Codex のモデル（`~/.codex/config.toml` の `model`）と Decision 1・2 の prompt の
  文面を変えない。先取りの判定は orchestrator が処分記録の上で行い、著者が確かめる
- plugin の `task` の仕様が変わる、または中継役の停止が繰り返して結果が取り出せない — 起動経路を引き直す（下の
  `codex exec` 直接起動の案を再訪する）
- このアカウントで使える Codex のモデルが変わる（`~/.codex/config.toml` の `model` を見直す）

## Alternatives Considered

- **現状維持：Claude の `prose-clarity-reviewer` を残し、cross-model review を plugin で別に 1 回回す（panel 4 本）** —
  今回、Claude の初見の読みは凍結稿の本文にあった矛盾 3 件を拾わず PASS を返した。系統の違う読みが同じ checklist を持つなら、
  Claude の読みを重ねて得るものは観測されていない。panel を 1 本減らせるので統合した。Open — revisit when: 上の
  Review-when 1 つ目が発火したとき
- **Bash から `codex exec --sandbox read-only` を直接起動する** — 中継役の停止を避けられる。ただし起動の flag と sandbox の
  指定を repo 側で持ち続けることになり、harness ADR-0084 が退役させた追従コストを別の場所に作り直す。Open — revisit
  when: 中継役の停止が繰り返す
- **`/codex:adversarial-review` を使う** — 人間しか起動できず、prompt がコード前提で prose に合わない。不採用
- **global `codex-review` の wrapper script を直して使い続ける** — harness ADR-0084 で退役済みで、この repo の選択肢に無い
- **Herdr の pane から Codex を起動する** — Codex は非対話で走るので pane が要らず、Herdr 側の起動条件だけが増える。不採用

## Consequences

- 初見の読みが orchestrator（Claude）と別系統のモデルになる
- panel は 4 本（channel editor・`prose-clarity-reviewer`・`fact-checker`・`codex-review`）から 3 本（channel editor・
  `fact-checker`・Codex の初見の読み）に減る。失うのは Claude 系統の初見の読みと、初見の読みから独立した cross-model pass
- 外部 plugin・ChatGPT の契約・`~/.codex/config.toml` のモデル固定に依存する。plugin が無い環境では Decision 3 の代替に落ちる
- 中継役の停止を 1 回観測している。`result` での取り出しが手順に入る。rescue agent は依頼文を書き直してよい設計なので
  （`~/.claude/plugins/cache/openai-codex/codex/1.0.6/agents/codex-rescue.md`）、Decision 1 の「path だけ渡す」が中継段で変形されうる
- checklist の正本は Claude agent の定義ファイルのまま、主な実行者が Codex に移る。以後の checklist 改修で、どちらのモデルの
  読みに合わせるかがずれうる
- 根拠は記事 1 本（n=1）で、Review-when の 1 つ目がその検証になる
- 参照更新箇所: `.claude/skills/writing-ecosystem/SKILL.md`、`.claude/rules/publishing-channels.md`、`docs/CODEMAPS/skills.md`、
  `llms-full.txt`
