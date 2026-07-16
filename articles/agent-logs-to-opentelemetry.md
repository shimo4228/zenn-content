---
title: "AI エージェントの自前ログ、OpenTelemetry につないだら何が見える？"
emoji: "🔌"
type: "tech"
topics: ["opentelemetry", "observability", "jaeger", "llm", "エージェント"]
published: false
---

> **この記事でわかること**: エージェント本体のコードを 1 行も変えずに、既存の JSONL ログを OpenTelemetry のトレースに変換して Jaeger で可視化する方法。あわせて、LLM 呼び出しログと GenAI semantic conventions（LLM 向けの標準属性名）の対応表と、変換で信頼できないテキスト（外部由来の本文）を持ち込まないための設計を共有します。

AI エージェントに OpenTelemetry（テレメトリ = システムの動作データを記録・送出する仕組みの標準仕様。以下 OTel）を入れたい。でも、こんな壁はないでしょうか。

- **SDK と Collector の常時運用は、個人規模のエージェントには重い。** 監視ダッシュボードを見る運用チームがいるわけではない
- **すでに自前の構造化ログがある。** 同じ情報を二重に計装したくない
- **LLM 向けの標準属性（GenAI semantic conventions）がまだ Development ステータス**で、どこまで乗っていいか判断できない

筆者が運用している [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) も同じ状況でした。Moltbook（AI エージェント同士が投稿・コメントし合う SNS）で自律的にポストやコメントを書く、ローカル LLM エージェントです。フィードから読むテキストは他のエージェントが書いたもので、プロンプトインジェクション（本文に命令を紛れ込ませて読み手のエージェントを操る攻撃）が日常的に飛び交う、セキュリティ的には悪夢のような環境です。だからこそ、外部との入出力を監査ログに全量残す設計にしていました。

出した答えは「runtime には入れず、**すでに持っている監査ログを後からトレース（1 回の処理の流れを、時刻付きの区間の集まりとして記録したデータ）に変換する**」です。転送には OTLP（OTel の標準転送プロトコル）を使います。

本体無改変・依存 2 つの小さな変換スクリプトで、手元のログが Jaeger（トレースを可視化する OSS ビューア）の waterfall（処理の区間を時系列に積んだ滝状の図）として見えるようになりました。障害があった日は、開いた瞬間にわかる絵になります。

なお、この記事は前作[「AIエージェントの『なぜその判断？』に答えるオブザーバビリティ設計3パターン」](https://zenn.dev/shimo4228/articles/agent-observability-patterns)の続編です。前作で「トレースやメトリクスが既定で教えてくれるのは『リクエストが何をしたか』まで」と書きました。本作はその続きで、**では自前ログと OTel 標準は何をつなげるのか**を実際に変換して確かめた話です。単体でも読めます。

## 前提

- 変換対象: エージェントが出力済みの append-only（追記専用）JSONL ログ（LLM 呼び出しテレメトリ / API 監査 / CAPTCHA solver 監査の 3 種類）
- Python 3.10+、パッケージ管理は uv
- 依存は 2 つだけ: `opentelemetry-sdk` + `opentelemetry-exporter-otlp-proto-http`
- ビューア: Jaeger v2.19.0（単一バイナリ。Docker 不要、保存はメモリ内）
- 変換スクリプトは公開しています: [contemplative-agent-otel](https://github.com/shimo4228/contemplative-agent-otel)（読者の手元のログ形式に合わせて `records.py` / `mapping.py` を差し替える前提の、全体で 800 行ほどの小さな実装です）

## 入れる・入れないは「誰がテレメトリを読むか」で決まります

最初に判断軸を 1 つに絞ります。OTel のトレースと筆者の監査ログは、同じイベントを記録していても**読む人（消費者）が違います**。

| | OTel トレース | 筆者の監査ログ |
|---|---|---|
| 主な読者 | ダッシュボードを見る人・アラート | 障害調査で再実行する replay スクリプト |
| プロンプト等の本文 | **デフォルト非記録**（opt-in） | **全量保存**（base64 + sha256） |
| データの性質 | サンプリングされうる・揮発してよい | append-only・全件・消さない |
| 答える問い | 「今なにが遅い？ 壊れてる？」 | 「あの判断はなぜそうなった？」 |

右列は監査ログ一般の性質ではなく、筆者が障害のオフライン再現を目的に選んだ設計です。読者のログが全量保存とは限りません — 一般化できるのは「**消費者が違えば保持方針も変わる**」という判断軸の方です。

象徴的なのが本文の扱いです。GenAI semantic conventions は、プロンプトや応答の本文を**デフォルトで記録しない**と定めています（ビューアの画面に出るものだから、機微情報を運ばないのが既定）。一方、筆者の監査ログは**逆に全量保存**します。障害調査では「判断が見たバイト列そのもの」がないとオフラインで再現できないからです。

つまりどちらが正しいという話ではなく、**同じイベント・違う消費者・逆の保持方針**です。この整理をすると、選択肢は 2 択ではなくなります。

1. runtime に OTel を入れる（運用監視が要るなら）
2. 何もしない
3. **既存ログを後からトレースに変換する** — 標準語彙との接続と可視化だけを、runtime に触れず手に入れる

この記事は 3 の実装です。

## 手持ちのログは標準語彙とほぼ 1:1 でした

LLM 呼び出しごとに 1 行書いている自前テレメトリのフィールドを、GenAI semantic conventions の属性名と突き合わせたのが次の表です。

| 自前ログのフィールド | OTel 属性 |
|---|---|
| `model` | `gen_ai.request.model` |
| `prompt_eval_count`（入力トークン数） | `gen_ai.usage.input_tokens` |
| `eval_count`（生成トークン数） | `gen_ai.usage.output_tokens` |
| `done_reason`（`stop` / `length`） | `gen_ai.response.finish_reasons`（配列型なので `[done_reason]` に包む） |
| `num_predict`（生成上限） | `gen_ai.request.max_tokens` |
| `temperature` | `gen_ai.request.temperature` |
| `error_kind`（`timeout` / `http_429` 等） | `error.type` |
| `ts` + `duration_ms` | span（トレースの 1 区間）の開始・終了時刻 |
| `caller`（どの処理段からの呼び出しか）、`prompt_sha256` など | 対応なし → 独自 namespace `ca.audit.*` |

ほぼ 1:1 で写りました。今回のようなシンプルな LLM 呼び出しログ（モデル・トークン数・停止理由・パラメータ）なら、記録したくなる項目は設計者が違っても同じ集合に収束しやすいのだと思います（ツール呼び出しや streaming、ルーティングまで記録するログではこうはいきません）。

標準語彙に乗せる価値はここにあります。属性名が `gen_ai.usage.input_tokens` なら、外部のツールも人も説明なしで読めます。

面白いのは**写らなかった側**です。`caller`（障害調査でログを処理段ごとに集計するためのキー）や `prompt_sha256`（本文を保存せずに同一プロンプトを突き合わせるためのハッシュ）には標準の対応がありません。標準が表現できない部分は、そのまま「運用監視には要らないが、障害のオフライン再現には要る情報」のリストになっていました。

:::details Development ステータスへの実務対応
GenAI semantic conventions（以下 semconv）は執筆時点（2026-07）で Development ステータスです（[正本リポジトリ](https://github.com/open-telemetry/semantic-conventions-genai)）。`opentelemetry-semantic-conventions` パッケージにも属性名定数はありますが、`_incubating` というアンダースコア付き（= 不安定）の import パスの下にあります。

変換スクリプトではパッケージから import せず、**属性名を文字列定数として自前で定義し、参照した semconv のバージョンをコメントで固定**しました。標準が動いたら追従はこのファイル 1 箇所で済みます。
:::

## 変換スクリプトの設計は 3 点だけです

変換の本体は「JSONL を読んで、過去のタイムスタンプで span を作る」です。設計判断は 3 つでした。

### 1. span は過去の時刻で作れます

OTel SDK は span の開始・終了時刻を epoch ナノ秒で明示指定できます。ログの `ts` と `duration_ms` からそのまま復元します。

```python:emit.py（抜粋・簡約）
# ログの記録時刻で span を作る（変換スクリプトの核）
span = tracer.start_span(
    name,                      # 例: "text_completion gemma4:e4b"
    context=parent_ctx,
    kind=kind,
    attributes=attrs,
    start_time=start_ns,       # ts を epoch ns に変換した値
)
if is_error:
    span.set_status(Status(StatusCode.ERROR, error_type))
span.end(end_time=end_ns)      # start_ns + duration_ms
```

duration を記録していないログ（API 監査・solver 監査）は**ゼロ幅の span** にしました。それらしい幅を推定で与えると、計測していないレイテンシを捏造することになります。Jaeger はゼロ幅 span を細いマーカーとして描くので、実 duration を持つ LLM span と見分けもつきます。「duration を持たないログはゼロ幅になる」という事実自体が、ログスキーマへのフィードバックでした。

### 2. トレースのまとまりは「時間の空白」で再構成します

トレースは本来、実行時に発行する ID で span を束ねます。過去ログにはそれがありません。そこで、3 種類のログを時刻順にマージし、**一定時間（既定 300 秒）の空白が空いたら新しいトレース**として区切りました。スケジュール起動のエージェントは「数分の活動 → 長い無音」を繰り返すので、この区切りが実際の 1 実行とよく一致します。

ただしこれは推定です。トレースのルート span に `ca.convert.grouping = "time-gap"` という属性を付けて、**計測ではなく再構成であること**をデータ自身に言わせています。

逆に言えば、これは変換作業から得られたいちばん実用的なフィードバックでした。ログの各行に**実行単位の ID**（OTel の trace ID に相当するもの）を 1 フィールド足せば、この再構成は推定から計測に変わります。

SDK を入れなくても「実行に ID を振っておく」という機構だけは先に借りる価値があります。

筆者のエージェントにはこの記事を書く過程で実装しました — 全監査ログが共有する書き込み関数 1 箇所に、`run_id`（プロセス単位）と `session_id`（エージェントセッション単位）をスタンプする形です。変換側は `run_id` があれば ID で束ね、無い過去ログだけ時間ギャップに切り替えます。ログ設計をこれからやる方は、最初から入れておくことをおすすめします。

### 3. 信頼できないテキストは変換の入口で捨てます

監査ログには、外部から来た生テキスト（CAPTCHA の問題文、サーバのエラー応答ボディ）が base64 で入っています。冒頭で書いたとおり、このエージェントの入力はプロンプトインジェクションが飛び交う SNS 由来 — 「外部から来た文字列は攻撃入力かもしれない」が既定です。こうしたテキストを span 属性に載せると、**攻撃者が制御可能な文字列が Jaeger の画面（= スクリーンショット、= この記事）にそのまま流れ込みます**。

変換では、パーサの段階で本文を捨てて sha256 ハッシュと分類コード（`http_400` 等）だけを通します。「載せるためのフラグ」も作りません。さらに、テスト用の fixture 全件の全属性値を走査して本文断片が現れないことを assert する回帰テストを置きました。「後で気をつける」ではなく、載らない構造にしてから可視化する、が安全側です。

なお、ここでの目的は本文の秘匿ではなく「外部由来の文字列を画面に運ばない」ことです。sha256 は同じ入力を突き合わせるための相関用の識別子であって、秘匿化ではありません（短い定型文なら総当たりで元の文字列を推測できます）。機密データを扱うログなら、鍵付きハッシュ（HMAC）にするか、ハッシュ自体を載せない選択も検討してください。

## Jaeger で眺めます — 障害の日は開いた瞬間にわかりました

Jaeger v2 は単一バイナリで、起動すると OTLP を受けてメモリ内に保持します。

```bash
# ビューア起動（Docker 不要。終了すればデータも消える）
curl -sLO https://github.com/jaegertracing/jaeger/releases/download/v2.19.0/jaeger-2.19.0-darwin-arm64.tar.gz
tar xzf jaeger-2.19.0-darwin-arm64.tar.gz
./jaeger-2.19.0-darwin-arm64/jaeger    # OTLP :4318 / UI :16686

# 変換して送信（実行例）
contemplative-agent-otel --date 2026-07-15
# => emitted 1031 spans across 5 runs -> http://localhost:4318
```

通常の日はこう見えます。1 本のトレースが 1 回のエージェント実行で、実 duration を持つ LLM 呼び出し（`text_completion gemma4:e4b`、36 秒や 1.3 分）と、ゼロ幅の API 呼び出しが時系列に並びます。

![通常日のトレース。agent run のルート span の下に、LLM 呼び出しと API 呼び出しが時系列で並ぶ waterfall](/images/agent-logs-to-opentelemetry-waterfall.png)

span を開くと、先ほどの対応表がそのまま属性として見えます。`gen_ai.usage.input_tokens: 1560` のような標準属性と、`ca.audit.caller: core.skill_selection` のような独自属性が同居しています。

![span 詳細。gen_ai.* の標準属性と ca.audit.* の独自属性が並ぶ](/images/agent-logs-to-opentelemetry-span-genai.png)

そして障害があった日（実際に LLM バックエンドがリトライストームを起こした日）を変換すると、こうなります。

![障害日の検索結果。30442 spans / 33 errors のトレースが最上位に出ている](/images/agent-logs-to-opentelemetry-incident.png)

通常の実行が数十〜数百 span のところ、**30,442 span・33 エラーのトレースが 1 本**そびえています。この日のログファイルはサイズも通常日の 30 倍近くありました。数字としてはすでにログにあった情報ですが、「開いた瞬間に異常な日だとわかる」のはトレース可視化の固有の強みです。

エラーの中身も追えます。CAPTCHA の解答がサーバに拒否された実行では、`captcha solve` と `POST /verify` がペアで赤くマークされます。エラー本文は変換で捨てているので、画面に出るのは `error.type: http_400` という分類だけです。

![エラーを含む実行。captcha solve と POST /verify に赤いエラーマーク](/images/agent-logs-to-opentelemetry-error-run.png)

:::details 落とし穴: 30,442 span を一気に送ると黙って捨てられる
障害日の変換で、送信側の `BatchSpanProcessor` が既定キュー長 2048 を超えた span を **警告 1 行だけ残して破棄**しました（`Queue full, dropping Span.`）。リアルタイム計装なら妥当な自衛ですが、オフライン一括変換では「全件送る」が正しい仕様です。

変換対象の件数は送信前に分かっているので、キュー長を件数に合わせて確保して解決しました。一括変換で SDK を使う場合は、既定値がリアルタイム前提であることに注意してください。
:::

## OTel から何を借りて、何を見送ったか

最後に、この取り組み全体で OTel の各要素をどう判断したかを一覧にします。「標準を入れる/入れない」の一括判断ではなく、**要素ごとに借りる・見送るを選べる**というのが今回いちばんの学びでした。

| OTel の要素 | 判断 | 理由 |
|---|---|---|
| GenAI semantic conventions の語彙（`gen_ai.*`） | ✅ 採用 | 外部のツールも人も説明なしで読める。属性名を写すだけなので依存ゼロ |
| 実行 ID の機構（trace ID / session ID 相当） | ✅ 採用（`run_id` / `session_id` をログに実装） | 1 フィールドでトレースの再構成が計測に変わる |
| OTLP（転送プロトコル） | ✅ 採用（オフライン変換の出口として） | どのビューアとも話せる共通言語。依存は 2 パッケージで済む |
| runtime SDK 計装 | ❌ 見送り | 既存の監査ログと二重計装になる。本体の依存も増える |
| Collector の常駐運用 | ❌ 見送り | 単一プロセス・個人規模には重い。変換は必要なときに都度実行で足りる |
| 本文のデフォルト非記録（redaction） | 部分採用 | トレース側では従う（信頼できないテキストを画面に運ばない）。監査ログ側は逆に全量保存 — オフライン再現に必要なため |
| semconv パッケージからの属性名 import | ❌ 見送り | Development 段階で import パスが不安定（`_incubating`）。文字列定数 + バージョン注記で pin |

## まとめ

- OTel を「入れるか入れないか」の 2 択にせず、**既存ログの事後変換**という第三の選択肢を試しました。本体無改変・依存 2 つで、Jaeger の waterfall・エラー表示・標準属性がすべて手に入ります
- 自前の LLM 呼び出しログは GenAI semantic conventions と**ほぼ 1:1** で写りました。写らなかったフィールドは「障害のオフライン再現に要る情報」のリストとして残ります
- トレースは運用監視向け（本文は非記録が既定）、監査ログは障害再現向け（本文は全量保存）。**消費者が違えば保持方針は逆になる**ので、変換では信頼できない本文を入口で捨てるのが安全です
- 過去タイムスタンプの span 生成・ゼロ幅 span・時間空白によるトレース再構成、の 3 点を押さえれば、時刻と実行のまとまりを復元できる構造化ログなら同じ方法でつなげます。そしてログに実行 ID を 1 フィールド足しておけば、再構成そのものが不要になります — SDK を入れない場合でも、この機構だけは OTel から先に借りる価値があります（筆者は本記事の執筆過程で実装しました）

## 関連リンク

- [contemplative-agent-otel](https://github.com/shimo4228/contemplative-agent-otel) — 本記事の変換スクリプト（対応表・テスト込み）
- [ADR-0078: OTel Connection via Vocabulary Mapping and Offline Export](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0078-otel-connection-via-vocabulary-and-offline-export.md) — この判断の一次資料（[ADR-0075](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0075-observability-by-default.md): 監査ログを機能と同じ PR で出荷する側の判断）
- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai) — 標準語彙の正本（Development ステータス）
- [前作: AIエージェントの「なぜその判断？」に答えるオブザーバビリティ設計3パターン](https://zenn.dev/shimo4228/articles/agent-observability-patterns) — 監査ログ側の設計 3 パターン
- [自律エージェントをあえて M1 Mac で作る — 制約が設計を鍛えるという選択](https://zenn.dev/shimo4228/articles/small-llm-by-choice) — 本記事が属する小型 LLM 運用シリーズのハブ
- [筆者の GitHub](https://github.com/shimo4228) — エージェント本体・関連リポジトリの一覧
