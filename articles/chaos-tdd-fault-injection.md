---
title: "LLM エージェントに fault injection TDD を入れたら silent failure が3件出た"
emoji: "🧪"
type: "tech"
topics: ["llm", "testing", "pytest", "hypothesis", "エージェント"]
published: true
published_at: 2026-07-16 09:00
---

LLM を組み込んだパイプラインには、こういう壁があります。

- LLM が微妙に形の違う JSON を返す。パースは成功するのに、結果だけが空になる
- ローカル LLM の応答が途中で切れていた（`done_reason=length`）ことに数日後に気づく
- ログには `outcome="error"` としか残っておらず、レート制限なのか timeout なのか判別できない

共通するのは、**テストは全部通っているのに、本番で黙って壊れる**ことです。処理は止まらず例外も飛ばないまま、結果やその記録が静かに劣化する——この記事ではこれを silent failure と呼びます。

筆者が運用しているローカル LLM の CLI エージェントでも、この族の障害が 5 回繰り返されました。5 回とも事前のテストでは捕まらず、事後デバッグで判明しています。そこで「運用障害の履歴から fault カタログ（障害の類型表）を起こし、障害をわざと注入するテストを先に書き、それを通す最小ガードを同じ PR で入れる」進め方を導入しました。分類としては **fault injection testing（障害注入テスト）× TDD** です。着想元の chaos engineering（わざと障害を起こして耐性を確かめる手法）から何を借り、何を借りなかったかは本文で整理します。

初回適用で、既存の約 1800 本のテストが見逃していた silent failure が 3 件見つかりました。

> **この記事でわかること**: daemon 不要・決定論・pytest ネイティブで、単一プロセスの Python アプリに fault injection testing を入れる型（fault カタログ → RED → GREEN）と、初回適用で実際に出た silent failure 3 件の中身

## 前提

- Python 3.13 / pytest 9.0（検証時点。特別な新機能は使わないので近いバージョンなら動きます）
- [hypothesis](https://hypothesis.readthedocs.io/en/latest/) 6.156.6 / [responses](https://github.com/getsentry/responses) 0.26.0（いずれも dev 依存として追加）
- 対象: `requests` で LLM サーバー（Ollama 等）を呼ぶ単一プロセスの Python アプリ
- LLM 呼び出しが Protocol などで差し替え可能な層になっていること（なっていなければ、最初の一歩はその層を切ることです）

なお、この記事は前作[「AIエージェントの『なぜその判断？』に答えるオブザーバビリティ設計3パターン」](https://zenn.dev/shimo4228/articles/agent-observability-patterns)の続編です。前作が「エージェントの判断を**記録する**側」の話だとすると、本作は「その記録チャネルを**assert する**側 + 障害を**事前に注入する**側」の話になります。単体でも読めます。

## きっかけは chaos engineering、採ったのは fault injection testing

筆者のエージェントは SNS（Moltbook）上で自律的に活動し続けるものです。運用を続けるかぎり、次にどんな障害に遭遇するかは事前に分かりません。「想定外の障害に強い運用」を作る仕組みを探すなかで行き着いたのが chaos engineering でした。

ただし、正典である [Principles of Chaos Engineering](https://principlesofchaos.org/) の 5 つの実践原則と照らすと、そのままなぞってはいません。

| 正典の実践原則 | 今回 |
|---|---|
| 定常状態の仮説を立てて検証する | ○ 採った（実行ログ（telemetry）チャネルへの assert） |
| 実世界のイベントを変動させる | △ 半分（fault は運用履歴由来だが、注入は既知カタログの決定論的再生） |
| 本番環境で実験する | ✕ 却下 |
| 実験を自動化して継続的に走らせる | △ CI で自動実行はするが、derandomize しているので「未知を探索する実験」ではなく「既知を固定する回帰テスト」 |
| 爆発半径（影響範囲）を最小化する | ○ 極端な形で採った（テスト内注入なので本番への影響はゼロ） |

本番実験を却下した理由は 2 つです。第一に、対象は単一のローカルプロセスで、落とすべき「冗長化されたインスタンス群」がそもそもありません。第二に、エージェントが蓄積するログは再生成できない一次データで、本番へのランダム注入はそれを壊すリスクがあります。ランダム探索を見送ったのは、CI を flaky にしないためです。

chaos engineering の核は「テスト（既知の期待挙動の assert）」ではなく「**実験**（未知の弱点の発見）」なので、本番実験とランダム探索を欠いた時点で chaos engineering とは呼べません。冒頭の通り、分類は fault injection testing × TDD です。chaos engineering から借りたのは、「障害カタログを実世界のイベントから起こす」「定常状態を観測チャネルで assert する」という 2 つの考え方だけです。

ツールも分散系の定番ではなく、pytest の上に組みます。導入前の外部調査の結論です。

| 候補 | 判定 | 理由 |
|---|---|---|
| chaostoolkit / toxiproxy | 却下 | 宣言的な実験ランナー・常駐ネットワークプロキシ。分散トポロジ向けで、単一ローカルプロセスには対象のスケールが合わない |
| pytest 系の障害注入プラグイン | 却下 | 実用可能なものが存在しない（例: pytest-disrupt は TODO のみの scaffold） |
| [agent-chaos](https://github.com/deepankarm/agent-chaos) | 参考にのみ使用 | 概念的には最も近いが、Anthropic SDK / DeepEval / pydantic-ai に結合しており、pytest 統合もローカルバックエンド対応もない |
| hypothesis + responses + 自作の注入バックエンド | **採用** | 既存のテスト基盤（pytest）の上に、依存 2 つで乗る |

こうして「**テストの中で決定論的に障害を注入する**」方針に落ちました。daemon もプロキシも要らず、pytest がそのまま実行環境になります。

ただし、見送った 2 要素（探索・実験）は捨てたのではなく、**手法を chaos engineering 側へ拡張するときの入口**として残してあります——PR の CI は決定論のまま nightly 実行だけ randomize + seed 記録にする二層構成（見つけた失敗系列は seed から再現して `@example` で pin）と、sandbox で実パイプラインをランダム注入モードで回す実験です。今回のパイロットが決定論側に寄せたのは、「既知の障害履歴すら assert されていない」状態を先に潰すためです。既知の穴を塞ぎ終えたら、この 2 つの入口から広げていくつもりです。

## 手法の型 — fault カタログがテスト仕様になる

進め方は 3 ステップです。

1. **カタログ**: 運用障害の履歴を fault クラス（障害の類型）に分類し、既存テストとの差分を取る。未テストの類型が fault カタログになる
2. **RED**: 各 fault を注入したとき「システムがどう振る舞う**べき**か」を先にテストで主張する。現状の実装では落ちる（ここが TDD の RED）
3. **GREEN**: そのテストを通す最小ガードを、テストと**同じ PR** で入れる

ポイントは、fault カタログが仕様書を兼ねることです。「timeout が来たら telemetry に `error_kind=timeout` が残るべき」「形の違う JSON が来たら理由コード付きで棄権（abstain）すべき」という望ましい挙動が、実行可能なテストとして固定されます。

普通の TDD との違いは入力の起こし方だけです。機能要件からテストを書くのではなく、**障害履歴からテストを書く**——それ以外は RED → GREEN の規律をそのまま使います。

## fault カタログは想像ではなく障害履歴から起こす

「どんな障害を注入すべきか」を想像で列挙すると、実際には起きない障害のテストを量産しがちです。今回は過去の運用障害 5 件（コンテキスト長超過による silent truncation、`done_reason=length` の途中切れ、重複排除の無発火、外部 API のレート制限、スクレイピング対象の CAPTCHA 化）を出発点にして、「同じ族の障害のうち、既存テストが覆っていないもの」を洗い出しました。

注意点として、履歴の 5 件と fault クラスは 1:1 対応ではありません。履歴から取り出したのは「LLM か外部 I/O が想定外の応答を返すと、パイプラインが黙って劣化する」という共通の族で、その族に属する障害のうち**既存テストが覆っていない**5 クラスを起こしています。

結果が次の 5 クラスです。

| # | fault クラス | 既存テストの状態 |
|---|---|---|
| F1 | 生成中の read-timeout | `ConnectionError` のみカバー。ストリーム途中の timeout は未テスト |
| F2 | embedding API の障害 — 転送層の失敗（429・timeout）と、成功応答の内容不正（次元不揃い・行数不足） | 未テスト |
| F3 | 構文的には valid な JSON だが期待 schema に違反（トップレベル型違い・キー違い・非文字列要素） | 未テスト |
| F4 | LLM サーバー自身からの HTTP 429 | 別の外部 API クライアント側のみカバー。LLM バックエンド側は未テスト |
| F5 | flapping（成功と失敗が交互・連続する系列） | 単発の失敗→回復のみカバー |

導入前後の変化はこうなりました。

| 指標 | Before | After |
|---|---|---|
| fault クラスを直接注入するテスト | 0/5（上表の通り、近縁ケースの部分カバレッジのみ） | 5/5（決定論的な fault injection テスト 32 本） |
| telemetry の障害種別判別 | 不可（全部 `outcome="error"`） | 7 種の `error_kind` |
| 抽出失敗の可観測性 | 黙って欠落 | 理由コード 3 種 + 理由別の集計サマリ |
| フルスイート | — | 1832 passed / 1 skipped |

テスト本数の 32 は、`pytest --collect-only` で実測した値です（本記事の数値は、いずれも執筆時に再実測しています）。

## 実装 — 差し替え点 2 つと決定論の規律

### 注入する場所は既存の 2 箇所に固定する

障害の注入には seam（本番コードを書き換えずにテスト側から実装を差し替えられる継ぎ目）が要ります。今回は既存の 2 箇所だけを使い、**本番コード側に注入用のフックは一切足さない**と決めました。テスト対象のパイプラインは、自分がテストされていることを知りません。

1. **LLM バックエンドの Protocol** — テスト側に `ChaosBackend` を実装して差し替える
2. **requests の HTTP 層** — `responses` ライブラリで HTTP レスポンスを偽装する

`ChaosBackend` は「何回目の呼び出しでどの fault を起こすか」のリスト（schedule）で駆動します。クラス名・ファイル名に chaos が残っているのは着想時の命名の名残です。また、コード中の `FAULT_VOCABULARY` は注入の最小単位（プリミティブ）で、F1-F5 の fault クラスとは粒度が違います——1 つのクラスは複数のプリミティブの組み合わせでテストします。

```python:tests/chaos.py（抜粋・簡約。完全版は関連リンクの公開 skill を参照）
# fault 語彙は順序付きタプル（順序が不定だと seed 導出の決定論が崩れる）
FAULT_VOCABULARY = (OK, NONE, EMPTY, EXC_TIMEOUT, EXC_CONNECTION, TRUNCATED, SHAPE_VIOLATION)

@dataclass
class ChaosBackend:  # LLMBackend Protocol 準拠
    schedule: List[str] = field(default_factory=list)
    calls: List[dict] = field(default_factory=list)

    @classmethod
    def from_seed(cls, seed: int, n: int, weights=None) -> "ChaosBackend":
        rng = random.Random(seed)
        vocab = list(weights.keys()) if weights else list(FAULT_VOCABULARY)
        wts = list(weights.values()) if weights else None
        return cls(schedule=rng.choices(vocab, weights=wts, k=n))

    def generate(self, prompt, system, num_predict, format, *, temperature=1.0, think=False):
        idx = len(self.calls)
        self.calls.append({"prompt": prompt, "num_predict": num_predict})
        fault = self.schedule[idx] if idx < len(self.schedule) else OK
        if fault == NONE: return None
        if fault == EXC_TIMEOUT: raise requests.exceptions.ReadTimeout("chaos")
        if fault == TRUNCATED: return BackendResult(text=self._ok_text(idx), finish_reason="length")
        ...
```

schedule は明示リストでも seed 導出でも作れますが、どちらも**実行前に中身を確認できます**。「ランダムに壊す」のではなく「この系列で壊れることが仕様」という扱いです。

### hypothesis は決定論プロファイルで走らせる

fault の組み合わせを手で列挙する代わりに、property-based testing（個別の入出力例ではなく「どんな入力でも成り立つ性質」を主張するテスト手法）を使います。ただし CI で flaky にならないよう、hypothesis を決定論モードに固定します。

```python:tests/conftest.py（抜粋）
# database=None が抑止するのは example DB のみ。constants/unicode キャッシュは
# HYPOTHESIS_STORAGE_DIRECTORY の退避が必要（hypothesis の import 前に）
os.environ.setdefault("HYPOTHESIS_STORAGE_DIRECTORY", str(_TEST_HOME / ".hypothesis"))
from hypothesis import settings
settings.register_profile("ci", derandomize=True, max_examples=50, deadline=None, database=None)
settings.load_profile("ci")
```

`derandomize=True` で毎回同じケース列が生成されます。実際に fault injection テスト一式を 2 回連続で実行して、出力が同一であることを確認しました。

もう 1 つの決定論規律として、**latency 系の fault は実 sleep ではなく `ReadTimeout` 例外の注入で表現**します。この呼び出し経路では timeout の観測可能な結果は「`ReadTimeout` を捕捉して処理する」ことに尽きるので、その範囲では例外注入で等価に検証でき、テストは 0 秒で走ります。実 sleep + 短い timeout 設定の方式は flaky 化するので避けました。なお、ストリーミング中の部分出力の後始末など**実時間でしか露出しない挙動はこの方式では検証できない**ので、そこが対象なら別の手当てが要ります。

### RED を書く — 望ましいガード挙動を先に主張する

F3（valid JSON だが shape 違反）の RED はこう書きました。

```python:tests/test_distill_chaos.py（抜粋）
class TestParsePatternsShapeViolationFuzz:
    @given(raw=non_patterns_json())
    @example(raw='{"patterns": [123]}')   # str() 昇格の実バグを pin
    @example(raw="null")                  # json.loads("null") is None の罠を pin
    def test_wrong_shape_abstains_with_no_patterns(self, raw):
        patterns, mode = _parse_patterns(raw)
        assert mode == "shape_violation"
        assert patterns == []
```

`@given` が「どんな shape 違反 JSON でも棄権すべき」という性質を主張し、`@example` が既知の失敗形を恒久的な回帰テストとして pin します。この 2 つの `@example` が、次の節の silent failure ①② そのものです。

## 初回適用で出た silent failure 3 件

RED を書いた時点で、既存実装の 3 つの穴が露出しました。①②は処理結果が黙って劣化するタイプ、③は観測チャネル側——障害そのものは記録されるのに、原因究明に要る種別情報が黙って失われるタイプです。

### ① 数値が文字列に昇格して schema 違反が素通りする

- **現象**: LLM が `{"patterns": [123]}` のような非文字列要素を返すと、旧実装は各要素を `str(item)` で文字列化していたため、`"123"` が正当なパターンとして通過し得た
- **なぜ silent か**: JSON として valid なので parse は成功し、`str()` 昇格は例外を出さない。schema 違反の痕跡がどこにも残らない
- **ガード**: 全要素に `isinstance(item, str)` を要求し、違反したら `shape_violation` の理由コード付きで棄権。`@example(raw='{"patterns": [123]}')` で回帰を pin

### ② `json.loads("null")` は `None` を返す

- **現象**: レスポンス body が JSON の `null` だと、`json.loads` は例外を出さずに `None` を返す。旧実装は「parse 結果が `None` = parse 失敗」を判定に使っていたため、valid な JSON がパース失敗扱いになり、本来通るべきでない fallback 経路（テキストの箇条書きスキャン）へ誤ルートしていた
- **なぜ silent か**: fallback 経路は「JSON でない応答への救済」として正当に存在するので、誤ルートしてもログ上は正常な fallback と区別できない
- **ガード**: `_JSON_PARSE_FAILED = object()` という識別用 sentinel を導入し、「parse に失敗した」と「`None` が parse された」を型レベルで分離

### ③ telemetry が障害の種別を全部 `error` に潰す

- **現象**: 429・timeout・接続失敗・不正 body のどれが起きても、telemetry には `outcome="error"` としか残らず、オフラインでの障害分析ができなかった
- **なぜ silent か**: エラー自体は記録されているので「何かが失敗した」ことは見える。潰れているのは**種別**で、これは実際に障害調査をするまで欠落に気づけない
- **ガード**: 例外を分類する `_classify_request_error` を入れ、失敗行にのみ `error_kind` フィールド（`timeout` / `connection` / `http_<status>` / `bad_json` / `bad_url` / `request_error` / `backend_exception` の 7 種）を追加。既存の `outcome` の値集合は変えない追加のみの変更なので、過去ログの分析コードは壊れません

3 件に共通するのは、**正常系の顔をした異常系**であることです。例外が出るバグは普通のテストで捕まりますが、この 3 件はどれも「処理は最後まで走る。結果や記録が静かに間違う」ため、正常系（happy path）のテストをいくら足しても捕まりませんでした。fault を注入して「望ましい失敗の仕方」を assert する RED だけが、この穴を露出させます。

:::details ハマりポイント 2 つ（hypothesis のキャッシュ / circuit breaker × property test）

**`.hypothesis/` が `database=None` でも生成される**

プロファイルで `database=None` を指定しても、repo 直下に `.hypothesis/constants/` などのキャッシュが出現します。[settings リファレンス](https://hypothesis.readthedocs.io/en/latest/reference/api.html)にある通り `database=None` が抑止するのは example DB だけで、constants キャッシュ等は `HYPOTHESIS_STORAGE_DIRECTORY` 配下に無条件で書かれます。対処は、hypothesis を import する**前に**この環境変数をテスト用 tempdir へ向けること（上のコード例に含めています）。

**circuit breaker が property test の予測を壊す**

「成功数 = schedule 内の OK の数」という性質を主張したところ、失敗 fault が 5 連続する schedule でだけ崩れました。原因は本番コード側の circuit breaker（連続失敗時に呼び出しを遮断する仕組み。このプロジェクトでは連続 5 失敗で open）。breaker が open すると以降の OK 呼び出しが backend に届かないため、正しい挙動なのに exact-count の性質が成り立ちません。対処は 2 段構えにしました。breaker を作動させる schedule を `trips_circuit()` フィルタで exact-count の性質から除外し、代わりに「どんな schedule でもクラッシュしない」という弱い性質を全 schedule に残す。

:::

## まとめ — 事後デバッグを事前の仕様に変える

- silent failure は happy path のテストでは捕まらない。**障害を注入して「望ましい失敗の仕方」を assert する**テストだけが捕まえる
- fault カタログは想像でなく**運用障害の履歴**から起こす。履歴 5 件 → 未テストの fault クラス 5 つ → 決定論的な fault injection テスト 32 本
- 単一プロセスのローカル LLM アプリなら、daemon もプロキシも不要。**hypothesis + responses + 差し替え用バックエンド**で pytest の上に乗る
- 決定論の規律（`derandomize` / seed 導出 schedule / 実 sleep 禁止）で、乱数と実時間という 2 大 flakiness 源を注入テストから排除できる（実測: 2 回連続実行で出力同一）
- ガードはテストと**同じ PR** で入れる。fault schedule が仕様、ガードはそれを満たす実装
- chaos engineering は着想元であって分類ではない。借りたのは「カタログを実世界のイベントから起こす」「定常状態を観測チャネルで assert する」の 2 点で、本番実験と未知の探索は意図的に後回しにした（nightly randomize と sandbox 実験が、chaos 側へ拡張するときの入口）

今回の型（fault 語彙・ChaosBackend・hypothesis プロファイル・RED テンプレート）は、汎用化した Claude Code skill として公開しています。他のパイプラインへの持ち込みは、そちらが入口として使えます。

## 関連リンク

- [chaos-tdd-fault-injection](https://github.com/shimo4228/chaos-tdd-fault-injection) — 本記事の型を汎用化した公開 skill（repo・ADR 上の実装時の呼び名は「chaos-TDD」）
- [ADR-0077: Chaos-TDD Fault Injection](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0077-chaos-tdd-fault-injection.md) — 設計判断の一次資料（英語。同ディレクトリに日本語版あり）
- [前作: AIエージェントの「なぜその判断？」に答えるオブザーバビリティ設計3パターン](https://zenn.dev/shimo4228/articles/agent-observability-patterns)
- [自律エージェントをあえて M1 Mac で作る — 制約が設計を鍛えるという選択](https://zenn.dev/shimo4228/articles/small-llm-by-choice) — 本記事が属する小型 LLM 運用シリーズのハブ
- [hypothesis ドキュメント](https://hypothesis.readthedocs.io/en/latest/) / [responses](https://github.com/getsentry/responses)
- [Chaos Toolkit](https://chaostoolkit.org/) / [toxiproxy](https://github.com/Shopify/toxiproxy) — 分散システム向けの chaos ツール（本記事では対象規模の違いから不採用）
- [agent-chaos](https://github.com/deepankarm/agent-chaos) — AI エージェント向け chaos engineering の先行 OSS（fault 分類の参考にした prior art）
- [著者の GitHub](https://github.com/shimo4228) — その他のリポジトリ・ツール
