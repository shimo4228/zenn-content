# Plan: writing-backbone — 執筆規約を背骨（方針と価値観）に一本化する

## Context

2026-09-29 の記事 `jev-guard-blind-to-local-verify` の執筆で、著者の通読指摘 C1〜C10 の大半が
「reviewer が見ない層」（確度・語・節の切れ目・テンプレの装置）に集中した。原因を辿ると、
規約が症状ごとの細則として 3 層（writing-ecosystem の Craft / Draft craft / AI slop / Voice、
contract の Author orientation、auto memory の feedback 18 本）に散り、互いに食い違っていた
（例: SKILL の「締めは具体的な takeaway」と「テンプレのために装置を足さない」）。

著者の依頼（原文）: 「memoryとかに散在しているものもハーネスの規約として一本化して矛盾した
指示がClaudeに行かないようにして。冗長な指示よりも背骨となる執筆方針と価値観の規約となるようにして」

材料: 著者指摘からの価値抽出と zenn-content の generation-audit（Fable 5.1 subagent 2 本、
統合メモは drafts/ に非公開で保存）、それを受けた Plan agent の設計。著者は 2026-09-29 に
決定点 14 項目をすべて推奨どおりで承認した。

## 背骨: 前文 + 原理 6 本（新規 `.claude/rules/writing-principles.md`、30 行以内）

- **前文**: 中心命題・主張・構成は著者の判断が決める。著者は、読者がものの見方を更新し、自分の
  目的・前提・進む方向を問い直せる文章を重視する。原理は判断の補助で、守った結果が不誠実になる
  なら原理の方を破る（吸収元: SKILL Content integrity、Craft 末尾、contract Author orientation）
- **P1 確度は著者の言葉が上限**: 事実・数値・観察は断定し、評価と因果は著者が対話で言った強さで
  書く。現在形の主張は今日の観察で支え、日付のある発言は経緯として引く
- **P2 語は著者の発言と一次資料から取る**: 物と概念は定着名で呼ぶ。orchestrator は総称・比喩・
  言い換えラベル・硬い言い回しを作らない。別の記事に貼っても通じる文は著者の観察に置き換える
- **P3 持ち帰るものは命題そのもの**: 因果線は著者の判断（決めたこと・決めなかったこと）で終える。
  要約・教訓・手順・チェックリストの装置を足さない。未解決のまま終えるのも判断
- **P4 執筆は著者の思考の続き**: 考えが進んだら本文の厚みとして戻す。前提が反転したら継ぎ足さず
  著者に聞く。未検証の推論は Out of scope に落とす前に「今確かめるか、未検証と書くか」を聞く
- **P5 読者は前から一度だけ読む**: 既知の語で開く。導入した物は使い切るまで別の話題を挟まない。
  時間は一直線、錨は 1 本。節は発見の数で割る
- **P6 証拠は役割で選び、発見の順に置く**: 台帳を節に割り付けない。主張が先、数値の前に実物 1 件。
  仕組みの節は 1 件を追う。証拠の全文は本文の外へ

置き場を rule にする理由: rules は main loop と全 reviewer agent に常駐し、agent 本文へ複製せずに
届く唯一の層（ADR-0010）。コストは非執筆タスクにも 30 行が載ること。

## 置き場と畳み方

- `writing-ecosystem/SKILL.md`（459 → 約 225 行）: 手順だけにする。Craft 規約・AI Slop・
  Section Length・Theme discovery boundary を削除、Draft craft と Voice は原理へ吸収、ジャンル表は
  3 行（「締めは takeaway」を消す）、エッセイ 4 段構成は残す。brief テンプレ: Central thesis に
  「確度は Author's words のまま」、Causal spine の終端を「著者の判断」、Out of scope に P4。
  図の規約は zenn-format の Figures に一本化（SKILL は 1 行ポインタ）。引用の検証水準と AI 開示は
  新規 `references/publication-procedures.md` へ。自リポ言及は contract を正にして SKILL 側を削除
- **凍結**: Title Conventions、§5 Title、Map / Related の title 行、title-reviewer、headline-craft、
  contract の Title constraints 列（並行する title-harness セッションの領分）
- `references/style-diagnostics.md`: 残す。文レベルの 4 項目（副詞より数値、能動態、平易な言い回し、
  第 2 稿は短い）を移す。症状語の表は追記を止める旨を冒頭に
- `publishing-channels.md`: Author orientation を背骨の前文へ移して削除、冒頭説明を更新
- reviewer agent: 背骨は常駐するので複製しない。checklist は「原理に対して本文で観測できること」の
  検査文に。prose-clarity-reviewer は Codex に渡すので自己完結のまま、ポインタ文言だけ直す

## 矛盾・重複の解消（18 組 → 0）

1. SKILL 締めの takeaway ⇄ 装置を足さない ⇄ editor:65,72 → P3（takeaway 削除、editor を検査文に）
2. brief の Causal spine 終端「読者の判断・行動」→ 著者の判断
3. essay-reviewer の宣言調ラプス禁止 ⇄ 事実は断定 → P1 の検査文に
4. 既存の名前 / 比喩 ⇄ eli5 比喩 1 個 → P2 + zenn-format（hero 比喩は P2 の唯一の例外）
5. editor / essay-reviewer / fact-checker の「Use PROACTIVELY … substantially revising」⇄ panel は凍結時 1 回 → 「writing-ecosystem が凍結稿へ 1 回 dispatch」
6. editor の職掌「構造・コード…」4 箇所 ⇄ editor はコード照合をしない → 統一
7. 「global writing-ecosystem / quality-gate / title-reviewer」表記 ⇄ 実体は project-local → 是正
8. Section Length 30% ⇄ essay-reviewer 論点 4 → P5、閾値は判定側
9. SKILL 自リポ言及 ⇄ contract → contract
10. contract Author orientation ⇄ SKILL の参照 → 前文
11. Theme discovery boundary ⇄ §1 → §1
12. N reasons : N questions → 削除
13. SKILL 図 ⇄ zenn-format Figures → zenn-format
14. memory の「語りかけの積極形」⇄ SKILL に節が無い → memory 削除（復活しない）
15. editor Example 3（TDD に説明を足す）⇄ P2 → 削除
16. MEMORY.md のペース正本パス誤り → 修正
17. MEMORY.md「機械チェックは validate のみ」⇄ ADR-0012 → 修正
18. devto-translator「必ず読む」の平文化案 ⇄ ADR-0010 D7 → 平文化しない

## 監査項目の処分

- 採用: R2, R3, F1, F2, F4（Step 見出しを畳む。claim 種別表と verdict 尺度は原文のまま）, F5, F8, B1〜B3, B5〜B10, 追加 1 行（P4）, editor に「断定の強さ」1 項目
- R1: fact-checker の git / jq 手順を「orchestrator が抜粋を dispatch prompt で渡し、agent は Read / Grep で照合」に書き換え（Bash は足さない）
- 不採用: R4（emoji は format pin）, F3（article-stocktake の script 化）, F6, F9（ADR-0013 の手順）
- B4（タイトルの目的）: title-harness セッションへ引き渡す

## memory の処分（git 外。削除は著者承認後、C5）

規約へ移して削除（13）: article-structural-review-patterns, dated-quotes-are-history,
decide-here-and-ask-before-discarding, draft-from-discovery-not-ledger, linear-time-one-anchor,
premise-flip-restart-from-brief, reader-open-axis-for-tool-reports, reader-problem-not-author-framing,
specificity-vs-clarity, writing-as-thinking（以上 P1〜P6 へ）、content-integrity（前文・ADR-0001）、
dedup-consolidate-over-pointer（ADR-0010）、review-cadence-and-no-paragraph-cap（処分規律）

失効で削除（3）: eval-purpose-deepen-not-select（ADR-0011）、lint-timing（textlint 撤去済み）、
reader-address-positive-form（指す節が無い）

一次資料として残す: architectural-argument-deep-research（Deep Research ソース一覧。バナーを P1/P5 へ）、
writing-env-design（reviewer モデル階層の判断記録）、visual-first-eli5-figures（パス 1 行修正）。
無関係で残す: branding-shift、article-quality、各 pipeline memory。

MEMORY.md: 「執筆プロセスの学び」節を「規約は repo の rules/writing-principles.md と writing-ecosystem。
memory には置かない」の 1 行 + 一次資料 1 行に。構造レビューパターン・Content Integrity の行を削除、
機械検査とペース正本の行を修正。

## 実行手順（branch `writing-backbone`）

- C0 `docs(plan): writing-backbone` — 本ファイル単独
- C1 `docs(adr): ADR-0014` — 背骨を常駐 rule に置き細則を原理へ畳む。ADR-0010 D2・0007・0006・0011 D4 に注記。adr-writer の evidence と adr-reviewer
- C2 `refactor(writing)` — 背骨 rule 新設と SKILL の畳み込みを 1 commit で（2 版が同時に存在する window を作らない）。skill-creator の手順: intent packet → 草稿 → fresh-context subagent の named verdict → 著者通読
- C3 `refactor(agents)` — editor / essay-reviewer / prose-clarity-reviewer / fact-checker を背骨の検査文に。skill-creator の草稿ゲート。試走: 内容 GO 済みの jev-guard 稿に新 editor を 1 回 dispatch し、新規 CRITICAL が出ないことを確認（記事には反映しない）
- C4 `docs(harness)` — global 表記の是正、llms-full.txt と docs/CODEMAPS の追従
- C5（git 外）memory の処分
- harness 側の別 commit: harness-sync で公開 skill repo に rules/writing-principles.md を同梱

検証: `npm run validate`、`npm run check:index`、harness_lint、skill-health の参照検査（dangling 0）、
「Craft 規約 / Section Length / 語りかけの積極形 / Author orientation」の grep が ADR 注記以外 0 件、
Title Conventions ブロックの diff が空。

title-harness との合流: 本 plan は Title 関連に触れない。先に main へ入った側を正とし、後の側が rebase
する（Title ブロックは title セッションの版を採る）。両方が入った後、タイトルの誠実さを P1 へ寄せるかを
1 commit で決める。

## 見積もり

規約合計（skill + references + rules + agents）約 1,360 → 1,080 行（−21%）。SKILL の規範部分
約 180 → 46 行。memory の執筆 feedback 18 本・約 430 行 → 3 本。同じ規則が 2 か所にある組 18 → 0。
