# Editorial brief — harness-stocktake の告知記事

plan: [fuzzy-giggling-pearl.md](fuzzy-giggling-pearl.md)。調査: [research/2026-11-02-harness-stocktake-article.md](research/2026-11-02-harness-stocktake-article.md)。
集計: `~/.claude/docs/plans/research/2026-11-01-state-of-aggregate.md`。

Reader: 検索・feed から来た engineer で、Claude Code の harness（skills / rules / agents / hooks / CLAUDE.md）を自分で育てている人。数秒で用途が分かり、自分の harness で試すか判断できる

Channel: Zenn（`articles/harness-stocktake-after-doctor.md`）。EN は JP の受け入れ後に Dev.to

Author's words:
- 「ハーネスは放っておくと衛生状態が悪化するので、まとめて綺麗にする方法はないかと考えた。なぜなら、こここそあなたの考えがエージェントを通して発露する場だから、これが整理されていないというのは頭が整理されていないのに近い」
- 「新たに考えたわけじゃないけどね、この半年間ECCにこれらの構成スキルをコントリビュートしたりしてきたが、それぞれのパーツを一つずつ拡張したり改善を続けていた。その洗練されたひとつひとつのパーツを統合することが可能だと気づいた」

Personas:
- primary: Claude Code を業務で使い、skill 10〜30 本と CLAUDE.md を自分で書いてきた engineer。`/doctor` は回したことがある。自分の harness で試すかを 3 分で決めたい
- inflow: X の告知か Zenn の claudecode topic から来た人。harness という語は知っているが、棚卸しを定期的にしたことはない。冒頭 1 画面で読み続けるかを決める
- practitioner: 日本のハーネス実践者。自分でも coding agent の harness を組み、ECC や他人の公開 harness を読み比べてきた。「既存の道具を寄せ集めただけか」「数字はどこまで言えるか」を厳しく読む。15 分を使う

Central thesis: harness は持ち主の考えがエージェントを通して出てくる場所で、放っておくと衛生状態が悪化する。半年かけて ECC にコントリビュートしながら一つずつ磨いてきた棚卸しのパーツを統合すれば、まとめて綺麗にできると気づいた — それが harness-stocktake で、私の harness では 192 項目が 2 回の判断で片付いた

Entry bridge: 「harness が散らかっているのは、頭が散らかっているのに近い」という著者の見方から入り、読者自身の harness（いつ書いたか思い出せない skill、誰も読まない rule）に置き換えられる場面を 1 つ置く

Figure plan: 内容 GO の後に埋める（候補: 節 2 の「パーツ 7 本 → 1 枚の report → 判断 2 回」の流れ）

Causal spine:
- 観察: harness は持ち主の考えの出口で、放っておくと悪化する（著者の見立て。時間で変わったことは測っていないので、見立てとして書く）
- 緊張: 棚卸しのパーツは半年かけて一つずつ磨いてきた（skill-stocktake は 2026-02 に ECC へ）。しかし別々に回り、1 件ずつ聞かれるので、まとめて綺麗にならない（著者の発言 2026-10-31「1 個 1 個私に判断を聞く形だから、一括承認しづらい」）
- 機序: パーツ 7 本は判定までを受け持ち、承認と適用は 1 つの契約（1 枚の report → 承認 → task branch で適用 → 完了 report を見て取り込み）に渡す。AKC の Curate phase をこの形で回す
- 看板の数字: 私の harness の初回（2026-10-31）で 192 項目、判断 2 回
- 他人の harness でも汚れは残っているか: 公開 20 本で回すと、非 Keep は docs・skills・assets に偏って出た（各 19/20 run）。rules は 2/20。n = 20 は 1 つの検索 query から選んだもので、母集団の推定ではない
- `/doctor` との関係: native は使用履歴と書き方を見て、こちらは横断の判定・配線・台帳と実物の差を見る。補完関係なので、`/doctor` の後に回す
- 著者の判断（決めたこと）: 統合して 1 本の plugin と Action にした。他人の repo には連絡せず、集計だけを出した。telemetry は入れない
- 著者の判断（決めなかったこと）: 公開 20 本で `/doctor` と比べてはいない。照合も Claude 系の model で、持ち主の判断ではない。plugin 形式の harness は入っていない

Selected evidence:
- 過去記事 `skill-stocktake-design-journey`（2026-02-24）と `ecc-marketplace-contribution`（PR #265）: 系譜の起点
- ADR-0097 Context の著者の発言と Decision 1・2: 緊張と機序
- 親 plan:12（192 項目・非 Keep 74・判断 2 回）: 看板の数字
- aggregate 表 1（source 別の出た run）: 他人の harness の節
- doctor-comparison 結論 3・4（逆向きの指摘、答えが割れる例）: `/doctor` との関係。数字は出さない
- akc-cycle README:69: Curate phase の定義

Out of scope:
- 正答率 57/60、最初の指摘までの秒数、見立ての的中 9/10、大きさとの ρ: 道具の性能を測った数字で、命題を進めない（看板を 1 つに絞る決定）。State of の英語版と CSV（公開 OK の後に plugin repo の `docs/state-of-2026/` へ置く）に回す
- `/doctor` が拾わない 48/74（65%）: n = 1 で看板にしない決定。本文は定性的な補完関係だけにする
- 費用（`total_cost_usd`）
- ECC の有料化と、PR を出さなくなった経緯
- 本文に「ECC に出した」と書くのは、fact-checker が ECC の repo で確かめたパーツだけにする（手元の記録で確かなのは skill-stocktake の #265）
