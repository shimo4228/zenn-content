---
title: "ReAct エージェントが本当に必要な業務はどれか"
emoji: "🧩"
type: "idea"
topics: ["ai", "llm", "agent", "architecture"]
published: true
published_at: 2026-04-29 13:12
---

> **用語の更新 (2026-04-30):** [AAP repository](https://github.com/shimo4228/agent-attribution-practice) 側との整合のため、4 象限名のうち 2 つを改名した。(2) 古典 AI 象限 → (2) Algorithmic Search 象限、(4) ReAct 象限 → (4) Autonomous Agentic Loop 象限。スクリプト象限と LLM ワークフロー象限は維持。本文中で象限名として使われていた表記は新名前に置換しているが、ReAct パターン (Yao et al. 2022) や ReAct ループへの言及はそのまま。

## 違和感

AI エージェントを構築している立場から、現行のエージェント製品の README を眺めていて違和感が消えない。

"Run on a $5 VPS"。"Spawn isolated subagents"。"Self-improving"。"Cron scheduling, running unattended"。"Voice memo transcription via Telegram"。

語彙が全部デモのものだ。業務の語彙が一語も出てこない。監査。承認ワークフロー。ロールベースアクセス制御。変更管理。SLA。DR。これらは実務でのデプロイが当然必要とする語彙だが、代表的なエージェント製品の README には現れない。

これは本番運用を前提とした設計ではない、と感じた。本番を射程に入れていないように見える。

最初は「自分が業務寄りの感覚に偏っているだけかもしれない」と思った。だが違った。違和感の正体は別のところにある気がした。**現行のエージェント製品の多くは、ReAct という自律ループをエージェントの本質として前提しすぎている**。ただし業務に AI を入れるとき、ReAct エージェントが正当に必要になる領域は、実装してみると非常に狭い。

## 前提: ReAct はどう動くか

先に ReAct について整理しておく。

ReAct は 2022 年に Yao らが提案した LLM エージェントの動かし方だ。論文タイトルは "ReAct: Synergizing Reasoning and Acting in Language Models" (arXiv:2210.03629)。3 つの要素を 1 セットとして繰り返し回す。

1. **Thought (思考)**: 今の状況をどう解釈し、次に何をすべきかを LLM が言語で考える
2. **Action (行動)**: 検索ツール、ブラウザ、ファイル操作などの外部ツールを呼び出す
3. **Observation (観測)**: ツールから返ってきた結果を読む

このループを LLM 自身が「もう情報が揃った」と判断するまで回す。鍵は **LLM が毎ターン「次の行動」を自分で決める** ことだ。事前に手順を書かないので、何度ツールを呼ぶか、どのツールを使うか、いつ終わるかがすべて実行時に決まる。

なお論文の評価対象は 4 種類のタスクだった。HotpotQA (オープンドメイン QA)、Fever (事実検証)、ALFWorld (家庭環境の interactive 探索)、WebShop (open-ended な商品検索) の 4 つだ。いずれも未知環境での探索や open-ended な情報統合が求められるタスクで、business workflow への適用は論文中に議論されていない。

これが ReAct の力であり、同時に重さでもある。動的に決まるからこそ、業務に当てはめると不要な場面が大半を占める。その腑分けを 4 象限で見ていく。

## 業務 AI を 4 象限で見る

業務に AI を入れるとき、業務の性質を 2 軸で切ると 4 象限に分かれる。

- 横軸: 処理が **決定論で書ける / 意味判断を要する** (= LLM 不要 / LLM 必要)
- 縦軸: ワークフローが **事前定義可能 / 探索的** (= 次の行動を **人間が事前に書いた経路** が決める / **モデルが実行時に動的に** 決める)

縦軸の表現は Anthropic 用語に橋渡しできる。"Building Effective Agents" (2024) で使われる "predetermined code paths vs LLM dynamically directs its own process" が、本質的に同じ概念にあたる。

|  | ワークフロー定義可 | 探索的 |
|---|---|---|
| **決定論で書ける** | (1) スクリプト象限 / pipeline | (2) Algorithmic Search 象限 (本記事の射程外) |
| **意味判断が必要** | (3) LLM ワークフロー象限<br>(3a) 対話 → 専門 chat agent<br>(3b) バッチ → 単機能 LLM 関数 | (4) Autonomous Agentic Loop 象限 (= ReAct エージェント) |

(2) は Algorithmic Search / OR (Operations Research) の領域だ。配送ルート最適化、生産スケジューリング、組合せ最適化などが該当する。これらは A* 探索、動的計画法、Monte Carlo Tree Search、強化学習で解かれてきた。LLM が必要な問題ではないので、本記事の射程からは外す。残る (1) (3) (4) を順に見ていく。

### (1) 決定論 × 事前定義可 — スクリプトで足りる

帳票転記。データ整形。ルックアップ。検証。これは LLM すら不要だ。スクリプトとワークフローエンジンで十分。AI を持ち込む理由がない領域。

### (3) 意味判断 × 事前定義可 — workflow + LLM 関数で足りる

ここが業務 AI の主戦場だ。Anthropic は "Building Effective Agents" の中で、この領域に対応する 5 つの workflow pattern を整理している。具体的には prompt chaining / routing / parallelization / orchestrator-workers / evaluator-optimizer の 5 つだ。OpenAI も "A Practical Guide to Building Agents" (2025) で同じ領域を扱っている。"manager pattern" と "decentralized pattern" が提示されている。

共通する性質は、**経路 (どの順序で何をするか) が事前に決まっており、その経路の中の 1 ステップとして LLM が呼ばれる** ことだ。LLM 自身が次の行動を決めることはない。

業務によって I/O modality が違うので、(3) の中はさらに variant に分かれる。本記事では対話形とバッチ形を見ていく。

#### 対話形

法務相談、診断補助、社内 FAQ、専門知識サポート。判断ばかりの業務。

ここで自律エージェントが必要なのか、私には疑問に見える。**専門知識を持ったチャットエージェント** で足りる場面が多い。これが私の直感だ。RAG + システムプロンプト + (必要なら履歴を保持した) LLM 呼び出しで足りる。人間が最終判断を担い、AI は知識の検索と整理を担う形になる。少なくともこの分担で十分な場面は多そうに見える。

ただし対話業務にも spectrum がある。単純な FAQ なら単発の LLM 呼び出しで足りる。多ターンで条件を詰める法務相談や、tool を呼びながら鑑別を進める診断補助では話が変わる。Anthropic の workflow patterns (prompt chaining / routing / orchestrator-workers) が刺さる場面が増える。それでもなお、**LLM 自身が次の行動を決めるループ** (ReAct) が必要かは別の問題に見える。判断業務の大半は、判断主体である人間が次の行動を決めれば足りるからだ。

判断ばかりの業務こそ自律エージェントが要らないかもしれない。これが私には直感に反する点だ。

判断 = 思考 = エージェントと短絡しがちだ。だが判断業務の思考は **知識の検索と整理** に近い場面が多く、エージェントのループが必要な推論とは別種に見える。

#### バッチ形

請求書マッチング。チケット振り分け。住所の正規化。閾値判定。決定論パイプラインの中に意味判断が点在するパターン。

ここも ReAct は要らない。決定論パイプラインがフローを制御し、例外箇所で単機能 LLM 関数を呼ぶ。LLM 関数の出力は確率的に揺らぐ — 同じ入力に毎回まったく同じ出力が返るわけではない — が、関数として果たす役割は固定されている。「定義された入力を受け取り、定義されたスキーマで判定を返す」という形が変わらない。次に何をするかはパイプラインが知っている。

#### 例: 請求書マッチング

請求書 (invoice) を発注書 (PO) と照合して承認・差戻し・要レビューに振り分ける業務を考える。8 割は決定論で機械的に処理できる。

```python
def process_invoice(invoice: Invoice) -> Action:
    po = lookup_po(invoice.po_id)              # 決定論: PO 検索
    if po is None:
        return Action.REJECT_NO_PO
    if invoice.date > po.expiry:               # 決定論: 期日チェック
        return Action.REJECT_EXPIRED
    if is_duplicate(invoice):                  # 決定論: 重複チェック
        return Action.REJECT_DUPLICATE

    if abs(invoice.amount - po.amount) / po.amount <= 0.01:
        return Action.APPROVE                  # 決定論: 金額が誤差 1% 以内なら承認

    # ここから意味判断ゾーン
    # 金額が合わないが、line item の表現違いで実質一致しているかもしれない
    verdict = match_line_items(invoice.lines, po.lines)  # ← 単機能 LLM 関数
    if verdict == "MATCH":
        return Action.APPROVE
    elif verdict == "PARTIAL":
        return Action.ESCALATE_FOR_HUMAN_REVIEW
    else:
        return Action.REJECT_AMOUNT_MISMATCH
```

`process_invoice` の本体は決定論パイプラインで、判断 (PO 存在 / 期日 / 重複 / 金額) はすべてルールで書ける。意味判断が必要なのは「金額が合わないが、line item の表現違いで実質一致しているか?」という 1 ポイントだけだ。そこで単機能 LLM 関数 `match_line_items(invoice_lines, po_lines) -> Verdict` を呼ぶ。

この関数は「2 つの line items が意味的に対応するか」を判定するだけで、それ以外の責務は持たない。プロンプトは「請求書と発注書の line items を比較して、表現は違っても内容として対応しているか判定せよ。出力は MATCH / PARTIAL / NO_MATCH のいずれか」という単純な指示だ。LLM は schema に沿って判定を返す。入力を渡せば判定が返る (出力自体は確率的なので、稀に揺らぐことはある)。だが次のステップを LLM 自身が決める要素はない。次に何をするかは呼び出し側のパイプラインが既に決めている。

ReAct ループとの違いは明確だ。LLM は「考えて → ツールを選んで → 結果を見て → また考える」の主体ではなく、パイプラインの 1 ステップとして「入力 → 判定」を返すだけの部品になっている。

#### この構造が意味するもの

業務自動化の世界では古くから知られた構造がある。どんな業務にも、決定論ルールで書ける 80% と、そこに収まらない 20% の例外がある傾向だ。この 20% がデプロイのボトルネックになる。長年「より複雑なルール」「機械学習による分類器」「自然言語処理アドオン」などで解こうとされてきたが、本質を解いていなかった。LLM がここに単機能関数として入った瞬間、解ける問題に変わった。

ここで強調したい論点がある。**この例外判断は、もともと人間が手作業でやっていた役割だ**ということだ。人間も毎回まったく同じ基準で判断していたわけではない。同じ請求書を見ても、その日の状況や担当者によって判定は揺らぐ。マニュアルがあっても、最後は人間の確率的な解釈に任せられていた。例外判断は本質的に確率的な仕事だった。

LLM 関数が果たすのも、まさに同じ役割だ。確率的に揺らぐ判断を、揺らぐ仕組みで引き受けるだけ。完全な決定性が要求されない領域だから、LLM の確率性は本質的な障害にならない。むしろ「人間が確率的にやっていたことを、人間相当の判断品質で、低コストで引き受けられる」という意味で、ここに適合した道具に見える。「LLM は確率的だから業務に向かない」という反論は、人間の業務判断がそもそも何だったのかを過大に見積もっているのだろう。

その上で重要なのは、**「汎用エージェント」 が要らない** ことだ。1 カテゴリにつき単機能の関数が 1 つあればいい。50 カテゴリなら関数 50 個だ。汎用に何でもできる必要はない。

### (4) 意味判断 × 探索的 — Autonomous Agentic Loop 象限 (= ReAct エージェントの正当領域)

冒頭で説明した ReAct ループ (Thought → Action → Observation) が必要になるのは、ワークフローが事前に決められず、次の行動をエージェント自身が判断しなければならないタスクだ。

- コーディング (どこを修正すべきか、どうテストすべきか、エージェントが判断)
- ブラウザ自動操作の探索的タスク (操作対象が動的)
- Deep Research (情報の枝分かれが事前に予測できない)

LLM が自分で次の行動を選ばなければ先に進めない。研究的にも実務的にも、ReAct はこの象限のために設計された技法だと言える。Yao らの論文の評価対象 (HotpotQA / Fever / ALFWorld / WebShop) はいずれもこの象限に属するタスクだった。

## カテゴリエラー — エコシステムが (4) を全象限に持ち込んでいる

production 実装では (3) と (4) の境界線上に hybrid pattern が頻出することは先に断っておく。**Plan-and-Execute** (計画は (4) 的に立て、実行は (3) 的に決定論で行う)、**Router agent** ((3) workflow の中で「どの分岐に流すか」だけを LLM 判断にする)、**tiered handoff** ((3) でまず対応し、必要時のみ (4) に escalate する)。これらは「(3) を基盤にしつつ、(4) が必要な箇所だけに限定して使う」設計指針として読める — 本記事の主張の延長線にある。

問題は別のところにある。現行のエージェントエコシステムの喧伝が **(4) のアーキテクチャを全象限に常時持ち込もうとしている** ことだ。これはカテゴリエラー — 性質の異なるものを同種として扱う種類の誤り — に他ならない。

具体的に観察される現象は次のとおりだ。

- カスタマーサポートを自律エージェントで実装する。だが大半は (3) の対話形 (専門チャットエージェント) で済む
- 営業支援をマルチツールエージェントで実装する。だが大半は (3) のバッチ形 (単機能 LLM 関数) で済む
- 業務自動化の高度化を ReAct ベースで実装する。だが (3) の決定論パイプライン + LLM 関数で済む
- 社内アシスタントを自律エージェントとして売る。だが (3) のチャットエージェントで済む

論点を言い直すなら、**ワークフローが事前定義できる業務に、ワークフローが事前定義できない前提のアーキテクチャを持ち込んでいる**、ということだ。

この現象は業界でも認識されつつある。Thoughtworks は "agentwashing" という言葉でこの傾向を批判している。Gartner は agentic AI プロジェクトの 40% 以上が 2027 までに canceled されると予測している。Anthropic 自身も "Building Effective Agents" で *"This might mean not building agentic systems at all"* と述べ、シンプルな解で済む場合はエージェントを建てるなと示唆している。本記事の 4 象限は、こうした業界 consensus を business 視点から再キャストしたものだ。

なお、こういう category error が量産される背景にはマーケティング側の問題があると感じる。LLM の喧伝は「エージェントが思考する」を前提にしている。(3) の地味なチャットエージェント + 決定論パイプラインの語彙はプレスバズに乗らない。「自律!」「自己改善!」の方が売りやすい。だからマーケティングが (4) 象限の語彙で全業務を一括りにする。結果的に (3) の業務に (4) のアーキテクチャを被せる category error が現場で発生する、という構造に見える。

結果としてアカウンタビリティの側で次のことが起きる。

- 必要のない自律性が責任の曖昧さを生む
- 必要のないループがコストを膨らませる
- 必要のないブラックボックスが監査・アカウンタビリティを破壊する

そして技術品質の側でも、必然性の問題がある。(3) の業務は経路が事前に決まっているのだから、ReAct ループの自由度を持ち込む技術的理由が見当たらない。1 ポイントの意味判断に、自律的に次の行動を選ぶ仕組みを被せる必然性がない。

## アカウンタビリティの絵が整理される

(3) のアーキテクチャを取ると、アカウンタビリティの話が一気に整理される。

- LLM 呼び出しごとに入力 / 出力 / 判断内容が明示される
- 「次に何をしたか」はパイプラインのログで完全に追跡可能
- エージェントの自律性に起因する責任の曖昧さが消える
- LLM = プロダクトとして限定スコープでの使用、デプロイ者が責任主体
- 製造物責任のモデルに乗る

これは現行の法制度と何も衝突しない (別記事で書いた [事故のあとで因果を辿れるか](https://zenn.dev/shimo4228/articles/agent-causal-traceability-org-adoption) で詳述した)。単機能関数 + パイプラインと専門チャットエージェントは **責任主体が常に人間 (デプロイ者)** に明確に帰属するので、AI の特別な法的位置を一切必要としない。

ペットを殺せば法的には「物の傷害」として扱われる法体系に (動物愛護法という特別法はあるが、動物に独立した権利主体性は認めていない)、エージェントを「責任を持つ主体」として導入できるはずがない。(3) 象限のアーキテクチャは、その法的現実と最初から整合する。

(4) 象限 — つまり ReAct エージェントが正当な領域 — でこそ、アカウンタビリティ問題は深刻に立ち上がる。だがこれは自律性が本質的に必要な少数領域の話であって、業務全般の話ではない。**業務全般の議論を (4) の語彙で行うこと自体が間違いの起点**だと感じる。

## 実装での裏付け: ReAct エージェントを使う場面と使わない場面

ここまでの議論を支える実装経験を、両象限から書いておく。

### (4) で ReAct エージェントを使ったケース

以前、あるソフトウェアの公式ナレッジが膨大で、人間が必要な情報を探索するのに困難な状態だった現場があった。そこでユーザーの質問を受け取ってナレッジ空間を探索しながら最適な回答を組み立てる Copilot を作ったことがある。

笑ってしまうくらい強力に動いた。挙動は Deep Research 系の探索エージェント — 検索ツールを反復呼び出ししながら回答を構築する仕組み — にそっくりだった。実装の素地は Coursera のプロンプトエンジニアリング講座で学んだ ReAct パターン (Thought → Action [検索ツール呼び出し] → Observation → Thought...) だ。講座で出会ったその構造をナレッジ探索の文脈にそのまま載せた形だった。「未知のナレッジ空間を探索して、答えに辿り着く」というタスクは、(4) 象限そのものだ。次に何を検索するかが事前に決まらない。LLM が前回の Observation を見て次の Action を決める必要があった。

ただ、強力すぎることの裏返しに、制御不能性を感じる場面もあった。ループが目的に向かって走る間、LLM がどんな経路でツールを呼ぶかは事前に予測できない。何ターンかかるかも分からない。途中で枝分かれが膨らむと、目的達成までのエネルギーが制御の効かない暴走に近づく感覚があった。動くものは動く、ただし運用の予測可能性は低い、と感じた。これが (4) 象限の根本性質だろう。その性質ごと業務に持ち込めば、当然コストやアカウンタビリティの問題に直撃する。

だから ReAct エージェントの力は知っている。知った上で、業務に当てはめると (4) は限定的だ、と判断している。

### (3) で ReAct エージェントを使わなかったケース

私が公開している [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) は、こちらの逆側にある。ReAct ループを一切使っていない。

Contemplative Agent は、与えられた憲法 (constitution)、スキル、ルール、アイデンティティに基づいて出力を生成する仕組みだ。本質は任意の規範・役割・スキル定義を引き受ける汎用構造にある。生成パイプラインの各ステップは事前に決まった順序で並ぶ。それぞれが定義された入力に対して定義されたスキーマで判定を返す単機能 LLM 関数として動く。LLM の出力自体は確率的に揺らぐが、どのステップを実行するか・次に何をするかは LLM ではなくパイプラインが決めている。位置づけで言えば (3) — 意味判断 × 事前定義可 — のバッチ形に該当する。

CA で ReAct を検討する場面はそもそもなかった。CA を運用するとき、問題は「どのような基準でどのようなコメントを発するか」しかない。次に何をするかは事前に決まっているので、ReAct ループを回す余地がない。蒸留パイプラインも同じで、毎回違うルートで処理されては困る。LLM の判断自体は確率的に揺らぐが、どのステップでどの判定をかけるかが固定されていることが、運用上の必須要件になる。

だから 4 象限の (4) か (3) かという選択ですらなかった。業務の性質上、(3) しか選びようがない。本記事の 4 象限 framework は、こうした実装上の所与を後から言語化したものに近い。先に framework があって実装したのではなく、実装してみたら framework がそこにあった、という順序だった。

### 適用域を分けるということ

ReAct エージェントを使うべき業務 ((4)) には ReAct エージェントを使い、使わない業務 ((3)) には使わない。本記事の主張は、ReAct エージェントを知らないからの否定ではなく、知った上で適用域を絞り込みたい、というものだ。現行のエージェントエコシステムが落ちている穴は「(4) の道具を全象限に持ち込んでしまう」ことであって、「ReAct エージェントそのものが悪い」ではない。

## おわりに

業務に AI を入れるとき、ReAct エージェントから始めてしまうと象限の選択肢が見えなくなる、と気づいた。

業務をまず腑分ける。判断業務なら専門チャットエージェント ((3) 対話形) で足りる場面が多そうだ。例外処理なら単機能 LLM 関数 + 決定論パイプライン ((3) バッチ形) で足りそうに見える。古典的な最適化なら古典 AI / OR ((2)) の問題で、LLM の出る幕ではない。ReAct エージェントが必要なのは、ワークフローが事前定義できない探索的タスクだけだ ((4))。

現状のエージェントエコシステムが対象としている業務の大半は、(4) ではなく (3) の象限にあると感じている。(4) で実装した経験と (3) で実装した経験を並べてみても、その印象は揺るがなかった。

ReAct エージェントが本当に必要な業務はどれか — この問いから始めれば、アーキテクチャの選択肢が見えてくる、と思うようになった。逆に、この問いを飛ばして「エージェントで全部やる」から始めると、(3) の業務に (4) のアーキテクチャを被せるカテゴリエラーに必ず行き着く。

## 参考文献・関連リンク

### 主要な技術ソース

- Yao et al., ["ReAct: Synergizing Reasoning and Acting in Language Models"](https://arxiv.org/abs/2210.03629) (2022)
- Anthropic, ["Building Effective Agents"](https://www.anthropic.com/engineering/building-effective-agents) (2024)
- OpenAI, ["A Practical Guide to Building Agents"](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) (2025)
- Perplexity, ["Introducing Perplexity Deep Research"](https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research)
- OpenAI, ["Introducing deep research"](https://openai.com/index/introducing-deep-research/)

### 業界批判・予測

- Thoughtworks, ["The dangers of AI 'agentwashing'"](https://www.thoughtworks.com/insights/blog/generative-ai/Agentwashing-and-how-AI-agents-fail-us) (2025)
- Gartner, ["Predicts Over 40% of Agentic AI Projects Will Be Canceled by End of 2027"](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027) (2025)

### 関連記事 (三部作)

- [登れる壁に看板を立てても意味がない](https://zenn.dev/shimo4228/articles/ai-agent-accountability-wall) — エージェントの責任の所在
- [AI エージェントのブラックボックスは二層ある](https://zenn.dev/shimo4228/articles/agent-blackbox-capitalism-timescale) — 説明不能性の構造
- [事故のあとで因果を辿れるか](https://zenn.dev/shimo4228/articles/agent-causal-traceability-org-adoption) — 因果遡及の困難さ

### 関連リポジトリ

- [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) — 本記事の (3) に該当する実装。ReAct ループを使わない決定論パイプライン構造
- [Agent Attribution Practice (AAP)](https://github.com/shimo4228/agent-attribution-practice) — エージェントの責任主体・帰属を扱う研究 repo
- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/react-agent-business-quadrant.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧
