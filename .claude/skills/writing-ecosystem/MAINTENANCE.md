# writing-ecosystem — maintenance notes

規則の理由と経緯。SKILL.md からはリンクしない。

## ペルソナ読み（references/persona-read.md）

- 手順・prompt・照合・drift_count.py は 2026-10-18 に harness の skill: `persona-read-loop`（article preset）へ移した
  （harness の plan `docs/plans/persona-read-skill.html`）。ここに残るのは Zenn の記録の置き場と比較材料。以下はこの repo で
  回したときの出所と実測

- 出所: 2026-10-09 の著者の提案「Readme judgeみたいに記事ごとのジャッジのペルソナを設定してループ回す形にしたらどう？」。
  止めどきは著者の言葉で「私が日本のハーネス構築において並ぶ者がいないほど考えていることがわかるレベルまでにして」。
  決定は ADR-0015、plan は `docs/plans/article-persona-loop.html`、調査は `docs/plans/research/2026-10-09-article-persona-loop.md`
- 先例: `~/.claude/skills/readme-writer/references/visitor-read.md`（訪問者役の読み）。人選の 3 型・隔離の起動形・新しい機能の語の扱いを移した
- 止めどきを「深さの印象」でなく判断の言い直しにした理由: LLM の判定は研究アイデアの質の判別で人間同士の一致を下回り
  （Si et al. arXiv:2409.04109 §7.2）、研究課題の新規性の判定は過大評価の方向だった（arXiv:2606.12071）。as-of 2026-10-09。
  印象で止めると改稿役が権威の語を足して登る
- 比較材料を記録だけにした理由: 参照と並べた採点でモデル側の勝ちが増えたという読み（2606.12071、調査 report の読みで論文は
  pairwise の語を使っていない）。比較を渡す既存実装は見つからなかった
- 3 周の理由: readme-writer の運用に合わせた値で較正していない。改稿 1 回ごとに Clarity が下がり（arXiv:2609.14767、LLM judge の点）、
  同一モデルの反復で最終反復に人間の点が落ちた（arXiv:2407.04549）ので、増やす向きには逆らう。2 との比較は ADR-0015 の Open
- drift の機械 diff の出所: arXiv:2608.28596 の drift 指標（未裏付けの数値・最上級の追加、hedge の除去）。語彙リストは論文に無く、
  `drift_count.py` の語は手書き。カタカナを exit から外したのは、普通の外来語（ケース・ポイント）が毎ラウンド発火したため
  （/code-review の指摘を再現して確認）
- 隔離の確かめ: 2026-10-09、2.1.295 で `--setting-sources ""` だけで repo の中から起動しても著者の rules の見出しは見えず、外すと
  見えた。`--bare` はサブスクの認証を読まない
- 凍結前に置いた理由: 凍結稿への panel 各 1 回（処分規律）を保ち、ADR-0011 が外した reviewer の読み直しに戻さないため
- 未測定: Claude 5 世代と日本語記事での判定の妥当性。Review-when は ADR-0015

## 著者の指摘の記録（処分規律の「著者の指摘を積む」「著者の撤回」「commit へ写す」）

- 出所: 著者の指摘が会話の中で消え、公開物から辿れなかった（harness RFC-0027）。commit を一次記録にする案が harness RFC-0028。
  2026-09-28〜10-12 に zenn-content の rule `.claude/rules/correction-trailers.md`（commit `76bcf5b`）で試した。試行中は
  公開 skill repo へ同期される本 skill を変えなかったので、rule として置いた
- 試行の読み（数えた値と判断の正本は harness RFC-0028 の Status）: triage 2026-10-18 に判断役が数え、`drafts/*.corrections.md`
  7 本に 137 件、試行期間の commit 本文に `指摘:` ブロック 122 件（22 commit）。原文の「」181 個を session ログと照合し、著者の発言に
  一字一句で一致 171、tool の結果に一致 9、出所不明 1、食い違い 0。著者判断は 2026-10-18「続ける」（出所不明の 1 件は確かめずに進める）
- 2026-10-25 に rule の手順を処分規律へ移し、rule を消した（harness RFC-0028 S1）。rule は常駐したが、処分規律は本 skill が
  載ったときに読まれる。writing-ecosystem を通さずに記事を書く経路（detail-loop 等）では、その経路の手順が処分規律のこの 3 項目を指す必要がある
- 積むのを著者の指摘だけにし、修正前の稿を公開しない（抜粋は非公開の `drafts/`）のは、試行開始時に判断役が置いた仮の答え
  （RFC-0028 の Unresolved への答え）を試行がそのまま通したもの。引用と会話の一致を機械で検査する仕組みは持たない

## 外部言説の調査（§1）

- 出所: 2026-10-26、claude.com の記事「サブエージェントを主ループに畳むべきとき」（Diane Sarkis、2026-10-22）を起点に、
  この repo の agent を畳むか残すかを著者と詰めた。reviewer を畳む・統合するかは、凍結稿と処分記録の採用指摘を replay して
  決める（今の版と新しい版を各 3 回、反転した指摘を著者が見る）と決めた
- §1: `theme-reviewer` agent を退役した。2026-09-21（commit b5eebb9）に、経験の報告へ回すと論点が増え、reviewer を
  2 回通った稿が著者の通読で「全体的に意味がわからない」になったため opt-in にした。その後 36 日起動 0 回で、外部言説との差は
  orchestrator の `search-first` と Deep Research の prompt（例: claude-code-eval-concepts の drafts）で調べていた。
  観点を §1 に移さないのは、毎本で論点が増える形に戻るため。経緯は ADR-0011 Decision 1 の注記
