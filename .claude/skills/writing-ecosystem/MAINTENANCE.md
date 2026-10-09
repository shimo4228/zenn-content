# writing-ecosystem — maintenance notes

規則の理由と経緯。SKILL.md からはリンクしない。

## ペルソナ読み（references/persona-read.md）

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
  `scripts/drift_count.py` の語は手書き。カタカナを exit から外したのは、普通の外来語（ケース・ポイント）が毎ラウンド発火したため
  （/code-review の指摘を再現して確認）
- 隔離の確かめ: 2026-10-09、2.1.295 で `--setting-sources ""` だけで repo の中から起動しても著者の rules の見出しは見えず、外すと
  見えた。`--bare` はサブスクの認証を読まない
- 凍結前に置いた理由: 凍結稿への panel 各 1 回（処分規律）を保ち、ADR-0011 が外した reviewer の読み直しに戻さないため
- 未測定: Claude 5 世代と日本語記事での判定の妥当性。Review-when は ADR-0015
