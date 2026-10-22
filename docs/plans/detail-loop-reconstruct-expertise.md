# 細部を要素に分けて専門知を組み立て直す — detail-loop の記事（Zenn）

## Context

2026-10-22 のセッション（a2562592）で、著者は「神は細部に宿るスキルを作った件で記事を書きたい」と依頼し、執筆は
writing-ecosystem の通常フローでなく skill `detail-loop` で進めると決めた。初稿の作り方は「中心命題と因果線を
この brief で確かめる → orchestrator が初稿 → detail-loop のラウンド」（著者の選択「じゃあ1で」）。review panel の
代わりに detail-loop の detail-review（fresh な専門家レビュアー）と単位の凍結を回す。detail-loop は文章では見せ方
（マークアップ、表記、用語、リンク、コード、図）だけを直し、言い回しと主張の変更は著者への提案として返す。
文章を対象に detail-loop を回すのはこれが初回。

素材（drafts/ は gitignore の下）:

- 証拠台帳: `drafts/article-context_detail-loop_2026-10-22.md`（Claims C1〜C26）
- skill: `~/.claude/skills/detail-{review,units,loop}/`, `~/.claude/skills/unit-eval/`（公開 copy は shimo4228/claude-harness）
- 実験先: shimo4228/shimo4228.github.io の `source` branch、`eval/`（units.yaml, ledger.md, reviews/, mutate.sh）

## Editorial brief

Reader: Zenn — 検索・feed から来た engineer が、数秒で用途を理解し再現または判断できる。誰に向けるかを直接言った著者の
発言はない

Channel: Zenn（`articles/detail-loop-reconstruct-expertise.md`）。EN は Dev.to（通常どおり、JP の公開 GO 後）

Author's words:

- 「専門外の知識でも個々の要素に分解して各々の評価基準をリサーチの上適切な評価を設定できれば、個々の要素にアプローチすることで専門知を高いレベルで再構成できないかと言う仮説だな」（本セッション）
- 「ある程度成立したと思う。シンプルながらクオリティ感を感じるものになった。」（本セッション）
- 「そしてこの記事でも試すと言う感じだな」（本セッション）
- 「骨格ができたのは早かったんだけどそこから半日ずっと細かなDetailを詰めていた」（967ef8e5, 2026-10-18）
- 「あまりある実装力をDetailを突き詰めることに使い、他とは違うこだわりを見せることが差を作ると思うから」（X 投稿、967ef8e5, 2026-10-19）
- 「結局専門家というのは、物事の構成要素がわかるから、何をいじればどう変化するかわかるし、どう評価すればいいのかもわかるという感じだ」（967ef8e5, 2026-10-19）

Personas:

- primary: Claude Code などの coding agent で個人の製品（サイト、CLI、app）を作っている engineer。骨格までは agent で速く
  作れると知っている。比べる相手は「agent で作ったもの」の記事全般。時間の予算は冒頭 30 秒で読み続けるか決める
- inflow: X 告知か Zenn の Claude Code topic から来た人。「神は細部に宿る」や skill 名に惹かれて開いた。eval という語は
  知っているが、自分の製品に検査を書いたことは少ない。比べる相手は skill 紹介の記事。5 分で読めるかを見る
- practitioner: 日本のハーネス実践者。自分でも skill / hook / eval を組み、日本語の記事を読み比べてきた。比べる相手は
  eval ループ・LLM-as-judge の記事。仕組みが自分の環境に移せるかと、失敗が書いてあるかを見る

Central thesis: 専門外の分野でも、細部を要素に分け、要素ごとの評価基準をリサーチして設定できれば、要素に一つずつ当たる
ことで専門知を高いレベルで組み立て直せるのではないか。個人サイトで試し、ある程度成立した — シンプルながらクオリティ感の
あるものになった（確度は「仮説」「ある程度」のまま）

Entry bridge: 個人サイトの骨格はすぐできたのに、細部に半日かかった。モデルは頼めば細部を直したが、直した細部を守る検査は
一つも残っていなかった（凍結前の `eval/run.mjs` は汎用の検査だけ）。細部は専門家の領域で、専門外の人はどこを見て何で
評価するかを知らない

Figure plan: 内容 GO の後に埋める

Causal spine:

- 観察: 骨格は早く、細部に半日。細部を直しても、直したことを保つものが無い（C21、C24）
- 緊張: 細部の良し悪しを決めるのは専門家の知識で、著者はその分野の専門家ではない。頼むだけでは、何が直ったか・何を
  見ればいいかが残らない
- 機序: 専門家は構成要素がわかるから、何をいじれば変わり、どう評価するかがわかる（Author's words）。そこで細部を作法
  1 つずつの単位に分け、各単位に「何の規則か・読者に何をするか・出力にどう現れるか・何を変えれば動くか」を書き、評価
  基準は外の標準（JLReq、WCAG）から取る。fresh な専門家役のレビュアーが見つけ、直した単位は検査に凍結し、変異で
  赤になれることを確かめる。1 件を追う（候補: ja-quote-hang — +0.84px で赤 → 修正 → 変異で赤、C10・C13・C16 周辺）
- 届かなかったところ: 3 ラウンドで新しい指摘 0 には届かなかった（C14）、ループ自身の修正が退行を 2 回生んだ（C15）、
  偽の緑（C16）、任されて決めた 2 件が著者の Safari で覆った — 判断したエンジンが違った（C19・C20）
- 著者の判断: ある程度成立した。シンプルながらクオリティ感のあるものになった。決めたこと: 任せて完成形まで回し、
  著者の環境で決める（C18・C19、aea98f0）／全体の印象は検査にせず著者の目に残す（C5）／コード・Web・文章へ一般化した
  （C22）／そしてこの記事でも試す（この稿自体が文章での最初の試行）。決めなかったこと: done（新しい指摘 0 の
  ラウンド）は未到達のまま

Selected evidence:

- C21 / C24: 観察（凍結前に検査が無かった、半日の細部）
- C3 / C5: 機序（単位の 4 面、判定 3 種と「好みは著者の目」）
- C6 / C16: 機序（変異で赤を証明する、偽の緑）
- C10 / C13: 結果の数（56 単位、49 凍結、両エンジン緑）
- C14 / C15 / C19 / C20: 届かなかったところ
- C18: 委任
- C22: 一般化と、この記事での試行（締め。試行の結果 — 単位数・採否・著者の読み — は detail-loop を回した後に
  著者の判断で本文へ足すか決める）

Out of scope:

- 4 skill の分け方と各 SKILL.md の手順全文（リンクで渡す）
- Fable 5.1 による設計の過程、skill-creator の草稿ゲート
- サイトの公開経路（GitHub Actions、main の削除）
- persona-read-loop との重なりの比較（10/18 の見送り）
- Boris Cherny の effort の発言（C25。原文未確認。著者の判断「外す」、本セッション）
- 単位の 4 面の由来（C4、上座部注釈の法の四面定義・著者の「アビダルマ的な発想」。著者の判断「外す」、本セッション）

## 進め方

1. この brief の著者確認
2. orchestrator が初稿（`articles/detail-loop-reconstruct-expertise.md`、published: false）。執筆の背骨に従う
3. detail-loop: detail-review（editor・domain expert・Zenn の組版役の fresh レビュアー）→ detail-units（`drafts/detail-loop-reconstruct-expertise/eval/`）→ unit-eval。著者は初稿 r0 を通読して GO を出し、判断を委任した（「読んだ。Go。任せる。言い回しと主張の変更も任せる。」本セッション）。言い回しと主張の変更もループが決め、著者の発言の引用は原文のまま、公開は著者に残す
4. 中心命題が届くかは persona-read-loop（detail-loop の Start 節の線引き）
5. 公開の受け入れ（quality-gate の profile と、detail-loop の記録の対応）は初稿の後に著者と決める

## 受け入れ（2026-10-22）

著者は detail-loop 3 ラウンド後の r3 を通読し、「じゃあgo。公開して。即時公開で。devtoもお願い。」と公開 GO を出した。
detail-loop の記録（`drafts/detail-loop-reconstruct-expertise/eval/`: reviews/r1–r3、ledger.md、units.yaml、mutate.sh）を
受け入れの記録として扱う。対応:

- channel editor → 各ラウンドの editor 役（fresh、3 回）。指摘は全件を ledger で採用・不採用に処分
- fact-checker → 各ラウンドの domain 役（サイトの一次記録・セッションログ・フォント・W3C で照合、3 回）
- 処分記録 → ledger.md
- 機械検査 → `npm run evidence`（deviations 0）、`npm run validate`、凍結した 8 単位（全緑、各 mutation で赤を確認）
- ペルソナ読み（persona-read-loop）と初見の読み（codex）→ 回していない。著者が r3 の通読で公開 GO を出した
- 3 ラウンド目の反映後の稿は reviewer に再度は読ませていない（著者の通読が最後の読み）
- title-reviewer → 内容 GO の後に実行、著者が選ぶ
