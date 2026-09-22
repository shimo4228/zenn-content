---
title: "Jevの判断をローカルで再現するには何が要るか"
emoji: "📏"
type: "tech"
topics: ["jev", "llm", "aiエージェント", "ollama"]
published: true
published_at: 2026-09-24 09:00
---

| モデル | 方式 | Opus天井との一致 | 1行の時間 | 結果 |
|--------|------|------------------|-----------|------|
| Jev (hosted) | choice+noul | 0.346 | 0.3秒 | ✓ 基準値 |
| gemma4:e4b | logits×54問 | 0.162 | 51秒 | 既存baseline |
| **qwen3:8b** | logits×54問 | — (4行で停止) | 43–74秒 | ❌ 遅すぎ |
| **Laya** | noul | 0.075 | 39秒 | ❌ 無作為並み |
| **kev-0.8b** | choice | — (25行で停止) | 6.9秒 | ❌ メモリ不足 |
| **AFM 3 Core** | verbalized | — (20行のみ) | 20.7秒 | ❌ コンテキスト長不足 |

*「Opus天井との一致」= 最も高性能なOpus 5の選択を「正解の上限（天井）」として、各モデルの選択がどれだけ重なるかをJaccard係数で測定（詳細は「150行のリプレイで測る」節）。無作為の期待値0.056。方式の説明は次節。AFM = Apple Foundation Models（macOS 27のオンデバイスモデル）。コンテキスト長（モデルが一度に処理できるテキスト量の上限）が4,096 tokenしかなくprompt全量が入らないため、catalogを半分に切った20行でAUC 0.443。Jevの数字は前回の記事から。*

TypeSafeの判断モデルJevが0.3秒で解いたスキル選択の判断を、ローカルで動く4つの候補で再現しようとしました。結果は表のとおり全滅です。ただし失敗の原因は3つに分かれていて、次にローカル判断モデルを評価するときの条件が見えました。

## 30本のオープン代替と、3つの試し方

[前回の記事](https://zenn.dev/shimo4228/articles/jev-vs-opus-skill-selection)で、Jevは自律エージェントのスキル選択において1行0.3秒で、最も高性能なOpus 5の選択を正解の上限（天井）としたとき約半分の一致率、という結果を出しました。ただしJevはクローズドAPIで、2026年9月時点で重みの公開もセルフホスト経路もありません。

Jev公開から1週間で、オープンな代替モデルが30本超出ました（[systemonemodels.org](https://systemonemodels.org/examples/alternatives/)に一覧があります）。ただし、学習済みの判断専用モデル（kev、von、Layaなど）はいずれもOllamaでは動きません。Ollamaがモデルを読み込むにはGGUF形式の重みファイルが必要ですが、判断専用モデルにはGGUFが用意されていません。加えて、これらのモデルは通常の「文章を生成する出力層」の代わりに「選ぶ/選ばない」の確率だけを返す専用の出力層（カスタムhead）を持っており、Ollamaの汎用的な推論エンジンでは動かせません。

試せる方法は3つに分かれます。

![ローカル判断モデルの3つの方式](/images/local-decision-approaches.png)

1. **logits方式** — 汎用LLMに「このスキルを選ぶべきか？」とYes/No質問を投げ、YesとNoそれぞれの確率（ログ確率 = logits）をOllamaの`logprobs`オプションで読む。追加学習は不要だが、54スキルに1問ずつ投げるので54コールかかる
2. **typed-decisions方式** — 判断タスク専用に学習した分類器を使う。たとえば54スキルの一覧と状況を一度に渡すと、各スキルの「選ぶべき確率」をまとめて返す。汎用LLMのように文章を生成するのではなく、確率の配列だけを出力する
3. **specialized decoder方式** — 汎用LLMの「文章を生成する部分」を「判断だけを出力する部分」に取り替えた小型モデルを、専用サーバー経由で使う

それぞれから1つずつ選びました。qwen3:8bはOllamaで動く汎用LLMの中でprefix cache（後述）が効く最小モデル。Layaは判断専用モデルの中で唯一Python APIが公開されていたもの。kev-0.8bはJevの再実装を掲げる最も注目度の高いプロジェクトです。さらに、macOS 27のFoundationModels frameworkで動くAppleのオンデバイスモデル（AFM 3 Core、Apple Foundation Models）も加えています。AFMはオープンではありませんが、macOSに標準搭載されており追加インストールなしで動きます。

## 150行のリプレイで測る

測定方法は前回と同じです。自律エージェントが実際に実行したスキル選択のログ150行を各モデルに再入力して、Opus 5の選択との一致率を比べます。測定環境はApple Silicon M1（16 GB）、GPUにはMPS（Metal Performance Shaders = Apple独自のGPU演算基盤で、NVIDIAのCUDAに相当）を使い、Ollama 0.34.2です。

指標は3つです。

- **Jaccard@topk** — Opusが選んだスキル集合と、評価対象モデルが選んだスキル集合の重なり具合。計算は「両方が選んだスキル数 ÷ どちらかが選んだスキル数」。たとえばOpusが{A, B, C}を選び、モデルが{A, B, D}を選んだ場合、重なりは{A, B}の2個、全体は{A, B, C, D}の4個で、Jaccard = 2/4 = 0.5。1.0で完全一致、0で重なりゼロ
- **AUC** — モデルが「選ぶべき」と高い確率を付けたスキルが、実際にOpusも選んだものなら高くなる。確率の順位付けの良さを測る指標で、0.5なら無作為と同じ、1.0なら完璧な順位付け
- **ECE（較正誤差）** — モデルが「80%の確信度で選ぶべき」と言ったとき、本当に80%当たるかの一致度。較正（calibration）とは、モデルが返す確率と実際の的中率が一致する性質のこと。ECE 0なら完璧に較正されている。ECEが高いと、確率の数字を信じて判断に使えない

スキル選択のpromptは約12,000字です（スキルカタログ約9,600字 + 状況記述の中央値1,537字）。モデルが一度に処理できるテキスト量の上限をコンテキスト長（context length）と呼びます。このpromptサイズが後で効いてきます。

## qwen3:8b — 54問が積み上がる

最初にlogits方式を試します。Ollama 0.34.2は`logprobs: true`でトップ20のtoken確率を返します。

```bash
curl -s http://localhost:11434/api/generate \
  -d '{"model":"qwen3:8b","prompt":"...Should we select this skill? Answer yes or no:","stream":false,"logprobs":true,"top_logprobs":5,"options":{"num_predict":1,"temperature":0}}'
```

54スキルそれぞれに「このスキルを選ぶべきか」と問い、Yesのログ確率を読みます。

54問のpromptは「スキルカタログ + 状況記述」（約12,000字）を共通の前半部分（prefix）として持ち、末尾の「このスキルを選ぶべきか？」の部分だけが問いごとに変わります。prefix cache（プレフィックスキャッシュ）とは、この共通部分の処理結果をメモリに保持して、2問目以降は変わった末尾だけを処理する仕組みです。

![prefix cacheの仕組み](/images/local-decision-prefix-cache.png)

まずqwen3.5:9bで試したところ、共通prefixを持つ54問なのに2問目以降も1問5秒以上かかりました。prefix cacheが効いていません。同じことをqwen3:8bで試すと、suffix違いの2問目は0.4秒で返ります。

```text
qwen3.5:9b — 同一prompt再送: 0.3秒 / suffix違い: 7〜12秒（全量再評価）
qwen3:8b   — 同一prompt再送: 0.3秒 / suffix違い: 0.4秒（prefix cache成立）
```

LLMは入力テキストを処理するときに「注意機構（attention）」でトークン間の関係を計算します。標準的なTransformer注意はすべてのトークンの組を見るため計算量が大きいですが、処理の途中結果（KVキャッシュ）を保存して再利用できます。qwen3.5が採用しているhybrid線形注意は計算を軽くする代わりに、共通prefix部分だけのKVキャッシュ再利用ができないと推測されます。標準的なTransformer注意のqwen3:8bに替えました。

cache成立後の結果です。初回14.2秒、以降は中央値0.63秒。1行あたり43〜74秒になります。前回試したgemmaのenum方式は54スキルの一覧を一度に渡して1コールで回答を得るため13秒/行で済みましたが、logits方式は54コールの直列なので3〜5倍遅くなります。4行で打ち切りました。

logits方式は54コールの直列が本質的なボトルネックです。prefix cacheが効いても、0.63秒 × 54 = 34秒が下限になります。

:::message
prefix cacheが効いているかの判定方法: Ollamaのレスポンスに含まれる`prompt_eval_count`（入力トークン数）はcacheが効いていても元の全トークン数を返すので、この数字だけではcacheの有無が分かりません。`prompt_eval_duration`（入力の処理にかかった時間）が大幅に短くなっていれば、cacheが効いていると判断できます。
:::

## Laya — 較正という名の壁

較正（calibration）とは、前節で説明したとおり、モデルが返す確率と実際の的中率が一致する性質です。「70%」と言えば本当に10回中7回当たる — これが較正されている状態です。Layaはこの較正で壁にぶつかりました。

![較正（calibration）とは](/images/local-decision-calibration.png)

typed-decisions専用のLayaを試します。mmBERT-base（322M params）ベースで、[HuggingFace](https://huggingface.co/convaiinnovations/laya)で公開されています。2種類の問い方を使いました。

- **noul** — スキルごとにyes/noの確率を返す
- **choice** — 選択肢からベストを1つ選び、各選択肢の確率を返す

150行の結果です。

| 指標 | Laya (noul) | Laya (choice) | gemma (logits) | 無作為 |
|------|-------------|---------------|----------------|--------|
| Jaccard@topk | 0.075 [0.062, 0.089] | 0.051 [0.041, 0.061] | 0.162 [0.141, 0.182] | 0.056 |
| AUC | 0.587 [0.561, 0.611] | 0.477 [0.455, 0.499] | 0.728 [0.704, 0.750] | 0.500 |
| ECE | 0.469 | — | — | — |

*角括弧内は95%信頼区間。*

noulのJaccard 0.075は無作為（0.056）をわずかに上回るだけです。choiceの信頼区間は無作為を含んでおり、区別がつきません。

問題の核は較正です。ECE 0.469の内訳を見ると、全判定8,207件のうち6,382件（78%）が確率0.5〜0.7の帯に集中し、その帯の実際の的中率は10〜14%でした。「60%の確信度で選ぶべき」と言われても、実際に当たるのは10回に1回です。

Layaは起動時にこの警告を出します。

```text
laya: this checkpoint ships temperatures outside [0.5, 5]
which would distort confidence; clamping choice:11+=0.1006.
Treat confidence from the affected buckets as uncalibrated.
```

この警告の意味はこうです。Layaは確率を計算するときに内部でtemperature（出力の確率分布の鋭さを調整するパラメータ）を使います。このcheckpointでは選択肢が11個以上のケース（bucket = 選択肢数ごとのグループ）でtemperatureが正常範囲外になっており、確率の値を強制補正（clamping）しています。54スキルからの選択は11件以上に該当するため、返される確率は較正されていません。

レイテンシについても確認しました。model cardはNVIDIA T4 GPUで1問33ms（バッチ7ms）としていますが、今回の測定環境はApple Silicon（MPS）です。ハードウェアが異なるので単純比較はできませんが、この環境での実測値は1行（54問）あたりnoul中央値39.4秒（最小6.8秒）、choice 10.5秒（最小1.7秒）でした。

Layaの問題は速度ではなく品質です。確率が判断の根拠にならない以上、「高確信度の行だけJevの代わりに任せる」という運用もできません。

## kev-0.8b — 0.8Bが12 GBを食いつくす

最後にspecialized decoderのkev-0.8bです。Qwen3.5-0.8B-Baseに判断headを載せたモデルで、独自サーバーを起動して呼び出します。

設計どおりの1リクエスト（約6,000 token、choice + noul 54問）を投げたら、即座にメモリ不足で停止しました。

```text
RuntimeError: MPS backend out of memory
(MPS allocated: 12.50 GiB, other allocations: 7.02 GiB,
 max allowed: 20.13 GiB).
Tried to allocate 880.00 MiB on private pool.
```

分割すれば通ります。choice単独（2,432 token）で8.6秒、noulは14問ずつ分割で7〜27秒です。ただしchoice単独で連続して走らせると、17行を処理した後にMPS（前述のApple GPU演算基盤）のメモリ管理（allocator）が16 KBの確保にも失敗しました。サーバーがリクエスト間でGPUメモリを解放しません。

背景には2つの制約があります。

- **推論カーネル**（モデルの計算をGPU上で実行するプログラム）: kevが使う`flash-linear-attention`という高速な実装はNVIDIA（CUDA）とAMD（ROCm）のGPU向けに書かれており、Apple SiliconのMPSには対応していません。そのため最適化されていない基本実装（reference実装）に自動的に切り替わり（fallback）、サーバー起動時に`"much slower"`の警告が出ます
- **入力長**: 学習は384 token以下で行われています。serving時の`num_ctx`は8,192に設定できますが、12,000字のpromptに対して学習時の入力長との乖離は大きいままです

25行でchoice単独の結果だけ見て打ち切りました。allocatorの問題を回避するにはサーバーの定期再起動が要り、150行を完走させる見通しが立ちませんでした。

## AFM 3 Core — コンテキスト長が足りない

macOS 27でFoundationModels frameworkが使えるようになりました。M1（16 GB）に来るのは`AFM 3 Core`（3B）で、コンテキスト長は4,096 token。生成バックエンドとしては窓が小さすぎて使えなかったのですが、判断モデルなら入出力が短いので、ダメ元で試しました。上位の`AFM 3 Core Advanced`（20B sparse）はSDKにモデル選択APIがなく、M1には降りてきません。

最初の壁はコンテキスト長です。スキル選択のpromptは約12,000字ですが、AFMのコンテキスト長は4,096 tokenしかありません。catalogを半分に切り、round 1の20行だけで測りました。

`fm serve`はOpenAI互換のendpointを持ちますが、`logprobs`は黙って無視されます。確率を数値として喋らせるverbalized方式のAUCは0.443（temp 0）でした。同じ20行のgemma logprobsは0.736です。20行中5行はguardrailの`RefusalError`でcatalogの半分が未採点でした。

唯一の強みは同居性です。生成中のメモリは約2 GBで、Ollamaのモデルと同居してもswapは増えません。ただし窓に入らない以上、候補になりません。

## ローカル判断モデルに必要な3つの条件

4候補の脱落原因を並べると、ローカル判断モデルの実用に必要な条件が3つ見えます。

![判断モデルに必要な3つの条件](/images/local-decision-conditions.png)

**1. 較正された確率**

Layaは確率を返しますが、その数字で判断を切り分けられません。ECE 0.469は「確率が飾り」の状態です。model cardのtyped-decisionsベンチマーク（0.766）と実タスク（0.075）の差が示すように、較正はタスクとpromptの構成に依存します。

**2. prefix cacheが効く注意機構**

54問のスキルは共通のprefixを持ちます。cacheが効かなければ1問ごとに12,000字を全量処理します。qwen3.5のhybrid線形注意はこの再利用ができず、kevのflash-linear-attentionはCUDA/ROCm向けでApple Siliconでは動きません。注意機構の種類と推論環境の両方が条件になります。

**3. 12,000字が入るコンテキスト長と、その長さでの学習**

kevは384 token以下で学習されています。serving時に`num_ctx`を伸ばせても、学習との乖離が大きいと品質は保証されません。AFMはコンテキスト長そのものが4,096 tokenで、12,000字のpromptが物理的に入りません。入力長が「設定で受け入れられる」だけでなく「その長さで学習されている」こと、そして窓が十分に広いことの両方が要ります。

---

これらの結果を受けて、自律エージェント側に`DecisionBackend`という継ぎ目を入れました。環境変数`DECISION_MODEL`を設定するだけで判定面がローカルモデルに切り替わる設計です。条件を満たすモデルが出たら差し替えられる状態です。

改めて振り返ると、Jevの性能は桁違いです。較正された確率、長い入力を受け止めるコンテキスト長、prefix cacheが効く注意機構 — 判断モデルに必要な3条件をすべて満たしたうえで、1行あたり0.3秒、Opus天井の半分の精度を返す。4候補がそれぞれ別の条件で脱落したことが、Jevがあの価格と速度で何を実現しているかを浮き彫りにしました。

再開条件は4つあります。kevがMLXバックエンドを実装する、Layaが対象タスクのデータでfine-tuneされる、Jev自体がopen weightsを公開する、AFMのコンテキスト長が拡張される。どれか1つが動いた時点で、同じ150行で再測定します。

## 関連リンク

- [前回の記事: 文章を書かないモデルJevのスキル選択は、0.3秒でOpusにどこまで近づくか](https://zenn.dev/shimo4228/articles/jev-vs-opus-skill-selection)
- [systemonemodels.org — オープン代替のカタログ](https://systemonemodels.org/examples/alternatives/)
- [kev (GitHub)](https://github.com/jaredpalmer/kev) / [Laya (HuggingFace)](https://huggingface.co/convaiinnovations/laya) / [Laya (GitHub)](https://github.com/NandhaKishorM/laya)
- [Apple Foundation Models — 第3世代](https://machinelearning.apple.com/research/introducing-third-generation-of-apple-foundation-models) / [apple-fm-sdk (PyPI)](https://pypi.org/project/apple-fm-sdk/)
- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/local-decision-model-conditions.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧
