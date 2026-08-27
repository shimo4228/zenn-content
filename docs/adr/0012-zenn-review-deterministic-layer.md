# ADR-0012: Zenn レビューの決定論層を evidence script へ降ろす

## Status

Accepted

## Date

2026-08-27

本 ADR は 2026-07-05 の prose/markdown lint 撤去（`c0e98f0`）を supersede しない。撤去の対象は
prose/style 層で、本 ADR が立てるのは存在・書式・実在・一致の層。両者は別クラスとして扱う。
唯一の交差は `lint:links`（下記 Decision 4）。

## Context

Zenn チャンネルのレビュー面は `editor` / `prose-clarity-reviewer` / `fact-checker` の 3 agent と
受け入れゲート `quality-gate` で構成される。その checklist には、LLM が読んで数えるより script が
数える方が正確で安い項目が混ざっていた。

**1. 規約違反が誰にも気づかれずに 49 本まで積んだ。** 2026-08-27 に全公開記事へ Markdown 正本
リンクを追加した結果、`## Related links` の著者 hub 規約（「関連リンク節で自 repo を紹介するなら
hub を含める」）が全 68 本に発火する状態になった。実測で 49 本が違反。人間もレビュアーも
気づかなかった。存在の一致は目で数える仕事ではないという実例。

**2. `npm run validate` はほぼ何も検査していなかった。** 実体は `zenn list:articles`（記事一覧の
表示）。zenn-cli 0.4.5 に validation ロジックは同梱されているが、到達口は `zenn preview` の
ブラウザ UI だけで CLI サブコマンドが無い。`published_at` の必須性・書式、topics 件数、title
文字数、相対内部リンクの禁止はどれも未検査のまま「機械チェック済み」として扱われていた。

**3. 公開後の修正 30 件のうち、script が捕まえられたクラスは約 4 分の 1。** `git log` の
`fix(article)` を分類すると、`62c3110`（出典リンクが private repo で読者に 404）、
`56bf025`（broken external links found by lint:links）、`e6f5762`（published_at 書式）、
`2429a2b`（閉じ忘れた code fence）、`c86f78f`（Zenn slug 要件）が決定論クラス。残りは語調・
事実訂正・タイトル選択で、reviewer の領分だった。

## Decision

**1. 3 分類で境界を引く。** 判定の入力が構造・書式・実在・一致なら script、意図・忠実性・
両面性・妥当性なら reviewer、script が数えて LLM が解釈するなら hybrid。迷う項目は semantic に
倒す — 誤って機械化した項目は偽陰性を「検査済み」の顔で通す。

**2. `scripts/zenn_evidence.py` を evidence モードで置く。** JSON 出力・判定しない・exit 0。
出力は 3 層に分ける。

- `deviations` — contract が述べる規則の違反
- `grandfathered` — 同じ規則の違反だが、検査導入前に公開済みの記事のもの。報告するが
  deviation に数えない（lint を初日から赤くしない）
- `signals` — hybrid 層。register 混在、self-link の位置、段落密度。reviewer が解釈する

置き場は review-to-lint §3 の既定（`skills/<owner>/scripts/`）から外して repo の既存 uv
sub-project に置く。検査対象がこの repo の channel contract で cross-repo 性が無く、global
`writing-ecosystem` は RFC-0005 row 3 で「設計安定後」に保留されているため。流動中の global 正本へ
接木すると drift 負債になる。

**3. 免除境界は実測で決める。** 記事 70 本全件に当ててから確定した。

| 実測 0 件（初日から緑） | frontmatter 必須 field / `published_at` の存在と書式 / topics 件数・lowercase / type enum / emoji 単一 / 相対内部リンク / `:::` 開閉均衡 / code fence 均衡 / 画像実在 / 用語表 / 正本リンクの slug 一致 / 個人 path / secret |
|---|---|
| grandfathered | 本文 H1 開始 5 / title 60 字超 3 / code fence の language 無し 6 ブロック（2 記事） |
| 今回 0 にした | 著者 hub 併記 49 → 0（遡及追加） |

**偽陽性として除外した検出**は 2 つとも実測が根拠。

- 個人 path を素朴な `/Users/` で見ると 3 件ヒットするが、全部 `/Users/you/` `/Users/hanma/` の
  説明用プレースホルダで偽陽性 100%。実ユーザー名の混入は 0 件だった。検出はユーザー名ベースに限定
- 見出しと用語表は fenced code block を除外しないと誤検出する。bash コメント `# foo` が本文 H1 に
  見えたのが 2 記事、prh.yml の設定例が意図的に列挙した誤用語を拾ったのが 1 記事

**4. `lint:links` は `--online` flag として戻す。** 2026-07-05 の `c0e98f0` で撤去されたが、これは
textlint プラグイン実装だったための巻き添えであって、signal が低かったからではない。実害を
捕まえた実績が 2 件ある（`56bf025`、`62c3110`）。既定は offline 完結で、ネットに触るのは
`--online` を明示したときだけ。

**5. reviewer の薄化は project 側に配線する。** `editor` は他 project と共有する global agent なので
Zenn 固有の Step 0 を書き込まない。配線先は 3 箇所。

- channel 表 Zenn 行の Deterministic checks 列 → `quality-gate` が Procedure 3 で自動的に拾う
- `zenn-format` の Validation and handoff に Step 0（script 実行 → deviations を findings へ転記 →
  目視で数え直さない）
- `publish-article` の Validate target（deviations 1 件でも公開操作を始めない）

**6. commit hook / verify.sh へは配線しない。** 記事を触らない commit にも課税する
（review-to-lint §5）。この repo は husky + lint-staged で常時配線して撤去した経緯があり、
同じ形に戻さない。実行座標は writer skill のステップと公開前ゲート。

**7. 著者 hub と正本リンクは併記する。** 行き先が違う — 正本リンクは書いたもののコーパスへ、
hub は作ったものの DOI 付き repo 群へ。Zenn の記事ページは hub へのリンクを `<a href>` として
持たない（`githubUsername` は `__NEXT_DATA__` の JSON 値のみ、profile card のリンク先は Zenn 内
`/shimo4228`）ため、本文末の 1 行が唯一の導線になる。

## Review-when

- `writing-ecosystem` の設計が安定し、RFC-0005 row 3 の global 束が実施されたとき — 本 script の
  汎用部分（fence 除外パーサ、register カウント、self-link 位置）が global 側と重複するので、
  どちらを正本にするか引き直す
- `grandfathered` が 0 になったとき — 免除層そのものを畳めるか見る
- Zenn CLI が validation サブコマンドを公開したとき — Decision 3 の実測 0 件群のうち
  frontmatter 系を載せ替えられるか見る
- `deviations` が公開前に一度も引っかからない状態が 3 ヶ月続いたとき — 形骸化として
  検査項目を削るか、commit 面への配線を再訪する
- 記事本文へ AI 生成物の開示要件が Zenn 側の規約として入ったとき — 開示 block の存在検査は
  deterministic なので script 側へ移す

## Alternatives Considered

**`zenn-validator` を採用する。** 公式 `zenn-dev/zenn-editor` の一部。単独 package の最終公開が
2023-04-12 で 3 年以上動いていない。ロジックは zenn-cli 0.4.5 に同梱されているが CLI 到達口が無く、
内部を直接叩く形になる。カバー範囲は frontmatter schema・slug・ローカル画像リンクの 4 項目で、
いずれも本 corpus では実測 0 件。載せ替えコストに見合わない。repo 固有の規約（正本リンク、hub 併記、
相対内部リンク禁止、用語表、title 字数）は外部ツールが原理的にカバーしない。

**textlint / markdownlint を戻す。** 2026-07-05 に「Lint の中身がしょうもない」（低シグナル ×
偽陽性摩擦）として撤去した判断を覆さない。本 ADR が扱うのは prose/style ではなく存在・構造で、
そもそも同じ層ではない。

**`--gate` を付けて blocking にする。** evidence モードのまま置く。判定は fresh-context の
reviewer と著者が持つ、という repo の既存の分業（ADR-0011 で判定器を畳んだ判断）と揃える。
blocking が要ると分かってから足す。

**既公開の grandfathered を今回まとめて直す。** title 60 字超 3 件は検索流入と既存被リンクに
影響するため触らない。H1 5 件と fence 6 ブロックは表示に影響しないが、直す動機が「lint を緑に
したい」しかない。免除層があれば済む。

## Consequences

- 公開前に数える作業が reviewer から script へ移る。`editor` の Review Criteria は意味的項目
  （中心命題・因果線・証拠の役割・AI slop・技術的正確性）に集中する
- `npm run validate` が実質何も見ていなかった状態が解消される。channel 表の Deterministic checks 列が
  実際に検査になる
- **偽陽性の設計が資産になる**。プレースホルダ path、code block 内のコメントと設定例は
  fixture としてテストに固定した。同じ誤検出が再発すると 4 本のテストが落ちる
- 検査項目が増えるほど「script が見ているから大丈夫」の錯覚が育つ。`signals` を判定に使わない
  こと、`grandfathered` を blocking にしないことがその歯止め
- global `writing-ecosystem` 側の lint 化（RFC-0005 row 3）が来たとき、汎用部分の重複を
  引き直す作業が発生する。Review-when に条件として置いた
- script 1 本 + テスト 1 本（131 tests、coverage 98%）が保守対象に増える。uv sub-project の
  既存 gate に乗るので独立した保守面は作らない
