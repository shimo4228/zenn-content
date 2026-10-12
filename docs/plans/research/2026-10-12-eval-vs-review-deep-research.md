# 非数値のアセスメントは「eval」なのか？— LLMアプリ／コーディングエージェントにおける「評価」と「レビュー」の境界

> 来歴: 2026-10-12、著者が Deep Research（LLM による調査ツール）に依頼して得た出力を、そのまま保管したもの。依頼文は記事「Claude Code の eval」執筆中に作成した（下の「依頼の要点」）。記事本文で使った主張は、別途一次資料と照合している。ここにある引用・判定は調査ツールの出力で、照合していない箇所を含む。
>
> 照合で分かった食い違い（2026-10-12）: Braintrust の “Evaluators are scorers and classifiers.” は一次資料の逐語ではない。実在する文は “Scorers measure quality with numeric scores, while classifiers assign labels so you can group and analyze results.”（https://www.braintrust.dev/docs/evaluate）。

依頼の要点: 「数値を出さない評価（点数も合格率も出さないもの）を eval と呼ぶのか」。主要な一次資料の定義、点数にしない出力の扱い、二値判定、AI のコードレビュー、生成→批評→修正のループ、語の系譜、HCI の質的評価との関係を問うた。

調査時点：2026年10月12日

結論を先に置くと、「数値を返さないから eval ではない」という定義は、主要な一次資料を横断すると成立しません。LangSmith は数値 score と並んでカテゴリカルな value を正式な evaluator 出力とし、Braintrust は evaluator を数値の scorer またはラベルの classifier と定義し、Arize Phoenix では数値 score 自体が optional です。Hamel Husain / Shreya Shankar はさらに明確に、各 eval は “a score or structured review” を返すとしています。

一方で、「自由記述なら何でも eval」でもありません。Anthropic の狭い定義では、入力に対して grading logic を適用し成功を測ることが eval の核であり、transcript を読む行為は grader が正しいか確かめる手段として説明されます。また、manual transcript review は automated evals と並ぶ別の理解手段として列挙されています。つまり「判定基準・成功条件・ラベル・比較・集計を伴わない、自由記述による助言だけ」の位置づけはソース間で割れています。

したがって、質問にある README を persona が読み、「どこで読むのをやめたか」「一つ変えるなら何か」を自由記述し、その場で改稿するループについては、最も誤解の少ない呼称は現在のまま review loop / qualitative review loop です。ただし Hamel / Shankar の広義の用法なら「evals の一部である qualitative error analysis / structured review」と呼ぶ余地もあります。「数値がない」こと自体ではなく、「体系的な判定を返しているのか、それとも生成物について助言しているのか」が、実務上より重要な境界だというのが今回の資料から得られる最も強い結論です。

## 定義：主要ソースは eval をどこまで広く取っているか

**Anthropic — 数値そのものより「grading logic」が必須。自由読解は狭義の eval から分離される。**
Anthropic の 2026 年の記事は eval を「AI システムへのテスト」と定義し、input → output → grading logic という構造を要求します。grader は code-based、model-based、human のいずれでもよく、各 task の scoring は binary でも構いません。しかし transcript を読む行為は grader を検証するための手段として説明され、さらに manual transcript review は automated evaluations と並列の理解手段です。したがって 数値スカラーが定義上必須とは言えないが、何らかの成功判定・採点は必須に近い、というのがもっとも忠実な読みです。

- Source URL — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents — Anthropic — 2026-01-09 — read depth: full — quote: “give an AI an input, then apply grading logic to its output to measure success” — kind: definition / docs

**OpenAI API evals guide — per-example の testing criteria が中心で、必ずしも連続値を要求しない。**
現行ガイドは各 output が要件を満たすかを testing_criteria によって判定する構造を採り、exact/string checks のような離散的な判定も eval に含めます。ここからは「必ず実数 score を返さなければ eval ではない」とは読めません。ただしガイドは再現可能なテスト／測定の文脈にあり、無構造な感想だけを eval と呼ぶ明示例は確認できませんでした。

- Source URL — https://developers.openai.com/ の Evals / Working with evals — OpenAI — 現行 docs、閲覧 2026-10-12 — read depth: full — quote: “conclude if the model output satisfies the requirements” — kind: docs

**OpenAI Evals — framework の定義自体は数値を要件化していないが、benchmark/testing 色が強い。**
README は OpenAI Evals を LLM および LLM systems を評価する framework と benchmark registry と定義します。model-graded evals も含みます。一方、README のトップレベル定義だけから「自由記述レビューも eval」とまでは言えません。

- Source URL — https://github.com/openai/evals — OpenAI — 現行 README、閲覧 2026-10-12 — read depth: full — quote: “a framework for evaluating LLMs and LLM systems, and an open-source registry of benchmarks” — kind: definition / docs

**Google — 現行 Gen AI Evaluation Service は明確に measurement / metrics / rubric 中心。**
Google の現行サービスは生成モデルの quality を「テスト駆動型の評価」と「適応型ルーブリック」で測定し、LLM-as-a-judge と計算型 metrics を提供します。自由記述だけを eval result とする明示例は今回確認できず、Google 側は metric-centric な側にあります。ただし「数値でなければならない」という明文も、検索できた overview にはありません。

- Source URL — https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/evaluation-overview — Google Cloud — 現行 docs、閲覧 2026-10-12 — read depth: snippet — quote: 「テスト駆動型の評価と適応型ルーブリックを使用して、生成モデルの品質を測定します。」 — kind: docs

DeepMind については、「非数値レビューを eval と呼ぶか」という境界を明記した一次資料を今回の targeted search では確認できませんでした。

**Hugging Face — evaluation の公式ツール群はかなり metric / benchmark 中心。**
Evaluate は ML models / datasets の evaluation library とされ、Hub 上では leaderboard、model-card evaluation scores、metrics が中心です。これは「evaluation＝常に数値」という論理的定義ではありませんが、運用上は quantitative evaluation がデフォルトの資料です。

- Source URL — https://huggingface.co/docs/evaluate/index — Hugging Face — 現行 docs、閲覧 2026-10-12 — read depth: full — quote: “A library for easily evaluating machine learning models and datasets.” — kind: docs

**LangChain / LangSmith — 数値不要を最も明確に示す主要ベンダーの一つ。**
LangSmith は evals を「good が何かを分解し、それを measure する方法」と定義します。重要なのは evaluator の feedback schema で、score は numerical metrics、value は categorical metrics に使われ、reasoning/comment も付加できます。さらに Human evaluation は outputs / traces の manual review を含み、annotation queues で structured human feedback を集めます。したがって カテゴリカルな非数値判定は unequivocally eval です。自由記述 comment 単独が eval になるかはより曖昧です。

- Source URL — https://docs.langchain.com/langsmith/evaluation-concepts — LangChain / LangSmith — 現行 docs、閲覧 2026-10-12 — read depth: full — quote: “score for numerical metrics, value for categorical metrics” — kind: definition / docs

**Braintrust — scorer と classifier の両方を evaluator と呼ぶ。**
Braintrust の evaluation anatomy では evaluators は scorers and classifiers です。前者は numerical score、後者は label を割り当てます。よって数値は要件ではありません。ただし UI / docs 上では “Annotate / Human review” が独立した機能領域としても扱われているため、自由記述レビューまで無条件に eval と同一視しているわけではありません。

- Source URL — https://www.braintrust.dev/docs/evaluate — Braintrust — 現行 docs、閲覧 2026-10-12 — read depth: full — quote: “Evaluators are scorers and classifiers.” — kind: definition / docs

**Arize Phoenix — numeric score は明示的に optional。**
Phoenix の evaluator は Score object を返しますが、その numeric score は optional で、categorical label も独立して提供できます。explanation も保持できます。これは「eval result に数値は必須か」という問いへの非常に直接的な反例です。ただし schema が explanation-only の object を実質的な評価として推奨しているかまでは docs から断定できません。

- Source URL — https://arize.com/docs/phoenix/evaluation/how-to-evals — Arize — 現行 docs、閲覧 2026-10-12 — read depth: full — quote: “score | optional | Numeric result” / “label | optional | Categorical outcome” — kind: docs

**Hamel Husain / Shreya Shankar — 本調査で最も明示的に「非数値」を eval に含める定義。**
FAQ は evaluation を systematic measurement of quality とした上で、個々の eval は “a score or structured review” を返すと明記します。さらに error analysis を “the most important activity in evals” とし、人間が outputs/traces を読み open-ended notes を付ける open coding、そこから failure taxonomy を作る axial coding を evals の中心的活動として扱います。ここでは、少なくとも structured review と定性的 error analysis は eval practice の内部です。

- Source URL — https://hamel.dev/blog/posts/evals-faq/what-are-llm-evals.html / https://hamel.dev/blog/posts/evals-faq/ — Hamel Husain, Shreya Shankar — 2025-07-03、modified 2026-09-01 — read depth: full — quote: “returns a score or structured review” — kind: definition / opinion

**Chip Huyen — human evaluation と manual inspection を evaluation practice に明確に入れる。**
Huyen は AI-as-a-judge に全面依存して human evaluation を捨てることを “pitfall” とし、優れたチームは毎日 30–1000 examples 程度を human experts に evaluate させていると述べます。その目的には judge-score の較正だけでなく、user behavior の理解や、人間が読んで pattern/change を見つけることも含まれます。つまり、彼女の用法では 人が読んで質的な insight を得ることが human evaluation の一部です。ただし「完全に無構造な感想を一個返すこと」を一個の eval と定義してはいません。

- Source URL — https://huyenchip.com/2025/01/16/ai-engineering-pitfalls.html — Chip Huyen — 2025-01-16 — read depth: snippet — quote: “all have human evaluation to supplement their automated evaluation” — kind: opinion / practitioner guidance

**Jason Liu — “eval” を実務上の evaluation technique 集合として広く使うが、数値境界の明示定義は確認できず。**
2025 年の RAG evals 記事は複数の fundamental evaluation patterns を整理していますが、今回取得できた一次ページ断片では、「非数値 free-text review 単独でも eval」という明示的な定義までは確認できませんでした。

- Source URL — https://jxnl.co/writing/2025/05/19/there-are-only-6-rag-evals/ — Jason Liu — 2025-05-19 — read depth: snippet — quote: “There Are Only 6 RAG Evals” — kind: opinion / practitioner taxonomy

**Academic survey — “evaluation” は benchmark score だけを意味する語ではないが、文献の中心は methods / benchmarks。**
Chang et al. の survey は LLM evaluation を「what / where / how」の三軸で捉え、task-level だけでなく societal-level の assessment を含む discipline とします。したがって evaluation という学術語そのものを single numerical metric に限定してはいません。ただし survey の abstract は「自由記述 review が単独で eval か」という今回の語用論的境界には答えていません。

- Source URL — https://arxiv.org/abs/2307.03109 — Yupeng Chang et al. — arXiv 2023-07-06、ACM TIST 2024 — read depth: snippet/abstract — quote: “evaluation should be treated as an essential discipline to better assist the development of LLMs” — kind: paper / survey

Weights & Biases / Eugene Yanについては、後述の Not found のとおり、「数値を返さない assessment を eval と呼ぶか」に直接答える一次資料を今回の検索では確保できませんでした。これらについて「yes/no」を推測で埋めることはしていません。

## 非数値出力：critique、structured review、error notes、vibe check は eval なのか

ここでは 三つを分けると資料間の食い違いがかなり整理できます。

第一は categorical judgment、たとえば pass/fail、good/bad、fully_correct/partially_correct、failure-class label です。これは主要プラットフォームではほぼ疑いなく eval output です。LangSmith は categorical value を正式に認め、Braintrust は classifier を evaluator と呼び、Phoenix は categorical label を Score object の正式フィールドにしています。したがって 「非数値＝非 eval」ではありません。

第二は structured qualitative review です。たとえば「この criterion は満たす／満たさない＋理由」「failure category＋説明」「rubric-based critique」のようなものです。Hamel / Shankar はこれを文字通り “structured review” として eval の return value に含めています。LangSmith の evaluator comment / reasoning、Phoenix の explanation もこの方向を支えます。ここでも 数字は不要ですが、評価対象・基準・判断構造は残っています。

- Source URL — https://hamel.dev/blog/posts/evals-faq/what-are-llm-evals.html — Husain / Shankar — 2025/2026 — full — quote: “a score or structured review” — kind: definition

第三が最も境界的な open-ended reading / critique です。Hamel / Shankar は error analysis の open coding で、人が outputs を読み open-ended notes を作る行為を “in evals” の最重要活動とします。ただしこれは「その note 一つ一つが eval」というより、eval methodology / eval development process の一部と読む余地があります。

- Source URL — https://hamel.dev/blog/posts/evals-faq/ — Hamel Husain / Shreya Shankar — 2025-07-03、modified 2026-09-01 — full — quote: “Error analysis is the most important activity in evals.” — kind: opinion / methodology

Anthropic は逆方向の境界を引きます。transcript を読むこと自体には価値を認めつつ、それを grader の correctness を確認するために使い、automated evaluation と manual transcript review を並列に挙げます。したがって Anthropic の taxonomy に従うなら、読む→自由記述 feedback を返すだけの loop は “manual review” と呼ぶ方が自然で、grader による成功判定を加えた時点で eval に近づきます。

- Source URL — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents — Anthropic — 2026-01-09 — full — quote: “manual transcript review” — kind: definition / docs

Chip Huyen の立場はこの二つの中間に見えます。彼女は manual human evaluation を正式な evaluation と呼び、その目的の一つを「output を読んで patterns や user behavior を理解する」ことに置いています。一方で automated judges と human judgments を比較する校正も重視するため、単なる casual eyeballing と systematic human evaluation を同一視してはいません。

- Source URL — https://huyenchip.com/2025/01/16/ai-engineering-pitfalls.html — Chip Huyen — 2025-01-16 — snippet — quote: “Daily manual evaluation serves 3 purposes” — kind: opinion

“vibe checks” について。 今回アクセスできた Chip Huyen 本人の一次資料では human/manual evaluation は確認できましたが、vibe check という語を使って境界を定義する本人の公開テキストまでは取得できませんでした。『AI Engineering』の公式出版社ページは evaluation benchmarks / metrics / AI-as-a-judge を主要トピックとして掲げていますが、公開概要にはその語がありません。したがって、二次的な book review が「Chip は vibe checks を批判する」と要約していることを、一次証拠として採用するのは避けました。

ここで重要なのは、“vibe check” と “qualitative evaluation” は同義ではないことです。今回の一次資料群では、human reading や qualitative judgment 自体を否定するものはむしろ少なく、問題視されるのは ad hoc・基準不明・再現性なし・sampling 不明の eyeballing を性能比較の代替にすることです。Hamel / Shankar の open coding のように、最初は自由記述でも体系的に failure taxonomy へ進むなら、かなり明瞭に eval methodology の内部になります。

この点からユーザーの README-persona の例を見ると、where I stopped reading や one thing to change は 観察・診断・critique であって、現在の形では「success/failure を測る grader」ではありません。Anthropic 流なら review、Hamel / Shankar 流なら qualitative error analysis / structured review に近い、という二重の分類が可能です。

## Pass/fail：二値判定は「数値」なのか、それとも judgment なのか

主要ソースでは binary pass/fail は明確に eval に入ります。 Anthropic は task scoring の形式として explicitly binary を挙げています。ここで重要なのは、まず 一つの task / trial に対する verdict が出て、その後に複数 trial を集計して pass rate が得られるという階層です。つまり「pass rate が数値だから初めて eval になる」のではありません。

- Source URL — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents — Anthropic — 2026-01-09 — full — quote: “binary (all graders must pass)” — kind: docs / definition

Hamel / Shankar も product evals では binary pass/fail を強く推奨する文脈を持ちます。これは曖昧な 1–5 scalar より criterion を明瞭にし、個々の failure を読めるようにするためです。したがって彼らにとって binary judgment は「数値化以前の judgment」であると同時に、集計すれば rate になる eval datum です。

- Source URL — https://hamel.dev/blog/posts/evals-faq/ — Hamel Husain / Shreya Shankar — 2025/2026 — full — quote: “binary pass/fail evals” — kind: opinion / methodology

LangSmith の設計も同じ区別を示します。per-example の categorical value は evaluator output として成立し、それを dataset 単位で aggregate できます。カテゴリカル判定をコンピュータ内部で 0/1 に encode できることと、その評価概念自体が「数値 metric」であることは別問題です。

では 「一件だけ、PASS と返したもの」を単独で “an eval” と呼ぶか。ここは一次資料から community-wide な統一用法を導けません。Anthropic は eval を test と呼ぶ一方で task / grader / harness / trial を区別しており、一件の PASS は厳密には eval の中の grader result / trial result と読むのが安全です。Braintrust、LangSmith、Phoenix も individual evaluator output と experiment/evaluation run を区別します。

したがって記事で用語を厳密にするなら、

binary verdict は立派な evaluative judgment であり eval の構成要素だが、一 verdict だけを “an eval” と呼ぶかはツール／話者依存。pass rate はその verdict 群の aggregate metric。

という書き分けが最も資料に忠実です。

これは今回の中心質問にも効きます。「eval かどうか」を numeric/non-numeric の一本線で分けるより、judgment-producing か、observation/critique-producing かで分ける方が一次資料との整合性が高いです。

## Code review と eval：AI に PR をレビューさせる行為は eval と呼ばれているか

少なくとも今回確認した主要製品の一次資料では、PR を AI に読ませて defects / suggestions / comments を返させる行為自体は “eval” ではなく “code review” と呼ばれています。

**GitHub Copilot — 明示的に “code review”。** GitHub の機能名・docs 名は “Copilot code review” です。これは source code / PR に対して review comments を生成する開発ワークフローとして扱われており、「Copilot という AI システム自体の performance を測る eval」とは別の語彙です。

- Source URL — https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-code-review — GitHub — 現行 docs、閲覧 2026-10-12 — read depth: full — quote: “Using GitHub Copilot code review” — kind: docs

**CodeRabbit — 製品カテゴリそのものが AI code review。** 同社 docs は “AI code reviews on pull requests, IDE, and CLI” と表現します。ここでも reviewer が output に comments / findings を返す行為を eval と呼んでいる証拠は見つかりませんでした。

- Source URL — https://docs.coderabbit.ai/overview/architecture — CodeRabbit — 現行 docs、閲覧 2026-10-12 — read depth: full — quote: “AI code reviews on pull requests, IDE, and CLI” — kind: docs

これに対し Anthropic の coding-agent eval は別物です。agent に repository-level task を与え、その成果を tests や LLM rubric などの graders によって判定するものです。つまり、

- AI がコードを review する → code review application behavior
- その AI reviewer が defects を正しく見つけるかを test set 上で採点する → eval

という二階建てにするのが、Anthropic の eval 定義と GitHub / CodeRabbit の product terminology の両方に最もよく一致します。これは複数資料からの推論であり、三社が共同でこの境界を定義しているわけではありません。

同じ意味で、Claude Code に「この diff の問題点を教えて」と依頼し、その回答を developer が読むだけなら review と呼ぶ方が自然です。その Claude Code reviewer に既知 bug を埋め込んだ 200 PR を与え、検出率・false positives・rubric verdict を測るなら eval です。これは Anthropic の「input + grading logic + success measurement」という定義から直接導ける区別です。

一方、software engineering 文献において “review と eval の境界” を LLM-eval 用語論として明示的に論じる一次資料は今回見つかりませんでした。したがって「software engineering community では必ずこう使う」とまでは言えません。

## Critique loops：generate → critique → revise は eval loop なのか

ここでも “evaluation が内部にある” と “そのシステム全体が eval である” は別にした方が整理できます。

**Anthropic evaluator–optimizer — “eval benchmark” ではなく workflow pattern として分類。**
Anthropic は「一つの LLM call が response を生成し、もう一つが evaluation と feedback を与える」という反復を Evaluator-Optimizer Workflow と呼びます。したがってこのケースでは evaluation は loop 内部の機能ですが、記事全体の taxonomy 上は agent workflow / generation-improvement pattern です。スカラー score は定義上必須ではなく、feedback が中心になりえます。

- Source URL — https://www.anthropic.com/engineering/building-effective-agents および https://platform.claude.com/cookbook/patterns-agents-evaluator-optimizer — Anthropic — 2024-12-19 — read depth: snippet — quote: “another provides evaluation and feedback in a loop” — kind: docs / pattern

**Self-Refine — refinement method。**
Madaan et al. の Self-Refine はタイトルどおり self-feedback による iterative refinement として導入された方法です。生成物について feedback を生成して、それを次の revision に使います。これは「固定 dataset 上で system quality を報告する eval」より、evaluation/critique-like operation を inference loop の中に組み込んだ optimization/refinement method と分類する方が原論文の目的に近いです。

- Source URL — https://arxiv.org/abs/2303.17651 — Aman Madaan et al. — 2023 — read depth: snippet / bibliographic — quote: “Iterative Refinement with Self-Feedback” — kind: paper

**Constitutional AI — critique / revision は training-data generation / alignment procedure。**
Constitutional AI では principles に照らして model が自分の answer を critique し、それを revise する段階があります。その critique は品質判断ではありますが、論文の taxonomy では standalone benchmark eval ではなく alignment/training procedure の一部です。

- Source URL — https://arxiv.org/abs/2212.08073 — Yuntao Bai et al. / Anthropic — 2022 — read depth: snippet / bibliographic — quote: “Constitutional AI: Harmlessness from AI Feedback” — kind: paper

**Reflexion — verbal feedback を learning signal / memory として使う。**
Reflexion は scalar-weight update の代わりに、言語的 reflection / feedback を蓄積して次の trial を改善する “verbal reinforcement learning” framework と位置づけます。したがって、ここでも 非数値 feedback は optimization signal になりうるが、それを benchmark eval と呼ぶ必要はないという例になります。

- Source URL — https://arxiv.org/abs/2303.11366 — Noah Shinn et al. — 2023 — read depth: snippet / bibliographic — quote: “Language Agents with Verbal Reinforcement Learning” — kind: paper

この四つに共通するのは、critique は evaluative だが、その目的が measurement/reporting ではなく次の generation を変えることです。特に Anthropic 自身が “Evaluator-Optimizer” を workflow と呼んでいることは、ユーザーの「review loop」と「eval loop」を分ける語彙にかなり近い先例です。

それに対し hillclimbing / DSPy optimizer / OPRO 型では、候補を objective / metric によって比較・選択することが loop の中心になります。ここでは evaluation signal が「批評文」ではなく search objective として機能するため、「score-driven optimization loop」という呼称がかなり明瞭になります。ただし metric が最終的に categorical evaluator を内部利用する可能性はあるため、「optimizer = 必ず raw numerical human-facing metric」とまでは一般化できません。

この違いを記事用に短くまとめるなら、

- Critique loop: 「何が悪いか」を返して次を直す。
- Eval/selection loop: 「どちらが良いか／合格か」を判定して候補・version を選ぶ。
- Benchmark eval: その判定を dataset 上で系統的に集計し、system performance を理解・比較する。

という三層に分けると、Self-Refine 系と Anthropic の agent-eval 系を無理なく同じ図に置けます。Anthropic の evaluator-optimizer と agent-eval の別々の扱いもこの整理を支持します。

autoresearch については、今回の検索で「critique loop と score-driven eval loop の用語上の境界」を明記する一次資料を確保できなかったため、この比較の証拠からは除外しました。

## 用語の系譜：「evaluation」から複数形 “evals” へ、何が広がったのか

学術 ML の伝統は “evaluation”, “benchmark”, “metric” が中心で、“evals” が発祥語だったわけではありません。 2022 年の HELM は名称そのものが Holistic Evaluation of Language Models であり、scenario / metric を組み合わせて language models を多面的に評価する academic benchmark program の系譜にあります。

- Source URL — https://arxiv.org/abs/2211.09110 — Percy Liang et al., Stanford CRFM — 2022 — read depth: snippet / bibliographic — quote: “Holistic Evaluation of Language Models” — kind: paper

OpenAI Evals は “Evals” を固有名／複数名詞として前面に出した著名な 2023-era project です。 現在の README も “Evals” を LLM systems と benchmarks の framework と定義しています。ただし、今回確認できた一次資料から「OpenAI が evals という複数名詞を発明した」ことを示す証拠はありません。したがって「OpenAI Evals が用語を coin した」と書くのは避けるべきです。

- Source URL — https://github.com/openai/evals — OpenAI — current repo; public project associated with 2023 — read depth: full — quote: “a framework for evaluating LLMs and LLM systems” — kind: docs / project

その後の product/application practice では “an eval” が 一つの behavior test を意味する方向がかなり明確になっています。Hamel / Shankar の “Each eval checks one behavior…” が典型で、Anthropic も eval を “a test for an AI system” と定義しています。この意味では eval は academic な “evaluation study” より、software testing の test case / behavioral check に近い可算名詞になっています。

同時に語義は benchmark score より広くなっています。2025–26 の practitioner tooling では code grader、LLM judge、human evaluator、categorical classifier、structured review、human annotation、error analysis まで eval ecosystem に入ります。LangSmith、Braintrust、Phoenix、Hamel/Shankar がその具体例です。

ただし、「いつ qualitative reading まで語義が広がったのか」という 一本の歴史的転換点は確認できませんでした。むしろ現在も taxonomy が統一されていません。Anthropic は manual transcript review を automated evals と分け、Hamel/Shankar は open-ended error analysis を “in evals” の中心に置くからです。

したがって、歴史について確実に言える範囲は、

benchmark/evaluation の学術用法 → “eval(s)” を可算の behavior test として使う product-engineering 用法 → grader を numeric metric から model/human/categorical/structured judgment まで拡張する流れ

までです。「いま most practitioners が free-text review まで eval と呼んでいる」ことを示す usage survey は今回見つかっていません。 数社・数人の語彙から community-wide majority を推定するべきではありません。

## HCI・質的研究との関係、矛盾点、未検出項目、早見表

LLM 界隈より広い “evaluation” の語義を見ると、非数値 evaluation は全く異例ではありません。

Nielsen Norman Group の heuristic evaluation は usability specialists が interface を principles / heuristics に照らして inspect し、usability problems を発見する方法です。評価結果は issue descriptions を中心にでき、数値の aggregate metric は方法の定義上の前提ではありません。

- Source URL — https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/ — Nielsen Norman Group — 現行版、閲覧 2026-10-12 — read depth: full — quote: “Heuristic Evaluations: How to Conduct” — kind: method / practitioner docs

同じく think-aloud usability testing は、participant が task を進めながら thoughts を verbalize し、researcher が confusion / expectations / breakdowns を観察する代表的な qualitative technique です。ここでも「まず数値を返す」ことは方法の本質ではありません。

- Source URL — https://www.nngroup.com/articles/thinking-aloud-the-1-usability-tool/ — Jakob Nielsen / NN/g — 現行掲載版、閲覧 2026-10-12 — read depth: full — quote: “Thinking Aloud: The #1 Usability Tool” — kind: method / HCI

LLM eval 側からこれに最も近い明示的な橋を架けているのが Hamel / Shankar です。彼らは open coding / axial coding を qualitative research methodologies から適応した方法として説明し、まず outputs を読んで open-ended notes を作り、後で failure categories にまとめます。したがって「定性研究 → LLM error analysis」への借用は明示的です。

- Source URL — https://hamel.dev/blog/posts/evals-faq/ — Hamel Husain / Shreya Shankar — 2025/2026 — full — quote: “Error analysis is the most important activity in evals.” — kind: methodology / opinion

ただし、今回調べた主要 LLM-eval docs から Nielsen、think-aloud、heuristic evaluation を直接 citation して「これも eval だから LLM eval も非数値でよい」と論じる資料は確認できませんでした。Hamel / Shankar の接続先は広く qualitative research methodology であり、HCI 固有の lineage を主張するには証拠不足です。

### Contradictions

最も明確な矛盾は **「manual reading の置き場所」**です。Anthropic は automated evals、manual transcript review、production monitoring、user feedback などを相補的だが別の方法として列挙します。対して Hamel / Shankar は outputs を人が読んで open-ended notes をつける error analysis を “in evals” の最重要活動と呼びます。これは単なる表現差ではなく、eval を「個々の test/grader」と呼ぶのか、「品質を理解する一連の evaluation practice」と呼ぶのかというスコープ差です。

第二の矛盾は measurement の意味です。LangSmith は eval を “measure” と呼びながら categorical value を正式な metric と認めます。Braintrust も numerical scorer と classifier を同格にします。Arize は numeric score を optional とします。つまり少なくともこれらのツールでは measure ≠ necessarily numeric measure です。

第三は free text の地位です。Hamel / Shankar では structured review は明示的に eval output になり、open-ended notes は eval work の中に入ります。しかし Braintrust では free-form human review/annotation に独立した product surface があり、Anthropic も manual transcript review を別項目にします。したがって 「criterion に対する categorical/structured judgment」までは合意が広いが、「助言・感想だけ」になると合意が崩れる、というのが最もよく証拠に合う境界です。

### Not found

今回、site:docs.wandb.ai、weave-docs.wandb.ai、wandb.ai で evaluation/scorer/human evaluation を検索し、Weave docs の直接 URL にもアクセスしましたが、Weights & Biases / Weave が「数値なしでも eval か」を明文化した一次資料を取得できませんでした。直接 docs URL は今回の取得ツールからアクセス不能でした。そのため W&B の欄は推測で埋めていません。

Eugene Yanについても site:eugeneyan.com evaluation LLM evals 等を検索しましたが、本問いの境界を明示する一次テキストを確保できませんでした。

Google DeepMindについては model evaluation / human evaluation を targeted search しましたが、Google Cloud の現行 evaluation service とは別に、「free-text qualitative review が an eval か」を定義する DeepMind の一次資料を取得できませんでした。

“vibe check / beyond vibe checks” は二次的な書評・解説では Chip Huyen の『AI Engineering』との関連が多数見つかりましたが、今回アクセスできた Chip 本人の一次公開テキスト／出版社公開箇所でその語を確認できなかったため、二次資料を根拠に本人の定義として引用することはしませんでした。Chip 本人から確認できたのは human/manual evaluation を重視する立場です。

Self-Refine、Constitutional AI、Reflexionについては書誌・abstract レベルの分類はできますが、今回の web retrieval では各一次論文本文を全文取得できなかったため、その節の read depth を snippet と明記しました。

autoresearch については、本問いの「score-driven optimization と critique-driven revision の境界」を明記する authoritative primary source を確保できませんでした。

そして最も重要な Not found は、「practitioners の何％が non-numeric assessment を eval と呼ぶか」「most people はどう使うか」を測った用語 usage surveyです。したがって本レポートから「コミュニティでは普通こう呼ぶ」と多数派を推定することはできません。

### 早見表

| Source | 数値が必須？ | qualitative reading を含む？ | locator |
|---|---|---|---|
| Anthropic, Demystifying evals | 不明確。数値スカラー必須とは書かないが grading/success judgment は必須 | grader の check として。manual review は automated eval と別枠 | “grading logic”; “manual transcript review” |
| OpenAI API evals guide | No に近い。binary/exact criteria が成立 | 不明確 | testing_criteria |
| OpenAI Evals | 不明確 | 不明確 | framework + benchmark registry |
| Google Gen AI Evaluation Service | 不明確。metric/rubric 中心 | No / 未確認 | evaluation metrics, adaptive rubrics |
| Hugging Face Evaluate | 不明確。実装は強く metric-centric | No / 未確認 | metrics / leaderboards |
| LangSmith | No | Yes。manual human review、comment；categorical value | score vs value |
| Braintrust | No | review は別 surface もある | scorers and classifiers |
| Arize Phoenix | No | explanation を含む。単独利用は不明確 | numeric score optional; categorical label optional |
| Hamel Husain / Shreya Shankar | No | Yes | “score or structured review”; error analysis/open coding |
| Chip Huyen | No と読むのが自然 | Yes。manual human evaluation を明示 | “Daily manual evaluation…” |
| Jason Liu | Unclear | Unclear | There Are Only 6 RAG Evals |
| Chang et al. survey | Unclear。evaluation を単一 metric には限定しない | 範囲は広いが本境界は未定義 | what / where / how evaluation |
| W&B / Weave | Unclear / not found | Unclear / not found | 今回 primary boundary statement を取得できず |
| Eugene Yan | Unclear / not found | Unclear / not found | 今回 primary boundary statement を取得できず |

以上を踏まえると、記事で最も安全かつ説明力のある線引きは次のものです。eval の必要条件を「数字」に置かない。代わりに、対象 behavior と criterion に対して再利用可能な judgment を生むものを eval と呼ぶ。 pass/fail や categorical label、rubric-based structured review はこの条件を満たします。これに対して、生成物を読み「ここで引っかかった」「ここをこう直すとよい」と自由記述して直すだけなら、それを review / critique loop と呼ぶのは非常に防御可能で、Anthropic の狭義 taxonomy とも整合します。

しかし、それを “not an eval” と断言するのも強すぎます。Hamel / Shankar の用法では structured review は明示的に eval result であり、open-ended error analysis も evals の中心です。したがって最も正確な記事上の表現は、**「非数値でも eval になりうる。境界は numeric vs non-numeric ではなく、systematic judgment vs open-ended review にある。ただし後者まで ‘eval’ に含めるかは主要実務家・ベンダー間で統一されていない」**です。
