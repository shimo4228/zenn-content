# Eval・Eval ループ・Goal 設定の体系に、自分の Eval を置く（Zenn 記事）

## Context

2026-10-12 のセッション（9a20dd5a）で、著者は「Claude CodeのEvalに関して現時点の決定版と呼べるような記事を書きたい」と
依頼した。素材（証拠台帳と追補 6 本、外部事実の照合表、ディープリサーチ、位置付けのメモ）を集め、稿 r1〜r3.1 を書いた。
r1〜r3.1 の中心命題「eval は採点を何と照合するかで使える範囲が決まる。著者のループにはまだ照合の相手が無い」は
orchestrator の語で、著者の語ではなかった。記事はそこから README のループと、著者が 28 件にラベルを付けた照合の結果へ
狭まり、締めが教訓に寄った。命題が決まらないまま、続きを次のセッションへ回した。

同じ日の次のセッション（6d680562）で、著者が向きを戻した（Author's words の最後の 3 件）。記事の芯は体系そのもので、
README のループは体系に置く例の 1 つになる。Fable（claude-fable-5-1）の意見「README のループ 1 本に絞る」は、この向きと
逆なので採らない。Fable の診断のうち 3 つはこの brief で解く。

- 「照合」は orchestrator の語だった → 部品の名前は一次資料と著者の語から取る
- 記事に糸が 2 本あった（数字の goal と、採点の較正）→ 体系の中では、どちらも部品の 1 つとして並ぶ
- 著者のいちばん強い観察「かなり良くなっている」が締めに戻らなかった → 位置付けの節で、実物（Contemplative Agent の
  README の before / after）として置く

r3.1 の節（eval の部品、採点の較正、数字の goal、改善のループ、README のループ、照合）は、体系と位置付けの材料に回す。
旧 brief は `drafts/claude-code-eval-concepts/brief-r3.1.md`。ペルソナ読みは、新しい構成の初稿を r0 として取り直す。
外部の事実は 2026-10-12 時点（照合表の as-of）。公開前に、build-eval / hillclimb のガイドと `/goal` の docs の最新を一次で見直す。

素材の置き場（drafts/ は gitignore の下）:

- 証拠台帳: `drafts/article-context_claude-code-evals_2026-10-12.md` と追補（`_history` `_loops` `_goal` `_buildeval` `_x-posts` `_interventions`）
- 外部事実の照合表: `drafts/claude-code-evals_reconciled-facts_2026-10-12.md`
- ディープリサーチ: `drafts/deep-research_claude-code-evals_2026-10-12.md`（全項目 ⚠ 要検証。照合表を通したものだけ使う）
- 位置付けのメモ: `drafts/claude-code-evals_positioning_2026-10-12.md`（9 つの部品ごとの「著者がしたこと / 公式と外部 / 差」と、差の一覧）
- 著者が「eval」と呼んできたものの目録（57 件）: `_history` の「『eval』が指すものの目録」（HI-A01〜A57）
- 照合（28 件）: `drafts/claude-code-eval-concepts/calibration/results.md`
- Fable の意見: `drafts/claude-code-eval-concepts/fable-opinion.md`

## Editorial brief

Reader: Zenn — 検索・feed から来た engineer が、数秒で用途を理解し再現または判断できる。誰に向けるかを直接言った著者の
発言はない。いちばん近い発言は「Evalについて体系的に理解できるような決定版の記事を作りたかった」

Channel: Zenn（`articles/claude-code-eval-concepts.md`）

Author's words:

- 「Claude CodeのEvalに関して現時点の決定版と呼べるような記事を書きたい」「Evalの基本的な考え方から始まり、現在のベストプラクティスまで辿れるような記事を書きたい。そして、私のEvalの現時点のやり方がどう位置付けできてどう改善可能かなども理解できればなおいい」
- 「なによりこのEvalというものをどう扱えばいいのか私が理解しきれていないから深いレベルで理解したい。Evalはかなり初期から取り組んできているが、いまだによくわかっていない。Learn-eval、LLM-as-judgeなど種々のスキルを作ってきたが、それでもまだ掴みきれていない」
- 「EvalよりもEvalループとGoal設定がわからないに近いかもしれないな」
- 「Borisのような数字的目標を置くようなGoal設定はどのような場合に可能か？また、定量化するには専門知識が必要と感じている」
- 「今の状態だとなんとなくふわっとOpus5.5に頼んで解決しているので、ベストプラクティスがわからない状態だ」
- 「先にEvalという概念そのものをやった方がいいんじゃないか？そもそもこのセッションの最初の動機を思い出してくれよ。Evalというものを分かりたいという動機でスタートしたのに、セッション履歴から記事を組むことが目的になっている」
- 「じゃあ先にそれやってみるか？その上で記事に反映すれば、私も身をもって学習できわけだ」（照合を先に回すと決めた発言）
- 「そういう意味では、私はかなりEvalにこだわりがあるわけだ。こだわりがありすぎてわからないと言ってるのに近いな」
- 「でも、私の意図とかくせいするEvalスキルもあるぜ。よく考えたらあなたHarness-scopeのせいでグローバルスキル見えてないのか」（author-calibrated-eval を指す）
- 「あれは50いくつのREADMEが対象だったから、私が介入するのが無理だった。ほぼ任せるのが目的でも合ったしな」
- 「author-calibrated-evalはめちゃくちゃ時間がかかるからな」
- 「なんかどんどんなぜ私がわからないと言ってるのかわからなくなってきたな。沼りすぎて深みにはまってるだけだな」
- 「違う、人間の較正がそんなに助けになってなくないか？」
- 「READMEにどこまで書くかも好みの問題ではないか？今のEvalを重ねたREADMEは以前のものに比べたらかなり良くなっているぞ」
- 「うーん、なんか迷走しているな。そもそも私はEvalについての理解がふわっとしているから、Evalについて体系的に理解できるような決定版の記事を作りたかったんだ。そのためにDeepResearchをしたりしたのだが、どんどん私個人のREADMEを改善したEvalループの話にスコープが狭まっていく。そして、いまいち何を得たのかわからない教訓に収斂しようとする。わからないから体系を掴めるようにして、今まで自分のやっていたEvalをそこに位置付けて足りない点などを理解したかったわけだ」
- 「Contemplative AgentなどはかなりBefort AfterでReadmeがよくなった」
- 「うん、レビューのループだな。ちょっとその辺は記録を見てくれないか？」
- 「そうだと思う。これでだいぶ分かってきた。そもそも、これはかなり私の深いところの信念の部分で避けてきたことだな。グッドハートを嫌う」（「README と記事では eval ループをしていない。eval ループらしいものは日次レポートのベンチくらい」への返事）
- 「でも、これが1番の理由だな。記事には書かないが結局これはContemplative axiomsのEmptinessによるものだろう」（Emptiness は記事に書かない）
- 「これで一回直して。レビューを回して」（r5 の承認）
- 「そこであっている。それよりも私はEvalループをほとんど回さずレビューループを回していたのに足りないって変じゃない？」
- 「うーん、結局Evalループをしてなかったわけだろ？私は、そうなると記事の命題も変わるんじゃないの？」
- 「そうなると思うな。」（新命題の承認）
- 「じゃあお願い」（骨組み — 体系 / 位置付け / 足りない点 / 締めは著者の判断 — の承認）

Personas:

- primary: Claude Code を毎日使うアプリ開発者。eval という語と Boris Cherny の「goal・測り方・頑張り具合」の投稿は知っているが、自分で eval を組んだことはない。比べる相手は Anthropic の公式 docs。15 分で読む
- inflow: X で Boris の投稿を見て、topic「claudecode」から来た人。LLM-as-a-Judge の日本語記事を 1〜2 本読んだことがある。流し読みで 3 分
- practitioner: 自分で Claude Code / coding agent の harness を組み、eval と LLM-as-a-Judge の日本語記事を読み比べてきた人。Hamel Husain の FAQ も知っている。著者がどこまで考えたかを一番厳しく読む

Central thesis: Eval・Eval ループ・Goal 設定を部品に分けて自分のやり方を置いてみると、私が「Eval ループを回して」と頼んでいたのは、
数で比べて登る eval ループではなく、読んで直す所を探すレビューのループだった。eval ループは、グッドハートを嫌って避けてきた。
（2026-10-12 に命題を書き換えた。旧命題「…どの部品が足りないかを言えるようになる」は、位置付けの結果「足りないのではなく使っていない」で
前提が反転した。著者「うーん、結局Evalループをしてなかったわけだろ？私は、そうなると記事の命題も変わるんじゃないの？」→ 新命題に「そうなると思うな」）

Entry bridge: Boris Cherny の 2026-10-11（JST）の投稿「goal・測り方・頑張り具合の 3 つを渡せば、たいていうまくいく」。
著者は Eval を 2026-02 から作ってきた（learn-eval、llm-as-judge など）が、2 つ目の測り方でいつも止まり、体系が掴めていない。
最近は Opus 5.5 に「Eval を回して」とふわっと頼めば README が良くなるので、なおさら自分が何をしているかを位置付けられない。

Figure plan: 「README でやっていたのは、レビューのループだった」節 → 対比 → 図 1 枚（`images/claude-code-eval-concepts-two-loops.png`、
eval ループとレビューのループを、回る手順・答える問い・止まり方で並べる）。ほかの節は表と箇条書きのまま

Causal spine:

1. 観察 — Boris の 3 点。著者は Eval を作ってきたが掴めず、ふわっと頼んで良くなっている（「ベストプラクティスがわからない状態だ」）
2. 緊張 — 「種々のスキルを作ってきたが、それでもまだ掴みきれていない」。部品の並びが無いと、自分の Eval のどこが厚く、
   どこが欠けているかを言えない。（資料が主に別々の部品を扱うこと — Anthropic のブログは Eval の語、build-eval は Eval の作り方、
   hillclimb はループ、Hamel の FAQ は採点の確かめ方、Boris と Jason Wei は Goal — は orchestrator の整理。本文では各節の
   出典で示し、著者の声にしない）
3. 機序（体系）— Eval（部品と、採点を信じられる条件）→ Eval ループ（部品と、ループが採点の穴も登ること）→ Goal 設定
   （数字の goal は、同じ量を測る道具が先にあるときに置ける。確かめ方の無い条件では、判定役は会話の語を読むだけになる）。
   Claude Code の公式の道具（`/claude-api build-eval`・`hillclimb`、`claude plugin eval`、`/goal`）がどの部品を受け持つかを、各節に添える
4. 位置付け — Contemplative Agent の README の before / after を実物に、README のループを部品に分ける。部品はそろっているが、
   点の使い方が hillclimb と違い、README と記事でやっていたのは eval の部品を使ったレビューのループだった（著者確認 2026-10-12）。
   eval ループの形をしていたのは日次レポートのベンチ（手で組んだ）。28 件の照合は、レビューの指摘がどれだけ当たっていたかとして置く
5. 著者の判断 — README と記事で eval ループをしてこなかったのは、足りなかったからではなく避けてきた。いちばんの理由はグッドハートを
   嫌うこと（Emptiness との結びつきは書かない）。eval ループの側の足りない部品（goal の確かめ方、止めどきの数）を埋めるかは決めていない

Sections（r12 時点）:

0. 導入 — Boris の 3 点、測り方で止まる、「eval という語は人によって指すものが違う気がする」という問い
1. eval は入力・走らせ方・採点でできている
2. eval という語は、人によって指すものが違う — 7 軸の型の表、返すものの 3 分類、evaluator-optimizer とコードレビュー、usage の調査は無い（Deep Research: docs/plans/research/2026-10-12-eval-vs-review-deep-research.md）
3. 採点は、人の判断と揃えてから使う
4. ループは、採点の穴も一緒に登る
5. 数字の goal は、同じ量を測る道具が先にあるときに置ける（/goal は 1 段落に縮めた。専門性の研究は落とした — 著者「2で縮めて」）
6. 私の eval を部品の上に置く — Contemplative Agent の README の実物
7. README でやっていたのは、レビューのループだった — 2 つのループの定義（答える問いで分ける）、対比表、日次レポートのベンチ
8. レビューの指摘は、どれだけ当たっていたか — 28 件
9. 私が決めたこと — 避けてきた。グッドハート。数値の goal を渡せる題材を扱ってこなかった

Selected evidence:

- settled-cherny-1010（XP4）: 入口。goal・測り方・頑張り具合、p95 と BigQuery
- demystifying-evals-1・2: Eval の語（task / trial / grader / transcript / outcome）、capability と regression（1 節）
- build-eval-core-1: Eval の定義（入力・走らせ方・採点）、2 つの承認、15〜100 件、ノイズ床 1/√(n·reps)、採点の選び順（1・2 節）
- plugin-eval-spec-1・2: `claude plugin eval` の grader 6 種と llm grader の 3 票（1・2 節。公式の道具が受け持つ部品）
- hamel-faq-1・2・4・5: error analysis、二値、TPR / TNR、件数、ラベルは文脈を知る人（2 節）
- mtbench-judge-human-agreement-1・4: 採点役と人の一致は条件つき（2 節。使うなら 1 文）
- WR-13 / LP-08: jev で Opus の判定が両方の順序で著者と逆（2 節。著者の 1 例）
- build-eval-core-2、hillclimb の解説記事（台帳の post-3）、skill-dates-1・3: hillclimb の split・analyzer は train だけ・plateau の K≥3・test の delta、train と test の使い方、ガイドの日付と呼び出し名（3 節）
- autoresearch-claude-vs-codex-gaming-1〜4: ループが採点の穴を登った例と、4 点の束（3 節。仕組みの節で追う 1 件）
- hillclimb の objective と budget: ディープリサーチ Q0a が eval-hillclimb.md を出典に挙げる。照合表に行が無いので、本文で断定する前に一次で照らす（3 節）
- verifiers-law-1: 検証しやすさの 5 性質（4 節）
- goal-command-intro-and-evaluator-2・3、GS-07〜09、goal 台帳の /goal #10・#11: `/goal` の判定役は transcript だけを読む、plateau の検知なし、著者の 41 回、同じ条件文の別の読み（4 節。仕組みの節で追う 1 件）
- expertise-verified-success-2・3・5: 完了の定義はユーザーが担う、専門性と検証済みの成功（予備的）（4 節）
- 目録 HI-A01〜A57 と位置付けのメモ §1〜9: 著者の Eval の位置付け（5 節）。代表の候補: learn-eval（A01）、llm-as-judge（A02）、author-calibrated-eval（A03）、skill-comply（A05）、readme-judge と訪問者役（A12・A16）、ペルソナ読み（A40）、jev の prose bench（A53）、CA relevance の holdout（A49）、退役した theme-eval・title-eval（A32・A35）
- AV-04・AV-06、contemplative-agent の commit 3720d79（2026-10-08）と af7f7c7（2026-10-11、PR #12）: CA README の before / after（5 節の実物。抜粋は repo の履歴から取る）
- settled-local-no-invocation（HN-07、BE-01）: 公式 build-eval / hillclimb の起動 0 件（5 節）
- 位置付けのメモの差の一覧、calibration/results.md、RD-04 / HI-A13: 足りない点、28 件の照合、README の通読指摘数（6 節）

Out of scope:

- 記事 A（Eval ループと委任。差し戻しは委任である以上 0 にならない。IV 追補）
- 「なぜ Opus 5.5 で Eval が簡単になったか」（著者の問いだが、体系と位置付けを進めない。載せるなら著者に聞く）
- ハーネスの evals.md の PROCTOR への帰属（ハーネス側の判断。著者へ渡し済み）
- クラウドのセッション（README 一括改稿、ロードマップ）の中身
- 目録 57 件の全件（部品ごとの代表だけを載せる）
- 飽和の理論、捕獲再捕獲、ペルソナ研究の詳細、二値と Likert の比較研究の詳細、自己選好の研究
- Opus 5 ガイドの「検証指示を外せ」と、Boris の「どう確かめるか」の関係
- Claude Code の品質報告の postmortem、Managed Agents の outcomes、Console の eval の退役
