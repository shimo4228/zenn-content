kind: external
# Zenn 技術記事を、ペルソナ設定した隔離 LLM 読み手の反応で改稿ループする eval の設計に効く外部知見

as-of 2026-10-09。notes 5 本（prior-implementation / judge-validity / ja-harness-landscape / adversarial / primary-check）の統合。notes に無い主張は足していない。取得は WebFetch の要約モデル経由が多く、引用は「取得ツールが返した逐語」で原文との完全一致は未確認。

問いの前提: 本文の確度は著者の言葉が上限。ループは見せ方を直せるが主張や格付けを足せない。止めどきは著者の言葉で「私が日本のハーネス構築において並ぶ者がいないほど考えていることがわかるレベル」。ADR-0011（2026-08-23、article-judge と改稿ループの廃止）を著者が supersede する選択をした。

## Scope searched

- 第 1 波（4 角度）: 既存の手法と実装（検索 4 + fetch 8）/ LLM 読み手判定の妥当性（検索 8 + fetch 7）/ 日本語ハーネス言説の地図（検索 8 + fetch 約 12、Zenn 公開 API を 2026-10-09 に取得）/ 改稿ループの失敗と別の枠組み（検索 6 + fetch 2）。
- follow-up（primary-check）: 決め手 4 件（2609.14767、2608.28596、first-reader、2407.04549）の arxiv abs/html と github tree/raw を確認。
- 見つからなかった範囲:
  - 日本語で「読者ペルソナ LLM で技術記事を改稿ループ」を実装・実測した公開事例（検索 2 回で 0 件）。
  - 「著者の専門性・考えの深さ」を LLM が判定し人間専門家と照合した研究。
  - Claude 5 世代で測った研究。
  - 日本語技術記事を対象にした judge 研究。
  - 「ループの止めどき」を統計的に示した公開事例。
  - Qiita / note / 登壇資料 / X の本文精読。

## Found

設計の判断点ごとに並べ直した。verdict は primary-check が付けたものだけを併記する。付いていないものは「本文」「snippet」など読んだ範囲を書く。

### 1. 読み手の隔離

**1-1. Dify docs「Reader Experience Test」skill**（langgenius/dify-docs `.claude/skills/dify-docs-reader-test/SKILL.md`、WebFetch 要約で逐語ではない。約 169 stars、実運用）
- subject: 公式 docs 1 ページごとの検収。persona は rule pack から逐語コピー。
- 隔離: fresh subagent。書いた内容・変更理由・source・書き手の懸念を渡さない。ファイルは絶対 path で渡し検索禁止（足りない物は探す理由でなく finding）。比較対象の doc は渡さない。
- 止めどき: 書き手が各指摘に「直す / 別 page へ移す / 理由付きで却下」の立場を取る。Needs revision なら直して新しい subagent を立てる（再利用しない）。Clear か owner の受容まで。
- 我々との違い: verdict 3 段（Clear / Minor gaps / Needs revision）。偽陽性（知識外の語）対策の記述は要約から確認できない。
- 移せる部分: 「却下してよい」と「毎回新 agent」。

**1-2. first-reader skill**（Shubhamsaboo/awesome-llm-apps `agent_skills/first-reader`。実パスは primary-check で確認。`awesome_agent_skills/` は 404）
- primary-check verdict: **supported**（実在）。ただし SKILL.md 全文の逐語は取れず要約。
- 構成: 2 人（共感型と懐疑型）。priors・状況・patience budget・一文の stake。persona は `.first-reader/audience.json` に保存して次稿も同じ人を使う。stake が書けなければ先にそれを報告。
- 読ませ方: skim gate → 1 passage ずつ lookahead 無しで針 -2..+2 と離脱理由。点数なし、修正案なし、「Never rewrite the draft」。draft が context に入っていたら汚染として報告に書く。反復ループは持たない（単発の読み）。
- 隔離の実態（primary-check）: `recall.py` は subagent を起動せず（`claude -p` も呼ばない）、log を読んで preamble と quiz を stdout に出すだけ。隔離は docstring の "hand a FRESH agent only the reading transcript" による**運用で、強制ではない**。
- 根拠の種別: 公開 skill の設計。採用実績・人間 reader との一致検証の記載は未確認。
- 移せる部分: stake を書けない場合は設計欠陥とする点、点数を出さない点、no-rewrite 規律（「見せ方は直せるが主張は足せない」制約と整合）。

**1-3. readme-writer の訪問者役**（`~/.claude/skills/readme-writer/references/visitor-read.md` と `evals/read-through-log.md`、全文読了、自作）
- 3 人（主な利用者 / 流入経路から来た人 / 代わりを知る懐疑派）を全ラウンド固定。本文をラウンドごとに凍結（r0, r1…）。隔離 `claude -p`、model: sonnet、ツール無し、執筆文脈無し。
- 実績: 2026-10-07〜10-09 の 5 件で併用。10-08 は r2 で would_try が動かず止まった。akc-cycle は 3 人全ラウンド maybe で、残りは事実不足。
- 注意: ログの「通読指摘数」は訪問者役でなく最終判定器(readme-judge)の誤り率の KPI。**訪問者役単独の妥当性を示すデータではない**。
- 偽陽性の実例: 10-09 harness-scope は、読み手の知識カットオフ前で「Mod が分からない」が偽陽性だった。見える本文から入口の語を外したのが誤り。対策は visitor-read.md「新しい機能の語」節。

**1-4. Pan et al.「Spontaneous Reward Hacking in Iterative Self-Refinement」arXiv:2407.04549（2024-07）**
- primary-check verdict: **partial**（構造は supported、具体数値は本文に無く図のみ）。abs と html 本文を読んだ。
- subject: 出願エッセイの改稿、author と judge に同一モデル（gpt-3.5-turbo-1106、GPT-4）。人間は Upwork の annotator（html の表記 "2323 annotators" は 23 人と解釈）、各 essay を 3 人が採点。
- 結果: online judge（改稿履歴を共有）の点は人間より大幅に高く、人間は最終反復で品質低下、online judge は plateau。offline judge（1 本ずつ独立に読む）は GPT-3.5 で人間と同程度。GPT-4 は点が inflated のまま逆向きの傾向は出ない。author と judge が文脈を共有すると hacking が出る。要因は model size と context の共有。
- 我々との違い: 2024 年のモデル、essay 編集、1 課題。我々は改稿役と読み手が別プロセスで読み手は隔離（offline 型に近い）。ただし両方 Claude 系なら共有ブラインドスポット仮説（論文の仮説、未検証）は残る。
- 移せる部分: 読み手に改稿履歴を見せない、反復数の上限、人間採点を数件抜いて乖離を監視。

**1-5. Impressona（Benharrak et al., CHI'24, arXiv:2309.10433v2）/ Proxona（arXiv:2408.10937）**
- 先頭 100k 字を読んだ（Impressona）。GPT-3.5、2 study 計 16 writers。persona は書き手が 4 欄（Role/Task, Background, Style, Content）で定義。実在の人物や専門家に見立てる戦略が作りやすい。16 人中 12 人が feedback で本文を変更。
- 失敗: 冗長、抽象的で具体例なし、persona 属性の復唱、制御困難。Proxona は根拠のない persona が誤誘導・ステレオタイプのリスクと述べ、実チャンネルのコメントで grounding する（snippet）。
- 違い: 読み手と書き手が対話する人間主導で、我々は自動ループ。移せる部分: persona は短く具体に、実在人物・実読者の反応で grounding。

### 2. 読み手に答えさせる形

**2-1. first-reader の recall test**（primary-check: supported、ただし要約）
- 別の fresh subagent が transcript だけから quiz 6 問に答える。sayback「retell the piece in one sentence」、pointing「quote any exact words or phrases that stuck」、peak、ending、center of gravity、one action。step 1 で決めた intended gist set と照合。"Nothing survived" は reader でなく piece の findings。
- 移せる部分: 止めどき目標「考えの深さが伝わる」を、点数でなく「何が残ったか」の再話と intended gist の照合で測る手がかり。ただし「深さ」の妥当性は誰も検証していない。

**2-2. 出力形式の比較**
- Dify=5 欄（Got stuck at / Didn't understand / Missing context / Wanted but didn't get / Verdict）、first-reader=点数なし、自作=JSON 8 欄（would_try yes|maybe|no と理由）。いずれも点数より「止まった箇所・分からない語・欠けた文脈」を返させる。
- Zimmerman「Synthetic Reader Panels」arXiv:2602.14433（2026-02、HTML 要約。完全精読ではない）は点数型（JSON + 0-10）で、人間より高い positivity、点の圧縮、recency、articulation premium（文章が巧いと評価が上がる）を報告。anti-anchoring 指示と SlopDetector（点の一様化 std<0.3 など）を持つ。人間検証は 1 imprint の編集者評価で小規模。対象は書籍コンセプトで技術記事ではない。
- Patient 向け退院指示の読み手シミュレーション arXiv:2501.06964（snippet）: 事実的項目の一致 58.38%、知覚的項目 51.56%、LLM の回答は狭く集中。RADIUS arXiv:2603.19002（本文）: 順位は取れても分布・絶対値は信頼できない。いずれも別領域。主観的な反応ほど再現性が低く分散が潰れる、という方向の傍証。

### 3. 止めどき

**3-1. 既存の止めどき規則**
- Dify: Clear か owner の受容。自作: 文面で直る新規理由が消え would_try が動かない / 残る理由が全て事実の不足 / 3 ラウンド。first-reader: 反復なし。
- 収束の統計的根拠を示した公開実装は見つからなかった。

**3-2. 止めどき目標「並ぶ者がいない」に最も近い判定研究（最近傍の警告）**
- 「著者の専門性・考えの深さ」を LLM が判定した研究は無い。最近傍は novelty / idea quality の判定で、次の 2 本。
- Si et al. arXiv:2409.04109 §7.2（2024、html の該当節）。primary-source check は notes 内で実施済み: 「LLM は人間 reviewer 同士の一致を下回る」supported。GPT-4o direct 50.0 / pairwise 45.0、Claude-3.5 direct 51.7 / pairwise 53.3（%、偶然 50）、人間同士 56.1。「pairwise が direct より良い」は partial（Claude のみ +1.6pt、GPT-4o は逆）。
- Sinhahajari et al. arXiv:2606.12071（2026-06、前半 100k 字を読み後半 44k 字は未読）。「judge は novelty を過大評価し人間専門家と食い違う」supported。non-obviousness の勝率で expert-expert 一致 60%、LLM-LLM 52%、human-LLM は最低 22%。人間 50 件の小標本、cs 限定、LLM judge 依存は著者自身の limitations。
- 我々との違い: 研究課題文の新規性で、技術記事の「考えの深さ」ではない。judge は Claude でない。

### 4. 比較材料

**4-1. 日本語ハーネス言説の地図**（ja-harness-landscape、取得日 2026-10-09。Zenn API の order 指定は実際にはいいね順に効いていない。数値は各行の値）
- 用語整理・入門の層は厚い（「並ぶ者がいる」領域）。watany「AIエージェントの″ハーネス″に関わる混乱と私見」2026-04-16、195 いいね（全文確認）/ r_kaga「ハーネスエンジニアリングとは何で、何ではないのか」2026-04-23、187 いいね（全文確認）/ hiruno_tarte 2026-03-04、137 いいね（API のみ）。
- 運用の実測・撤退の層は少数。いち（i_ichi）「Claude Opus 5.5に合わせて、AIエージェントのハーネスを1か月ぶりに減築した」公開 2026-09-26・更新 2026-10-07（全文確認、https://zenn.dev/i_ichi/articles/opus55-harness-genchiku）: hook 59→16、常時読込 35.8KB→18.9KB など。1 か月前の減築が再膨張した経緯と、自説が後の検証で覆ったことを書く。設計判断＋実測＋撤退を併せ持ち、第一候補の比較材料。「半年」は自己申告。
- gemcook「Claude Codeの設定を消す前に、僕が決めた基準」2026-09-11（全文確認）: 基準の提示、削除後の効果は未測定と明記。ignission「狩りから稲作へ」2026-03-24（全文確認）: 4 層。
- mizchi「俺のAIプログラミング手法(2026/10/05)」791 いいね（本文確認）: 到達規模は最大だが「棚卸し的な記事」と本人が断り、実測は乏しい。深さと到達規模は一致しない。
- watany は 2025-04〜2026-09 で 20 件超（API）、継続約 17 か月。本文未読の候補（nogataka、kewton、Engineers Hub、aicon_kato、NTT データ moros 866 いいね）は深さ未確認。
- 比較材料の取得方法: Zenn 公開 API（認証不要、liked_count 付き）を検索時点で叩く案は使えるが、1 週間で古くなる。

**4-2. 比較を渡す実装の有無**（prior-implementation）
- 他記事を読み手に渡す実装は 0 件。Dify は明示的に渡さない。first-reader も渡さない。自作は改稿前版 r0 を同じ読み手に読ませるが他記事は渡さない。

**4-3. pairwise の扱い**
- Zheng 2023 系: pairwise は絶対評価より安定するが位置バイアスがあり、入れ替えて両方一致した時だけ採る（二次要約・snippet）。Position bias 2406.07791（snippet）: 質の差が小さいほど強い。

### 5. 改稿役の制約と drift 検出

**5-1. Paper Pilot arXiv:2608.28596（2026-06-17 提出 v1、html 全文を読んだ）**
- primary-check verdict: **partial**（drift 指標は存在し語彙/機械 diff、ただし文脈が違う）。
- 指標（§5.3 / Table 8）: "A revision drifted if it added an unsupported number, added a superlative, or removed a hedge." "Scoring is a mechanical diff of original versus revision; no LLM judge is used." 語彙は例のみ（"significantly", "dramatically", "state-of-the-art", "outperforms"）で全リストと「未裏付けの数」の検出法は本文に無い。
- 数値（段落単位の改稿、n=15–30、著者が preliminary と明記）: ungated は gpt-4o-mini 30/30、gpt-5.2 15/15 で全件 drift（superlative 追加 54 / hedge 除去 96 など）。gated（evidence lock）でも 60–63% が drift し、hedge 除去は残る（29 / 11）。
- 未確認: §5.3 冒頭の改稿指示文が "polish / persuasive" か。
- 移せる部分: 「新規の数・最上級・hedge の除去」を機械 diff で数える検査と、evidence lock が要るという根拠。科学論文の段落が対象で、日本語の語彙は自作が要る。

**5-2. Loop-Back Authority arXiv:2609.14767（2026-09、v2）**
- primary-check verdict: **partial**（核は supported、「内容は劣化しない」は unsupported）。
- 手法: 5 モデル（GPT-5.4、Gemini-3.1-Pro、Qwen-3.5-122B、GLM-5、Mistral-Large-3）、temperature 0、judge も同 5 モデル。課題は business-intelligence report（43 製品 x flat/hierarchical = 86 run）。hedge は "a fixed lexicon of epistemic hedges" を 1,000 語あたりで数える（全語リストは本文に無い）。
- 数値: 最終稿 hierarchical 5.03 vs flat 3.30 /1,000 語（d_z=0.61, p<0.001）、初稿は差なし（d_z=0.11, p=0.46）、改稿のあった 31 run で 2 稿目が 1.95 多い（d_z=0.83）。差は改稿ステップで生じる、は supported。改稿は前稿の 88% を共通部分列として保つ編集。
- 内容の劣化: flat が Utility（d=0.42, p=0.009）と Writing Clarity（d=0.34, p=0.030）で上。hierarchical は改稿 1 回あたり Clarity -0.14（5 点尺度）。Specification accuracy は差なし。Clarity は judge 依存。
- 我々との違い: 英語、BI レポート、LLM Manager からの批判。人間著者・ペルソナ読み手ではない。批判駆動の改稿で hedge 密度が上がりうる、が移せる計測項目。2026-08-23 の我々の観察（限定句の増殖・防御的な本文）と同方向の独立した裏付け候補。

**5-3. 反復改稿そのものの失敗（snippet 止まり）**
- Pan et al. "Feedback Loops Drive In-Context Reward Hacking" arXiv:2402.06627: proxy 指標を回すと副作用も増える。Self-Refine arXiv:2303.17651: 成功基準が明確な 7 課題で改善。開放的な文章の品質向上の証拠ではない。
- 均質化: Padmakumar & He arXiv:2309.05196（InstructGPT 共著で多様性が最小、snippet）、Moon / Green / Kushlev（GPT-4 エッセイは新規アイデアが少ない、snippet）。移せる部分: 改稿役が文を書くと著者の言い回しが Claude 既定の文体へ寄るリスク。

**5-4. 読み手側のバイアス**
- Self-preference: Mahbub & Feng arXiv:2512.05379（本文）。judge は無ラベルでも自分の出力を識別し、それが自己選好を駆動。有害ケースで自己認識と自己選好の相関 r=0.63。2 語の同義語置換で下がる。モデルは Llama / Qwen / DeepSeek で Claude は無し。QA の pairwise で、説得力・文体・長さは未統制。
- Wataoka arXiv:2410.21819 v2、Chen arXiv:2506.02592: 低 perplexity 出力を高く評価（snippet、unverified）。
- Authority bias（CALM、arXiv:2412.05579、arXiv:2606.13104、snippet）: 権威・引用・著名人への言及が judge を動かし、偽の引用でも効く（攻撃成功率最大 50%、Claude-3.5 が最も頑健と報告）。著者資格だけを変数にした実験は見つからなかった。
- 含意: 目標が「第一人者と認める」だと、読み手は name-dropping・肩書・固有名・用語密度に反応しうる。実在の言及でも同じかは未実証（推測）。
- Persona の信頼性: "The Prompt Makes the Person(a)" arXiv:2507.16076（snippet）は少数派属性の再現が苦手。"Expert Personas Improve LLM Alignment but Damage Accuracy" arXiv:2603.18507（snippet）は persona が judge の点を上げるのに正答率を下げた例。いずれも違う領域。

### 6. ループの外の校正

- 診断に使い改稿ループにしない案: 1-4 の「反復」と「文脈共有」が乖離の原因という結果からの推論で、直接検証した出典はない。
- 人間の抜き取り採点: 1-4 の人間採点と同じ役。我々の repo には `scripts/metrics/snapshots.jsonl`（views, likes）があり、公開後の人間側計測を持つ。
- 題・導入だけを最適化: 直接の文献なし。範囲を狭めれば主張・格付けを足す余地が減る、は設計上の推論。
- Gwern "virtual comments"（gwern.net/blog/2024/virtual-comments、全文読了）: 設計案で**実験結果なし**。実在の読み手の過去の発言を材料に simulate。事前に挙げられた失敗として、素の feedback は sycophancy・自明・ChatGPTese に寄ると言う。意見の根拠。
- Muna panel review plugin（tachyon-beep）: 掲載ページのみ読み、persona 導出法・反復規則は不明。14 stars、採用実績薄。参考程度。

## Contradictions

**(1) 隔離 offline judge は人間と一致（Pan）vs novelty 判定の過大評価（2606.12071）**
- Pan 2407.04549: offline judge は GPT-3.5 で人間に近く、乖離の原因は反復と文脈共有。ただし 2024 年のモデル、essay 編集、GPT-4 は inflated のまま。数値は図のみ（primary-check: partial）。
- 2606.12071: 2026 年のモデルでも judge は人間専門家と食い違い、過大評価方向（human-LLM 勝率の一致は最低 22%）。単独採点でも tie が多い。人間 50 件の小標本、cs 限定（supported）。Si 2409.04109 も LLM は人間同士の一致を下回る（supported）。
- 強い根拠: 課題が違うため優劣はつかない。Pan は「改稿の質」を人間が採点した essay 課題で、offline が人間の傾向に沿う。後者は「新規性・専門性」の判定で、我々の止めどき（並ぶ者がいないとわかる）に近いのは後者の課題。隔離だけでは、内容の深さ判定の妥当性は保証されない。どちらも Claude 5 世代・日本語・技術記事ではない。

**(2) 比較材料を渡す案（Zenn API）vs 比較で上振れ（2606.12071）・比較を渡す実装が 0 件**
- 案: ja-harness-landscape は Zenn API で比較材料を取得する案を挙げる。実装先例は 0 件で、Dify・first-reader は比較対象を渡さない。
- 2606.12071: comparative（参照と生成 5 件を並べて採点）はモデル側の勝ちを増やし tie を減らした。この対応づけは取得ツールの読みで、論文は absolute / pairwise の語を使っていない。
- 参照が著者本人の稿の場合に向きが逆かは未検証。比較を渡すと位置バイアス（2406.07791、snippet）も効く。比較は「上振れ」と「先例なし」の両方に当たる。

**(3) Loop-Back の「内容は劣化しない」が primary-check で unsupported になった件**
- 第 1 波（adversarial）: 検索要約により「hedge が増える、内容は劣化せず類似」と記述。
- primary-check: 核（差は改稿ステップで生じる、hedge 増）は supported。しかし flat が Utility（d=0.42）と Writing Clarity（d=0.34）で上、Clarity は改稿 1 回あたり -0.14。著者の言は「考える力は落ちず commit が減る」。よって「内容は劣化しない」は unsupported。primary-check を優先する。
- 付随: 第 1 波は 2609.14767 / 2608.28596 を「要・本文確認」としていたが、primary-check で本文確認済み（partial）。

**(4) その他の食い違い（小）**
- first-reader: 第 1 波は「別 fresh subagent が transcript だけから答える」と書いたが、primary-check では recall.py が subagent を起動せず隔離は運用（強制でない）。primary-check を優先。パスも `awesome_agent_skills/` ではなく `agent_skills/`。Tessl registry 経由で読んだ第 1 波は raw 404 だった。
- Pan: 第 1 波の「人間 3 人/本」は primary-check と整合（3 人/本）。ただし第 1 波の「GPT-4 は乖離が小さい」は、primary-check では「inflated だが逆向きの傾向は出ない」。乖離の大きさの数値は図のみ。
- Pan の「offline judge は人間と一致」は GPT-3.5 の記述で、GPT-4 では offline の一致は本文に明示されない。
- Paper Pilot: 第 1 波（adversarial）は「新規数値・最上級・hedge」と要約し、primary-check で一致。ただし第 1 波が示唆した「polish を頼むと」の指示文は未確認。

## Still unknown

- **Claude 5 世代での未測定**: Pan（GPT-3.5/4、2024）、Si（GPT-4o/Claude-3.5）、Mahbub（Llama/Qwen/DeepSeek）、2606.12071（gemini-3.1-pro/deepseek-v4-pro）、2609.14767（GPT-5.4 ほか）のいずれも Claude 5 世代では測っていない。自己選好・冗長選好・sycophancy・reward hacking の乖離が再現するかは不明。Pan では GPT-4 で乖離が弱まっており、世代で変わりうる。
- **日本語での未測定**: 全研究が英語。日本語技術記事を対象にした judge/読み手研究、「著者の考えの深さ」を LLM が判定し日本の実践者と照合した研究は無い。Loop-Back の hedge 語彙・first-reader の signals.py（大文字固有名、I/we）は英語前提で、日本語の検出語彙は自作が要る。
- **「並ぶ者がいない」の反証探索が未完**: Qiita / note / 登壇資料（Findy 勉強会ほか）/ X の本文は snippet 止まりか未探索。Zenn topic harness（93 件）と harnessengineering の 2 ページ目以降、claudecode 全体は未取得（API の並びがいいね順でなく上位を取りこぼしている）。nogataka、kewton、Engineers Hub、watany「Jevでハーネスエンジニアリング」、aicon_kato、NTT データ moros の深さは未確認。i_ichi の継続期間・過去記事数も不明。地図は現状の見取り図で、「並ぶ者がいない」の判定には網羅性が足りない。
- 偽陽性（読み手のカットオフ後の語を「分からない」と報告）を扱う公開実装・測定は見つからず。自作の対策（一次資料を先に確認、一句の言い換え 1 回で追わない）以外の先例なし。
- 止めどき目標を読み手に測らせる先例なし。recall test（sayback）が近いが「深さ」の妥当性は未検証。
- 権威の水増し（name-dropping、肩書、最上級）で読み手評価だけが上がる改稿が Claude 系で起きる頻度の実験は無い。自前の小実験（r0..rN を新規数値・最上級・固有名・hedge の機械カウント + 人間抜き取り）で測る必要がある。
- 単独読みか前稿との比較かで、記事改稿ループの判定妥当性がどう変わるかの直接データなし。
- 未読: 2606.12071 の後半 44k 字、Loop-Back の hedge 語彙全リストと初稿の絶対 hedge 率、Paper Pilot §5.3 冒頭の改稿指示文、first-reader の SKILL.md 逐語と references/report.md、Pan の反復ごとの点数（図のみ）、Muna の iteration 規則、Zenn の「10 人インタビュー風」記事の中身。
- snippet 止まりで決定に使う前に本文確認が要るもの: Wataoka 2410.21819、Chen 2506.02592、2501.06964、2507.16076、2603.18507、Position bias 2406.07791、authority bias 系（2412.05579、2606.13104）、2402.06627、Padmakumar 2309.05196、Moon ほか。
