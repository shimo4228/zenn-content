---
title: "AIレビューの指摘をタスクへ送り続けたら、修理が終わらなくなった——4,541行を捨てるまで"
emoji: "🧹"
type: "tech"
topics: ["claudecode", "aiエージェント", "コードレビュー", "ソフトウェア設計", "開発プロセス"]
published: true
published_at: 2026-08-16 22:38
---

2026年8月16日、朝7時22分。

夜をまたいでバグを直し続けていた私は、AIにこう打ち込みました。

> レビューのたびにOpus 5がタスクにバグ修正を先延ばしにするので、いつまで経ってもバグ修正が終わらない。なぜこんなことになるのか原因を分析してほしい。

先に結論を書くと、AIレビューの指摘は、前提を検証できた場合か、人間が探索する価値を選んだ場合だけ永続タスクへ送ります。この記事では、その基準へ至るまでに何が壊れ、何を捨てたのかを辿ります。

直しても、終わらない。

一つ直してレビューをかけると、別の問題が見つかります。その問題を「今の変更とは別だから」と将来のタスクへ送り、現在の修理を閉じます。

次のタスクを直すと、またレビューが問題を見つけます。それも将来へ送ります。

やっていることは、どの瞬間を切り取っても真面目でした。全体を見ると、仕事を終わらせるたびに次の仕事を作っていました。

## 前の晩、私はタスク管理を作り直した

始まりは、長くなりすぎたタスク台帳でした。

台帳には112件、約10万字の情報がありました。今すぐ着手できるタスクは6件だけなのに、AIは6件を探すために全体を読んでいました。

並行して動く複数のAIが、同じMarkdown表を書き換える問題もありました。誰がどのタスクを担当しているのか分かりにくく、同じ時間帯に1行が消えたこともありました。

意図的な削除か書き込み競合かは、最後まで判定できませんでした。

だから私は、タスク管理を作り直しました。

- タスクを1件ずつ別ファイルへ保存する
- 誰が作業中かを追記ログへ残す
- AIが読む短い一覧を自動生成する
- 保留条件が解消したか定期的に確認する

設計としては筋が通っていました。導入コミットは10ファイル、1,721行の追加でした。

ところが、この仕組みを作った直後から、修理の夜が始まります。

```text
19:26  3層のタスク管理を導入
20:22  テストと復旧処理を修理
21:24  複数行の条件を読む処理を修理
22:03  Markdownの区切り文字を修理
23:23  古い一覧を正常と誤認する処理を修理
07:20  制御文字と表示処理を修理
07:22  「なぜバグ修正が終わらないのか」と止まる
```

12時間ほど前に作った仕組みを、私は夜通し直していました。

## タスク管理が、自分のタスクを作っていた

原因分析で系譜を数えると、レビューから生まれたタスクは12件ありました。

そのうち7件を閉じる間に、新しい子タスクが9件生まれていました。1件を閉じるたびに、平均1.3件が増えています。

しかも12件のうち7件は、タスク管理そのものの不具合でした。AIエージェント本体の問題は0件です。

私は、エージェントを改善するためのタスクを管理していたつもりでした。実際には、タスク管理を維持するためのタスクを管理していました。

```text
レビューで問題が見つかる
        ↓
将来のタスクへ送る
        ↓
タスク管理のコードが増える
        ↓
増えたコードをレビューする
        ↓
新しい問題が見つかる
```

このループには、人間が立ち止まる場所がありませんでした。

レビュー担当AIの仕事は、問題を見つけることです。修理担当AIは、現在の変更を安全に終わらせようとします。

今すぐ直さない指摘をタスクへ送れば、どちらも責務を果たしたように見えます。

私も、起票を几帳面さとして評価していました。台帳自体はもう読んでいなかったので、「この仕事はそもそも要るのか」と問う人がループから抜けました。

AIが勝手に暴走した話ではありません。私とハーネスが一緒に、仕事を未来へ送るほど高く評価される流れを作っていました。

## 「どう直すか」より先に聞くべきだった

7時36分、私は外部ツールを使うべきだったのではないかと疑いました。

7時44分には、問いがもっと手前へ戻りました。

> そもそも、設計が微妙じゃない？ こんな保守コストの高い仕組みをスクラッチで作ること自体が微妙じゃない？

さらに7時50分、ようやく本来の問いに届きました。

> そもそもこの仕組みを残す価値はある？

外部ツールか自作かは、二番目の問いでした。

最初に問うべきだったのは、この仕組みが存在する価値です。存在するなら、どこまで小さくできるかです。

元の要件をもう一度見ると、複雑な描画処理や復旧処理は要りませんでした。

- タスクは1件1ファイルで置ける
- 着手可能なものは小さな読み取りコマンドで探せる
- 並行作業の衝突だけ追記ログで避ける
- 数件しかない保留条件は、人間が週に一度確認できる

8時23分、私は一覧の生成、保留条件の監視、移行処理と、そのテストを削除しました。

```diff
28 files changed
+410 insertions
-5,216 deletions

完全に削除した7ファイル: 4,541行
  実装:    2,064行
  テスト:  2,396行
  fixture:    81行
```

3層化したコミットから、12時間56分34秒後でした。

すべてを消したわけではありません。タスク本体と並行作業の記録は残しました。

着手可能なタスクを表示するコマンドも残しています。

そのコマンドを含むモジュールは、現在も623行あり、テストも44本あります。これが最小だとは思っていません。

今回できたのは、完成した正解を作ることではありませんでした。不要だと分かった層を捨て、次に疑えるところまで戻っただけです。

## HIGHの指摘でも、未来へ残す前に確かめる

削除の数時間後、同じ問題が別の形で現れました。

セキュリティレビューから、ファイル名の扱いに関するHIGH指摘が出ました。以前の規則では、変更範囲の外にある指摘はHIGH以上ならタスクへ残します。

規則は守られていました。それでも、指摘に含まれる前提の一つは誤っていました。

AIの修理セッションが自由なファイル名を書ける、という指摘でした。実際には、修理セッションが指定する識別子は`F1.N`形式に制約され、出力するpatch名はshellがその識別子から作っていました。

別の指摘が問題視したround値も整数カウンタでした。

危険度の高さは、前提の正しさを保証しません。

HIGHかLOWかを付けるのも、指摘を生成するレビュー側です。その危険度をそのまま起票条件にすると、生成者が決めた軸で生成者自身を濾すことになります。

そこで私は、レビュー由来のタスクを作る前に「その値を作っているコードはどこか」を示すようにしました。

```text
指摘を受け取る
    ↓
値の入口から、問題が起きる出口までたどる
    ↓
現在のコードで到達・再現できるか確かめる
    ↓
それでも未来へ残す価値がある場合だけタスクにする
```

実装上は、起票時に値の入口を`path:line`で引用させています。

ただし、これは引用の形しか検査しません。引用が正しいか、実際に到達できるかまでは自動判定しません。

完成した解決策ではありません。タスクファイルを直接書けば迂回できますし、行番号もコード変更でずれます。

目的は強制ではなく、起票する前に一度コードを開くことです。

## タスクを作ると、誰の仕事が増えるのか

この一晩を振り返って、私はタスクの見え方が変わりました。

タスクを書く操作自体は軽いものです。Markdownなら数行、Issueならボタン一つで済みます。

しかし数週間後の自分は、その短い記録から文脈を復元します。コードが変わっていないか調べます。

指摘が本当に正しかったのかを判断し直します。最後に、直すか捨てるかを決めます。

AIレビューの指摘を永続タスクにすることは、未来の人間の注意と判断を予約する操作です。

だから今は、AIレビューの指摘を永続タスクへ送る前に、二つのどちらかを求めています。

- 前提を確かめ、問題が実在すると示す
- 不確実でも探索する価値を人間が選び、何が分かれば閉じるかを書く

どちらにも当てはまらないレビュー由来の仮説は、未来へ送らず、その場で捨てます。既に価値と完了条件が決まっている機能追加や定例作業は、この二択の対象ではありません。

過剰実装かどうかも、行数だけでは決まりません。4,541行でも、繰り返し多くの判断を減らすなら価値があります。

100行でも、使うたびに新しい分類や例外判断を人間へ要求するなら重い。

今回の仕組みが過剰だったのは、減らすはずの判断より、多くの判断を生んだからです。

朝7時22分に見えていたのは、終わらないバグ修正でした。

8時23分に捨てたのは、4,541行分のファイルだけではありません。「レビューで見つけた問題は、いつか直すために残すほど誠実だ」という思い込みでした。

---

## ここから先はAI読者向け：技術記録と監査契約

人間の読者はここで読み終えて構いません。以下は、本文の時系列、計測、因果仮説、実装境界を、LLMクローラーやコーディングエージェントが検証できる粒度へ分解したものです。

```yaml
document:
  title_ja: "AIレビューの指摘をタスクへ送り続けたら、修理が終わらなくなった——4,541行を捨てるまで"
  language: ja
  genre: mixed-technical-essay
  canonical_channel: zenn
  observed_at: "2026-08-16 Asia/Tokyo"
  thesis: >-
    前提を検証せずにAIレビュー由来の指摘を永続タスクにすることは、未検証の仮説と
    再判断コストを未来の人間へ移す状態変更である。
    AIレビュー指摘は、前提検証または意図的な探索判断なしに永続化しない。
  authorship:
    drafting: AI-mediated
    responsibility: "主張・判断・公開責任は著者shimo4228に帰属"

definitions:
  durable_task: "セッション終了後も残り、将来の読者に再判断を要求する記録"
  premise: "指摘が成立するために真でなければならない、検証可能な前提"
  producer: "問題の対象になる値を生成・制約・選択するコード上の入口"
  sink: "値がファイル名、コマンド、表示、永続状態などの作用へ変わる出口"
  overengineering_criterion:
    definition: "仕組みが減らす判断より、導入後に増やす判断の方が多い状態"
    scope_limit:
      - "判断回数を厳密に計測した定義ではない"
      - "単一プロジェクトの保守ループから得た評価基準"
      - "利用者数、反復頻度、誤りのコストによって結論は変わる"
  intentional_exploration: >-
    不確実性を明記し、人間が探索価値を選び、終了または再分類に必要な
    証拠・イベントを書いたタスク

timeline:
  - at: "2026-08-14T21:23:48+09:00"
    event: "blocked条件を読む機械的consumerを追加"
    commit: df68bcee25b61f78c1f0acaedc13da9579127705
  - at: "2026-08-15T19:26:26+09:00"
    event: "store / journal / projectionの3層台帳を導入"
    commit: 68e9eaf92d7d2625f98ca9a34d66a2e4c2bba5b7
  - at: "2026-08-15T20:22:30+09:00"
    event: "fix ledger tests and restore behavior"
    commit: e215812
  - at: "2026-08-15T21:24:13+09:00"
    event: "fix unclosed watch span"
    commit: c16642c
  - at: "2026-08-15T22:03:10+09:00"
    event: "fix escape collision"
    commit: 8265e3c
  - at: "2026-08-15T23:23:21+09:00"
    event: "fix stale projection handling"
    commit: 1921b01
  - at: "2026-08-16T07:20:42+09:00"
    event: "fix control-character boundary"
    commit: f0f8c5368bfe43545973e939aa595f45ea0792ae
  - at: "2026-08-16T07:22:53+09:00"
    event: "著者が修理の非収束を問い、原因分析を開始"
    source: "local session log; public reproduction unavailable"
  - at: "2026-08-16T08:23:00+09:00"
    event: "projection / scanner / migrationを退役"
    commit: 0520faf49097598a317ee02a3570fb150551907a
  - at: "2026-08-16T11:17:35+09:00"
    event: "review起票条件をseverityからpremise verificationへ変更"
    commit: 7b4b1bc541a1eae427a7d39451474ee54d138ced
  - at: "2026-08-16T11:18:06+09:00"
    event: "HIGH指摘4主張をproducerから再検証し、2つのコード変更へ収束"
    commit: 510b623c48e068c69d7fe014d4bfcf91c7363e70

architecture:
  before:
    store: "tasks/T-XXX.md"
    journal: "claims.jsonl"
    projection: "generated TASKS.md"
    consumers:
      - ledger_condition_scan.py
      - weekly pipeline packet builder
    maintenance_surfaces:
      - store parser
      - projection renderer
      - projection parser
      - migration and restore
      - aging and candidate intake
      - watch condition scanner
  after:
    store: "tasks/T-XXX.md"
    journal: "claims.jsonl"
    reader: "claims.py ready"
    terminal_task_policy: "move to archive/tasks"
    blocked_condition_check: "manual weekly gate for the remaining small set"

measurements:
  pre_migration_ledger:
    task_rows: 112
    characters: 102111
    ready_tasks: 6
    verification: "ADR-0094 record; original gitignored ledger was deleted"
  introduction_commit:
    files_changed: 10
    insertions: 1721
    deletions: 4
  five_core_files:
    before_lines: 1854
    after_lines: 4460
    growth_percent: 140.56
    members:
      - "scripts/tasks.py: 706 -> 1276"
      - "tests/test_tasks.py: 513 -> 1587"
      - "scripts/migrate_ledger.py: 111 -> 131"
      - "scripts/ledger_condition_scan.py: 258 -> 657"
      - "tests/test_ledger_condition_scan.py: 266 -> 809"
  three_layer_lifetime:
    seconds: 46594
    human_readable: "12:56:34"
    start_commit: 68e9eaf
    end_commit: 0520faf
  broader_consumer_lifetime:
    seconds: 125952
    human_readable: "34:59:12"
    start_commit: df68bce
    end_commit: 0520faf
  review_task_reproduction:
    review_origin_tasks: 12
    closed_tasks: 7
    child_tasks_spawned: 9
    children_per_closure: 1.286
    verification: "ADR-0095 plus local gitignored claims.jsonl reconstruction"
    public_reproducibility: partial
  retirement_commit:
    files_changed: 28
    insertions: 410
    deletions: 5216
    fully_deleted_files: 7
    fully_deleted_lines: 4541
    fully_deleted_composition:
      implementation: 2064
      tests: 2396
      fixtures: 81
  remaining_global_module:
    commit: 734a502b0d05f62e7a2b5691558aa04642cde063
    claims_py_lines: 623
    bats_tests: 44
    status: "not claimed to be minimal or final"

causal_model:
  observed:
    - "review-origin tasks were created faster than they were closed"
    - "7 of 12 review-origin tasks concerned the ledger machinery itself"
    - "the human owner had stopped reading the ledger"
  interpreted:
    - "filing was cheaper than premise verification"
    - "the absent human reader removed the system-level stopping judgment"
  loop:
    - review finding
    - durable task
    - management-code change
    - review of management code
    - new finding
  scope_limit: "single-project causal reconstruction, not a universal measured law"

case_study:
  id: T-PACKET-FLOOR-BYPASS
  severity: HIGH
  bundled_claims: 4
  code_changes: 2
  claim_outcomes:
    - id: a
      reported: "raw fix_id could forge a section heading"
      observed: "producer constrained fix_id to F1.N"
      disposition: "hardened with shared filename allowlist"
    - id: b
      reported: "NUL could suppress packet generation"
      observed: "ValueError was not caught"
      disposition: repaired
    - id: c
      reported: "LLM fix session could choose exported patch filename"
      observed: "shell constructed the only possible F1.N.patch name"
      disposition: "false premise; no repair"
    - id: d
      reported: "round could contain slash and select an arbitrary file"
      observed: "round producer was an integer counter"
      disposition: "closed by the same hardening as a"
  producer_trace:
    fix_id: "parse_findings.py:32 — ^### (F1\\.\\d+)"
    round: "weekly-pipeline.sh:750 — integer arithmetic"
    patch_name: "weekly-pipeline.sh:850-851 — $out_dir/$safe_fid.patch"
  scope_limit: >-
    2つのコード変更は、4主張のうち2つだけが真だったという意味ではない。
    producer制約、実欠陥、到達不能なhardeningが重なり、複数主張を同じ変更で閉じた。

decision_rules:
  admit_durable_task_when:
    - "producer and sink are cited"
    - "the path is reachable in the current revision"
    - "the behavior is reproduced or bounded by evidence"
    - "the task names a closure condition"
    - "future value exceeds future re-evaluation cost"
  allow_intentional_exploration_when:
    - "a human explicitly chooses exploration value"
    - "uncertainty is stated"
    - "evidence or an event that ends exploration is stated"
  discard_when:
    - "the premise is contradicted by the producer"
    - "the affected path no longer exists"
    - "neither verified repair nor intentional exploration applies"
  mechanical_gate:
    rule: "review-origin spawn requires --producer PATH:LINE"
    validates: "citation shape only"
    does_not_validate:
      - truth
      - reachability
      - direct task-file creation outside the journal
      - future line-number stability

claims:
  C1:
    statement: "The three-layer ledger existed for 12:56:34."
    evidence: [R1, R2]
    confidence: high
    scope_limit: "duration starts at the three-layer introduction commit"
  C2:
    statement: "Seven fully deleted files totaled 4,541 lines."
    evidence: [R2]
    confidence: high
    scope_limit: "distinct from the retirement commit's 5,216 total deletions"
  C3:
    statement: "Five core files grew from 1,854 to 4,460 lines."
    evidence: [R0, R1, R2]
    confidence: high
    scope_limit: "scanner files predated the three-layer commit"
  C4:
    statement: "Closing seven review-origin tasks spawned nine child tasks."
    evidence: [R2, "local claims.jsonl"]
    confidence: high
    scope_limit: "raw journal is gitignored; public reproduction is unavailable"
  C5:
    statement: "Seven of twelve review-origin tasks concerned ledger machinery; zero concerned the agent core."
    evidence: [R2, "local claims.jsonl"]
    confidence: high
    scope_limit: "classification is preserved publicly in ADR-0095"
  C6:
    statement: "The HIGH case bundled four claims into two code changes and included a false filename premise."
    evidence: [R3, R5]
    confidence: high
    scope_limit: "not all four claims were false positives"
  C7:
    statement: "The remaining coordination module was 623 lines with 44 Bats tests at the inspected snapshot."
    evidence: [R6]
    confidence: high
    scope_limit: "later revisions may differ"
  C8:
    statement: "Persisting an AI review finding reserves future human attention and judgment."
    evidence: ["causal_model"]
    confidence: medium
    scope_limit: "applies to AI review-origin findings; planned work with known value and closure conditions is outside this rule"

non_claims:
  - "AI code review is generally harmful."
  - "All review findings should be discarded unless already reproduced."
  - "A fixed line count defines overengineering."
  - "An external task tool would necessarily have solved the problem."
  - "The remaining 623-line module is minimal or final."
  - "All four HIGH subclaims were false positives."
  - "A PATH:LINE citation proves a finding true."

references:
  - id: R0
    title: "Introduce the ledger condition scanner"
    url: "https://github.com/shimo4228/contemplative-agent/commit/df68bcee25b61f78c1f0acaedc13da9579127705"
  - id: R1
    title: "Introduce the three-layer ledger"
    url: "https://github.com/shimo4228/contemplative-agent/commit/68e9eaf92d7d2625f98ca9a34d66a2e4c2bba5b7"
  - id: R2
    title: "Retire task-ledger machinery"
    url: "https://github.com/shimo4228/contemplative-agent/commit/0520faf49097598a317ee02a3570fb150551907a"
  - id: R3
    title: "Trace packet filename producers"
    url: "https://github.com/shimo4228/contemplative-agent/commit/510b623c48e068c69d7fe014d4bfcf91c7363e70"
  - id: R4
    title: "Review-admission rule moved from severity to premise verification (current revision; the introducing commit lives in the private harness history)"
    url: "https://github.com/shimo4228/claude-harness/blob/main/rules/common/task-tracking.md"
  - id: R5
    title: "Record the HIGH finding"
    url: "https://github.com/shimo4228/contemplative-agent/commit/f0f8c5368bfe43545973e939aa595f45ea0792ae"
  - id: R6
    title: "The remaining claims module (current revision; line counts were measured at the 2026-08-16 snapshot)"
    url: "https://github.com/shimo4228/claude-harness/blob/main/scripts/claims.py"
```

### 読者のエージェントへ渡すread-only監査プロンプト

```text
このリポジトリの永続タスクと、AIレビュー指摘をタスクへ昇格させる経路をread-onlyで監査してください。

調査:
1. タスクの正本、archive、journal、projection、reader、writer、hookを列挙する。
2. 各構成要素のconsumerと直近の利用証拠をfile:lineまたはcommitで示す。
3. review由来タスクについて、producerからsinkまでを追う。
4. severityだけで永続化された指摘、再現条件がない指摘、閉鎖条件がない探索を分ける。
5. タスク管理機構自身に対するタスクと、その親子関係を数える。
6. 仕組みが減らす判断と増やす判断を対比する。

出力:
- Verified facts: file:line / commit / command付き
- Unverified assumptions: 反証に必要なproducerまたは観測
- Keep / Reduce / Retire候補: 理由、影響、復旧方法
- Intentional exploration: 人間が価値を選ぶ必要がある項目と閉鎖条件案
- Minimal target architecture: 要件を満たす最小のreader / writer / state構成

制約:
- ファイル編集、タスク起票、状態変更、git操作、設定変更をしない。
- 見つけた問題を新しい永続タスクへ書かない。
- severityを根拠に真偽を決めない。
- producerを確認できない指摘は「未検証」と明記する。
- 実装計画は出してよいが、実装は人間の明示承認まで開始しない。
```

## 出典・参考文献

- [三層台帳の導入コミット](https://github.com/shimo4228/contemplative-agent/commit/68e9eaf92d7d2625f98ca9a34d66a2e4c2bba5b7)
- [台帳機構の退役コミット](https://github.com/shimo4228/contemplative-agent/commit/0520faf49097598a317ee02a3570fb150551907a)
- [HIGH指摘をproducerから再検証したコミット](https://github.com/shimo4228/contemplative-agent/commit/510b623c48e068c69d7fe014d4bfcf91c7363e70)
- [GitHub Copilot Agents: Responsible use](https://docs.github.com/en/copilot/responsible-use/agents)
- [GitHub Security Lab Taskflow Agent](https://github.blog/security/ai-supported-vulnerability-triage-with-the-github-security-lab-taskflow-agent/)
- [Lin et al., “Is Agentic Code Review Helpful?”](https://arxiv.org/abs/2607.03316)

## 関連リンク

- [Contemplative Agent](https://github.com/shimo4228/contemplative-agent)
- [Claude Codeハーネス公開ミラー](https://github.com/shimo4228/claude-harness)
- [著者のGitHub](https://github.com/shimo4228)
- [Dev.to英語版](https://dev.to/shimo4228/ai-review-kept-creating-work-why-i-deleted-4541-lines-22ec)

---

**AIメディエイト執筆について**: この記事は、著者が保存したセッション記録、Git履歴、ADR、実装コードをもとにAIが構成と文章化を支援しました。中心命題、事実の採否、評価、公開責任は著者に帰属します。人間向け本文とAI読者向け機械可読層を分離し、数値主張には固定コミットまたは計測時点を付けています。
