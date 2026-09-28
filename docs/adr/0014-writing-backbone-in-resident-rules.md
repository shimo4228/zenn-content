# ADR-0014: 執筆の背骨を常駐 rule に置き、writing-ecosystem の細則を原理へ畳む

## Status

Accepted

## Date

2026-09-29

本 ADR は [ADR-0010](./0010-channel-values-in-the-resident-layer.md) Decision 2（`writing-ecosystem` が canon を持つ）、
[ADR-0006](./0006-authorial-values-and-editorial-judgment-skills.md) Decision 2（feedback memory を一次資料として残置）、
[ADR-0007](./0007-kaguura-writing-principles-intake.md) の配置表（Craft 規約の正本）、
[ADR-0011](./0011-dismantle-the-eval-layer.md) Decision 4（craft の移し先として「Craft 規約」「語りかけの積極形」を名指し）を
部分 supersede する。各 ADR の該当節に日付つき注記を置く。背骨の前文は [ADR-0001](./0001-content-integrity-principle.md)
（Content integrity）の運用上の置き場になる。ADR-0001 は置き場を指定していないので supersede ではない。

## Context

Plan: [docs/plans/writing-backbone.md](../plans/writing-backbone.md)（承認 2026-09-29）

2026-09-29 の Zenn 稿 `articles/jev-guard-blind-to-local-verify.md` で、凍結稿に panel（`editor`・Codex の初見の読み・
`fact-checker`）を各 1 回回した。panel が拾ったのは事実・日付・帰属の誤りだった。その後、著者が本文を変えた指摘は 10 件で、
うち 6 件は著者の通読で出た。commit `9c28579` の本文に 9 件を原文のまま写した（1 件は写し漏れ）。通読の 6 件は次の型だった。

- 断定が著者の実感より強い（「本来の挙動を損ないます」→ 著者は「損なっているかどうかすら分からない」）
- orchestrator が作った語（「名指し」「次の一手」「口」「コストとして数える」）
- 導入した物を使う前に別の話題が挟まる節の切れ目（`CHECK` の導入と使用の間に別プラグインの話が入った）と、長い節
- 命題から浮いた締めの装置（読者向けの確認リスト 3 項目。著者は「とってつけたよう」「私のケースだけの個別の対策」と指摘）

最後の型は規約が直接の原因だった。`.claude/skills/writing-ecosystem/SKILL.md` のジャンル表は実用記事に
「締めは要約でなく具体的な takeaway」を求め、同じファイルの 4 行下は「テンプレートを満たすために節・装置・例を足さない」
と書いている。`.claude/agents/editor.md` も「結びが読者の持ち帰るものを残す」を検査する。

残りの型のうち、確度と造語には既に規則があった（SKILL の Craft 規約「物や概念は、既存の名前で呼ぶ」と Voice の
「未解決の正直さ」、editor の用語の項）。規則はあったのに、orchestrator も panel も守れなかった。規則が細則として
散らばり、別の規則と食い違っていたことが原因だという読みは仮説で、Review-when の 1 項目目で確かめる。

同じ日に、著者指摘からの価値抽出と、この repo の `.claude/` の generation audit を別々の subagent に行わせた
（どちらも read-only）。規約は 3 層に散っていた。

- `writing-ecosystem` の Craft 規約・Draft craft・AI Slop・Voice・Section Length。症状ごとの細則で、見出し範囲で約 143 行
  （2026-09-29、SKILL.md の 5 節の見出しから次の見出しまでを数えた）
- `.claude/rules/publishing-channels.md` の Author orientation。価値観がチャンネルの値の表と同居している
- auto memory の `feedback_*.md`。19 本のうち執筆に関わるものが 17 本・419 行（2026-09-29 に `ls` と `wc -l` で計測）。
  うち 8 本は退役済み skill を正本として指している

plan の解消表は 18 項目で、うち 14 項目が同じ規則の 2 か所記述や食い違い、3 項目がパスと表記の誤り、1 項目が採らなかった
監査の提案である。memory は fresh-context の reviewer に届かず、stale なポインタ（現行 SKILL に存在しない「語りかけの
積極形」節を正本と呼ぶ memory など）が残っていた。

著者の依頼は「memoryとかに散在しているものもハーネスの規約として一本化して矛盾した指示がClaudeに行かないようにして。
冗長な指示よりも背骨となる執筆方針と価値観の規約となるようにして」。plan の決定点 14 項目は 2026-09-29 に著者が
推奨どおりで承認した。

## Decision

1. **執筆の背骨を新規の常駐 rule `.claude/rules/writing-principles.md` に置く。** 前文（Content integrity と著者の方針）と
   原理 6 本、30 行以内。P1 確度は著者の言葉が上限 / P2 語は著者の発言と一次資料から取る / P3 持ち帰るものは命題そのもの /
   P4 執筆は著者の思考の続き / P5 読者は前から一度だけ読む / P6 証拠は役割で選び発見の順に置く。rules は main loop と
   全 agent プロセスに常駐するので、reviewer へ複製せずに届く。rules が常駐しない入口（別 repo からの `--add-dir`、
   global skill からの参照）のために、`writing-ecosystem` の冒頭に「執筆の前に背骨の rule を読む」を命令形で 1 行置く
2. **`writing-ecosystem` は手順の正本に絞る。** Craft 規約・AI Slop・Section Length・Theme discovery boundary を削除し、
   Draft craft と Voice の規範部分は原理へ吸収する。文レベルの 4 項目（副詞より数値・能動態・平易な言い回し・第 2 稿は短い）は
   `references/style-diagnostics.md` へ移す。引用の検証水準と AI 開示の要素は新規 `references/publication-procedures.md` へ
   移す。自リポ言及の規則は contract を正にして SKILL 側を消す。ジャンル表から「締めは具体的な takeaway」を消す。brief
   テンプレの Causal spine の終端を「著者の判断（決めたこと・決めなかったこと）」にし、Central thesis に確度の条件を 1 句
   足す。図の規約は `zenn-format` の Figures に一本化する。Scope の「執筆時の規範は本 skill と local contract だけ」と
   repo の `CLAUDE.md` の Writing harness 節は、背骨 rule を含む形に直す
3. **reviewer agent は背骨を複製しない。** checklist は「原理に対して本文で観測できること」の検査文として持つ。例外は
   Codex に渡す `prose-clarity-reviewer` で、Codex は Claude の rules を受け取らないので、原理と重なる検査文を自分で持ち続ける。
   食い違いを防ぐため、背骨の原理を変える commit では同じ commit でこの agent の該当項目を確かめる
4. **`publishing-channels.md` はチャンネルの値だけを持つ。** Author orientation は背骨の前文へ移して削除する
5. **執筆の規約を memory に置かない。** 執筆に関わる `feedback_*.md` 17 本のうち、背骨へ移す 13 本と失効した 3 本を削除し、
   Deep Research の主要ソース一覧を持つ 1 本を一次資料として残す。`feedback_*` でない執筆関連の memory 2 本（reviewer の
   モデル階層の判断記録、図の pilot 記録）も一次資料として残す。削除は著者の承認後に行い、削除する各ファイルの要旨は
   plan の付録に写す
6. **global skill の参照を背骨へ付け替える。** `public-comment`・`x-draft`・`readme-writer`・`prose-translation` は
   `writing-ecosystem` の AI Slop・Craft 規約・Voice を正本として指しており、zenn-content 以外の cwd で発火する。削除する節を
   指す行は、`~/MyAI_Lab/zenn-content/.claude/rules/writing-principles.md` と `references/style-diagnostics.md` の path に
   付け替える（harness 側の別 commit）。公開 skill repo `claude-skill-writing-ecosystem` の同期対象に背骨の rule を足す
7. **タイトル関連（Title Conventions、`title-reviewer`、`headline-craft`、contract の Title constraints 列）は本 ADR の
   範囲外とする。** 並行して改訂された（commit `8561849`）ので、その版をそのまま引き継ぐ

## Review-when

- 著者の通読で、同じ型の指摘が 2 稿続けて出る — 原理に穴があるので、該当する原理の文を直す（細則を足さない）。記録は
  commit 本文の「指摘:」ブロック（`.claude/rules/correction-trailers.md` の試行が終わったら、その後継の記録先）で、
  同じ型かどうかは著者が判定する
- `writing-ecosystem` か `.claude/rules/` に、原理の再述でない細則が合計 20 行以上戻る — 背骨化が崩れているので棚卸しする
- rules の読み込み機構が変わる、または `--add-dir` 経由で背骨の rule が載らないことが分かる — Decision 1 の前提が崩れるので、
  置き場を見直す
- Title Conventions が `writing-ecosystem` の外へ出る — Ecosystem Map と Related の title 行を引き直す

## Alternatives Considered

- **背骨を `writing-ecosystem` の冒頭に置く** — 却下。skill なら repo の外の global skill からも path で読めるが、発火した
  ときにしか読まれず、fresh-context の reviewer にはポインタ経由で届く。agent 側に要旨を複製する必要が残り、2 か所に同じ
  規則がある状態に戻る。repo の外からの参照は Decision 6 の付け替えで足りる
- **背骨を repo の `CLAUDE.md` に置く** — 却下。常駐はするが、`CLAUDE.md` は共通の手順を書かず入口と境界だけを持つ規約
  （同ファイル Writing harness 節）で、価値観を足すと役割が混ざる
- **背骨を既存の `publishing-channels.md` に置く** — 却下。Author orientation はここにあったが、このファイルはチャンネルの
  値の表で、価値観が同居していたことが散在の一因だった
- **原理を 5 本にする（P6 を P3 に畳む）** — 却下。証拠の選び方と置き方（旧 Draft craft）を受ける原理が無くなる
- **memory を一次資料として全部残す（ADR-0006 Decision 2 の方針）** — 却下。残した memory が stale なポインタを持ち、
  矛盾した指示の源になっていた
- **細則を残したまま矛盾する行だけ直す** — 却下。症状ごとの規則は新しい症状が出るたびに増え、今回の takeaway 規則のように
  別の規則と食い違う。依頼は「冗長な指示よりも背骨」

## Consequences

- 同じ規則が 2 か所にある組は、Decision 3 の `prose-clarity-reviewer` を除いて無くなり、main loop と reviewer が同じ背骨を読む
- 規約の総量は plan の見積もりで約 1,360 行から約 1,080 行（skill + references + rules + agents）
- この repo では、執筆以外の作業でも背骨 30 行が常に読み込まれる
- 原理から判断を導く分、細則よりも解釈の幅が出る。reviewer の試走（plan の C3）と Review-when の 1 項目目で見る
- memory の削除は git の外で戻せない。要旨は plan の付録に残るが、memory が持っていた originSessionId と生の事例は失われる。
  今後の事例は commit 本文の著者指摘に残る
- global skill 4 本の参照行を直す harness 側の commit が要る。直すまでの間、それらの skill の参照先の節は存在しない
