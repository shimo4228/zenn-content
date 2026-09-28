# Plan: lost-referents-in-generated-prose（note エッセイ）— editorial brief

## Context

著者が 2026-09-28 に選んだ問い「LLM が書いた文章で、読み手が『何の話か』を見失うのはなぜか」を、
証拠台帳 `drafts/article-context_lost-referents-in-generated-prose_2026-09-28.md` だけを入力に
1 本の原稿にする。channel は著者の傾き（note）で組む。著者の懸念「材料的には技術的な話に終始しないか」
への答えは下の「技術に寄らないための選択」。この plan の承認 = brief の著者確認。承認後に構成と本文へ進む。

## Editorial brief

**Channel**: note（`note/lost-referents-in-generated-prose.md`、JA 正本・frontmatter なし・ですます発見調）。
EN は後で `prose-translation` → `substack/…-en.md`。reviewer は essay-reviewer + Codex 初見 + fact-checker。

**Reader**: AI を仕事で使い、要約・報告・下書きを AI に書かせている人。AI に「わかりやすく」「専門用語を
使わずに」と頼むのは良い指示だと思っている（仮説）。AI の文章を読んで、滑らかだったのに「で、何の話
だったか」が残らなかった経験がある（仮説）。プロンプト設計や評価の仕組みは知らない前提で書く。

**Central thesis**: 「何の話か分かるか」は、読みやすさとも正確さとも別の問いで、書く AI も確かめる側も
この問いを立てていなかった。だから「わかりやすく」は何の話かを運ぶ名前まで削り、読み手が持たない
書き手の呼び名は素通りで入ってくる。

**Entry bridge**: 毎朝 AI が書く研究レポートは読みやすかった。けれど「一つ目の研究が扱った問題は…」
「別の研究では…」と続き、著者は「どの論文やツールの話なのかわかりにくい」と言った。わかりやすく
という指示が、何の話かの手がかりを消していた。

**Causal spine**（エッセイ 4 段）:
1. Calm story — 朝のレポートの場面。指示は「専門用語を使わずに」「平易に言い換え」（A3）。出てきた文は
   「一つ目の研究が扱った問題は」（A11）。著者の一言（A1）
2. Plunge — この文章は 2 回確かめられて通っていた。著者自身が読み比べで「とても読みやすい」と読み（A7）、
   確かめ役の AI は全部の事実に出典の印が付いていると判定した（A10）。逆向きも起きていた: AI と書いた記事
   には読み手が持たない名前（「朝の記事」B3、「判断」「幻覚」B1）が入り、確かめ役の AI はその「判断」「幻覚」を
   「この記事で最も成功している用語運用」と評していた（V2）。誰も規則を破っていないのに、何の話かが消える
3. Solution（機序）— それぞれの確かめは、別の問いに答えていた。著者への問いは「読めるか」「どこで止まったか」
   （V1）で、著者は材料を開かずに読み、読めると答えた。確かめ役の AI への問いは忠実さで、出典一覧を持って読むので
   「S1 の研究」が解決し、印が付いていれば通る（A10/A11）。書く AI は作業の文脈の中で書くので「朝の記事」が指す
   ものが見えている。そこへ「読みやすさは事実と名前の数で決まる」という読み（A8）が重なり、名前は減らす対象に
   なった。直したのは「研究 1 本につき名前を 1 つ、それ以上は増やさない」（A4）で、著者は「なんのソースが
   わかるようになっただけで、かなり良くなった」（A2）。1 本ずつ読む読み比べでは困らず、毎朝の本番で何本も
   読むときに困った理由は、本文では仮説として置くか問いにする（台帳に根拠なし）
4. Higher Ground — 名前は減らす負荷ではなく、何の話かの錨。減らすのは錨以外。読み手の手に無い名前は、既存の
   語か「やったことの名前」に置き換える（B6）。「読めるか」と「何の話か分かるか」は別々に問わないと、読みやすい
   文章ほど後者を落とす。AI に「わかりやすく」と頼むとき、何の話かの名前を 1 つ残すよう頼み、読み終えて
   「何の話だったか」を一言で言えるか確かめる。それでも見えない残りがあることは開いたままにする

**Selected evidence**:
- A1 / A2: 著者の指摘と、名前を戻した後の評価（入口と解決の実感）
- A3: v7 の指示文（日本語のまま引ける。「わかりやすく」の中身）
- A11: 指し方の 3 例（「S1の研究は」→「一つ目の研究が扱った問題は」→「HAACは」）。第三者の論文名は 1 語だけ
- A7 + V1: 著者の読み比べも通っていた / そのときの問いは「読めるか」「どこで止まったか」で、材料は開いていない（著者確認）
- A10: 確かめ役は忠実さだけを見て、出典の印で満たされる（Q5 だけを平易に）
- A8: 「読みやすさは事実と名前の数」— 名前が削られた理由
- A4: 名前 1 つ・それ以上は増やさない（解決の形）
- B3: 「朝の記事」— 書き手の事情が名前として漏れる例（B4「計測記事」は同じ役割なので落とす）
- B1 + V2: 「判断」「幻覚」を確かめ役が高評価し、著者が「要はスキル呼び出しだろ？」と差し戻した
- B6: 既存の用語は初出で説明して使う、造語はしない（逆向きへの手当て）

**台帳外で確かめた一次ソース（本セッション、2026-09-28）**:
- V1: `~/MyAI_Lab/jev-research-pipeline` commit `797c1fd` の `prose_bench.py` `read_file` — 各 case の稿の上に
  `> [!note]- 材料(claim N 件)` の折りたたみで主張と出典 title を置き、問いは「読めるか」「どこで止まったか」。
  著者は折りたたみを開いていない（2026-09-28 著者確認）。本文が使うのは問いの文面だけ
- V2（台帳 B9 の一部を確認）: session `85d5fc2d` の prose-clarity-reviewer 出力（09-20 07:56Z / 08:42Z）が
  「判断」「幻覚」を「維持」「この記事で最も成功している用語運用」と評価。著者の差し戻しは 23:08Z。
  `2a489f6e` / `748bbe7a` でも reviewer は差し戻しより前に走り、出力に「朝の記事」「計測記事」「手元」「梯子」の
  言及は 0 件。ただしレビュー時の稿にその語があったかは未確認なので、この 2 件は「通過した」とは書かない

**Out of scope**:
- モデル交代（qwen → GPT-5.6 Sol → GPT-6 Luna）の効果。原因の切り分けはしていない（A9 / A17）。触れるなら「確かめていない」と書く
- 長さの話（目安を外しても長くならなかった、A14 / A15）、太字行の計測値（A12 / A13）、holdout 未評価（A16）
- 確かめ役の rubric の全項目、判定器の設計、style-diagnostics・ADR など執筆側の運用（B7 / B8）
- 別台帳（jev-guard-blind-to-local-verify）

**Figure plan**: note は channel contract の Figure plan 対象外。図なし。

**技術に寄らないための選択**（著者の懸念への答え）:
- 軸は「プロンプトの直し方」ではなく「読み手がどこに立って読むか」。直し方の詳細（v10 の全文、rubric）は出さない
- 語の置き換え: プロンプト → AI への指示文 / ベンチ → 読み比べ / 判定器 → 確かめ役の AI / モデル名・版番号は出さない
- 場面は 2 つ（朝のレポート、AI と書いた記事）。数値は使わない
- 残るリスク: 題材がどちらも著者自身の AI パイプラインと記事執筆なので、読者が「自分の話」にするには
  Entry bridge と Higher Ground で読者の場面（AI の要約・報告）へ橋を架ける必要がある。ここが弱ければ Zenn へ戻す

## 承認後の手順

0. brief を変えた著者の発言 2 件（channel を note へ、折りたたみは読んでいない）を
   `drafts/lost-referents-in-generated-prose.corrections.md` の C1 / C2 に積む
1. 構成（節ごとに causal spine の役割 1 つ + 証拠 ID）を提示 → 本文を `note/lost-referents-in-generated-prose.md` に執筆
2. 著者の指摘は `.claude/rules/correction-trailers.md` に従い `drafts/lost-referents-in-generated-prose.corrections.md` に積む
3. 構造凍結 → panel を各 1 回・並列: essay-reviewer / `codex:codex-rescue`（read-only、prose-clarity-reviewer checklist、
   原稿・contract・checklist の path だけ渡す）/ fact-checker（台帳と一次資料の path: jev-research-pipeline の
   prompts・rubric・design、Obsidian daily-research 3 本、session jsonl）
4. 処分記録を 1 行ずつ → 反映 → 著者通読・内容 GO
5. headline-craft → title-reviewer → 著者がタイトル選択 → AI-mediated 開示ブロックの収録・出典末尾編入 → `/quality-gate`
6. 公開は著者 GO 後に `note-publishing`。EN は `prose-translation` → Substack

## Verification

- `/quality-gate note/lost-referents-in-generated-prose.md` が PASS（panel report + 処分記録 + 内容 GO + title findings）
- public-safety: 本文に個人 path・session id を出さない。第三者論文の抜粋は名前 1 語まで
- 公開後 `scripts/corpus.yml` 更新 → `npm run generate:index` → `npm run validate` / `npm run check:index`
