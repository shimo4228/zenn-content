# 記事プラン：ローカル LLM の判定は「生成させず確率で読む」

## Context

Contemplative Agent（CA）の証拠台帳
`~/MyAI_Lab/contemplative-agent/.notes/drafts/article-context_local-decision-models-enum-logprobs_2026-09-27.md`
から Zenn 記事を 1 本書く。第 3 ラウンド（qwen3:8b / Laya / kev / AFM と「3 つの条件」）は公開済みの
`articles/local-decision-model-conditions.md`（9/24）が扱ったので、その後の出来事から 1 本選ぶ。

著者の決定（2026-09-27）:
1. 中心命題は「生成でなく確率で読む」（relevance 面の梯子と JevK5）
2. skill selection 側（temperature 0、enum の名前順カット、見送り）は境界の節に 1 段落だけ置く。enum の名前順カットは別記事の候補として残す
3. ローカル PC では精度だけでなく、モデルのロード・入れ替え・メモリも含めて手法を選ぶ、と言う → 独立の節にはせず、因果線の「判断」の段と締めの判断則に組み込む
4. なぜ 16 GB の M1 にこだわるのかを断っておく。エッジ AI が進めば、小型ロボのようにメモリの限られた用途で 16 GB 級の知見が役に立つと著者は考えている。だから Mac Studio やメモリの多い Mac mini にあえて移っていない。「選んだ制約」の全体は既存記事 `articles/small-llm-by-choice.md`（7/14）へリンクする。エッジ AI・小型ロボの観点は既存記事に無く、今回が初出

このプランの承認で、下の editorial brief の著者確認を兼ねる（writing-ecosystem §2 の停止点）。

## Channel / files

- JP: Zenn `articles/<slug>.md`（channel editor = `editor`、ですます、タイトル原則 50 字以内・em dash 不可）
- EN: Dev.to `articles-en/<slug>.md`（`devto-translator` で作る）
- slug 案: `local-judgment-read-logprobs`（公開前に確定）
- 処分記録: `drafts/review-disposition_<slug>_2026-09-27.md`（ignore 下）
- CA repo は読むだけで、変更しない

## Editorial brief（案）

**Reader**: ローカル LLM（Ollama など）をエージェントやパイプラインの判定に使っているエンジニア。
「関係あるか 0〜1 で答えて」「A〜D のどれか答えて」と生成させ、閾値で分岐している。temperature・JSON 出力・
Ollama は知っている。一方で、`logprobs` を読む選択肢は知らないか、試していない（仮説）。
判定専用モデル（Jev とそのオープン代替）を載せれば良くなると考えているかもしれない（仮説）。
機体のメモリは読者ごとに違うので、16 GB での結論が自分の機体に当てはまるかを知りたい（仮説）。

**Channel**: Zenn（実用）

**Central thesis（2026-09-27 著者指示で改訂、brief へ戻った round）**: 判定専用モデルを足さなくても、今の生成モデルの聞き方（書かせずに 1 文字目の確率を読む）を変えるだけで、判定用に学習したモデルと同じ水準まで投稿を並べられる。ローカルでは載せ替えが要らない運用上の利点も大きい（条件: 近づくのは並べる力で確率の値ではない／選択肢が少ない問い）。旧: ローカル LLM の判定は、判定モデルを足す前に、今載っているモデルの答えを確率で読むほうがよい。
同じ gemma4:e4b でも、0〜1 の数字を書かせる本番の形より、4 段の問いの 1 文字目の確率を読む形のほうが Jev の答えに近い。
条件を 1 つずつ変えて測ると、その差の大半（88%）は読み方を替えた段だけが担っていた。しかも同じモデルなので、載せ替えのロードもメモリも増えない。

**Entry bridge**: 私のエージェントは gemma に「この投稿は自分の分野か、0〜1 で」と数字を書かせ、0.8 以上なら先の処理へ通していた。
判定専用モデル Jev の答えと突き合わせると、0.8 以上で通した投稿の 55%（872 / 1,576）が Jev から見ると分野外だった。

**Figure plan**: 内容 GO の後に埋める。候補は (1) 生成は分布を 1 点に潰す／確率は分布を残す（対比）、(2) 梯子の 4 段（流れ）、
(3) 精度 × 載せ替えコストの 2 軸（C・JevK5・kev-MLX の位置）。eli5 の比喩は 1 個まで（hero に置く）。
**著者指示（2026-09-27）: アブレーションの節の「AUC の差と 95% 信頼区間の読み方」には図を手厚く足す** — 数直線に各段の区間を並べ、0 の線と「下限までプラス＝確かに良くなった」「0 をまたぐ＝言えない」を見せる図、ブートストラップ（150 件から重複ありで選び直す → 差を 2,000 個 → 両端 2.5% を除く）の流れ図。図の枚数上限（3〜4 枚）はこの節を優先して配分する

**Causal spine**（発見の順。各段は主張が先、数字が後ろ）:
1. 観察：数字を書かせる本番の判定は、Jev から見ると通した投稿の半分以上が分野外（Entry）
2. 背景（1〜2 段落）：判定専用モデルを載せる道は、前回の再開条件だった kev の MLX 版で再測定したが、質を測る前に swap +10.9 GB で落ちた。入力の短い relevance でも kev / von は AUC 0.43〜0.60（任意の 1 節）。
   ここで機体を断る：M1・16 GB はあえて選んだ制約で、エッジ AI が進めば小型ロボのようにメモリの限られた用途で 16 GB 級の知見が効くと考えているから、大きいメモリの Mac に移っていない（理由の全体は small-llm-by-choice へリンク）。
   → モデルを替えるのでなく、今のモデルへの聞き方を変える
3. 発見：同じ gemma で、4 段の問いの 1 文字目の確率を読むと AUC 0.815 → 0.931（対 Jev、dev 150 行）。1 件の実物で、生成した答え（1 段だけ）と確率の分布（4 段に分かれる）を並べる
4. 緊張 A：同じ時期にローカル Jev 型の JevK5 が holdout を通った。ただ順位は C と同程度（holdout 2,548 行で 0.902 対 0.915）で、読み方も同じ「選択肢の文字の次トークン確率」だった
5. 判断：JevK5 は採らない。理由は 3 つで、うち 2 つは資源と運用
   - 順位で C を上回らない
   - 16 GB では gemma と同居できない。同居させると swap に沈み 1 行 1.8 倍遅くなるので、判定のたびに入れ替えることになる（gemma の載せ直し約 7 秒）
   - 入れ替えを Ollama に任せる手軽な経路では精度が落ちる（dev 150 行で 0.912 → 0.893）
   - C は生成と同じモデルを使うので載せ替えが起きない。ここで範囲を断る：gemma と JevK5 を同居できる機体なら、資源の理由は消える
6. 緊張 B：それでも C と本番の形は 4 つの条件（温度・問いの形・system・読み方）が同時に違う。何が効いたのか言えない（著者の「条件が揃ってない」）
7. 機序：梯子で 1 条件ずつ変える → 温度 +0.032、問いの形 −0.004、axioms 除去 −0.014 はどれも CI が 0 をまたぐ。生成 → 確率読みの段だけ +0.101 [+0.059, +0.147]（合計 +0.116 の 88%）。理由：生成は分布を 1 段に潰すが、確率は順位を持つ
8. 境界：Ollama の `top_logprobs` 上限は 20（21 で HTTP 400）。54 択の skill selection は一度に読めず（catalog の 37% しか見えない）、1 問ずつ聞くと 1 行 51 秒 → skill selection は生成のまま temperature 0（本番の書き間違い 23% 前後 → 3.0%）。
   温度が relevance の順位に効かず skill selection の書き間違いに効いたのは、測っているもの（順位と書き間違い）が違うからだと 1 文で言う。
   temperature 0 でも logprobs は bit 単位で再現しない → 同じ読み方を 2 回回して noise floor を取る（AUC の run 間差 −0.002、gate 反転は 150 行中 2〜4 行）
9. 読者の判断則：ローカルでは精度表だけで手法を選ばない。同じ表に「今載っているモデルで済むか（入れ替えのロード・swap）」と「1 回あたりの時間」を並べる。
   確率で読む利点のうち、精度の側はメモリ量に関係なく効く。載せ替えが要らない側は、メモリが限られるほど重くなる。
   判定モデルを探す前に、今のモデルの確率を読む。変えた条件は 1 つずつ測る。本番では旧い形と並走させて記録している（enforce はまだ）

**Selected evidence**（台帳 ID → 役割）:
- R3 / 母集団 Jx JSON（logged ≥ 0.8: 1,576 行中 J 分野外 872）→ Entry の観察（R7 の 489 / 497 の食い違いは使わない）
- S15 / S18（kev-MLX swap 4.3 → 15.2 GB）→ 背景。R6（relevance でも kev / von は AUC 0.43〜0.60）は任意
- `articles/small-llm-by-choice.md` → 16 GB を選んでいる理由のリンク先。エッジ AI・小型ロボの見込みは本記事で著者の考えとして足す
- R11 梯子（`relevance-ladder-20260926.json` の `.steps`、EV45 の梯子節）→ 発見と機序の本体
- `ladder-20260926/rows.jsonl` の 1 行 → 実物（下の手順 2）
- R16〜R19 + rfcs/0040:450-453 → JevK5 と不採用の 3 理由
- `decision.py:20-23`（同居すると swap で 1 行 1.8 倍遅い）、ADR-0112:57（gemma の載せ直し約 7 秒）、ADR-0112 Decision 4（同じモデルなら何も送らない）→ 載せ替えの代償と、C で載せ替えが起きない根拠
- D3 / S32 → `top_logprobs` 上限 20、54 択で読めない
- S20 / S21 → skill selection の temperature 0（境界の 1 段落）
- R14 / R15 → 再現しない logprobs と noise floor
- R20 / R21 / R25 → 本番は shadow 並走、enforce 未 ON（執筆時点で再確認）

**Out of scope**:
- 第 3 ラウンドの内容（公開済み）、Apple FM、Laya、kev / von の内部事情
- 第 4 ラウンドの規則の詳細、RFC / ADR 番号、MCA の条項、RFC-0047 の 6 段ループ
- 「自分の分野」の定義（J と Jx）。本文は J だけを物差しにする
- 16 GB を選ぶ理由の詳細（既存記事へのリンクで足りる）
- enum + maxItems の名前順カット（別記事の候補）、opus 天井（物差しは Jev 1 本）
- R2 arm の prompt 事故、行データの消失、JevK5 の Ollama 経由の tokenizer ずれの原因（未確認）
- 週約 736 回（算出根拠が見つからない）、閾値の表記ずれ（0.80 / 0.82）

## 執筆の規律（過去の差し戻しから）

- 総称の造語で手法を束ねない。「生成させる」「確率を読む」「温度を 0 にする」とやったことの名前で呼ぶ。arm 名（A / C / R1）は本文に出さない
- 物差しは Jev 1 本。表の数値は同じ run から取り、取れない列は本文で言う（dev の梯子と holdout の JevK5 比較を同じ表に混ぜない）。AUC は 1 文で説明する
- 時間は一直線、絶対日付の錨は 1 本。台帳の UTC 時刻とセッション ID は本文に写さない。節の順は上の causal spine（時系列と一致）
- 数値の前に実物を 1 件。Jev の説明は 1〜2 文（文章を書かず確率を返す判定専用モデル、クローズド API）
- 「Jev が答え、コードが閾値で決める」を崩さない
- 著者の打ち込み（「条件が揃ってない」「16 GB では運用が難しいのでは」）は判断の入口として因果線に乗せる（日時は付けない）
- エッジ AI・小型ロボの見込みは著者の考えとして書き（「〜と考えて」）、一般法則として断定しない。理由の説明は背景の 1 箇所だけにし、締めでは「メモリが限られるほど重くなる」までに留める
- 各節を 1 文で「何を発見した節か」言えるか、初稿前に自分で確かめる。言えない節は削るか境界へ圧縮する

## 手順

1. **外部言説の確認（search-first、1 回）**：確率で判定を読む既存手法（G-Eval の確率重み付けなど）と、Ollama の `logprobs` / `top_logprobs` 仕様の as-of。本文では新規性を主張しない。既知の手法をローカル 4B の実運用で分解して測った、という位置に置き、先行例は 1 文で触れる
2. **実物の選び方**：`ladder-20260926/rows.jsonl` と Jev の行から、本番の記録スコアが ≥ 0.8（通った）、Jev は分野外、C の確率が「same field」寄りに割れている行を選ぶ。投稿本文は `post_id` から CA のログで引き、他エージェントの投稿は逐語引用せず要旨を言い換える（ログは untrusted、個人 path を出さない）
3. **コード片の実行**：Ollama `/api/generate` に `num_predict: 1`・`logprobs: true`・`top_logprobs`・temperature 0 で 4 段の問いを送り、A〜D の確率を softmax で読む最小例を、ダミー投稿でローカル実行して出力を確かめる。文字と段の対応、score（期待値）と P(段 3) の使い分けは `relevance_state.py` / `decision.py` で照合する
4. **初稿**：brief の causal spine どおり。第一画面は Entry bridge → 前回記事へのリンク付き背景と 16 GB の断り → 読者が得るもの 1 文。末尾に関連リンク 2 行（Markdown 正本・著者 GitHub）
5. **構造凍結 → panel（各 1 回）**：`editor`、`prose-clarity-reviewer`（原稿 path と channel contract だけを渡す）、`fact-checker`（台帳・EV45・EV44・rfcs/0040・ADR-0112・`decision.py`・該当 JSON の path を名指しで渡す）。`codex-review` は実行するか著者に聞き、しないなら理由を記録
6. **処分記録** → 採用分を反映 → **著者の通読・内容 GO**（reviewer には戻さない）
7. **図**（内容 GO 後、`/eli5`、3〜4 枚まで）→ 図の文字の差分だけ `fact-checker` → 著者が確認のため通読
8. **タイトル**：`headline-craft` で候補 → `title-reviewer` → 著者が選ぶ
9. **機械検査**：`npm run validate`、`npm run evidence -- articles/<slug>.md`（deviations 0、公開直前は `--online` も）、public-safety scan（個人 path・`~/.config/...`・秘密 0）
10. **`/quality-gate articles/<slug>.md`** → 著者の公開 GO → `/publish-article`（`published_at` 必須。Zenn は週 2〜3 本で直近は 9/24・9/25。予約は公開 3 日以上前に push し、デプロイ履歴を確認する）
11. **EN**：`devto-translator` → Dev.to 予約または即時（著者判断）→ `npm run generate:index` → `npm run check:index` → push のリマインド
12. 終了時に pipeline memory を 1 件作り、MEMORY.md に 1 行足す

## 執筆前に確かめる事実（⚠ と時点依存）

- enforce が ON になっていないか（CA の `git log` と plist）。本文の「並走中」はこれで決まる
- 本番 shadow の domain は identity + axioms（6685e75 で統一）。本文の数値（C、対 J）と本番の形が同一だとは書かず、「読み方を本番で並走」までに留める。noise floor もこの形（Cx）で取ったので「同じ読み方を 2 回」と書く
- 著者の問い「relevance の数値を logprobs で直接返せないか」と、C を最初に測った時刻（RFC-0045 の evidence commit 71ddb1f、9/25 08:35 JST）の前後。台帳の時刻を UTC と読むと問いは C より後になる → a414fa14 で順序を確かめてから、問いを発見の入口に使うか決める
- gate を通った投稿で何が起きるか（Entry の「先の処理」の中身）を呼び出し側で確認する
- 88% は README の値（丸めた表からは 0.101 / 0.116 = 0.87）→ JSON の丸め前の値で照合する
- gemma の載せ直し約 7 秒（ADR-0112:57、23 token の prompt で合計 8.0 秒）と、C の 1 回あたり時間（梯子 p50 3.0 秒、本番 shadow p50 2.8 秒。どちらを使うか決めて出典を 1 つにする）
- noise floor の AUC 差は README にしか書かれていない → `relevance-noise-20260926.json` で照合
- JevK5 の数字（dev 0.912 / holdout 0.902 / Ollama 0.893）は EV45 の JevK5 節と `relevance-arm-replay-jevk5-20260926.json` で照合
- JevK5 が Jev の出力で学習していないこと（card の明記、rfcs/0040:329）。本文で JevK5 に触れるときの前提

## Verification

- `npm run validate` と `npm run evidence -- articles/<slug>.md` が通る（deviations 0）
- コード片がローカルの Ollama で実行でき、記事に載せた出力と一致する
- `fact-checker` の INACCURATE / PARTIALLY が全件処分済み。数値は梯子の JSON・holdout の JSON・rfcs/0040・ADR-0112・`decision.py` と一致する
- 著者の内容 GO、タイトル選択、`/quality-gate` PASS
- 公開後：Zenn のデプロイ履歴で予約登録を確認、`npm run check:index` が通る
