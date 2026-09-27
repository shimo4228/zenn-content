# Plan: 計器シリーズ 4 本目 — 「30 行サンプルは 11 秒の連打に盲目」記事（ゼロベース書き直し）

## Context

`articles/log-readers-census.md` は旧台帳で書いた初稿で、著者通読の途中で前提が変わり破棄対象。
新台帳 `drafts/article-context_instrument-series-projection_2026-09-12.md` を正本に、構成・文章を
引き継がず組み直す。系列は review-chain-damping → lint-as-subtraction →
instrument-consumption-plan の続編（同 repo、Contemplative Agent）。

この plan は writing-ecosystem Canonical workflow の Step 1〜2（Route / theme-reviewer /
editorial brief）までを固め、著者の brief 確認で止まる。初稿以降は GO 後。

## Route

- Channel: Zenn（`articles/*.md`、ですます、直接指示・具体観察、段落 3 文まで、タイトル 50 字原則）
- Slug: `log-projection-blind-by-construction`（旧 `log-readers-census.md` は削除。旧 slug は
  「読み手の census」が軸で、新稿の軸「投影が構造的に隠す形」と合わないため変える）
- 前提の検証済み事実（git で確認、2026-09-12）:
  - 採点改良 `ba95917` 2026-03-09（バグの起点）、llm-calls 出荷 `99c454f` 2026-06-10（テレメトリの起点）
  - 新 census の REGISTRY は `_census_registry.py` が所有、ADR-0107 D2 で導入（前編公開 8/31 の後）

## Theme review（theme-reviewer の findings、2026-09-12）

- One question: Yes。「見える」と「見えない」は別の 2 発見でなく、比較単位をセッションに固定した
  1 つの設計判断の両面（ADR-0110 Consequences "by construction, not by oversight"）
- Non-obviousness: Yes。「時間軸を足せば見える」で終わらず、同じ判断が慢性故障を原理的に隠す
- Discourse gap: Yes。log sampling が burst を落とす一般論・canonical log line・MAD 記事は既存。差分は
  無人 LLM が読む個人エージェントの自己書き込み JSONL、期待値 0.09 行の実測、28 点で MAD=0 に
  退化する具体ケース
- Reader connection: **Unverified** — 判断則が本文の言葉になっていない → brief の Higher Ground で結晶化
- One-artifact fit: **Unverified** — S16 のガバナンス劇（bounce / 3 分割 / ADR 衝突）は別テーマ → out of scope
- Durability: Yes、条件付き。慢性側の修理効果は 9/18・9/25 まで未検証 → 急性と慢性を同格の
  Before/After にしない（深化 Q4）
- 深化の問いへの答え（brief に反映）: Q1 登録簿の反転は「原則の撤回」でなく「退けた対象の違い」で書く /
  Q2 週跨ぎ比較を建てない理由は「4 点で限界は引けない、読む側が median 行を並べる」/ Q3 較正 3 つは
  このログ形状への経験的チューニングと明示 / Q4 急性は実証・慢性は設計時の宣言と段階を分ける /
  Q5 判断則を一文で置く

## Editorial brief（著者確認で止まる）

```markdown
Reader: 自分のエージェントやバッチが書くログを、週次で LLM（または人間）に読ませている engineer。
  問い:「読み手を付けたのに、なぜ故障が写らなかったのか。次の未知の故障が写る投影は何か」
Channel: Zenn（articles/*.md）
Central thesis: ログの投影は「何を見せるか」を決めた瞬間に、構造的に見えない故障の形を必ず持つ。
  30 行サンプルは行の間隔を消して 11 秒の連打に盲目になり、置き換えた「同じ週の他セッションとの差」
  は毎回起きる故障を消す。だから投影を建てる作業には、見せる形を決めることと、それが隠す形を
  投影の出力自身に書くことの両方が入る。
Causal spine:
  観察 — 9/12 朝、全ログに週次の読み手（census + Phase 0）を建てた。同日午後、記事を書くための
    手集計で、セッション末尾 11 秒に `GET /home` ×13 の連打（RFC-0036）が見つかった。
    census はこれを写せない: 4,035 行から 30 行、期待値 0.09 行。出力 130 KB の 97% は問いの無い行
  緊張 — 読み手はいた。問いを決めない窓（サンプル）も置いた。前編の「消費者を名指しせよ」は
    満たしている。それでも写らない。足りなかったのは読み手でも問いでもなく、投影の時間軸
  機序 1（見えるようにする）— サンプルは分布を見せるが間隔を消す。監視の定石を借りて単位を
    セッションにし、category ごとに件数 / 1 分最大 / 最小間隔の 3 軸を列にする。列は宣言せず
    データから導出する（`/home` は cycle と 1:1 でない、消えた category は 0 の列として残る —
    別モデルの反証で採用）。外れ値は同じ週の 28 セッションの median / MAD。連打は syslog 式に
    `×N in Ks` へ畳む。結果: RFC-0036 が z −19.6 で浮き、hunting window に `GET /home ×13 in 11s`
    と、RFC 本文に無かった `GET /feed ×12 in 10s` が出た。出力は 130 KB → 24 KB、2 回走らせて
    byte-identical
  機序 2（同じ判断が隠す）— 同一投稿の再採点（RFC-0032）は 2026-03-09 から全セッションで
    起きていた。テレメトリは 06-10 から写していたが、同じ週の他セッションと比べる限り departure は
    ゼロ。新投影はこれを「by construction, not by oversight」と出力ヘッダに書き、慢性の形は
    書かれた不変条件（Redundancy）と ledger の絶対値を読む側に委ねた。修理の効果は 9/18・9/25 の
    ledger 行で初めて読める（公開時点で未検証）
  較正の但し書き — 最小間隔は 4 event 以上、gap と合計は log1p、MAD=0 の床は列の 1 単位。
    3 つとも実データで単純形が失敗した順に足した、このログ形状への経験的チューニング
  反転の扱い — 前編は「登録簿は作らない」と書いた。今回の REGISTRY は各ログの「週次の問い」を
    データとして持つ行で、読み手（毎週の無人セッション）と編集者（土曜 gate の人間）と撤去条件を
    ADR に書いた。前編が退けたのは「消費者を名指しできない台帳」で、原則は変わっていないと
    言い直す。隠さず 1 節で
  Higher Ground（判断則）— ログを LLM に読ませるなら、(1) 行でなくセッション（リクエスト）を
    1 行にする、(2) 見せる形を決めた瞬間に、その形が構造的に隠す故障を出力自身に 1 行書く、
    (3) 慢性は差分でなく不変条件で拾う。効果の検証は 2 回の週次読み後
Selected evidence:
- C1 / C2: 旧投影の形と、期待値 0.09 行（観察の数式）
- C3 / C4: 130,547 B / 443 行、97% がサンプル（ADR の「約 200 行」は実測と違った）
- C6: 28 セッション、api-audit 4,035 行、llm-calls 4,519 行、score_relevance median 44.5（規模の提示）
- C7 / C8 / C20: 新投影での RFC-0036 の見え方（z −19.6、×13 in 11s、未記載の /feed ×12）
- C9: RFC-0032 は差分に写らない（機序 2 の核）、ADR-0110 の逐語引用 1 文
- C13 / C21: `/home` は cycle と 1:1 でない → cycle 数を主張しない、列は導出（機序 1 の根拠）
- C14: 24,463 B / 311 行、byte-identical、`_b64` 0（Before / After）
- C19: 較正 3 つ（但し書き）
- C22: 週跨ぎ比較は建てない（architect: Don't build、4 点で限界は引けない、median 行を読む側が並べる）
- git 確認: 採点改良 2026-03-09 `ba95917`、llm-calls 出荷 2026-06-10 `99c454f`（2 つの起点）
- 「弱いところ」に 1 行: 読み手は 616 行 → 1,079 行 3 モジュール + pandas 依存（C15）。前編の
  「退役のために建てた行数」の罠がここでも起きうる
Out of scope:
- S16 build セッションの経緯（bounce、500 行、3 分割、ADR 番号衝突、rebase、claims.py の cwd）
- spy テストが空 assert だった件（C17。1 行の言及可、節にしない）
- 監視古典の転用表の網羅、依存ポリシー（pandas / scipy、ADR-0109）、sqlite 試作（C26）
- 週別 median 系列（C10、⚠ 未検証）、comment report 全文読みの存廃（C23）、既製品照合（C24）
- cycle 数の中央値 6 / 最大 14 / 間隔 343 秒（新台帳に無く、新稿は cycle 数を主張しないので使わない）
```

著者が前稿で指摘した 6 点の当て方: 前提（Moltbook 上で採点 → 閾値で upvote / コメント、行動だけ
重複確認）は冒頭の 1 段落 / 数字は上の Selected evidence のみ / 起点 2 つは機序 2 で日付付きで分ける /
内部語（REGISTRY・週次チェーン・Phase 0・ledger）は初出で定義し、反転は 1 節 / 各節は目的 → 手段の順 /
段落 3 文まで。

## GO 後の手順（実行順）

1. `articles/log-readers-census.md` を `git rm` ではなく `rm`（未追跡）で削除し、
   `articles/log-projection-blind-by-construction.md` を新規作成（`published: false`、`published_at` 未設定）
2. 初稿: brief の causal spine に 1 節 1 役割で割り付け、採用 evidence を紐付ける。数字は台帳の
   実測のみ（C2 / C3 / C6 / C7 / C8 / C14 / C15 / C16 / C20）。C10 の週別系列と C26 の sqlite 試作は
   「試作で確認」以上に書かない
3. 使う前に再測するもの: 台帳に無い数字は使わない。cycle 数（中央値 6 / 最大 14）と間隔 343 秒は
   旧セッションの実測で新台帳に無いので、**使うなら** RFC-0036 Motivation（最大 14）と新 census の
   ledger 行で再測、使わないなら書かない（新稿の軸では不要の見込み）
4. `npm run validate`、`npm run evidence -- articles/<slug>.md`（deviations 0）
5. 並列レビュー: `editor` / `prose-clarity-reviewer` / `fact-checker`（fact-checker には台帳の
   Claims Register と一次資料 path を渡す）→ 反映 → 著者通読 → 内容 GO
6. GO 後: `headline-craft` → `title-reviewer` → 著者がタイトル選択 → `/quality-gate`
7. memory `log-readers-census-pipeline.md` を新 slug と状態で更新

## Verification

- `npm run validate` exit 0、`npm run evidence -- articles/<slug>.md` deviations 0
- 3 reviewer の verdict: editor CRITICAL 0 / clarity PASS / fact-checker INACCURATE 0
- 本文の数値が台帳の Claims Register の行番号に 1:1 で辿れること（fact-checker に確認させる）
- 段落 4 文以上が 0（`awk` で段落ごとの「。」数を数える）
